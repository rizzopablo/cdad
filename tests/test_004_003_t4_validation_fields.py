#!/usr/bin/env python3
"""RED tests for 004-003 T4 (PD-8 + PD-11 + review-t3 mandatory debt F1/F2):
the per-task validation plan is part of the declared plan-tasks block, and the
block's format has a single canonical home.

Contract: docs/specs/004-003-planning-procedures/spec.md — PD-8 ("Cada tarea
declara pruebas focales, regresiones afectadas, gate de integración y
responsable de ejecutar; el trabajo sin código declara comprobaciones
observables adecuadas al artefacto, sin inventar una suite de software. Puede
referenciar una estrategia común una vez") and PD-11 (code-less cycles declare
an observable check, not a fabricated software suite). Debt: review-t3.md F1
("variantes de fence (indentado, sin cierre, con tag, \\r\\n, segundo bloque)
caen en el camino 'bloque ausente' → rc=0, publicado, checks saltados — fallar
ruidoso") and F2 ("el formato del bloque no tiene hogar canónico — registrarlo
una vez en planning-contract-draft.md §4 y desambiguar T3/G5"). Plan row T4:
"un plan sin el campo se rechaza; un plan Go/sin-código con comprobación
observable pasa"; files: `planning-contract-draft.md` §4,
`stage-2-specification.md`, `tests/test_004_003_t4_validation_fields.py`.

Black-box: the CLI is invoked as a subprocess; implementation sources are
never read. Every project is a temporary fixture; the real HOME and the
repository state are never touched. The F2 check reads a docs/ file only.

Oracle decisions (interfaces defined by this RED, derived from the spec and
the review debt — superseding T3's declared leniency, which this contract
closes):

- Required block: a declared draft plan (contract `draft-plan`) MUST declare
  its per-task validation plan inside the canonical fenced ```plan-tasks
  block. A plan without the block (or without the per-task validation field)
  is rejected: rc != 0, `ERROR: ...` diagnostic, empty stdout, no packet
  published, unchanged state, unchanged tree. Absence is no longer lenient
  (T4 postcondition; the T1/T2/T3 no-block fixtures are grandfathered there).
- Per-task validation fields, inside the canonical ```plan-tasks block
  (JSON object with a `tasks` array):
  * code task (declares non-empty `files`): REQUIRED non-empty `focal_tests`
    ("pruebas focales"); every task REQUIRES present `regressions`
    ("regresiones afectadas" — an empty list declares "none affected"),
    non-empty `integration_gate` ("gate de integración") and non-empty
    `owner` ("responsable de ejecutar").
  * code-less task (no `files` or empty): REQUIRED non-empty
    `observable_checks` ("comprobaciones observables adecuadas al artefacto,
    sin inventar una suite de software") instead of `focal_tests`; it still
    requires `regressions` (present), `integration_gate` and `owner`.
  * common strategy once (PD-8): the block may declare a non-empty,
    plan-level `validation_strategy`; an individual task may then reference
    it ONCE with the literal value `"@validation_strategy"` instead of
    repeating content in `focal_tests`, `regressions` or `integration_gate`.
  The checks remain structural only (PD-2): the presence/emptiness of declared
  fields, never their quality — quality is the reviewer's judgment.
- Fail-loud fences (F1): a document that contains any `` ```plan-tasks `` open
  not matching the canonical open (at line start) is NOT silently treated as
  "block absent": the five malformed variants of review F1 — indented open,
  open without closing fence, open carrying a tag suffix (`​```plan-tasks
  json`), CRLF line endings, and a second plan-tasks block — are rejected
  loud: rc != 0 with an `ERROR: ...` diagnostic naming `plan-tasks`, and
  nothing is published.
- Canonical home (F2): `docs/epics/epic-004-single-source-planning/
  planning-contract-draft.md` §4 (owner of the plan-file fields per G5)
  declares the ```plan-tasks block format ONCE (a single literal fence in the
  whole document, inside §4) including the per-task validation fields of
  PD-8/G5 (pruebas focales, regresiones, gate de integración, responsable,
  comprobaciones observables) and stating the block's mechanical/structural
  role — the T3/G5 relationship written once, no competing second manual.
  Field/parameter names, not exact prose, are pinned.
- Canonical home, schema fidelity (F2, review-t4 F-B): §4.1 declares the
  parameter names the schema really accepts — `observable_checks` (the
  code-less field), `validation_strategy` (the plan-level strategy key) and
  the literal reference `@validation_strategy` — as literal tokens, not only
  the Spanish prose ("comprobaciones observables", "estrategia común"): the
  record cannot drift away from the schema again.
- Distribution/consumption (review-t4 F-A): the G5 consumer
  `skills/cdad-cycle/references/stage-2-specification.md` references the
  canonical home §4.1 exactly once and never re-declares the block format
  (no second manual; PD-12 / invariant 6).
- Strategy reference in regressions (review-t4 F-C): a task MAY reference the
  common strategy with the literal `@validation_strategy` in `regressions`
  too, as the oracle promises; a declared regression reference is not a
  defect.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
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
STRATEGY_REF = "@validation_strategy"


def plan_bytes(tasks: list[dict], *, strategy: str | None = None) -> bytes:
    """A declared draft plan whose per-task validation plan lives in the
    canonical fenced plan-tasks block."""
    doc: dict = {"tasks": tasks}
    if strategy is not None:
        doc["validation_strategy"] = strategy
    block = json.dumps(doc, indent=2, sort_keys=True)
    return (
        DRAFT_PLAN_BYTES
        + PLAN_TASKS_FENCE_OPEN.encode()
        + block.encode()
        + b"\n"
        + PLAN_TASKS_FENCE_CLOSE.encode()
    )


def task(
    task_id: str,
    *,
    consume: list[dict] | None = None,
    produce: list[dict] | None = None,
    depends_on: list[str] | None = None,
    parallel: list[str] | None = None,
    files: list[str] | None = None,
    focal_tests: list[str] | None = None,
    regressions: list[str] | None = None,
    integration_gate: str | None = None,
    owner: str | None = None,
    observable_checks: list[str] | None = None,
) -> dict:
    entry: dict = {
        "id": task_id,
        "consume": consume or [],
        "produce": produce or [],
        "depends_on": depends_on or [],
        "parallel": parallel or [],
        "files": files or [],
    }
    if focal_tests is not None:
        entry["focal_tests"] = focal_tests
    if regressions is not None:
        entry["regressions"] = regressions
    if integration_gate is not None:
        entry["integration_gate"] = integration_gate
    if owner is not None:
        entry["owner"] = owner
    if observable_checks is not None:
        entry["observable_checks"] = observable_checks
    return entry


CODE_VALIDATION = {
    "focal_tests": ["tests/test_004_003_t3_plan_checks.py"],
    "regressions": [],
    "integration_gate": "suite completa una vez por GREEN",
    "owner": "RED: test-writer; GREEN: implementer",
}

# Shape A (positive control): every task declares its validation plan inline.
# Structure follows T3's valid control (acyclic, matched contracts, declared
# parallel pair with disjoint files) so a rejection can only come from the
# validation-plan rules and never from older structural defects.
VALID_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        parallel=["t3"],
        files=["tests/only_t1.py"],
        **CODE_VALIDATION,
    ),
    task(
        "t2",
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
        **CODE_VALIDATION,
    ),
    task(
        "t3",
        produce=[{"artifact": "contract-b", "contract": "b-v1"}],
        parallel=["t1"],
        files=["tests/only_t3.py"],
        **CODE_VALIDATION,
    ),
]

# Defect A — the whole validation-plan field is absent: a plan with T3-clean
# structure but no plan-tasks block at all (the leniency T4 closes).
NO_BLOCK_BYTES = DRAFT_PLAN_BYTES

# Defect B — the field is half-declared: the block exists but the tasks omit
# the per-task validation fields (block presence alone is not a validation
# plan; the schema must demand the PD-8 fields per task).
MISSING_FIELDS_TASKS = [task("t1"), task("t2"), task("t3")]

# Defect C — a code-less task (no files) that invents neither a software suite
# nor an adequate observable check: owner/gate/regressions declared, but
# neither focal_tests nor observable_checks.
NOCODE_WITHOUT_CHECKS_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "dictamen-003-002", "contract": "e-v1"}],
        regressions=[],
        integration_gate="recorrido instalado en raíz aislada",
        owner="reviewer + orquestador",
    ),
]

# PD-11 (code-less, positive): a plan whose only task produces a documentary
# artifact, declares no files and validates through observable checks
# adequate to the artifact — no fabricated suite, no focal_tests.
NOCODE_WITH_CHECKS_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "dictamen-003-002", "contract": "e-v1"}],
        observable_checks=[
            "informe de revisión de plan + cambios registrados en "
            "docs/specs/004-003-planning-procedures/evidence/ (inspectable)"
        ],
        regressions=[],
        integration_gate="recorrido instalado en raíz aislada",
        owner="reviewer + orquestador",
    ),
]

# PD-11 (colocated Go, positive): a task whose tests live beside the code
# (`*_test.go`, not under tests/) passes the same schema — the per-task
# validation plan does not discriminate test layouts.
GO_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        files=["pkg/store.go", "pkg/store_test.go"],
        focal_tests=["TestStoreAppend (pkg/store_test.go)"],
        regressions=[],
        integration_gate="suite completa una vez por GREEN",
        owner="RED: test-writer; GREEN: implementer",
    ),
]

# PD-8 (common strategy referenced ONCE): the block declares the strategy at
# plan level; individual tasks reference it instead of repeating content.
STRATEGY_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        parallel=["t3"],
        files=["tests/only_t1.py"],
        focal_tests=[STRATEGY_REF],
        regressions=[STRATEGY_REF],
        integration_gate=STRATEGY_REF,
        owner=CODE_VALIDATION["owner"],
    ),
    task(
        "t2",
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
        focal_tests=CODE_VALIDATION["focal_tests"],
        regressions=[STRATEGY_REF],
        integration_gate=STRATEGY_REF,
        owner=CODE_VALIDATION["owner"],
    ),
    task(
        "t3",
        produce=[{"artifact": "contract-b", "contract": "b-v1"}],
        parallel=["t1"],
        files=["tests/only_t3.py"],
        focal_tests=[STRATEGY_REF],
        regressions=[STRATEGY_REF],
        integration_gate=STRATEGY_REF,
        owner=CODE_VALIDATION["owner"],
    ),
]
STRATEGY_TASKS_STRATEGY = (
    "Estrategia común del proyecto: focal por unidad + suite completa una "
    "vez por GREEN; RED test-writer, GREEN implementer (ver stage-3-tdd)."
)

# F1 — canonical block with a structural defect that the checks must see, so a
# variant can never be "published with the checks skipped".


class F1Fixture:
    """The five malformed plan-tasks fence variants of review F1.

    Each carries valid T4 validation fields AND a T3 structural defect
    (unproduced input t9 → contract-b), so:
    - fail-loud remedy → rejected, diagnostic names plan-tasks;
    - normalization remedy must at least not publish with checks skipped
      (the objective pins fail-loud: rc != 0, ERROR, no publication).
    """

    @staticmethod
    def malformed(inner_tasks: list[dict] | None = None) -> dict[str, bytes] | dict[str, str]:
        base = [
            task(
                "t1",
                produce=[{"artifact": "contract-a", "contract": "a-v1"}],
                files=["tests/only_t1.py"],
                **CODE_VALIDATION,
            ),
            task(
                "t2",
                consume=[{"artifact": "contract-b", "producer": "t9", "contract": "b-v1"}],
                files=["tests/only_t2.py"],
                **CODE_VALIDATION,
            ),
        ]
        doc = {"tasks": base}
        return doc, json.dumps(doc, indent=2, sort_keys=True)


F1_DOC, F1_BLOCK = F1Fixture.malformed()


def block_bytes(block_text: str) -> bytes:
    return (
        DRAFT_PLAN_BYTES
        + PLAN_TASKS_FENCE_OPEN.encode()
        + block_text.encode()
        + b"\n"
        + PLAN_TASKS_FENCE_CLOSE.encode()
    )


def f1_variants() -> dict:
    second_block_text = F1_BLOCK.replace('"t9"', '"t9-alt"')
    return {
        # v1 — fence open indented (leading whitespace): not the canonical open.
        "f1a_indentada": DRAFT_PLAN_BYTES
        + b"  " + PLAN_TASKS_FENCE_OPEN.encode()
        + F1_BLOCK.encode() + b"\n" + PLAN_TASKS_FENCE_CLOSE.encode(),
        # v2 — open without closing fence: the declaration never terminates.
        "f1b_sin_cierre": DRAFT_PLAN_BYTES
        + PLAN_TASKS_FENCE_OPEN.encode() + F1_BLOCK.encode() + b"\n",
        # v3 — open carrying a tag suffix: a different fence line entirely.
        "f1c_con_tag": DRAFT_PLAN_BYTES
        + b"```plan-tasks json\n" + F1_BLOCK.encode() + b"\n"
        + PLAN_TASKS_FENCE_CLOSE.encode(),
        # v4 — CRLF line endings: the canonical open never matches bare \n.
        "f1d_crlf": b"\r\n".join(
            [
                DRAFT_PLAN_BYTES.replace(b"\n", b"\r\n").rstrip(b"\r\n"),
                b"```plan-tasks",
                json.dumps(F1_DOC, sort_keys=True).encode(),
                PLAN_TASKS_FENCE_CLOSE.encode(),
            ]
        )
        + b"\r\n",
        # v5 — a second plan-tasks block: duplicated declaration, loud.
        "f1e_segundo_bloque": block_bytes(F1_BLOCK)
        + b"\n\n"
        + block_bytes(second_block_text),
    }


class PlanValidationCase(unittest.TestCase):
    def project(self) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t4-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")

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

    def prepare_valid_control(self) -> None:
        """The honest surface is green: a plan declaring the per-task
        validation plan (shape A) is accepted and renders its packet."""
        control = self.project()
        self.write_plan_bytes(control, plan_bytes(VALID_TASKS))
        result = run_prepare(PACKET_CLI, *control.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "honest validation-plan surface missing (T4 control): "
            + result.stderr.decode(errors="replace"),
        )
        self.assertTrue(
            (control.out_dir / control.packet_id() / "PACKET.md").is_file(),
            "the valid plan did not render its packet",
        )

    def assert_rejected_without_publication(
        self, project: PrepareProject, plan_bytes_: bytes, tokens: tuple[str, ...]
    ) -> None:
        self.write_plan_bytes(project, plan_bytes_)
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


class TestPd8ValidationPlanIsRequired(PlanValidationCase):
    def test_pd8_plan_without_the_block_is_rejected(self) -> None:
        """PD-8 + plan.md T4: "un plan sin el campo se rechaza". A declared
        draft plan with T3-clean structure but NO plan-tasks block is
        rejected with an ERROR diagnostic naming the missing declaration;
        nothing is published, the state is unchanged."""
        self.prepare_valid_control()

        project = self.project()
        self.assert_rejected_without_publication(project, NO_BLOCK_BYTES, ("plan-tasks",))

    def test_pd8_task_missing_validation_fields_is_rejected(self) -> None:
        """PD-8: the block's presence alone is not the field — every task must
        declare pruebas focales, regresiones afectadas, gate de integración y
        responsable. Tasks omitting the fields are rejected with a diagnostic
        naming the task id and the missing field name; nothing is published."""
        self.prepare_valid_control()

        project = self.project()
        fixture = plan_bytes(MISSING_FIELDS_TASKS)
        self.assert_rejected_without_publication(
            project, fixture, ("t1", "focal_tests")
        )

    def test_pd8_shape_a_and_common_strategy_render(self) -> None:
        """PD-8 (positives): shape A (all four fields inline) and the
        strategy shape (validation_strategy declared ONCE at block level,
        tasks referencing it) are both accepted and render their packets."""
        for fixture_name, fixture, strategy in (
            ("shape A", plan_bytes(VALID_TASKS), None),
            (
                "common strategy once",
                plan_bytes(STRATEGY_TASKS, strategy=STRATEGY_TASKS_STRATEGY),
                STRATEGY_TASKS_STRATEGY,
            ),
        ):
            with self.subTest(fixture=fixture_name):
                project = self.project()
                self.write_plan_bytes(project, fixture)
                result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{fixture_name} rejected: {result.stderr.decode(errors='replace')}",
                )
                self.assertTrue(
                    (project.out_dir / project.packet_id() / "PACKET.md").is_file(),
                    f"{fixture_name} did not render its packet",
                )


class TestPd11CodelessAndColocatedGoAreAccepted(PlanValidationCase):
    def test_pd11_codeless_plan_with_observable_checks_renders(self) -> None:
        """PD-11/AC-5 + PD-8: a code-less cycle (produces a documentary
        artifact, no files) declares observable checks adequate to the
        artifact — no fabricated software suite, no focal_tests — and is
        accepted."""
        self.prepare_valid_control()

        project = self.project()
        fixture = plan_bytes(NOCODE_WITH_CHECKS_TASKS)
        self.write_plan_bytes(project, fixture)
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "a code-less plan with observable checks was rejected: "
            + result.stderr.decode(errors="replace"),
        )

    def test_pd11_colocated_go_plan_with_declared_checks_renders(self) -> None:
        """PD-11/AC-5: a colocated Go task (`*_test.go` beside the code) with
        a declared per-task validation plan passes the same schema."""
        self.prepare_valid_control()

        project = self.project()
        fixture = plan_bytes(GO_TASKS)
        self.write_plan_bytes(project, fixture)
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "a colocated Go plan was rejected: " + result.stderr.decode(errors="replace"),
        )


class TestPd8CodelessTaskWithoutObservableChecksIsRejected(PlanValidationCase):
    def test_pd8_codeless_task_without_checks_is_rejected(self) -> None:
        """PD-8: "el trabajo sin código declara comprobaciones observables
        adecuadas al artefacto". A code-less task that declares neither
        observable checks nor focal tests is rejected: a validation plan with
        a hole is not a validation plan."""
        self.prepare_valid_control()

        project = self.project()
        fixture = plan_bytes(NOCODE_WITHOUT_CHECKS_TASKS)
        self.write_plan_bytes(project, fixture)
        self.assert_rejected_without_publication(
            project, fixture, ("t1", "observable_checks")
        )


class TestF1MalformedFencesFailLoud(PlanValidationCase):
    def test_f1_malformed_plan_tasks_fences_fail_loud(self) -> None:
        """Review-t3 F1: an indented fence, an unterminated fence, a tagged
        fence open, CRLF line endings and a second plan-tasks block all
        carry the ```plan-tasks token without matching the canonical open.
        None of them may fall into the "block absent" path (rc=0, published,
        checks skipped): each is rejected loud — rc != 0, `ERROR: ...`
        naming plan-tasks — and nothing is published. The honest control is
        the same content in the canonical fence, which renders."""
        self.prepare_valid_control()

        for name, data in f1_variants().items():
            with self.subTest(variant=name):
                project = self.project()
                self.assert_rejected_without_publication(project, data, ("plan-tasks",))


class TestF2BlockFormatHasCanonicalHome(unittest.TestCase):
    def test_f2_block_format_declared_once_in_planning_contract_s4(self) -> None:
        """Review-t3 F2: the ```plan-tasks block format has its canonical,
        editable home in the owner of the plan-file fields —
        docs/epics/epic-004-single-source-planning/planning-contract-draft.md
        §4 ("Ficha mínima de unidad ejecutable") — where it is declared ONCE
        (a single literal fence in the whole document, inside §4) and where
        the PD-8/G5 per-task validation fields (pruebas focales, regresiones,
        gate de integración, responsable, comprobaciones observables) and the
        block's mechanical/structural role (the T3/G5 disambiguation) are
        written once, with no competing second manual."""
        repo_root = Path(__file__).resolve().parents[1]
        doc = (
            repo_root
            / "docs"
            / "epics"
            / "epic-004-single-source-planning"
            / "planning-contract-draft.md"
        )
        self.assertTrue(doc.is_file(), f"canonical home missing: {doc}")
        text = doc.read_text(encoding="utf-8")

        section4 = text.split("## 4. Ficha mínima de unidad ejecutable", 1)
        self.assertGreater(len(section4), 1, "the §4 section is missing from the doc")
        body = section4[1]
        body = body.split("## 5. Criterios de revisión del plan", 1)[0]

        # The fence format itself is declared inside its canonical home (§4).
        self.assertIn(
            "plan-tasks",
            body,
            "the §4 canonical home does not declare the plan-tasks block format",
        )
        # The PD-8/G5 per-task validation fields are named in §4.
        for token in (
            r"pruebas focales",
            r"regresiones",
            r"gate de integraci[oó]n",
            r"responsable",
            r"comprobaciones observables",
        ):
            self.assertRegex(
                body,
                token,
                f"the §4 canonical home does not name the required field {token!r}",
            )
        # The T3/G5 disambiguation: §4 states the mechanical/structural role
        # of the block (what the checks read), not only the validation plan.
        self.assertRegex(
            body,
            r"mec[áa]nic|checks|estructur|productor",
            "the §4 canonical home does not state the block's mechanical role",
        )
        # Single source (PD-12/invariant 6): the literal fence declaration is
        # written exactly once in the whole document.
        self.assertEqual(
            text.count("```plan-tasks"),
            1,
            "the plan-tasks fence format is declared more than once "
            "(competing copies); it must have one canonical declaration in §4",
        )

    def test_f2b_canonical_s41_declares_schema_parameter_names(self) -> None:
        """Review-t4 F-B (PD-8/G5 fidelity): the canonical record must declare
        in §4.1 the parameter names the schema really accepts — not only the
        Spanish prose. Pinned as literal tokens so the record cannot derive
        from the schema again:
        - `observable_checks` — the code-less task field (PD-8/PD-11);
        - `validation_strategy` — the plan-level strategy key (declared once,
          PD-8 "una estrategia común");
        - `@validation_strategy` — the literal reference a task uses instead
          of repeating content.
        Spanish labels alone ("comprobaciones observables", "estrategia
        común") no longer satisfy the home: the drift it closed is precisely
        a name the prose never pinned."""
        repo_root = Path(__file__).resolve().parents[1]
        doc = (
            repo_root
            / "docs"
            / "epics"
            / "epic-004-single-source-planning"
            / "planning-contract-draft.md"
        )
        self.assertTrue(doc.is_file(), f"canonical home missing: {doc}")
        text = doc.read_text(encoding="utf-8")

        section41 = text.split("### 4.1", 1)
        self.assertGreater(len(section41), 1, "the §4.1 subsection is missing")
        body = section41[1].split("## 5. Criterios de revisión del plan", 1)[0]

        # The code-less field name the schema demands (PD-8/PD-11).
        self.assertIn(
            "observable_checks",
            body,
            "the §4.1 canonical home does not name the code-less parameter "
            "observable_checks (only Spanish prose)",
        )
        # The plan-level strategy key, distinct from the reference literal.
        self.assertIn(
            "validation_strategy",
            body.replace("@validation_strategy", ""),
            "the §4.1 canonical home does not declare the plan-level "
            "validation_strategy key (only Spanish prose or the reference "
            "literal)",
        )
        # The literal reference a task may use (PD-8, referenced once).
        self.assertIn(
            "@validation_strategy",
            body,
            "the §4.1 canonical home does not declare the literal "
            "@validation_strategy reference",
        )


class TestFAConsumerReferencesCanonicalHomeS41Once(unittest.TestCase):
    def test_stage2_consumer_references_canonical_home_once(self) -> None:
        """Review-t4 F-A (PD-12/invariant 6 + G5 distribution): the consumer
        of the per-task validation plan rule —
        skills/cdad-cycle/references/stage-2-specification.md, G5's derived
        consumer — must reference the canonical home §4.1 exactly once and
        must not re-declare the format: exactly one reference to
        planning-contract-draft.md, that reference names §4.1, and the
        consumer carries no plan-tasks fence of its own (no second manual;
        derived consumers reference, never copy)."""
        repo_root = Path(__file__).resolve().parents[1]
        consumer = (
            repo_root
            / "skills"
            / "cdad-cycle"
            / "references"
            / "stage-2-specification.md"
        )
        self.assertTrue(consumer.is_file(), f"the G5 consumer is missing: {consumer}")
        text = consumer.read_text(encoding="utf-8")

        self.assertEqual(
            text.count("planning-contract-draft.md"),
            1,
            "the consumer does not reference the canonical home exactly once "
            "(a missing or second manual defeats the single editable source)",
        )
        reference_line = next(
            line
            for line in text.splitlines()
            if "planning-contract-draft.md" in line
        )
        self.assertRegex(
            reference_line,
            r"4\.1",
            f"the single reference does not point to §4.1: {reference_line!r}",
        )
        self.assertNotIn(
            "```plan-tasks",
            text,
            "the consumer re-declares the block format (a second manual); "
            "it must only reference the canonical home §4.1",
        )


class TestFCStrategyReferenceAcceptedInRegressions(PlanValidationCase):
    def test_strategy_reference_in_regressions_renders(self) -> None:
        """Review-t4 F-C (PD-8 oracle): a task MAY reference the common
        strategy with the literal `@validation_strategy` in `regressions`
        too — the oracle promises the literal works in `focal_tests`,
        `regressions` OR `integration_gate`. A plan whose strategy reference
        appears in `regressions` (with every other validation field
        declared) is a declared plan, not a defect, and renders."""
        self.prepare_valid_control()

        regressions_task = task(
            "t1",
            produce=[{"artifact": "contract-a", "contract": "a-v1"}],
            files=["tests/only_t1.py"],
            focal_tests=CODE_VALIDATION["focal_tests"],
            regressions=[STRATEGY_REF],
            integration_gate=CODE_VALIDATION["integration_gate"],
            owner=CODE_VALIDATION["owner"],
        )
        project = self.project()
        self.write_plan_bytes(
            project, plan_bytes([regressions_task], strategy=STRATEGY_TASKS_STRATEGY)
        )
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "a task referencing @validation_strategy in regressions was "
            "rejected — the oracle allows the literal in regressions: "
            + result.stderr.decode(errors="replace"),
        )
        self.assertTrue(
            (project.out_dir / project.packet_id() / "PACKET.md").is_file(),
            "the regressions-reference plan did not render its packet",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
