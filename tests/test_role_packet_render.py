#!/usr/bin/env python3
"""Black-box RED tests for 003-001 Task 2: P1/P2/P3 and metric P5."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from tests.test_role_packets import (
    AUTHORITY_REF,
    EPIC_ID,
    EXECUTION_ID,
    FEATURE_ID,
    PACKET_CLI,
    REPO_ROOT,
    StateFixture,
    execution_document,
    state_document,
)


ROLE_SUBSTAGES = (
    ("architect", "discovery"),
    ("architect", "brainstorm"),
    ("architect", "draft"),
    ("test-writer", "audit"),
    ("test-writer", "post-audit"),
    ("test-writer", "red"),
    ("test-writer", "properties"),
    ("test-writer", "e2e"),
    ("implementer", "green"),
    ("implementer", "refactor"),
    ("implementer", "review-fix"),
    ("reviewer", "review"),
    ("scribe", "memory"),
)
ROLE_SEMANTICS = {
    "architect": (r"(?i)read[- ]only|no (?:edits?|writes?)|do not (?:edit|write)",),
    "test-writer": (
        r"(?i)(?:never|do not|must not) read implementation",
        r"(?i)(?:edit|write) only (?:declared )?test",
    ),
    "implementer": (r"(?i)(?:never|do not|must not) (?:edit|write|modify) tests",),
    "reviewer": (r"(?i)read[- ]only|no (?:edits?|writes?)|do not (?:edit|write)",),
    "scribe": (r"(?i)read[- ]only|no (?:edits?|writes?)|do not (?:edit|write)",),
}
PACKET_BEGIN = "---cdad-packet-json\n"
PACKET_END = "\n---end-cdad-packet-json\n"
PACKETS_ROOT = REPO_ROOT / "skills" / "cdad-cycle" / "packets"
STATIC_BEGIN = b"<!-- cdad-instructions:start -->\n"
STATIC_END = b"\n<!-- cdad-instructions:end -->"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_packet(packet: str) -> tuple[dict, str, str]:
    if not packet.startswith(PACKET_BEGIN) or PACKET_END not in packet:
        raise AssertionError("render output lacks the canonical metadata delimiters")
    metadata_text, body = packet[len(PACKET_BEGIN) :].split(PACKET_END, 1)
    metadata = json.loads(metadata_text)
    return metadata, metadata_text, body


def static_instruction_bytes(packet: str) -> bytes:
    rendered = packet.encode("utf-8")
    if rendered.count(STATIC_BEGIN) != 1 or rendered.count(STATIC_END) != 1:
        raise AssertionError("render output lacks unique static-instruction delimiters")
    return rendered.split(STATIC_BEGIN, 1)[1].split(STATIC_END, 1)[0]


class PacketFixture:
    """A complete public project/request fixture with no implementation assets."""

    def __init__(self, root: Path, role: str, substage: str, *, objective: str = "Verify contract") -> None:
        self.root = root
        self.role = role
        self.substage = substage
        self.execution = execution_document()
        self.execution["path_policy"].update(
            {
                "implementation_files": ["install.sh"],
                "documentation_files": ["README.md"],
                "test_files": ["tests/exact_test.py"],
            }
        )
        self.contract_kind = "approved-epic-plan" if role == "architect" else "approved-feature-spec"
        self.contract_relpath = (
            f"docs/epics/{EPIC_ID}/plan.md"
            if self.contract_kind == "approved-epic-plan"
            else f"docs/specs/{FEATURE_ID}/spec.md"
        )
        self.contract_bytes = f"# Contract fixture for {role}/{substage}\n".encode()
        self.contract_sha256 = hashlib.sha256(self.contract_bytes).hexdigest()
        self.packet_id = f"packet-{role}-{substage}"
        self.request = self._request(objective)
        # 005-001 T1 (D3/D1): la aprobación de spec del fixture es pineada
        # (path + sha256 de los bytes que este fixture escribe); para el
        # architect se agrega además la aprobación del plan del epic
        # (epic_history), su mandato propio (sin pin de hash, D2).
        spec_contract_sha256 = None if role == "architect" else self.contract_sha256
        self.state = state_document(
            self.execution,
            active_packet={
                "id": self.packet_id,
                "role": role,
                "substage": substage,
                "status": "prepared",
                "packet_version": 1,
                "contract_kind": self.contract_kind,
                "contract_sha256": self.contract_sha256,
            },
            contract_sha256=spec_contract_sha256,
        )
        if role == "architect":
            self.state["epic_history"] = [{
                "epic": EPIC_ID,
                "stage": "epic-plan",
                "approved_by": "Pablo",
            }]
        self.request_path = root / "REQUEST.json"
        self.packet_path = root / "PACKET.md"
        self.metric_path = root / "METRIC.json"

    def _request(self, objective: str) -> dict:
        if self.role == "test-writer":
            read_scope = [
                {"class": "contract", "root": f"docs/specs/{FEATURE_ID}"},
                {"class": "tests", "root": "tests"},
            ]
            write_scope = [{"class": "tests", "root": "tests"}]
        elif self.role == "implementer":
            read_scope = [{"class": "repository-read"}]
            write_scope = [
                {"class": "implementation", "path": "install.sh"},
                {"class": "docs", "path": "README.md"},
            ]
        else:
            read_scope = [{"class": "repository-read"}]
            write_scope = []
        return {
            "schema_version": 1,
            "packet_id": self.packet_id,
            "execution_id": EXECUTION_ID,
            "feature_id": FEATURE_ID,
            "role": self.role,
            "substage": self.substage,
            "objective": objective,
            "contract": {
                "kind": self.contract_kind,
                "path": self.contract_relpath,
                "sha256": self.contract_sha256,
                "commit": None,
            },
            "inputs": [{"path": self.contract_relpath, "purpose": "approved contract"}],
            "read_scope": read_scope,
            "write_scope": write_scope,
            "invariants": ["Preserve observable contract"],
            "expected_output": "Contract evidence",
            "evidence_required": ["command", "output"],
        }

    def write(self) -> None:
        StateFixture(self.root, self.execution, self.state).write()
        contract = self.root / self.contract_relpath
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_bytes(self.contract_bytes)
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "lib").mkdir(exist_ok=True)
        (self.root / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        (self.root / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (self.root / "tests" / "exact_test.py").write_text("# test\n", encoding="utf-8")
        self.write_request()

    def write_request(self) -> None:
        self.request_path.write_text(json.dumps(self.request), encoding="utf-8")

    def invoke(self, command: str, *extra: str) -> subprocess.CompletedProcess[str]:
        args = [
            command,
            "--project-root",
            str(self.root),
        ]
        if command != "validate-metric":
            args += ["--execution-context", str(self.root / "EXECUTION.json")]
        if command in {"render", "validate-request", "validate-packet"}:
            args += ["--request", str(self.request_path)]
        args += list(extra)
        return run_cli(*args)

    def render(self) -> subprocess.CompletedProcess[str]:
        return self.invoke("render")

    def metric(self) -> dict:
        return {
            "schema_version": 1,
            "execution_id": EXECUTION_ID,
            "packet_id": self.packet_id,
            "epic_id": EPIC_ID,
            "feature_id": FEATURE_ID,
            "role": self.role,
            "substage": self.substage,
            # 004-002 T6 PRE-GREEN (PD-6/PD-10): la identidad v2 no lleva
            # runtime global; el runtime de la métrica es una observación
            # desconocida (null) frente al portador, no un campo de identidad.
            "runtime": None,
            "model": {"configured": "openai/gpt-5.6-sol", "reported": None},
            "started_at": "2026-09-17T00:00:00Z",
            "ended_at": None,
            "input_tokens": None,
            "output_tokens": None,
            "context_limit": None,
            "retry_count": 0,
            "outcome": "dispatched",
        }


class RenderTestCase(unittest.TestCase):
    def make_fixture(self, role: str = "test-writer", substage: str = "red", **kwargs: str):
        temp = tempfile.TemporaryDirectory(prefix="cdad-render-fixture-")
        self.addCleanup(temp.cleanup)
        fixture = PacketFixture(Path(temp.name), role, substage, **kwargs)
        fixture.write()
        return fixture

    def require_render_baseline(self, fixture: PacketFixture) -> str:
        result = fixture.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def require_command(self, command: str) -> None:
        result = run_cli(command, "--help")
        self.assertEqual(result.returncode, 0, f"public subcommand {command!r} unavailable: {result.stderr}")


class TestPublicTask2Surface(RenderTestCase):
    def test_p1_all_role_substage_pairs_render_and_validate(self) -> None:
        for role, substage in ROLE_SUBSTAGES:
            with self.subTest(role=role, substage=substage):
                fixture = self.make_fixture(role, substage)
                rendered = fixture.render()
                self.assertEqual(rendered.returncode, 0, rendered.stderr)
                self.assertTrue(rendered.stdout.startswith(PACKET_BEGIN))
                fixture.packet_path.write_text(rendered.stdout, encoding="utf-8")
                validated = fixture.invoke("validate-packet", "--packet", str(fixture.packet_path))
                self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_p1_repeated_render_is_byte_deterministic(self) -> None:
        fixture = self.make_fixture()
        first = fixture.render()
        second = fixture.render()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout.encode(), second.stdout.encode())

    def test_p1_static_instruction_block_is_delimited_and_within_12000_bytes(self) -> None:
        fixture = self.make_fixture(objective="dynamic-objective-marker")
        packet = self.require_render_baseline(fixture)
        start_marker = "<!-- cdad-instructions:start -->\n"
        end_marker = "\n<!-- cdad-instructions:end -->"
        self.assertEqual(packet.count(start_marker), 1)
        self.assertEqual(packet.count(end_marker), 1)
        static_text = packet.split(start_marker, 1)[1].split(end_marker, 1)[0]
        self.assertLessEqual(len(static_text.encode("utf-8")), 12_000)
        self.assertGreater(packet.index("dynamic-objective-marker"), packet.index(end_marker))

    def test_p1_p3_each_pair_matches_public_instruction_sources_byte_for_byte(self) -> None:
        """P1/P3: public source bytes independently determine provenance and static body."""
        for role, substage in ROLE_SUBSTAGES:
            with self.subTest(role=role, substage=substage):
                fixture = self.make_fixture(role, substage)
                rendered = self.require_render_baseline(fixture)
                metadata, _, body = parse_packet(rendered)
                expected_paths = [
                    "common.md",
                    f"roles/{role}.md",
                    f"substages/{role}-{substage}.md",
                ]
                source_bytes = [(PACKETS_ROOT / path).read_bytes() for path in expected_paths]
                expected_sources = [
                    {"path": path, "sha256": hashlib.sha256(content).hexdigest()}
                    for path, content in zip(expected_paths, source_bytes)
                ]
                sources = metadata.get("instruction_sources")
                self.assertIsInstance(
                    sources,
                    list,
                    "packet metadata must expose instruction_sources as the independent composition oracle",
                )
                self.assertEqual(sources, expected_sources)
                expected_static = b"\n".join(source_bytes)
                self.assertEqual(static_instruction_bytes(rendered), expected_static)
                for marker in ROLE_SEMANTICS[role]:
                    self.assertRegex(body, marker)

    def test_p1_excludes_representative_other_role_and_substage_sources(self) -> None:
        exclusions = {
            ("test-writer", "red"): (
                "roles/implementer.md",
                "substages/test-writer-properties.md",
            ),
            ("implementer", "green"): (
                "roles/test-writer.md",
                "substages/implementer-refactor.md",
            ),
        }
        for (role, substage), excluded_paths in exclusions.items():
            with self.subTest(role=role, substage=substage):
                rendered = self.require_render_baseline(self.make_fixture(role, substage))
                static_block = static_instruction_bytes(rendered)
                for excluded_path in excluded_paths:
                    with self.subTest(excluded_source=excluded_path):
                        excluded = (PACKETS_ROOT / excluded_path).read_bytes().rstrip(b"\n")
                        self.assertNotIn(excluded, static_block)


class TestPacketIntegrity(RenderTestCase):
    def test_p2_metadata_is_canonical_and_matches_request(self) -> None:
        fixture = self.make_fixture()
        packet = self.require_render_baseline(fixture)
        metadata, metadata_text, _ = parse_packet(packet)
        self.assertEqual(
            metadata_text,
            json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        )
        self.assertEqual(metadata["packet_id"], fixture.packet_id)
        self.assertEqual(metadata["execution_id"], EXECUTION_ID)
        self.assertEqual(metadata["feature_id"], FEATURE_ID)
        self.assertEqual(metadata["role"], fixture.role)
        self.assertEqual(metadata["substage"], fixture.substage)
        self.assertEqual(metadata["contract"], fixture.request["contract"])
        self.assertEqual(metadata["read_scope"], fixture.request["read_scope"])
        self.assertEqual(metadata["write_scope"], fixture.request["write_scope"])

    def test_p2_validate_packet_rejects_tampered_body_metadata_and_hash(self) -> None:
        fixture = self.make_fixture()
        packet = self.require_render_baseline(fixture)
        metadata, _, body = parse_packet(packet)
        tampered_packets = {
            "body": packet + "tampered\n",
            "metadata": PACKET_BEGIN
            + json.dumps({**metadata, "packet_id": "other"}, sort_keys=True, separators=(",", ":"))
            + PACKET_END
            + body,
        }
        for label, value in tampered_packets.items():
            with self.subTest(tamper=label):
                fixture.packet_path.write_text(value, encoding="utf-8")
                result = fixture.invoke("validate-packet", "--packet", str(fixture.packet_path))
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")

        fixture.request["contract"]["sha256"] = "0" * 64
        fixture.write_request()
        result = fixture.invoke("validate-request")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")

    def test_p2_paths_inputs_and_symlinks_are_rejected(self) -> None:
        self.require_command("validate-request")
        cases = {}
        fixture = self.make_fixture()
        fixture.request["inputs"] = [{"path": "../escape", "purpose": "traversal"}]
        cases["traversal"] = fixture

        outside = tempfile.TemporaryDirectory(prefix="cdad-outside-")
        self.addCleanup(outside.cleanup)
        fixture = self.make_fixture()
        link = fixture.root / "docs" / "outside-link"
        link.symlink_to(Path(outside.name), target_is_directory=True)
        fixture.request["inputs"] = [{"path": "docs/outside-link/secret.md", "purpose": "escape"}]
        cases["symlink escape"] = fixture

        fixture = self.make_fixture()
        fixture.request["inputs"] = [{"path": "README.md", "purpose": "outside declared read scope"}]
        cases["input outside read scope"] = fixture

        fixture = self.make_fixture("test-writer", "red")
        fixture.request["substage"] = "green"
        cases["invalid role substage pair"] = fixture

        fixture = self.make_fixture("test-writer", "red")
        fixture.request["contract"]["kind"] = "approved-epic-plan"
        cases["contract kind path mismatch"] = fixture

        fixture = self.make_fixture("test-writer", "red")
        fixture.request["read_scope"] = [{"class": "docs", "path": "install.sh"}]
        cases["implementation relabeled as docs"] = fixture

        fixture = self.make_fixture("test-writer", "red")
        fixture.request["write_scope"] = [{"class": "tests", "root": "src"}]
        cases["broad root relabeled as tests"] = fixture

        fixture = self.make_fixture("implementer", "green")
        fixture.request["write_scope"] = [{"class": "implementation", "path": "src"}]
        cases["directory used as exact file selector"] = fixture

        fixture = self.make_fixture("implementer", "green")
        fixture.request["write_scope"] = [{"class": "implementation", "root": "install.sh"}]
        cases["file used as root selector"] = fixture

        fixture = self.make_fixture("implementer", "green")
        colocated = fixture.root / "src" / "component_test.go"
        colocated.write_text("// test\n", encoding="utf-8")
        fixture.execution["path_policy"]["implementation_files"].append("src/component_test.go")
        fixture.request["write_scope"] = [
            {"class": "implementation", "path": "src/component_test.go"}
        ]
        fixture.request["inputs"] = []
        cases["implementation selector cannot absorb colocated test"] = fixture

        for label, fixture in cases.items():
            with self.subTest(path_case=label):
                fixture.write_request()
                result = fixture.invoke("validate-request")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")


class TestRoleScopes(RenderTestCase):
    def test_p3_exact_file_scopes_are_accepted_for_declared_implementation_and_docs(self) -> None:
        fixture = self.make_fixture("implementer", "green")
        result = fixture.invoke("validate-request")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_p3_forbidden_role_scopes_are_rejected(self) -> None:
        self.require_command("validate-request")
        cases = []
        fixture = self.make_fixture()
        fixture.request["read_scope"] = [{"class": "implementation", "path": "install.sh"}]
        cases.append(("test-writer implementation read", fixture))
        fixture = self.make_fixture()
        fixture.request["write_scope"] = [{"class": "implementation", "path": "install.sh"}]
        cases.append(("test-writer implementation write", fixture))
        fixture = self.make_fixture("reviewer", "review")
        fixture.request["write_scope"] = [{"class": "docs", "path": "README.md"}]
        cases.append(("read-only role write", fixture))
        fixture = self.make_fixture("implementer", "green")
        fixture.request["write_scope"] = [{"class": "tests", "path": "tests/exact_test.py"}]
        cases.append(("implementer exact test write", fixture))

        for label, fixture in cases:
            with self.subTest(scope_case=label):
                fixture.write_request()
                result = fixture.invoke("validate-request")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")


class TestActivePacketBinding(RenderTestCase):
    def test_p5_render_rejects_each_active_packet_request_mismatch(self) -> None:
        mutations = {
            "packet id": ("id", "other-packet"),
            "role": ("role", "reviewer"),
            "substage": ("substage", "audit"),
            "contract kind": ("contract_kind", "approved-epic-plan"),
            "contract hash": ("contract_sha256", "0" * 64),
        }
        for label, (field, value) in mutations.items():
            with self.subTest(mismatch=label):
                fixture = self.make_fixture()
                fixture.state["active_packet"][field] = value
                state_path = fixture.root / "docs" / ".cdad-state.json"
                state_path.write_text(json.dumps(fixture.state), encoding="utf-8")
                result = fixture.render()
                self.assertNotEqual(result.returncode, 0, f"render accepted active_packet {label} mismatch")
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")


class TestMetrics(RenderTestCase):
    def test_p5_metric_accepts_unknown_nulls(self) -> None:
        fixture = self.make_fixture()
        fixture.metric_path.write_text(json.dumps(fixture.metric()), encoding="utf-8")
        result = fixture.invoke("validate-metric", "--record", str(fixture.metric_path))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_p5_metric_rejects_identity_and_numeric_errors(self) -> None:
        self.require_command("validate-metric")
        fixture = self.make_fixture()
        mutations = {
            "execution mismatch": ("execution_id", "other"),
            "packet mismatch": ("packet_id", "other"),
            "feature mismatch": ("feature_id", "other"),
            "role mismatch": ("role", "reviewer"),
            "substage mismatch": ("substage", "audit"),
            "runtime mismatch": ("runtime", "codex"),
            "epic mismatch": ("epic_id", "other-epic"),
            "invalid outcome": ("outcome", "unknown"),
            "invalid started timestamp": ("started_at", "yesterday"),
            "invalid ended timestamp": ("ended_at", "tomorrow"),
            "configured model wrong type": ("model", {"configured": 3, "reported": None}),
            "reported model wrong type": ("model", {"configured": None, "reported": False}),
            "negative tokens": ("input_tokens", -1),
            "boolean tokens": ("output_tokens", True),
            "fractional context": ("context_limit", 1.5),
            "negative retries": ("retry_count", -1),
        }
        for label, (field, value) in mutations.items():
            with self.subTest(metric_case=label):
                metric = fixture.metric()
                metric[field] = value
                fixture.metric_path.write_text(json.dumps(metric), encoding="utf-8")
                result = fixture.invoke("validate-metric", "--record", str(fixture.metric_path))
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")

    def test_p5_metric_accepts_distinct_configured_and_reported_models(self) -> None:
        fixture = self.make_fixture()
        metric = fixture.metric()
        metric["model"] = {"configured": "provider/configured", "reported": "provider/reported"}
        metric["ended_at"] = "2026-09-17T00:01:00Z"
        metric["outcome"] = "completed"
        fixture.metric_path.write_text(json.dumps(metric), encoding="utf-8")
        result = fixture.invoke("validate-metric", "--record", str(fixture.metric_path))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_p5_metric_rejects_valid_rfc3339_end_before_start(self) -> None:
        fixture = self.make_fixture()
        metric = fixture.metric()
        metric["started_at"] = "2026-09-17T00:00:00Z"
        metric["ended_at"] = "2026-09-16T23:59:59+00:00"
        fixture.metric_path.write_text(json.dumps(metric), encoding="utf-8")
        result = fixture.invoke("validate-metric", "--record", str(fixture.metric_path))
        self.assertNotEqual(result.returncode, 0, "metric accepted ended_at before started_at")
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")

    def test_p5_metric_accepts_all_four_closed_outcomes(self) -> None:
        fixture = self.make_fixture()
        for outcome in ("prepared", "dispatched", "completed", "failed"):
            with self.subTest(outcome=outcome):
                metric = fixture.metric()
                metric["outcome"] = outcome
                if outcome in {"completed", "failed"}:
                    metric["ended_at"] = "2026-09-17T00:01:00+00:00"
                fixture.metric_path.write_text(json.dumps(metric), encoding="utf-8")
                result = fixture.invoke("validate-metric", "--record", str(fixture.metric_path))
                self.assertEqual(result.returncode, 0, result.stderr)


class TestDeterministicProperties(RenderTestCase):
    def test_p1_p2_seeded_100_valid_requests_are_deterministic_and_canonical(self) -> None:
        rng = random.Random(3001)
        for case_number in range(100):
            role, substage = rng.choice(ROLE_SUBSTAGES)
            objective = "objective-" + "".join(rng.choice("abcXYZ019 -_") for _ in range(rng.randint(1, 80)))
            with self.subTest(case=case_number, role=role, substage=substage):
                fixture = self.make_fixture(role, substage, objective=objective)
                first = fixture.render()
                second = fixture.render()
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(first.stdout.encode(), second.stdout.encode())
                metadata, metadata_text, _ = parse_packet(first.stdout)
                self.assertEqual(
                    metadata_text,
                    json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                )
                self.assertEqual(metadata["contract"]["sha256"], fixture.contract_sha256)


if __name__ == "__main__":
    unittest.main(verbosity=2)
