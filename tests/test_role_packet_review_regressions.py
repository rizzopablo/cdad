#!/usr/bin/env python3
"""Black-box RED tests for the eight blocking 003-001 review findings."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.test_role_packet_render import PacketFixture
from tests.test_role_packets import (
    AUTHORITY_REF,
    INSTALLER,
    PACKET_CLI,
    REPO_ROOT,
    StateFixture,
    execution_document,
    invoke_validate_state,
    state_document,
)


ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")
PACKET_MARKER = "---cdad-packet-json"


def run_installer(
    *args: str,
    install_root: Path,
    include_home: bool = True,
    include_tmpdir: bool = True,
    extra_skill_dirs: tuple[Path, ...] = (),
    installer: Path = INSTALLER,
) -> subprocess.CompletedProcess[str]:
    # Portabilidad (review-t1/T6): el staging se garantiza en una raíz de
    # producto con manifest (el checkout real si la tiene, o una copia
    # temporal generada por `make staging`); nunca se escribe en el checkout.
    from tests.product_staging import product_root

    install_product = product_root() if installer == INSTALLER else installer.parent
    env = os.environ.copy()
    env["CDAD_INSTALL_ROOT"] = str(install_root)
    env["CDAD_SKILL_EXTRA_DIRS"] = os.pathsep.join(
        str(path) for path in extra_skill_dirs
    )
    if not include_home:
        env.pop("HOME", None)
    if not include_tmpdir:
        env.pop("TMPDIR", None)
    return subprocess.run(
        ["bash", str(installer), *args],
        cwd=install_product,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def packet_and_legacy_contract_errors(agent_text: str) -> list[str]:
    """Return missing observable branches in an installed Task agent contract."""
    errors: list[str] = []
    marker_match = re.search(re.escape(PACKET_MARKER), agent_text, re.IGNORECASE)
    if marker_match is None:
        return ["does not recognize the canonical packet marker"]

    marker_window = agent_text[
        max(0, marker_match.start() - 240) : marker_match.end() + 520
    ]
    if not re.search(r"(?i)\b(valid|validated|v[aá]lid[oa])\b", marker_window):
        errors.append("does not require the packet to be valid")
    if not re.search(
        r"(?is)(do not|must not|without|no (?:carga|recarga)).{0,100}"
        r"(?:load|reload|cargar|recargar).{0,100}cdad-cycle",
        marker_window,
    ):
        errors.append("valid-packet branch does not forbid reloading cdad-cycle")

    if not re.search(
        r"(?is)(legacy|otherwise|without (?:a )?valid packet|"
        r"if (?:the )?packet (?:is )?(?:absent|invalid)|flujo heredado).{0,500}"
        r"(?:load|reload|cargar|recargar).{0,100}cdad-cycle",
        agent_text,
    ):
        errors.append("legacy branch does not retain cdad-cycle loading")

    for paragraph in re.split(r"\n\s*\n", agent_text):
        if not re.search(
            r"(?is)(?:load|reload|cargar|recargar).{0,100}cdad-cycle", paragraph
        ):
            continue
        if re.search(
            r"(?is)(do not|must not|without|no (?:carga|recarga)).{0,100}"
            r"(?:load|reload|cargar|recargar)",
            paragraph,
        ):
            continue
        if not re.search(
            r"(?i)(legacy|otherwise|without (?:a )?valid packet|"
            r"packet (?:is )?(?:absent|invalid)|flujo heredado)",
            paragraph,
        ):
            errors.append("contains an unconditional cdad-cycle load directive")
            break
    return errors


RUNTIME_AGENT_PREFIXES = (".config/opencode/agents", ".claude/agents")
RUNTIME_SKILL_PREFIXES = (
    ".config/opencode/skills",
    ".agents/skills",
    ".claude/skills",
)


def assess_uninstall_runtime_plan(install_root: Path, published: str) -> list[str]:
    """Oracle for the signed review-7 amendment (PD-9, PD-8/D4).

    Enumerates the runtime destinations the installer actually wrote under
    ``install_root`` (real runtime trees, derived from what is installed,
    not a hand-written list) and returns the ways ``published`` — the
    ``--uninstall --force --dry-run`` output — contradicts them:

    - the plan must enumerate every installed runtime destination;
    - the plan must NOT enumerate the public layout (``<root>/agents/`` or
      ``<root>/skills/``), which PD-9 no longer installs by default;
    - an install root without runtime destinations cannot back an honest
      plan, so a plan satisfying the public layout alone must fail.
    """
    violations: list[str] = []
    expected_targets: list[Path] = []
    for prefix in RUNTIME_AGENT_PREFIXES:
        base = install_root / prefix
        if base.is_dir():
            expected_targets.extend(
                path for path in sorted(base.glob("cdad-*.md")) if path.is_file()
            )
    for prefix in RUNTIME_SKILL_PREFIXES:
        base = install_root / prefix
        if base.is_dir():
            expected_targets.extend(
                skill
                for skill in sorted(base.iterdir())
                if skill.is_dir() and (skill / "SKILL.md").is_file()
            )
    if not expected_targets:
        violations.append(
            f"{install_root}: no runtime agent/skill destinations installed; "
            "the uninstall plan has no installed layout to enumerate"
        )
        return violations
    missing = [str(path) for path in expected_targets if str(path) not in published]
    if missing:
        violations.append(
            "uninstall did not enumerate runtime destinations: " + ", ".join(missing)
        )
    for public_prefix in ("agents", "skills"):
        public_dir = str(install_root / public_prefix)
        if re.search(re.escape(public_dir) + r"(?:/|\b)", published):
            violations.append(
                "uninstall plan enumerates public-layout destination "
                f"{public_dir} which PD-9 no longer installs"
            )
    return violations


class TestReviewRegressions(unittest.TestCase):
    """One failing method per blocking review finding."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-review-install-")
        cls.install_root = Path(cls._install_tmp.name).resolve()
        cls.install_result = run_installer(
            "--basic", install_root=cls.install_root
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def make_packet_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], PacketFixture]:
        temp = tempfile.TemporaryDirectory(prefix="cdad-review-project-")
        self.addCleanup(temp.cleanup)
        fixture = PacketFixture(Path(temp.name).resolve(), "test-writer", "red")
        fixture.write()
        return temp, fixture

    def test_p1_p3_p6_all_task_agents_branch_valid_packet_from_legacy(self) -> None:
        """Finding 1: valid packets bypass full skills; legacy Tasks still load them."""
        violations: list[str] = []
        if self.install_result.returncode != 0:
            violations.append(
                "isolated install failed: "
                + (self.install_result.stderr or self.install_result.stdout).strip()
            )
        else:
            installed_agents = self.install_root / ".config/opencode/agents"
            for role in ROLE_AGENTS:
                agent_path = installed_agents / f"cdad-{role}.md"
                if not agent_path.is_file():
                    violations.append(f"{role}: installed Task agent is missing")
                    continue
                text = agent_path.read_text(encoding="utf-8")
                for error in packet_and_legacy_contract_errors(text):
                    violations.append(f"{role}: {error}")

        self.assertEqual(
            violations,
            [],
            "installed Task agents do not implement the valid-packet/legacy split:\n"
            + "\n".join(violations),
        )

    def test_p4_scoped_exception_rejects_self_consistent_other_epic(self) -> None:
        """Finding 2: ADR-010 cannot be coherently relabeled for another epic."""
        other_epic = "epic-004-other"
        other_feature = "004-001-other"
        other_authority = f"docs/epics/{other_epic}/execution.md"
        execution = execution_document()
        execution["execution"].update(
            {
                "epic_id": other_epic,
                "feature_id": other_feature,
                "authority_ref": other_authority,
            }
        )
        state = state_document(execution)
        state.update(
            {
                "active_epic": other_epic,
                "active_feature": other_feature,
                "epic_features": [{"id": other_feature, "status": "in-progress"}],
            }
        )
        state["hitl_delegation"].update(
            {"epic_id": other_epic, "source": other_authority}
        )

        with tempfile.TemporaryDirectory(prefix="cdad-other-epic-") as project_dir:
            root = Path(project_dir).resolve()
            fixture = StateFixture(root, execution, state, write_authority=False)
            fixture.write()
            authority = root / other_authority
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Other epic authority\n", encoding="utf-8")
            result = invoke_validate_state(fixture)

        self.assertNotEqual(
            result.returncode,
            0,
            "ADR-010 epic-003-single-model was accepted by a self-consistent other epic",
        )
        self.assertTrue(result.stderr.strip(), "rejection lacked a stderr diagnostic")
        self.assertEqual(result.stdout, "", "rejection emitted partial stdout")

    def test_p2_internal_symlink_cannot_relabel_implementation_as_docs_or_tests(self) -> None:
        """Finding 3: scope classification follows internal symlink targets."""
        accepted_relabels: list[str] = []
        for declared_class in ("docs", "tests"):
            with self.subTest(declared_class=declared_class):
                _, fixture = self.make_packet_fixture()
                secret = fixture.root / "src" / "secret.py"
                secret.write_text("implementation secret\n", encoding="utf-8")
                link = fixture.root / declared_class / "impl-link"
                link.symlink_to(Path("../src"), target_is_directory=True)
                fixture.request["read_scope"].append(
                    {"class": declared_class, "root": declared_class}
                )
                fixture.request["inputs"] = [
                    {
                        "path": f"{declared_class}/impl-link/secret.py",
                        "purpose": "attempted relabel",
                    }
                ]
                fixture.write_request()
                result = fixture.invoke("validate-request")
                if result.returncode == 0:
                    accepted_relabels.append(declared_class)
                else:
                    self.assertTrue(
                        result.stderr.strip(),
                        f"{declared_class} rejection lacked a stderr diagnostic",
                    )
                    self.assertEqual(result.stdout, "")

        self.assertEqual(
            accepted_relabels,
            [],
            "internal symlink relabeled src as: " + ", ".join(accepted_relabels),
        )

    def test_p6_install_and_uninstall_reject_source_overlap_and_list_runtime_targets(self) -> None:
        """Finding 4: every managed destination rejects source overlap before actions."""
        violations: list[str] = []
        operations = (
            ("install dry-run", ("--dry-run", "--basic")),
            ("check", ("--check",)),
            ("uninstall dry-run", ("--uninstall", "--force", "--dry-run")),
        )

        for operation, args in operations:
            result = run_installer(*args, install_root=REPO_ROOT)
            if result.returncode == 0:
                violations.append(
                    f"{operation} accepted CDAD_INSTALL_ROOT equal to source repo"
                )
            if re.search(r"(?m)^DRY-RUN (?:COPY|UNINSTALL|MARKER) ", result.stdout):
                violations.append(
                    f"{operation} published actions before rejecting source overlap"
                )

        with tempfile.TemporaryDirectory(prefix="cdad-repo-link-") as link_dir:
            repo_link = Path(link_dir) / "repo"
            repo_link.symlink_to(REPO_ROOT, target_is_directory=True)
            linked_installer = repo_link / "install.sh"
            for operation, args in operations:
                result = run_installer(
                    *args,
                    install_root=REPO_ROOT,
                    installer=linked_installer,
                )
                if result.returncode == 0:
                    violations.append(
                        f"{operation} accepted source repo through installer symlink"
                    )
                if not result.stderr.strip():
                    violations.append(
                        f"{operation} rejection through installer symlink lacked a diagnostic"
                    )
                if re.search(
                    r"(?m)^DRY-RUN (?:COPY|UNINSTALL|MARKER) ",
                    result.stdout + result.stderr,
                ):
                    violations.append(
                        f"{operation} published actions before rejecting installer symlink"
                    )

        source_skills = REPO_ROOT / "skills"
        with tempfile.TemporaryDirectory(prefix="cdad-overlap-link-") as link_dir:
            source_skills_link = Path(link_dir) / "skills"
            source_skills_link.symlink_to(source_skills, target_is_directory=True)
            overlapping_extras = (
                ("direct source skills", source_skills),
                ("symlink to source skills", source_skills_link),
            )
            for overlap, extra_dir in overlapping_extras:
                for operation, args in operations:
                    result = run_installer(
                        *args,
                        install_root=self.install_root,
                        extra_skill_dirs=(extra_dir,),
                    )
                    if result.returncode == 0:
                        violations.append(
                            f"{operation} accepted extra dir overlapping {overlap}"
                        )
                    if not result.stderr.strip():
                        violations.append(
                            f"{operation} rejection for {overlap} lacked a diagnostic"
                        )
                    if re.search(
                        r"(?m)^DRY-RUN (?:COPY|UNINSTALL|MARKER) ", result.stdout
                    ):
                        violations.append(
                            f"{operation} published actions before rejecting {overlap}"
                        )

        if self.install_result.returncode != 0:
            violations.append(
                "isolated install for enumeration failed: "
                + (self.install_result.stderr or self.install_result.stdout).strip()
            )
        else:
            dry_uninstall = run_installer(
                "--uninstall", "--force", "--dry-run", install_root=self.install_root
            )
            if dry_uninstall.returncode != 0:
                violations.append(
                    "isolated uninstall dry-run failed: "
                    + (dry_uninstall.stderr or dry_uninstall.stdout).strip()
                )
            else:
                published = dry_uninstall.stdout + dry_uninstall.stderr
                violations.extend(
                    assess_uninstall_runtime_plan(self.install_root, published)
                )

        with tempfile.TemporaryDirectory(prefix="cdad-valid-extra-") as extra_dir:
            valid_extra = Path(extra_dir).resolve()
            isolated_install = run_installer(
                "--basic",
                install_root=self.install_root,
                extra_skill_dirs=(valid_extra,),
            )
            if isolated_install.returncode != 0:
                violations.append(
                    "isolated extra dir install failed: "
                    + (isolated_install.stderr or isolated_install.stdout).strip()
                )
            else:
                valid_results = {
                    operation: run_installer(
                        *args,
                        install_root=self.install_root,
                        extra_skill_dirs=(valid_extra,),
                    )
                    for operation, args in operations
                }
                for operation, result in valid_results.items():
                    if result.returncode != 0:
                        violations.append(
                            f"isolated extra dir {operation} failed: "
                            + (result.stderr or result.stdout).strip()
                        )

                expected_extra_targets = [
                    valid_extra / path.name
                    for path in sorted(source_skills.iterdir())
                    if path.is_dir() and (path / "SKILL.md").is_file()
                ]
                for operation in ("install dry-run", "uninstall dry-run"):
                    published = (
                        valid_results[operation].stdout
                        + valid_results[operation].stderr
                    )
                    missing = [
                        str(path)
                        for path in expected_extra_targets
                        if str(path) not in published
                    ]
                    if missing:
                        violations.append(
                            f"isolated extra dir {operation} did not enumerate targets: "
                            + ", ".join(missing)
                        )

        self.assertEqual(violations, [], "install manifest is incoherent:\n" + "\n".join(violations))

    def test_p6_omitted_project_root_uses_current_working_directory(self) -> None:
        """Finding 5: every CLI command may resolve project root from cwd."""
        _, fixture = self.make_packet_fixture()
        result = subprocess.run(
            [
                sys.executable,
                str(PACKET_CLI),
                "validate-state",
                "--execution-context",
                str(fixture.root / "EXECUTION.json"),
            ],
            cwd=fixture.root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            "omitted --project-root did not use cwd: " + (result.stderr or result.stdout),
        )

    def test_p2_validate_packet_rejects_crlf_byte_variant(self) -> None:
        """Finding 6: canonical packet validation compares raw bytes, including LF."""
        _, fixture = self.make_packet_fixture()
        render = subprocess.run(
            [
                sys.executable,
                str(PACKET_CLI),
                "render",
                "--project-root",
                str(fixture.root),
                "--execution-context",
                str(fixture.root / "EXECUTION.json"),
                "--request",
                str(fixture.request_path),
            ],
            cwd=REPO_ROOT,
            text=False,
            capture_output=True,
            check=False,
        )
        self.assertEqual(render.returncode, 0, render.stderr.decode(errors="replace"))
        self.assertIn(b"\n", render.stdout)
        self.assertNotIn(b"\r\n", render.stdout)
        fixture.packet_path.write_bytes(render.stdout.replace(b"\n", b"\r\n"))

        result = fixture.invoke("validate-packet", "--packet", str(fixture.packet_path))
        self.assertNotEqual(
            result.returncode,
            0,
            "validate-packet accepted a CRLF byte variant of the canonical LF packet",
        )
        self.assertTrue(result.stderr.strip(), "rejection lacked a stderr diagnostic")
        self.assertEqual(result.stdout, "", "rejection emitted partial stdout")

    def test_p5_metric_without_active_packet_rejects_unbound_identity(self) -> None:
        """Finding 7: no metric identity may be invented when active_packet is null."""
        _, fixture = self.make_packet_fixture()
        fixture.state["active_packet"] = None
        state_path = fixture.root / "docs" / ".cdad-state.json"
        state_path.write_text(json.dumps(fixture.state), encoding="utf-8")

        accepted: list[str] = []
        metrics = {
            "invented packet": {"packet_id": "invented-packet"},
            "invented role/substage": {
                "packet_id": "invented-packet",
                "role": "operator",
                "substage": "deploy",
            },
        }
        for label, changes in metrics.items():
            metric = fixture.metric()
            metric.update(changes)
            fixture.metric_path.write_text(json.dumps(metric), encoding="utf-8")
            result = fixture.invoke(
                "validate-metric", "--record", str(fixture.metric_path)
            )
            if result.returncode == 0:
                accepted.append(label)
            else:
                self.assertTrue(result.stderr.strip(), f"{label} rejection lacked stderr")
                self.assertEqual(result.stdout, "")

        self.assertEqual(
            accepted,
            [],
            "metric identity was accepted without active_packet: " + ", ".join(accepted),
        )

    def test_p6_explicit_install_root_works_without_home(self) -> None:
        """Finding 8: an explicit install root is sufficient without HOME/TMPDIR."""
        with tempfile.TemporaryDirectory(prefix="cdad-no-home-install-") as install_dir:
            result = run_installer(
                "--dry-run",
                "--basic",
                install_root=Path(install_dir).resolve(),
                include_home=False,
                include_tmpdir=False,
            )
        self.assertEqual(
            result.returncode,
            0,
            "explicit CDAD_INSTALL_ROOT still depended on HOME/TMPDIR: "
            + (result.stderr or result.stdout),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
