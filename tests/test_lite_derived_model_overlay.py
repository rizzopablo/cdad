"""Lite spec 2026-11-10: the derived agent's `model:` belongs to the project
owner (docs/specs/lite-derived-agent-model-overlay-2026-11-10/spec.md)."""
from __future__ import annotations

import json
from pathlib import Path

from test_007_006_withdraw_and_republish import (
    DERIVED_DIR_REL,
    MANIFEST_REL,
    VERSION_V1,
    VERSION_V2,
    _DriftProject,
    _model_line,
    _mutate_source_agent,
    _republish,
    _simulated_install,
    _with_custom_model,
)

AGENT = "cdad-implementer.md"
INSTALLED = "opencode-go/installed-model#high"
OWNER = "claude-code/owner-model#low"


def _set_model(path: Path, model: str) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    lines = [f"model: {model}" if line.startswith("model:") else line
             for line in lines]
    path.write_text("\n".join(lines), encoding="utf-8")


def _project(tmp_path: Path) -> tuple[_DriftProject, Path]:
    install = _simulated_install(tmp_path, "install", version=VERSION_V1)
    _with_custom_model(install, AGENT, INSTALLED)
    fx = _DriftProject(tmp_path / "proj", install=install)
    derived = fx.root / DERIVED_DIR_REL / AGENT
    assert _model_line(derived) == [f"model: {INSTALLED}"], "fixture"
    return fx, derived


def test_owner_model_survives_republish_and_source_updates(tmp_path: Path) -> None:
    fx, derived = _project(tmp_path)
    _set_model(derived, OWNER)
    proc = _republish(fx)
    assert proc.returncode == 0, f"PC1: model-only edit accepted: {proc.stderr!r}"
    assert _model_line(derived) == [f"model: {OWNER}"], "PC2: owner model kept"

    (fx.install / "version.txt").write_text(VERSION_V2 + "\n", encoding="utf-8")
    _mutate_source_agent(fx.install, AGENT, b"<!-- v2 body -->\n")
    _set_model(fx.install / ".config/opencode/agents" / AGENT, "other/new-installed")
    proc = _republish(fx)
    assert proc.returncode == 0, f"PC2: republish after update: {proc.stderr!r}"
    text = derived.read_text(encoding="utf-8")
    assert "<!-- v2 body -->" in text, "PC2: behaviour comes from the source"
    assert _model_line(derived) == [f"model: {OWNER}"], "PC2: owner model kept"
    again = _republish(fx)
    assert again.returncode == 0 and _model_line(derived) == [f"model: {OWNER}"]


def test_body_edit_still_rejected(tmp_path: Path) -> None:
    fx, derived = _project(tmp_path)
    _set_model(derived, OWNER)
    derived.write_text(derived.read_text(encoding="utf-8") + "\n<!-- mano -->\n",
                       encoding="utf-8")
    proc = _republish(fx)
    assert proc.returncode != 0, "PC4: an edit outside model: is rejected"
    assert "modified by hand" in proc.stdout + proc.stderr


def test_legacy_manifest_accepts_model_only_edit(tmp_path: Path) -> None:
    fx, derived = _project(tmp_path)
    manifest_path = fx.root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest["agents"].values():
        entry.pop("base_sha256", None)
        entry.pop("project_model", None)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    _set_model(derived, OWNER)
    proc = _republish(fx)
    assert proc.returncode == 0, f"PC5: legacy manifest: {proc.stderr!r}"
    assert _model_line(derived) == [f"model: {OWNER}"]
