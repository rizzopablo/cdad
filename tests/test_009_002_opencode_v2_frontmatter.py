"""Static contract checks for generated OpenCode agent frontmatter.

Observable promises: PC-1..PC-4 (generated V2 schema, rule entries, reviewer
request temperature, and parseable orchestrator mode). Without these checks,
users can receive agents whose configured model/permissions are ignored.
"""
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
COMMITTED_AGENT_DIR = ROOT / "agents"
STAGING_AGENT_DIR = ROOT / "build/staging/agents/opencode"


def _frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path}: missing YAML frontmatter"
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw), raw


def test_generated_opencode_agents_use_v2_frontmatter():
    """PC-1..PC-4: every emitted OpenCode agent exposes valid V2 behavior."""
    committed = sorted(COMMITTED_AGENT_DIR.glob("*.md"))
    assert committed, "PC-1: expected committed generated OpenCode agent files"
    staged = sorted(STAGING_AGENT_DIR.glob("*.md")) if STAGING_AGENT_DIR.is_dir() else []
    files = committed + staged

    for path in files:
        data, raw = _frontmatter(path)
        assert "permission" not in data, f"PC-1: legacy permission key in {path}"
        assert "temperature" not in data, f"PC-1: top-level temperature in {path}"
        assert "edit: deny" not in raw, f"PC-1: inert edit deny in {path}"
        permissions = data.get("permissions")
        assert isinstance(permissions, list), f"PC-1: permissions must be a list in {path}"
        for entry in permissions:
            assert isinstance(entry, dict) and set(entry) == {"action", "resource", "effect"}, (
                f"PC-2: malformed V2 permission entry in {path}: {entry!r}"
            )
            assert entry["action"] in {"read", "edit", "grep", "shell", "*"}, (
                f"PC-2: unsupported permission action in {path}: {entry!r}"
            )

        is_reviewer = "reviewer" in path.stem
        request = data.get("request")
        if is_reviewer:
            assert isinstance(request, dict), f"PC-3: reviewer request missing in {path}"
            assert request.get("body", {}).get("temperature") == 0.1, (
                f"PC-3: reviewer temperature must be request.body.temperature=0.1 in {path}"
            )
        else:
            assert "request" not in data, f"PC-3: request is reserved for reviewer, found in {path}"

        if "orchestrator" in path.stem:
            assert data.get("mode") == "all", f"PC-4: orchestrator mode must remain all in {path}"
            assert isinstance(yaml.safe_load(raw), dict), f"PC-4: orchestrator YAML must parse in {path}"


def test_generated_permissions_preserve_v1_rules_and_order():
    """PC-2: each migrated agent retains its exact V1 policy and rule order.

    Without this check, users may receive agents with changed, missing, extra,
    or reordered access rules.
    """
    expected = {
        "cdad-test-writer": [
            ("read", "src/**", "deny"),
            ("read", "lib/**", "deny"),
            ("read", "src/**/*_test.go", "allow"),
            ("read", "src/**/test_*.py", "allow"),
            ("read", "src/**/*.test.js", "allow"),
            ("read", "src/**/*.test.ts", "allow"),
            ("read", "src/**/*.test.mjs", "allow"),
            ("read", "src/**/*.test.cjs", "allow"),
            ("read", "src/**/*.spec.ts", "allow"),
            ("read", "src/**/*.spec.js", "allow"),
            ("read", "lib/**/*_test.go", "allow"),
            ("read", "lib/**/test_*.py", "allow"),
            ("read", "lib/**/*.test.js", "allow"),
            ("read", "lib/**/*.test.ts", "allow"),
            ("read", "lib/**/*.test.mjs", "allow"),
            ("read", "lib/**/*.test.cjs", "allow"),
            ("read", "lib/**/*.spec.ts", "allow"),
            ("read", "lib/**/*.spec.js", "allow"),
            ("edit", "*", "deny"),
            ("edit", "tests/**", "allow"),
            ("edit", "**/tests/**", "allow"),
            ("edit", "**/*_test.go", "allow"),
            ("edit", "**/*.test.js", "allow"),
            ("edit", "**/*.test.ts", "allow"),
            ("edit", "**/*.test.mjs", "allow"),
            ("edit", "**/*.test.cjs", "allow"),
            ("edit", "**/*.spec.ts", "allow"),
            ("edit", "**/*.spec.js", "allow"),
            ("edit", "**/test_*.py", "allow"),
            ("shell", "*", "allow"),
            ("grep", "src/**", "deny"),
            ("grep", "lib/**", "deny"),
        ],
        "cdad-orchestrator": [("*", "*", "allow")],
    }

    directories = [COMMITTED_AGENT_DIR]
    if STAGING_AGENT_DIR.is_dir():
        directories.append(STAGING_AGENT_DIR)
    for directory in directories:
        for stem, rules in expected.items():
            path = directory / f"{stem}.md"
            assert path.is_file(), f"PC-2: expected {path}"
            data, _ = _frontmatter(path)
            actual = [
                (entry.get("action"), entry.get("resource"), entry.get("effect"))
                for entry in data.get("permissions", [])
            ]
            assert actual == rules, f"PC-2: permission rules/order differ in {path}"


def test_claude_code_agent_frontmatter_remains_on_its_own_schema():
    """PC-5: Claude Code agents retain their tools schema, not OpenCode V2."""
    files = sorted((ROOT / "agents/claude-code").glob("*.md"))
    assert files, "PC-5: expected Claude Code agent files"
    for path in files:
        data, _ = _frontmatter(path)
        assert "tools" in data, f"PC-5: Claude Code tools schema missing in {path}"
