"""Tests provider-aware commands — PC-004-01 a PC-004-06 (RED phase).

Cada test verifica el comportamiento ESPECIFICADO que AÚN NO está implementado.
Los tests DEBEN FALLAR con AssertionError porque la implementación actual:
- Usa `_require_api_key()` y `_make_llm_client(api_key=...)` (legacy)
- No llama a `resolve_provider`
- No acepta flag `--provider`
- No valida existencia de `cdad.toml`
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cdad.cli import main as cli_main
from cdad.llm.client import LLMClient
from cdad.llm.provider import ConfigurationError
from cdad.llm.registry import resolve_provider

runner = CliRunner()

# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------


def _make_fake_provider():
    """Crear un fake LLMProvider con _model_id."""
    fake = MagicMock()
    fake._model_id = "claude-opus-4-7"
    fake.send_message.return_value = "fake response"
    fake.name = "anthropic"
    return fake


def _create_cdad_toml(project_root: Path, default: str = "anthropic/claude-opus-4-7") -> Path:
    """Crear cdad.toml con [agents] default en project_root."""
    toml = project_root / "cdad.toml"
    toml.write_text(
        f'[agents]\ndefault = "{default}"\n',
        encoding="utf-8",
    )
    return toml


def _setup_project_with_toml(tmp_path: Path) -> Path:
    """Crear proyecto genérico con cdad.toml y estructura básica."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-project"\n')
    _create_cdad_toml(tmp_path)
    return tmp_path


def _patch_resolve(monkeypatch, fake_provider):
    """Mockear resolve_provider para retornar fake_provider."""
    monkeypatch.setattr(
        cli_main,
        "resolve_provider",
        lambda name, config=None, override=None: fake_provider,
    )


@pytest.fixture(autouse=True)
def _bypass_api_key_check(monkeypatch):
    """Evita que los comandos aborten por falta de ANTHROPIC_API_KEY.
    Esto permite que los tests lleguen a la lógica que realmente verificamos."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-for-provider-aware")


def _patch_llm_client(monkeypatch, mock_instance):
    """Mockear LLMClient para retornar mock_instance."""
    monkeypatch.setattr(cli_main, "LLMClient", lambda *a, **kw: mock_instance)


# ---------------------------------------------------------------------------
# PC-004-01: discover_uses_resolve_provider
# ---------------------------------------------------------------------------


class TestDiscoverUsesResolveProvider:
    """PC-004-01: discover calls resolve_provider(name="architect", ...) y
    construye LLMClient(provider=instance, model=model_id), NO LLMClient(api_key=...)."""

    def test_discover_calls_resolve_provider_with_architect(self, tmp_path, monkeypatch):
        """Verifica que discover llama a resolve_provider con name='architect'."""
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake discovery content.")

        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["name"] = name
            calls["config"] = config
            calls["override"] = override
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        result = runner.invoke(
            cli_main.app,
            ["discover", "--feature", "test feature", "--path", str(project)],
        )

        assert calls.get("name") == "architect", (
            f"discover debe llamar resolve_provider(name='architect'), got name={calls.get('name')}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_discover_builds_llm_client_with_provider_not_api_key(self, tmp_path, monkeypatch):
        """Verifica que discover construye LLMClient con provider=instance, no api_key=."""
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake discovery content.")

        fake_provider = _make_fake_provider()
        llm_calls = []

        def fake_resolve(name, config=None, override=None):
            return fake_provider

        def fake_llm_client(**kw):
            llm_calls.append(kw)
            return MagicMock()

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", fake_llm_client)

        result = runner.invoke(
            cli_main.app,
            ["discover", "--feature", "test feature", "--path", str(project)],
        )

        assert len(llm_calls) >= 1, (
            f"LLMClient debe ser llamado al menos una vez. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        # Verificar que NO se usa api_key
        for kw in llm_calls:
            assert "api_key" not in kw, (
                f"LLMClient no debe construirse con api_key=. Got kwargs: {kw}"
            )
        # Verificar que se usa provider
        assert "provider" in llm_calls[-1], (
            f"LLMClient debe construirse con provider=. Got kwargs: {llm_calls[-1]}"
        )


# ---------------------------------------------------------------------------
# PC-004-02: spec_uses_resolve_provider
# ---------------------------------------------------------------------------


class TestSpecUsesResolveProvider:
    """PC-004-02: spec llama resolve_provider(name="architect", ...) y
    construye LLMClient(provider=instance, model=model_id)."""

    def test_spec_calls_resolve_provider_with_architect(self, tmp_path, monkeypatch):
        """Verifica que spec llama a resolve_provider con name='architect'."""
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake discovery content.")

        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["name"] = name
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "test-spec", "--path", str(project)],
        )

        assert calls.get("name") == "architect", (
            f"spec debe llamar resolve_provider(name='architect'), got name={calls.get('name')}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_spec_builds_llm_client_with_provider_not_api_key(self, tmp_path, monkeypatch):
        """Verifica que spec construye LLMClient con provider=, no api_key=."""
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake discovery content.")

        fake_provider = _make_fake_provider()
        llm_calls = []

        def fake_resolve(name, config=None, override=None):
            return fake_provider

        def fake_llm_client(**kw):
            llm_calls.append(kw)
            return MagicMock()

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", fake_llm_client)

        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "test-spec", "--path", str(project)],
        )

        assert len(llm_calls) >= 1, (
            f"LLMClient debe ser llamado. Exit code: {result.exit_code}, Output: {result.output}"
        )
        for kw in llm_calls:
            assert "api_key" not in kw, f"LLMClient no debe usar api_key=. Got: {kw}"
        assert "provider" in llm_calls[-1], f"LLMClient debe usar provider=. Got: {llm_calls[-1]}"


# ---------------------------------------------------------------------------
# PC-004-03: architect_uses_resolve_provider
# ---------------------------------------------------------------------------


class TestArchitectUsesResolveProvider:
    """PC-004-03: architect llama resolve_provider(name="architect", ...) y
    construye LLMClient(provider=instance, model=model_id)."""

    def test_architect_calls_resolve_provider_with_architect(self, tmp_path, monkeypatch):
        """Verifica que architect llama a resolve_provider con name='architect'."""
        project = _setup_project_with_toml(tmp_path)
        target = project / "src" / "foo.py"
        target.parent.mkdir(exist_ok=True)
        target.write_text("def foo(): return 1\n")

        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["name"] = name
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        result = runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(project)],
        )

        assert calls.get("name") == "architect", (
            f"architect debe llamar resolve_provider(name='architect'), got name={calls.get('name')}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_architect_builds_llm_client_with_provider_not_api_key(self, tmp_path, monkeypatch):
        """Verifica que architect construye LLMClient con provider=, no api_key=."""
        project = _setup_project_with_toml(tmp_path)
        target = project / "src" / "foo.py"
        target.parent.mkdir(exist_ok=True)
        target.write_text("def foo(): return 1\n")

        fake_provider = _make_fake_provider()
        llm_calls = []

        def fake_resolve(name, config=None, override=None):
            return fake_provider

        def fake_llm_client(**kw):
            llm_calls.append(kw)
            return MagicMock()

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", fake_llm_client)

        runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(project)],
        )

        assert len(llm_calls) >= 1, "LLMClient debe ser llamado"
        for kw in llm_calls:
            assert "api_key" not in kw, f"LLMClient no debe usar api_key=. Got: {kw}"
        assert "provider" in llm_calls[-1], f"LLMClient debe usar provider=. Got: {llm_calls[-1]}"


# ---------------------------------------------------------------------------
# PC-004-04: test_command_uses_test_writer_role
# ---------------------------------------------------------------------------


class TestCommandUsesTestWriterRole:
    """PC-004-04: test llama resolve_provider(name="test_writer", ...) NO "architect"."""

    def test_test_command_calls_resolve_provider_with_test_writer(self, tmp_path, monkeypatch):
        """Verifica que test llama a resolve_provider con name='test_writer'."""
        project = _setup_project_with_toml(tmp_path)
        spec_file = project / "docs" / "specs" / "my-feature.md"
        spec_file.write_text("""---
title: My Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Something works
**Description**: Feature must work as expected
**Verification**: test
""")

        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["name"] = name
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        result = runner.invoke(
            cli_main.app,
            ["test", "my-feature", "--path", str(project)],
        )

        assert calls.get("name") == "test_writer", (
            f"test debe llamar resolve_provider(name='test_writer'), got name={calls.get('name')}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_test_command_does_not_use_architect_role(self, tmp_path, monkeypatch):
        """Verifica que test NO llama resolve_provider con name='architect'."""
        project = _setup_project_with_toml(tmp_path)
        spec_file = project / "docs" / "specs" / "my-feature.md"
        spec_file.write_text("""---
title: My Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Something works
**Description**: Feature must work as expected
**Verification**: test
""")

        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["name"] = name
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        runner.invoke(
            cli_main.app,
            ["test", "my-feature", "--path", str(project)],
        )

        assert calls.get("name") != "architect", (
            f"test NO debe llamar resolve_provider(name='architect'), got name={calls.get('name')}. "
            f"Debe usar 'test_writer'."
        )


# ---------------------------------------------------------------------------
# PC-004-05: commands_accept_provider_override
# ---------------------------------------------------------------------------


class TestCommandsAcceptProviderOverride:
    """PC-004-05: Los 4 comandos aceptan flag --provider que se propaga
    como override a resolve_provider."""

    OVERRIDE = "openai/gpt-4o"

    def _setup_discover_project(self, tmp_path):
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake content.")
        return project

    def _setup_spec_project(self, tmp_path):
        project = _setup_project_with_toml(tmp_path)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake content.")
        return project

    def _setup_architect_project(self, tmp_path):
        project = _setup_project_with_toml(tmp_path)
        target = project / "src" / "foo.py"
        target.parent.mkdir(exist_ok=True)
        target.write_text("def foo(): return 1\n")
        return project, target

    def _setup_test_project(self, tmp_path):
        project = _setup_project_with_toml(tmp_path)
        spec_file = project / "docs" / "specs" / "my-feature.md"
        spec_file.write_text("""---
title: My Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Something works
**Description**: Feature must work as expected
**Verification**: test
""")
        return project

    def test_discover_accepts_provider_override(self, tmp_path, monkeypatch):
        """discover --provider pasa override a resolve_provider."""
        project = self._setup_discover_project(tmp_path)
        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["override"] = override
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        runner.invoke(
            cli_main.app,
            ["discover", "--feature", "test", "--path", str(project), "--provider", self.OVERRIDE],
        )

        assert calls.get("override") == self.OVERRIDE, (
            f"discover debe propagar --provider como override='{self.OVERRIDE}', "
            f"got override={calls.get('override')}"
        )

    def test_spec_accepts_provider_override(self, tmp_path, monkeypatch):
        """spec --provider pasa override a resolve_provider."""
        project = self._setup_spec_project(tmp_path)
        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["override"] = override
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        runner.invoke(
            cli_main.app,
            ["spec", "--name", "test", "--path", str(project), "--provider", self.OVERRIDE],
        )

        assert calls.get("override") == self.OVERRIDE, (
            f"spec debe propagar --provider como override='{self.OVERRIDE}', "
            f"got override={calls.get('override')}"
        )

    def test_architect_accepts_provider_override(self, tmp_path, monkeypatch):
        """architect --provider pasa override a resolve_provider."""
        project, target = self._setup_architect_project(tmp_path)
        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["override"] = override
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(project), "--provider", self.OVERRIDE],
        )

        assert calls.get("override") == self.OVERRIDE, (
            f"architect debe propagar --provider como override='{self.OVERRIDE}', "
            f"got override={calls.get('override')}"
        )

    def test_test_accepts_provider_override(self, tmp_path, monkeypatch):
        """test --provider pasa override a resolve_provider."""
        project = self._setup_test_project(tmp_path)
        fake_provider = _make_fake_provider()
        calls = {}

        def fake_resolve(name, config=None, override=None):
            calls["override"] = override
            return fake_provider

        monkeypatch.setattr(cli_main, "resolve_provider", fake_resolve)
        monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: MagicMock())

        runner.invoke(
            cli_main.app,
            ["test", "my-feature", "--path", str(project), "--provider", self.OVERRIDE],
        )

        assert calls.get("override") == self.OVERRIDE, (
            f"test debe propagar --provider como override='{self.OVERRIDE}', "
            f"got override={calls.get('override')}"
        )


# ---------------------------------------------------------------------------
# PC-004-06: commands_abort_without_config
# ---------------------------------------------------------------------------


class TestCommandsAbortWithoutConfig:
    """PC-004-06: Sin cdad.toml o sin [agents]/default, los 4 comandos abortan
    con exit code 2, stderr contiene 'cdad config auto' y 'cdad config set'."""

    def test_discover_aborts_without_config(self, tmp_path):
        """discover sin cdad.toml → exit code 2 + mensaje de config."""
        project = tmp_path
        (project / "docs" / "specs").mkdir(parents=True)
        (project / "tests").mkdir(exist_ok=True)
        (project / "src").mkdir(exist_ok=True)
        # NO crear cdad.toml

        result = runner.invoke(
            cli_main.app,
            ["discover", "--feature", "test", "--path", str(project)],
        )

        assert result.exit_code == 2, (
            f"discover sin cdad.toml debe abortar con exit code 2, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        combined_output = result.output + (result.stderr if hasattr(result, "stderr") else "")
        assert "cdad config auto" in combined_output, (
            f"Output debe mencionar 'cdad config auto', got: {combined_output}"
        )
        assert "cdad config set" in combined_output, (
            f"Output debe mencionar 'cdad config set', got: {combined_output}"
        )

    def test_spec_aborts_without_config(self, tmp_path):
        """spec sin cdad.toml → exit code 2 + mensaje de config."""
        project = tmp_path
        (project / "docs" / "specs").mkdir(parents=True)
        (project / "tests").mkdir(exist_ok=True)
        (project / "src").mkdir(exist_ok=True)
        (project / "docs" / "discovery.md").write_text("# Discovery\nFake.")

        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "test", "--path", str(project)],
        )

        assert result.exit_code == 2, (
            f"spec sin cdad.toml debe abortar con exit code 2, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        combined_output = result.output + (result.stderr if hasattr(result, "stderr") else "")
        assert "cdad config auto" in combined_output, (
            f"Output debe mencionar 'cdad config auto', got: {combined_output}"
        )
        assert "cdad config set" in combined_output, (
            f"Output debe mencionar 'cdad config set', got: {combined_output}"
        )

    def test_architect_aborts_without_config(self, tmp_path):
        """architect sin cdad.toml → exit code 2 + mensaje de config."""
        project = tmp_path
        (project / "docs" / "specs").mkdir(parents=True)
        (project / "tests").mkdir(exist_ok=True)
        (project / "src").mkdir(exist_ok=True)
        target = project / "src" / "foo.py"
        target.write_text("def foo(): return 1\n")

        result = runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(project)],
        )

        assert result.exit_code == 2, (
            f"architect sin cdad.toml debe abortar con exit code 2, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        combined_output = result.output + (result.stderr if hasattr(result, "stderr") else "")
        assert "cdad config auto" in combined_output, (
            f"Output debe mencionar 'cdad config auto', got: {combined_output}"
        )
        assert "cdad config set" in combined_output, (
            f"Output debe mencionar 'cdad config set', got: {combined_output}"
        )

    def test_test_aborts_without_config(self, tmp_path):
        """test sin cdad.toml → exit code 2 + mensaje de config."""
        project = tmp_path
        (project / "docs" / "specs").mkdir(parents=True)
        (project / "tests").mkdir(exist_ok=True)
        (project / "src").mkdir(exist_ok=True)
        spec_file = project / "docs" / "specs" / "my-feature.md"
        spec_file.write_text("""---
title: My Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Something works
**Description**: Feature must work as expected
**Verification**: test
""")

        result = runner.invoke(
            cli_main.app,
            ["test", "my-feature", "--path", str(project)],
        )

        assert result.exit_code == 2, (
            f"test sin cdad.toml debe abortar con exit code 2, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        combined_output = result.output + (result.stderr if hasattr(result, "stderr") else "")
        assert "cdad config auto" in combined_output, (
            f"Output debe mencionar 'cdad config auto', got: {combined_output}"
        )
        assert "cdad config set" in combined_output, (
            f"Output debe mencionar 'cdad config set', got: {combined_output}"
        )
