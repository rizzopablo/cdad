#!/usr/bin/env python3
"""Black-box RED tests for 003-005 (Claude Code packets: port + prepare), P1-P6.

Contract: docs/specs/003-005-claude-code-packets/spec.md. The CLI is invoked as
a subprocess; implementation sources are never read. Every project is a
temporary fixture; the real HOME and the repository state are never touched.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

from tests.test_role_packet_render import PACKET_BEGIN, PacketFixture, parse_packet
from tests.test_role_packet_review_regressions import packet_and_legacy_contract_errors
from tests.test_role_packets import (
    EPIC_ID,
    EXECUTION_ID,
    FEATURE_ID,
    INSTALLER,
    PACKET_CLI,
    REPO_ROOT,
)
from tests.product_staging import product_root


BINDING_FIELDS = (
    # 004-002 T6 PRE-GREEN (PD-10): forma exacta del binding v2 publicado por
    # prepare (sin runtime/modelo de identidad; +policy_sha256).
    "id",
    "epic_id",
    "feature_id",
    "scope",
    "model_policy",
    "authority_ref",
    "policy_sha256",
)
DEFAULT_EXPECTED_OUTPUT = "Role report with the required evidence"
DEFAULT_EVIDENCE = ["modified files", "exact commands", "command output", "commit"]
DEFAULT_INVARIANTS = {
    "test-writer": ["Do not read implementation code", "Each test maps to a postcondition"],
    "implementer": ["Do not edit tests"],
    "architect": [],
    "reviewer": [],
    "scribe": [],
}
SPEC_CONTRACT = f"docs/specs/{FEATURE_ID}/spec.md"
PLAN_CONTRACT = f"docs/epics/{EPIC_ID}/plan.md"


def run_prepare(
    cli: Path, *args: str, cwd: Path = REPO_ROOT, env: dict | None = None
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(cli), "prepare", *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        check=False,
    )


# Fault injection for the review-1 race (B1): a stdlib-only sitecustomize that makes a
# foreign directory appear at the exact moment the CLI creates CDAD_TEST_RACE_TARGET.
# Every directory creation in CPython goes through os.mkdir, so this reproduces
# "the packet_id directory appears between the calculation and the mkdir"
# without reading or patching the implementation.
RACE_SITECUSTOMIZE = '''
import os

_TARGET = os.environ.get("CDAD_TEST_RACE_TARGET")
_PAYLOAD = os.environ.get("CDAD_TEST_RACE_PAYLOAD", "").encode("utf-8")
_original_mkdir = os.mkdir
_fired = []


def _racing_mkdir(path, mode=0o777, *args, **kwargs):
    if _TARGET and not _fired and os.path.abspath(os.fspath(path)) == _TARGET:
        _fired.append(True)
        _original_mkdir(_TARGET)
        with open(os.path.join(_TARGET, "REQUEST.json"), "wb") as handle:
            handle.write(_PAYLOAD)
    return _original_mkdir(path, mode, *args, **kwargs)


os.mkdir = _racing_mkdir
'''


def run_cli_bytes(cli: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(cli), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Every entry under root: files map to their bytes, directories to None."""
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = str(path.relative_to(root))
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


class PrepareProject:
    """PacketFixture project whose state has NOT been bound yet (003-005 Motivo).

    The pre-state carries `execution: null` and `active_packet: null`, so every
    binding observed after `prepare` was written by `prepare` itself.
    """

    def __init__(self, root: Path, role: str = "test-writer", substage: str = "red") -> None:
        self.root = root
        self.fixture = PacketFixture(root, role, substage)
        self.fixture.write()
        self.fixture.request_path.unlink()  # prepare must create its own REQUEST.json
        state = copy.deepcopy(self.fixture.state)
        state["execution"] = None
        state["active_packet"] = None
        state["custom_marker"] = {"kept": ["verbatim", 1]}
        self.pre_state = state
        self.state_path.write_text(json.dumps(state), encoding="utf-8")
        self.out_dir = root / "out"
        self.out_dir.mkdir()

    @property
    def role(self) -> str:
        return self.fixture.role

    @property
    def substage(self) -> str:
        return self.fixture.substage

    @property
    def state_path(self) -> Path:
        return self.root / "docs" / ".cdad-state.json"

    @property
    def execution_path(self) -> Path:
        return self.root / "EXECUTION.json"

    def args(self, *extra: str, objective: str = "Prepare objective", out_dir: Path | None = None) -> list[str]:
        return [
            "--project-root",
            str(self.root),
            "--execution-context",
            str(self.execution_path),
            "--role",
            self.role,
            "--substage",
            self.substage,
            "--objective",
            objective,
            "--out-dir",
            str(out_dir or self.out_dir),
            *extra,
        ]

    def packet_id(self, number: int = 1) -> str:
        return f"{FEATURE_ID}-{self.role}-{self.substage}-{number:03d}"


class PrepareTestCase(unittest.TestCase):
    def project(self, role: str = "test-writer", substage: str = "red") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-prepare-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), role, substage)

    def require_prepare(self) -> None:
        result = run_cli_bytes(PACKET_CLI, "prepare", "--help")
        self.assertEqual(
            result.returncode,
            0,
            "public subcommand 'prepare' unavailable: " + result.stderr.decode(errors="replace"),
        )

    def prepare_ok(self, project: PrepareProject, *extra: str, **kwargs) -> subprocess.CompletedProcess[bytes]:
        result = run_prepare(PACKET_CLI, *project.args(*extra, **kwargs))
        self.assertEqual(
            result.returncode,
            0,
            "prepare failed: " + result.stderr.decode(errors="replace"),
        )
        return result

    def request_of(self, project: PrepareProject, number: int = 1) -> dict:
        path = project.out_dir / project.packet_id(number) / "REQUEST.json"
        self.assertTrue(path.is_file(), f"prepare did not write {path}")
        return json.loads(path.read_text(encoding="utf-8"))


class TestPrepareEffects(PrepareTestCase):
    def test_p1_prepare_writes_three_files_and_stdout_equals_packet_and_render(self) -> None:
        """P1: exactly REQUEST.json, PACKET.md and the state; stdout == PACKET.md == render; validate-packet passes."""
        project = self.project()
        before = tree_snapshot(project.root)
        result = self.prepare_ok(project)
        after = tree_snapshot(project.root)

        packet_dir = project.out_dir / project.packet_id()
        request_rel = str((packet_dir / "REQUEST.json").relative_to(project.root))
        packet_rel = str((packet_dir / "PACKET.md").relative_to(project.root))
        packet_dir_rel = str(packet_dir.relative_to(project.root))
        state_rel = str(project.state_path.relative_to(project.root))
        added = sorted(set(after) - set(before))
        # Enmienda de oráculo (review-t3.md, Disposición + I5c del plan):
        # `.cdad` (creado por prepare sobre un proyecto sin `.cdad` previo)
        # y `.cdad/.lock` (rendezvous del flock, legítimo y PERMANENTE cuando
        # la operación publica algo) no son escrituras extra del paquete.
        lock_added = (project.root / ".cdad" / ".lock").is_file()
        # Enmienda de oráculo T6 PRE-GREEN (I9 del plan, PD-8): la publicación
        # de prepare incluye los derivados de agentes OpenCode del proyecto
        # (misma transacción y lock). El conjunto es el contrato congelado de
        # I9: cinco roles base + odoo + orquestador + manifest de derivados.
        derived_names = (
            ".cdad-derived.json",
            "cdad-architect-odoo.md",
            "cdad-architect.md",
            "cdad-implementer-odoo.md",
            "cdad-implementer.md",
            "cdad-orchestrator.md",
            "cdad-reviewer-odoo.md",
            "cdad-reviewer.md",
            "cdad-scribe-odoo.md",
            "cdad-scribe.md",
            "cdad-test-writer-odoo.md",
            "cdad-test-writer.md",
        )
        self.assertEqual(
            added,
            sorted(
                [packet_dir_rel, request_rel, packet_rel, ".cdad",
                 ".opencode", ".opencode/agents"]
                + [f".opencode/agents/{name}" for name in derived_names]
                + ([".cdad/.lock"] if lock_added else [])))
        changed = sorted(k for k in before if k in after and before[k] != after[k])
        self.assertEqual(changed, [state_rel])
        self.assertEqual(sorted(set(before) - set(after)), [])

        packet_bytes = (packet_dir / "PACKET.md").read_bytes()
        self.assertTrue(result.stdout.startswith(PACKET_BEGIN.encode()))
        self.assertEqual(result.stdout, packet_bytes)

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
        self.assertEqual(rendered.stdout, result.stdout)
        validated = run_cli_bytes(
            PACKET_CLI, "validate-packet", *common, "--packet", str(packet_dir / "PACKET.md")
        )
        self.assertEqual(validated.returncode, 0, validated.stderr.decode(errors="replace"))

    def test_p1_state_binding_and_active_packet_are_written_other_keys_kept(self) -> None:
        """P1 (§2.3): execution = 7 binding fields, active_packet prepared, rest JSON-equal, indent 2 + final newline."""
        project = self.project()
        self.prepare_ok(project)
        raw = project.state_path.read_bytes()
        state = json.loads(raw.decode("utf-8"))
        execution = json.loads(project.execution_path.read_text(encoding="utf-8"))["execution"]

        self.assertEqual(state["execution"], {k: execution[k] for k in BINDING_FIELDS})
        contract_sha = hashlib.sha256((project.root / SPEC_CONTRACT).read_bytes()).hexdigest()
        self.assertEqual(
            state["active_packet"],
            {
                "id": project.packet_id(),
                "role": "test-writer",
                "substage": "red",
                "status": "prepared",
                "packet_version": 1,
                "contract_kind": "approved-feature-spec",
                "contract_sha256": contract_sha,
            },
        )
        rest_after = {k: v for k, v in state.items() if k not in ("execution", "active_packet")}
        rest_before = {k: v for k, v in project.pre_state.items() if k not in ("execution", "active_packet")}
        self.assertEqual(rest_after, rest_before)
        self.assertEqual(raw, (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

        validated = run_cli_bytes(
            PACKET_CLI,
            "validate-state",
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
        )
        self.assertEqual(validated.returncode, 0, validated.stderr.decode(errors="replace"))


class TestPrepareDefaults(PrepareTestCase):
    def expected_scopes(self, role: str) -> tuple[list, list]:
        if role == "test-writer":
            return (
                [
                    {"class": "contract", "root": f"docs/specs/{FEATURE_ID}"},
                    {"class": "tests", "root": "tests"},
                ],
                [{"class": "tests", "root": "tests"}],
            )
        if role == "implementer":
            return (
                [{"class": "repository-read"}],
                [
                    {"class": "implementation", "root": "src"},
                    {"class": "implementation", "root": "lib"},
                    {"class": "implementation", "path": "install.sh"},
                ],
            )
        return ([{"class": "repository-read"}], [])

    def test_p2_default_request_derivations_per_role(self) -> None:
        """P2: packet_id, contract, inputs, scopes, invariants, output and evidence defaults.

        A-1 (declarado en el RED de 006-005 U1c
        `tests/test_006_005_u1c_packet_agent.py`, plan.md §4) — REEMPLAZADO:
        esta prueba fijaba el documento EXACTO de `REQUEST.json` sin el campo
        `agent`; REEMPLAZADA POR la misma igualdad exacta (el conjunto de claves
        del request sigue cerrado) CON el campo declarado `agent` presente,
        derivado del `stack` del estado del fixture (`stack: null` ⇒
        `cdad-<rol>`). POSTCONDICIÓN NUEVA: PD-7 de
        `docs/specs/006-005-native-path-parity/spec.md` §2.7 — `prepare` escribe
        `agent` = rol + `stack` del estado. RAZÓN: la extensión declarada del
        conjunto cerrado cambia el documento que es el oráculo de esta prueba;
        se actualiza el valor esperado sin relajar el oráculo.
        """
        cases = (
            ("test-writer", "red"),
            ("implementer", "green"),
            ("architect", "draft"),
            ("reviewer", "review"),
            ("scribe", "memory"),
        )
        for role, substage in cases:
            with self.subTest(role=role, substage=substage):
                project = self.project(role, substage)
                self.prepare_ok(project, objective=f"objective for {role}")
                request = self.request_of(project)
                contract_path = PLAN_CONTRACT if role == "architect" else SPEC_CONTRACT
                contract_kind = "approved-epic-plan" if role == "architect" else "approved-feature-spec"
                read_scope, write_scope = self.expected_scopes(role)
                self.assertEqual(
                    request,
                    {
                        "schema_version": 1,
                        "packet_id": f"{FEATURE_ID}-{role}-{substage}-001",
                        "execution_id": EXECUTION_ID,
                        "feature_id": FEATURE_ID,
                        "role": role,
                        "substage": substage,
                        "objective": f"objective for {role}",
                        # A-1 (006-005 U1c, PD-7 §2.7): el estado del fixture
                        # lleva `stack: null`, así que el agente del paquete es
                        # `cdad-<rol>`. La igualdad exacta del documento se
                        # conserva: el conjunto de claves sigue cerrado.
                        "agent": f"cdad-{role}",
                        "contract": {
                            "kind": contract_kind,
                            "path": contract_path,
                            "sha256": hashlib.sha256((project.root / contract_path).read_bytes()).hexdigest(),
                            "commit": None,
                        },
                        "inputs": [{"path": contract_path, "purpose": "approved contract"}],
                        "read_scope": read_scope,
                        "write_scope": write_scope,
                        "invariants": DEFAULT_INVARIANTS[role],
                        "expected_output": DEFAULT_EXPECTED_OUTPUT,
                        "evidence_required": DEFAULT_EVIDENCE,
                    },
                )

    def test_p2_packet_id_uses_first_free_number_in_out_dir(self) -> None:
        """P2: NNN is the first free 3-digit number (001 and 003 taken -> 002, then 004)."""
        project = self.project()
        (project.out_dir / project.packet_id(1)).mkdir()
        (project.out_dir / project.packet_id(3)).mkdir()
        self.prepare_ok(project)
        self.assertEqual(self.request_of(project, 2)["packet_id"], project.packet_id(2))
        self.prepare_ok(project)
        self.assertEqual(self.request_of(project, 4)["packet_id"], project.packet_id(4))

    def test_p2_default_execution_context_and_out_dir_under_project_cdad(self) -> None:
        """P2 (§1): without flags, EXEC = ROOT/.cdad/execution.json and OUT = ROOT/.cdad/packets."""
        self.require_prepare()
        project = self.project()
        cdad_dir = project.root / ".cdad"
        cdad_dir.mkdir()
        shutil.copyfile(project.execution_path, cdad_dir / "execution.json")
        project.execution_path.unlink()
        result = run_prepare(
            PACKET_CLI,
            "--project-root",
            str(project.root),
            "--role",
            "test-writer",
            "--substage",
            "red",
            "--objective",
            "defaults",
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        packet_dir = cdad_dir / "packets" / project.packet_id()
        self.assertTrue((packet_dir / "REQUEST.json").is_file())
        self.assertEqual((packet_dir / "PACKET.md").read_bytes(), result.stdout)


class TestPrepareExplicitFlags(PrepareTestCase):
    def test_p3_input_and_invariant_append_scopes_output_evidence_replace(self) -> None:
        """P3: --input/--invariant append; --read-scope/--write-scope/--evidence/--expected-output replace; dir->root, file->path."""
        project = self.project()
        self.prepare_ok(
            project,
            "--input",
            "tests/exact_test.py=existing test",
            "--read-scope",
            f"contract=docs/specs/{FEATURE_ID}",
            "--read-scope",
            "tests=tests/exact_test.py",
            "--write-scope",
            "tests=tests",
            "--invariant",
            "Keep fixtures self-contained",
            "--expected-output",
            "Custom report",
            "--evidence",
            "pytest output",
            "--evidence",
            "diff",
        )
        request = self.request_of(project)
        self.assertEqual(
            request["inputs"],
            [
                {"path": SPEC_CONTRACT, "purpose": "approved contract"},
                {"path": "tests/exact_test.py", "purpose": "existing test"},
            ],
        )
        self.assertEqual(
            request["read_scope"],
            [
                {"class": "contract", "root": f"docs/specs/{FEATURE_ID}"},
                {"class": "tests", "path": "tests/exact_test.py"},
            ],
        )
        self.assertEqual(request["write_scope"], [{"class": "tests", "root": "tests"}])
        self.assertEqual(
            request["invariants"],
            DEFAULT_INVARIANTS["test-writer"] + ["Keep fixtures self-contained"],
        )
        self.assertEqual(request["expected_output"], "Custom report")
        self.assertEqual(request["evidence_required"], ["pytest output", "diff"])

    def test_p3_bare_repository_read_and_empty_default_invariants_append(self) -> None:
        """P3: `--read-scope repository-read` has no selector; --invariant appends to an empty default."""
        project = self.project("reviewer", "review")
        self.prepare_ok(project, "--read-scope", "repository-read", "--invariant", "Report only")
        request = self.request_of(project)
        self.assertEqual(request["read_scope"], [{"class": "repository-read"}])
        self.assertEqual(request["write_scope"], [])
        self.assertEqual(request["invariants"], ["Report only"])
        self.assertEqual(request["evidence_required"], DEFAULT_EVIDENCE)


class TestPrepareFailureHasNoEffects(PrepareTestCase):
    def assert_failure_without_effects(self, project: PrepareProject, args: list[str], label: str) -> None:
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *args)
        stderr = result.stderr.decode(errors="replace")
        self.assertEqual(result.returncode, 2, f"{label}: expected exit 2, stderr={stderr!r}")
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"{label}: stderr lacks 'ERROR: ...'")
        self.assertEqual(result.stdout, b"", f"{label}: stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], f"{label}: out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, f"{label}: state changed")
        self.assertEqual(tree_snapshot(project.root), before, f"{label}: project tree changed")

    def test_p4_each_failure_exits_2_with_empty_stdout_and_no_files(self) -> None:
        """P4: invalid role, invalid pair, missing contract, scope outside policy, invalid execution, malformed flag."""
        self.require_prepare()

        project = self.project()
        args = project.args()
        args[args.index("--role") + 1] = "wizard"
        cases = [("invalid role", project, args)]

        project = self.project()
        args = project.args()
        args[args.index("--substage") + 1] = "green"
        cases.append(("invalid role/substage pair", project, args))

        project = self.project()
        (project.root / SPEC_CONTRACT).unlink()
        cases.append(("missing contract", project, project.args()))

        project = self.project()
        cases.append(("scope outside role policy", project, project.args("--write-scope", "implementation=src")))

        project = self.project()
        # 004-002 T6 PRE-GREEN (PD-10): el contexto inválido es un documento
        # v2 MALFORMADO (la forma v1 ya no es el portador de estos fixtures).
        project.execution_path.write_text(json.dumps({"schema_version": 2}), encoding="utf-8")
        cases.append(("invalid execution context", project, project.args()))

        project = self.project()
        cases.append(("malformed --input flag", project, project.args("--input", "tests/exact_test.py")))

        project = self.project()
        cases.append(("input outside read scope", project, project.args("--input", "README.md=outside")))

        for label, project, args in cases:
            with self.subTest(failure=label):
                self.assert_failure_without_effects(project, args, label)

    def test_p4_default_out_dir_is_not_created_on_failure(self) -> None:
        """P4: a failing prepare with the default OUT does not create ROOT/.cdad/packets."""
        self.require_prepare()
        project = self.project()
        cdad_dir = project.root / ".cdad"
        cdad_dir.mkdir()
        shutil.copyfile(project.execution_path, cdad_dir / "execution.json")
        (project.root / SPEC_CONTRACT).unlink()
        state_before = project.state_path.read_bytes()
        result = run_prepare(
            PACKET_CLI,
            "--project-root",
            str(project.root),
            "--role",
            "test-writer",
            "--substage",
            "red",
            "--objective",
            "missing contract",
        )
        self.assertEqual(result.returncode, 2, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout, b"")
        self.assertFalse((cdad_dir / "packets").exists(), "default out-dir created on failure")
        self.assertEqual(project.state_path.read_bytes(), state_before)

    def assert_clean_exit_2(self, result: subprocess.CompletedProcess[bytes], label: str) -> None:
        stderr = result.stderr.decode(errors="replace")
        self.assertEqual(result.returncode, 2, f"{label}: expected exit 2, stderr={stderr!r}")
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"{label}: stderr lacks 'ERROR: ...'")
        self.assertNotIn("Traceback", stderr, f"{label}: stderr carries a traceback")
        self.assertEqual(result.stdout, b"", f"{label}: stdout must be empty")

    def test_p4_packet_id_clash_on_dangling_symlink_keeps_foreign_entry(self) -> None:
        """P4 (§3 amendment, B1 black-box): a dangling symlink named like the next packet_id makes
        prepare fail with exit 2 and no effects; the foreign symlink is left intact."""
        self.require_prepare()
        project = self.project("reviewer", "review")
        foreign = project.out_dir / project.packet_id(1)
        dangling_target = project.root / "foreign-nowhere"
        os.symlink(dangling_target, foreign)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *project.args())
        self.assert_clean_exit_2(result, "dangling symlink clash")
        self.assertTrue(foreign.is_symlink(), "foreign symlink was removed or replaced")
        self.assertEqual(os.readlink(foreign), str(dangling_target))
        self.assertFalse(os.path.lexists(dangling_target), "prepare wrote through the foreign symlink")
        self.assertEqual(sorted(p.name for p in project.out_dir.iterdir()), [foreign.name])
        self.assertEqual(project.state_path.read_bytes(), state_before)

    def test_p4_packet_id_directory_appearing_before_mkdir_is_not_touched(self) -> None:
        """P4 (§3 amendment, B1 race): if the packet_id directory appears between the numbering
        and the mkdir, prepare exits 2 without deleting or modifying that foreign directory."""
        self.require_prepare()
        project = self.project("reviewer", "review")
        foreign = project.out_dir / project.packet_id(1)
        payload = '{"foreign": "request owned by another invocation"}\n'
        hook_dir = project.root.parent / (project.root.name + "-sitecustomize")
        hook_dir.mkdir()
        self.addCleanup(shutil.rmtree, hook_dir, True)
        (hook_dir / "sitecustomize.py").write_text(RACE_SITECUSTOMIZE, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(hook_dir), env.get("PYTHONPATH", "")]))
        env["CDAD_TEST_RACE_TARGET"] = str(foreign)
        env["CDAD_TEST_RACE_PAYLOAD"] = payload
        state_before = project.state_path.read_bytes()

        result = run_prepare(PACKET_CLI, *project.args(), env=env)

        self.assertTrue(foreign.is_dir(), "foreign packet directory was deleted")
        self.assertEqual(
            sorted(p.name for p in foreign.iterdir()),
            ["REQUEST.json"],
            "foreign packet directory was modified",
        )
        self.assertEqual((foreign / "REQUEST.json").read_text(encoding="utf-8"), payload)
        self.assert_clean_exit_2(result, "packet_id race")
        self.assertEqual(sorted(p.name for p in project.out_dir.iterdir()), [foreign.name])
        self.assertEqual(project.state_path.read_bytes(), state_before)

    def test_p4_unserializable_state_fails_without_effects(self) -> None:
        """P4 (§3 amendment, B2): a readable state holding a lone surrogate escape cannot be
        re-serialized as UTF-8; prepare exits 2 cleanly, leaves no .tmp and no packet."""
        self.require_prepare()
        project = self.project("reviewer", "review")
        text = json.dumps(project.pre_state)
        self.assertTrue(text.endswith("}"))
        project.state_path.write_text(text[:-1] + ', "extra": "\\udc80"}', encoding="utf-8")
        json.loads(project.state_path.read_text(encoding="utf-8"))  # fixture sanity: valid JSON
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()

        result = run_prepare(PACKET_CLI, *project.args())

        self.assert_clean_exit_2(result, "unserializable state")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertFalse((project.root / "docs" / ".cdad-state.json.tmp").exists(), "left state .tmp behind")
        self.assertEqual(project.state_path.read_bytes(), state_before)
        self.assertEqual(tree_snapshot(project.root), before)

    def test_p4_non_flat_feature_id_is_rejected_without_escaping(self) -> None:
        """P4 (§3 amendment, B3): feature_id must be a flat name ([A-Za-z0-9._-]+, no `..`);
        absolute or traversing ids fail with exit 2 and create nothing inside or outside OUT."""
        self.require_prepare()
        outside = tempfile.TemporaryDirectory(prefix="cdad-b3-outside-")
        self.addCleanup(outside.cleanup)
        outside_root = Path(outside.name).resolve()
        absolute_id = str(outside_root / f"feat-{uuid.uuid4().hex}")

        for label, feature_id in (("absolute", absolute_id), ("traversal", "a/../b")):
            with self.subTest(feature_id=label):
                project = self.project("reviewer", "review")
                execution = json.loads(project.execution_path.read_text(encoding="utf-8"))
                execution["execution"]["feature_id"] = feature_id
                project.execution_path.write_text(json.dumps(execution), encoding="utf-8")
                state = json.loads(project.state_path.read_text(encoding="utf-8"))
                state["active_feature"] = feature_id
                state["epic_features"] = [{"id": feature_id, "status": "in-progress"}]
                project.state_path.write_text(json.dumps(state), encoding="utf-8")
                # Make the contract exist wherever a naive join would look for it.
                contract_text = "# Contract for a non-flat feature id\n"
                for spec in {
                    project.root / "docs" / "specs" / feature_id / "spec.md",
                    Path(str(project.root / "docs" / "specs") + "/" + feature_id + "/spec.md"),
                }:
                    spec.parent.mkdir(parents=True, exist_ok=True)
                    spec.write_text(contract_text, encoding="utf-8")
                escaped = Path(f"{feature_id}-reviewer-review-001")
                outside_before = tree_snapshot(outside_root)
                project_before = tree_snapshot(project.root)
                state_before = project.state_path.read_bytes()

                result = run_prepare(PACKET_CLI, *project.args())

                if escaped.is_absolute():
                    self.assertFalse(os.path.lexists(escaped), f"prepare created {escaped} outside the project")
                self.assertEqual(tree_snapshot(outside_root), outside_before, "files created outside OUT")
                self.assert_clean_exit_2(result, f"{label} feature_id")
                self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
                self.assertEqual(project.state_path.read_bytes(), state_before)
                self.assertEqual(tree_snapshot(project.root), project_before)


CLAUDE_ROLE_AGENTS = {
    "cdad-architect": None,
    "cdad-test-writer": None,
    "cdad-implementer": None,
    "cdad-reviewer": None,
    "cdad-scribe": None,
    "cdad-architect-odoo": ("odoo-architect",),
    "cdad-test-writer-odoo": ("odoo-test-writer",),
    "cdad-implementer-odoo": ("odoo-expert", "odoo-make-env"),
    "cdad-reviewer-odoo": ("odoo-reviewer",),
    "cdad-scribe-odoo": ("odoo-make-env",),
}
# Barriers at base ddd3109 (spec §4: they do not change) — AMENDED by owner
# decision 2026-09-29 (permissive bash policy, spec
# docs/specs/permissive-bash-policy-2026-09-29/spec.yaml): the Bash
# content-guard hooks are RETIRED; only the path guards remain. Only these
# agents carry hooks.
EXPECTED_GUARDS = {
    "cdad-architect": [],
    "cdad-architect-odoo": [],
    "cdad-reviewer": [],
    "cdad-reviewer-odoo": [],
    "cdad-scribe": [],
    "cdad-scribe-odoo": [],
    "cdad-implementer": ["implementer"],
    "cdad-implementer-odoo": ["implementer-odoo"],
    "cdad-test-writer": ["test-writer-read", "test-writer-write"],
    "cdad-test-writer-odoo": ["test-writer-odoo-read", "test-writer-odoo-write"],
}
READ_ONLY_TOOLS = "Read, Grep, Glob, Bash, Skill"
EDIT_TOOLS = "Read, Grep, Glob, Bash, Edit, Write, Skill"


def frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("installed agent does not have delimited frontmatter")
    return parts[1]


def packet_branch_block(text: str) -> str:
    """The bullet/paragraph that contains the packet marker."""
    blocks = re.split(r"\n\s*\n|\n(?=\s*[-*] )", text)
    for block in blocks:
        if "---cdad-packet-json" in block:
            return block
    return ""


class TestPreparedInstalled(unittest.TestCase):
    """P5/P6: one isolated install (CDAD_INSTALL_ROOT, no extra skill dirs, real HOME untouched)."""

    @classmethod
    def setUpClass(cls) -> None:
        # Portabilidad (review-t1/T6): el staging se garantiza en un producto
        # con manifest (el checkout real si lo tiene, o una copia temporal
        # generada por `make staging`); nunca se escribe en el checkout real.
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-005-install-")
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
        cls.claude_agents = cls.install_root / ".claude/agents"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def assert_matches(self, text: str, pattern: str, message: str) -> None:
        """Regex assertion that reports `message` instead of dumping the whole document."""
        if re.search(pattern, text) is None:
            self.fail(message)

    def setUp(self) -> None:
        self.assertEqual(
            self.install_result.returncode,
            0,
            self.install_result.stderr or self.install_result.stdout,
        )

    def test_p5_installed_cli_prepare_matches_repo_prepare(self) -> None:
        """P5: installed cdad_packet.py prepare yields the same packet, request and state as the repo CLI."""
        self.assertTrue(self.installed_cli.is_file(), f"missing {self.installed_cli}")
        temp = tempfile.TemporaryDirectory(prefix="cdad-005-consumer-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve())
        self.assertFalse((project.root / "scripts/cdad_packet.py").exists())
        original_state = project.state_path.read_bytes()

        outcomes = {}
        for label, cli in (("repo", PACKET_CLI), ("installed", self.installed_cli)):
            project.state_path.write_bytes(original_state)
            out_dir = project.root / f"out-{label}"
            out_dir.mkdir()
            result = run_prepare(cli, *project.args(out_dir=out_dir), cwd=project.root)
            packet_dir = out_dir / project.packet_id()
            outcomes[label] = (
                result.returncode,
                result.stdout,
                result.stderr,
                (packet_dir / "REQUEST.json").read_bytes() if (packet_dir / "REQUEST.json").is_file() else None,
                (packet_dir / "PACKET.md").read_bytes() if (packet_dir / "PACKET.md").is_file() else None,
                project.state_path.read_bytes(),
            )
        repo, installed = outcomes["repo"], outcomes["installed"]
        self.assertEqual(repo[0], 0, repo[2].decode(errors="replace"))
        self.assertTrue(repo[1].startswith(PACKET_BEGIN.encode()))
        self.assertEqual(installed[0], 0, installed[2].decode(errors="replace"))
        self.assertEqual(installed[1], repo[1], "installed stdout differs from repo stdout")
        self.assertEqual(installed[3], repo[3], "REQUEST.json differs")
        self.assertEqual(installed[4], repo[4], "PACKET.md differs")
        self.assertEqual(installed[5], repo[5], "resulting state differs")

    def test_p6_claude_role_agents_have_packet_and_legacy_paths(self) -> None:
        """P6 (§4): the 10 installed Claude Code role agents branch valid packet vs legacy cdad-cycle load."""
        for name in CLAUDE_ROLE_AGENTS:
            with self.subTest(agent=name):
                path = self.claude_agents / f"{name}.md"
                self.assertTrue(path.is_file(), f"missing installed agent {path}")
                errors = packet_and_legacy_contract_errors(path.read_text(encoding="utf-8"))
                self.assertEqual(errors, [], f"{name}: {errors}")

    def test_p6_claude_packet_path_rejects_invalid_packets(self) -> None:
        """P6 (§4): a prompt that claims to be a packet but is invalid makes the agent stop and report."""
        for name in CLAUDE_ROLE_AGENTS:
            with self.subTest(agent=name):
                text = (self.claude_agents / f"{name}.md").read_text(encoding="utf-8")
                self.assert_matches(
                    text,
                    r"(?is)(claims?|dice ser|pretends?).{0,60}packet.{0,200}(invalid|absent|inv[aá]lido).{0,200}(stop|detien).{0,120}report",
                    f"{name}: no stop-and-report rule for an invalid claimed packet",
                )

    def test_p6_odoo_agents_keep_domain_skills_in_packet_path(self) -> None:
        """P6 (§4): odoo agents keep loading their domain skills also in the packet path."""
        for name, skills in CLAUDE_ROLE_AGENTS.items():
            if not skills:
                continue
            with self.subTest(agent=name):
                text = (self.claude_agents / f"{name}.md").read_text(encoding="utf-8")
                block = packet_branch_block(text)
                self.assertTrue(block, f"{name}: no packet-path block with ---cdad-packet-json")
                for skill in skills:
                    self.assert_matches(
                        block,
                        rf"(?is)(load|review|consult|cargar|carga).{{0,200}}`?{re.escape(skill)}`?",
                        f"{name}: packet path does not keep domain skill {skill}",
                    )

    def test_p6_claude_barriers_are_unchanged(self) -> None:
        """P6 (§4): tools and PreToolUse path-guard hooks stay exactly as before."""
        for name, guards in EXPECTED_GUARDS.items():
            with self.subTest(agent=name):
                meta = frontmatter((self.claude_agents / f"{name}.md").read_text(encoding="utf-8"))
                tools = re.search(r"(?m)^tools:\s*(.+?)\s*$", meta)
                self.assertIsNotNone(tools, f"{name}: tools line missing")
                self.assertEqual(tools.group(1), EDIT_TOOLS if guards else READ_ONLY_TOOLS)
                found = re.findall(r"path-guard\.sh ([a-z-]+)", meta)
                self.assertEqual(found, guards)
                if guards:
                    self.assertRegex(meta, r"(?m)^hooks:\s*$")
                    self.assertRegex(meta, r"(?m)^\s+PreToolUse:\s*$")
                    for guard in guards:
                        self.assertIn(f"~/.claude/cdad-scripts/path-guard.sh {guard}", meta)
                else:
                    self.assertNotIn("PreToolUse", meta)

    def test_p6_orchestrators_and_handoff_use_prepare_stdout_unchanged(self) -> None:
        """P6 (§4): orchestrators + handoff-prompts name `prepare` and pass its stdout unchanged as Task prompt."""
        consumers = (
            self.claude_agents / "cdad-orchestrator.md",
            self.install_root / ".config/opencode/agents/cdad-orchestrator.md",
            self.install_root / ".claude/skills/cdad-cycle/references/handoff-prompts.md",
        )
        for consumer in consumers:
            with self.subTest(consumer=str(consumer.relative_to(self.install_root))):
                self.assertTrue(consumer.is_file(), f"missing {consumer}")
                text = consumer.read_text(encoding="utf-8")
                label = consumer.name
                self.assert_matches(text, r"cdad_packet\.py", f"{label}: does not name cdad_packet.py")
                self.assert_matches(
                    text,
                    r"(?s)cdad_packet\.py`?\s+prepare\b|\bprepare\b.{0,120}cdad_packet\.py",
                    f"{label}: does not name `cdad_packet.py prepare` as the way to produce the packet",
                )
                self.assert_matches(
                    text,
                    r"(?is)prepare.{0,400}stdout.{0,160}(unchanged|sin cambios|byte)",
                    f"{label}: does not say prepare stdout passes unchanged",
                )
                self.assert_matches(
                    text, r"(?is)stdout.{0,200}Task", f"{label}: stdout is not tied to the Task prompt"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
