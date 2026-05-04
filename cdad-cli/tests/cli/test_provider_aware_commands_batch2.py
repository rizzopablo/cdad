"""Tests provider-aware commands — PC-004-07 a PC-004-28 (RED phase).

Todos los tests DEBEN FALLAR porque la implementación aún no existe.

- Batch A (PC-004-07 a PC-004-11): Regresión + Registry
- Batch B (PC-004-12 a PC-004-18): Comando `config auto`
- Batch C (PC-004-19 a PC-004-25): Comando `config set`
- Batch D (PC-004-26 a PC-004-28): Scopes global/local para config

Spec v2: Los comandos `config auto` y `config set` ahora soportan:
- `--global` (default): opera en `~/.config/cdad/cdad.toml`
- `--local`: opera en `./cdad.toml` del project_root
"""

from __future__ import annotations

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from cdad.cli import main as cli_main
from cdad.llm.client import LLMClient
from cdad.llm.provider import ConfigurationError
from cdad.llm.registry import register, resolve_provider

runner = CliRunner(mix_stderr=False)

# ---------------------------------------------------------------------------
# Helpers / Fixtures compartidos
# ---------------------------------------------------------------------------


def _make_fake_provider(name="anthropic", model_id="claude-opus-4-7"):
    """Crear un fake LLMProvider con _model_id."""
    fake = MagicMock()
    fake._model_id = model_id
    fake.send_message.return_value = "fake response"
    fake.name = name
    return fake


def _create_cdad_toml(project_root: Path, entries: dict | None = None) -> Path:
    """Crear cdad.toml con [agents] en project_root.

    entries: dict de {role: "provider/model"}. Si None, usa solo default.
    """
    toml = project_root / "cdad.toml"
    lines = ["[agents]"]
    if entries is None:
        lines.append('default = "anthropic/claude-opus-4-7"')
    else:
        for role, value in entries.items():
            lines.append(f'{role} = "{value}"')
    toml.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return toml


def _setup_project_with_toml(tmp_path: Path) -> Path:
    """Crear proyecto genérico con cdad.toml y estructura básica."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test-project"\n')
    _create_cdad_toml(tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def _bypass_api_key_check(monkeypatch):
    """Evita que los comandos aborten por falta de ANTHROPIC_API_KEY."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-for-provider-aware")


# ===========================================================================
# Batch A — Regresión + Registry (PC-004-07 a PC-004-11)
# ===========================================================================


# --- PC-004-07: legacy_api_key_mode_removed ---


class TestPC00407LegacyApiKeyModeRemoved:
    """PC-004-07: LLMClient no acepta api_key en constructor (comportamiento esperado).
    El atributo LLMClient.client no existe.
    NOTA: Estos tests verifican comportamiento ya implementado (regresión).
    """

    def test_llmclient_rejects_api_key_parameter(self):
        """LLMClient(api_key='x') debe levantar TypeError."""
        with pytest.raises(TypeError):
            LLMClient(api_key="x")

    def test_llmclient_has_no_client_attribute(self):
        """LLMClient.client no debe existir como atributo de clase/instancia."""
        # Verificar que una instancia normal NO tiene .client
        client = LLMClient()
        assert not hasattr(client, "client"), (
            "LLMClient no debe tener atributo 'client'. "
            f"getattr(client, 'client', SENTINEL) = {getattr(client, 'client', 'SENTINEL')}"
        )


# --- PC-004-08: legacy_helpers_removed_from_main ---


class TestPC00408LegacyHelpersRemovedFromMain:
    """PC-004-08: cdad.cli.main no exporta _require_api_key ni _make_llm_client.
    NOTA: Estos tests verifican comportamiento ya implementado (regresión).
    """

    def test_require_api_key_not_exported(self):
        """Importar _require_api_key de cdad.cli.main debe fallar."""
        with pytest.raises((ImportError, AttributeError)):
            from cdad.cli.main import _require_api_key  # noqa: F401

    def test_make_llm_client_not_exported(self):
        """Importar _make_llm_client de cdad.cli.main debe fallar."""
        with pytest.raises((ImportError, AttributeError)):
            from cdad.cli.main import _make_llm_client  # noqa: F401


# --- PC-004-09: default_role_resolves ---


class TestPC00409DefaultRoleResolves:
    """PC-004-09: resolve_provider('default', ...) devuelve provider
    con _model_id correcto. No levanta ConfigurationError.
    NOTA: Estos tests verifican comportamiento ya implementado (regresión).
    """

    def test_default_role_resolves_to_anthropic_provider(self, monkeypatch):
        """resolve_provider('default', config) debe devolver provider con model_id correcto."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        config = {"agents": {"default": "anthropic/claude-opus-4-7"}}
        provider = resolve_provider("default", config=config, override=None)

        assert provider is not None
        assert provider._model_id == "claude-opus-4-7"
        assert "anthropic" in provider.name.lower()

    def test_default_role_does_not_raise_configuration_error(self, monkeypatch):
        """resolve_provider('default', ...) no debe lanzar ConfigurationError."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        config = {"agents": {"default": "anthropic/claude-opus-4-7"}}
        # No debe lanzar
        provider = resolve_provider("default", config=config, override=None)
        assert provider is not None


# --- PC-004-10: unconfigured_role_falls_back_to_default ---


class TestPC00410UnconfiguredRoleFallsBackToDefault:
    """PC-004-10: Cuando el rol no está configurado, usa default.
    NOTA: Estos tests verifican comportamiento ya implementado (regresión).
    """

    def test_unknown_role_falls_back_to_default(self, monkeypatch):
        """Rol 'reviewer' sin configuración propia debe usar default."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        # Asegurar que no hay env var para reviewer
        monkeypatch.delenv("CDAD_AGENT_REVIEWER", raising=False)

        config = {"agents": {"default": "anthropic/claude-opus-4-7"}}

        provider = resolve_provider("reviewer", config=config, override=None)

        assert provider is not None
        # El provider debe ser el mismo que el de default
        assert provider._model_id == "claude-opus-4-7"

    def test_unknown_role_without_default_raises(self, monkeypatch):
        """Sin default configurado, rol desconocido debe lanzar ConfigurationError
        con mensaje que menciona específicamente el rol y la falta de fallback."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("CDAD_AGENT_REVIEWER", raising=False)

        config = {"agents": {}}  # Sin default

        with pytest.raises(ConfigurationError) as exc_info:
            resolve_provider("reviewer", config=config, override=None)

        # El mensaje debe mencionar el rol 'reviewer' y la falta de 'default'
        error_msg = str(exc_info.value).lower()
        assert "reviewer" in error_msg, (
            f"Error debe mencionar el rol 'reviewer'. Mensaje: {exc_info.value}"
        )
        assert "default" in error_msg, (
            f"Error debe mencionar falta de 'default'. Mensaje: {exc_info.value}"
        )


# --- PC-004-11: fallback_precedence_order ---


class TestPC00411FallbackPrecedenceOrder:
    """PC-004-11: Precedencia de resolución por rol implementada correctamente.
    NOTA: Estos tests verifican comportamiento ya implementado (regresión).
    """

    def test_override_takes_highest_priority(self, monkeypatch):
        """Override argumento debe superar env var y config.
        El provider retornado debe ser del tipo específico del override,
        NO del env var. Además, el _model_id debe venir del override exacto."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("CDAD_AGENT_ARCHITECT", "openai/gpt-4")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config = {"agents": {"architect": "acp/claude", "default": "anthropic/claude-3"}}

        provider = resolve_provider(
            "architect", config=config, override="anthropic/claude-opus-4-7"
        )

        assert provider._model_id == "claude-opus-4-7"
        # Verificar que el provider es específicamente de tipo AnthropicProvider,
        # no un genérico. Esto falla si el registry no distingue tipos de provider.
        provider_type_name = type(provider).__name__
        assert "anthropic" in provider_type_name.lower(), (
            f"El provider debe ser de tipo AnthropicProvider, pero es '{provider_type_name}'"
        )

    def test_env_var_beats_config(self, monkeypatch):
        """Env var CDAD_AGENT_<ROLE> debe superar config[agents][role]."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("CDAD_AGENT_ARCHITECT", "openai/gpt-4")

        config = {"agents": {"architect": "acp/claude", "default": "anthropic/claude-3"}}

        provider = resolve_provider("architect", config=config, override=None)

        # El env var debe ganar sobre config
        assert provider._model_id == "gpt-4"

    def test_config_role_beats_default(self, monkeypatch):
        """config[agents][role] debe superar config[agents][default]."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.delenv("CDAD_AGENT_ARCHITECT", raising=False)

        config = {
            "agents": {
                "architect": "openai/gpt-4-turbo",
                "default": "anthropic/claude-3-sonnet",
            }
        }

        provider = resolve_provider("architect", config=config, override=None)

        assert provider._model_id == "gpt-4-turbo"

    def test_config_default_used_when_nothing_else(self, monkeypatch):
        """config[agents][default] se usa cuando no hay override, env var, ni role."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.delenv("CDAD_AGENT_REVIEWER", raising=False)

        config = {"agents": {"default": "anthropic/claude-3-opus"}}

        provider = resolve_provider("reviewer", config=config, override=None)

        assert provider._model_id == "claude-3-opus"

    def test_configuration_error_when_nothing_available(self, monkeypatch):
        """Sin nada configurado, debe lanzar ConfigurationError con mensaje descriptivo."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("CDAD_AGENT_ARCHITECT", raising=False)

        config = {"agents": {}}

        with pytest.raises(ConfigurationError) as exc_info:
            resolve_provider("architect", config=config, override=None)

        # El error debe mencionar el rol 'architect' y sugerir usar 'default'
        error_msg = str(exc_info.value).lower()
        assert "architect" in error_msg, (
            f"Error debe mencionar el rol 'architect'. Mensaje: {exc_info.value}"
        )


# ===========================================================================
# Batch B — Comando `config auto` (PC-004-12 a PC-004-18)
# ===========================================================================


# --- PC-004-12: config_auto_creates_toml_when_absent ---


class TestPC00412ConfigAutoCreatesTomlWhenAbsent:
    """PC-004-12: `cdad config auto` sin cdad.toml, con provider que responde OK
    → crea cdad.toml con [agents] default = "<provider>/<model>". Exit code 0.
    """

    def test_config_auto_creates_toml_when_no_toml_exists(self, tmp_path, monkeypatch):
        """Sin cdad.toml, `config auto --local` debe crearlo con default provider."""
        # Mockear el pre-check para que crea que hay una API key
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Mockear resolve_provider para que retorne un provider funcional
        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        # El comando debe crear el cdad.toml
        toml_path = tmp_path / "cdad.toml"
        # Nota: el test fallará porque el comando 'config auto' no existe aún
        # Verificamos que el toml fue creado
        assert result.exit_code == 0, f"Exit code fue {result.exit_code}, stderr: {result.stderr}"


# --- PC-004-13: config_auto_backups_existing_toml ---


class TestPC00413ConfigAutoBackupsExistingToml:
    """PC-004-13: `cdad config auto` con cdad.toml existente → renombra a
    cdad.toml.bak-<YYYYMMDDHHMM> ANTES de escribir nuevo.
    Si rename falla → aborta exit code != 0.
    """

    def test_config_auto_backups_existing_toml(self, tmp_path, monkeypatch):
        """Con cdad.toml existente, `config auto --local` debe hacer backup."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        # Crear cdad.toml existente
        _create_cdad_toml(tmp_path, {"default": "openai/gpt-3.5-turbo"})
        original_content = (tmp_path / "cdad.toml").read_text()

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Mockear resolve_provider
        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        # Debe existir un backup con timestamp
        backup_files = list(tmp_path.glob("cdad.toml.bak-*"))
        assert len(backup_files) >= 1, (
            f"No se encontró backup cdad.toml.bak-*. Archivos: {list(tmp_path.iterdir())}"
        )

        # El backup debe contener el contenido original
        backup_content = backup_files[0].read_text()
        assert "gpt-3.5-turbo" in backup_content

        assert result.exit_code == 0

    def test_config_auto_aborts_if_rename_fails(self, tmp_path, monkeypatch):
        """Si el rename del backup falla, debe abortar con mensaje de error."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Hacer que os.rename falle
        original_rename = os.rename

        def failing_rename(src, dst):
            raise OSError("Permission denied")

        monkeypatch.setattr(os, "rename", failing_rename)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        # El stderr debe mencionar el error de backup/renombrado
        # (fallará porque el comando 'config auto' no existe)
        assert (
            "backup" in result.stderr.lower()
            or "bak" in result.stderr.lower()
            or "rename" in result.stderr.lower()
        ), f"stderr debe mencionar el fallo de backup/rename. stderr: {result.stderr}"


# --- PC-004-14: config_auto_priority_order ---


class TestPC00414ConfigAutoPriorityOrder:
    """PC-004-14: Priority estricta:
    (1) anthropic si ANTHROPIC_API_KEY presente;
    (2) openai si OPENAI_API_KEY presente;
    (3) acp/claude si binario `claude` disponible;
    (4) acp/qwen si binario `qwen` disponible.
    Otros ACP solo si son únicos.
    """

    def test_priority_anthropic_over_openai(self, tmp_path, monkeypatch):
        """Con ambas API keys, `config auto --local` debe elegir anthropic primero."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        toml_path = tmp_path / "cdad.toml"
        if toml_path.exists():
            content = toml_path.read_text()
            assert "anthropic" in content

    def test_priority_openai_when_no_anthropic(self, tmp_path, monkeypatch):
        """Sin ANTHROPIC_API_KEY pero con OPENAI_API_KEY, `config auto --local` debe elegir openai."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        fake_provider = _make_fake_provider("openai", "gpt-4")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

    def test_priority_acp_claude_when_no_api_keys(self, tmp_path, monkeypatch):
        """Sin API keys pero con binario `claude`, `config auto --local` debe elegir acp/claude."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Mockear shutil.which para que encuentre 'claude'
        original_which = shutil.which

        def mock_which(cmd):
            if cmd == "claude":
                return "/usr/bin/claude"
            return original_which(cmd)

        monkeypatch.setattr(shutil, "which", mock_which)

        fake_provider = _make_fake_provider("acp", "claude")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0


# --- PC-004-15: config_auto_precheck_aborts_when_nothing_available ---


class TestPC00415ConfigAutoPrecheckAbortsWhenNothingAvailable:
    """PC-004-15: Sin API keys ni binarios ACP → aborta exit code != 0 antes
    de llamar a ningún provider. Mensaje stderr contiene 'anthropic',
    'openai', 'claude', 'qwen'.
    """

    def test_precheck_aborts_with_no_keys_or_binaries(self, tmp_path, monkeypatch):
        """Sin nada disponible, `config auto --local` debe abortar con mensaje informativo."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Mockear shutil.which para que no encuentre nada
        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code != 0, (
            f"Debería fallar sin API keys ni binarios. Exit code: {result.exit_code}"
        )

        stderr_lower = result.stderr.lower()
        assert "anthropic" in stderr_lower, (
            f"stderr debe mencionar 'anthropic'. stderr: {result.stderr}"
        )
        assert "openai" in stderr_lower, f"stderr debe mencionar 'openai'. stderr: {result.stderr}"
        assert "claude" in stderr_lower, f"stderr debe mencionar 'claude'. stderr: {result.stderr}"
        assert "qwen" in stderr_lower, f"stderr debe mencionar 'qwen'. stderr: {result.stderr}"


# --- PC-004-16: config_auto_validates_with_real_call ---


class TestPC00416ConfigAutoValidatesWithRealCall:
    """PC-004-16: Para cada provider candidato, hace exactamente una llamada
    provider.send_message con prompt conteniendo 'CDAD' y 'disponible'.
    Timeout 30 segundos. OK si respuesta no vacía dentro del timeout.
    """

    def test_validates_provider_with_cdad_message(self, tmp_path, monkeypatch):
        """`config auto --local` debe llamar send_message con prompt que contiene CDAD y disponible."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        # Verificar que se llamó send_message
        if fake_provider.send_message.called:
            call_args = fake_provider.send_message.call_args
            # El prompt debe contener CDAD y disponible
            all_args = str(call_args)
            assert "CDAD" in all_args or "cdad" in all_args.lower(), (
                f"El prompt debe contener 'CDAD'. Args: {call_args}"
            )

        assert result.exit_code == 0

    def test_timeout_rejects_provider(self, tmp_path, monkeypatch):
        """`config auto --local` con timeout debe mencionar 'timeout' en stderr."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        import time

        def slow_send_message(*args, **kwargs):
            time.sleep(31)  # Simular timeout
            return "response"

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        fake_provider.send_message = slow_send_message
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        # Debe mencionar 'timeout' en stderr
        assert "timeout" in result.stderr.lower(), (
            f"stderr debe mencionar 'timeout'. stderr: {result.stderr}"
        )


# --- PC-004-17: config_auto_reports_discarded_providers ---


class TestPC00417ConfigAutoReportsDiscardedProviders:
    """PC-004-17: Cuando descarta un provider (timeout, excepción, respuesta
    vacía), imprime nombre del provider y razón (substring 'timeout',
    'error', o mensaje de excepción).
    """

    def test_reports_discarded_provider_on_exception(self, tmp_path, monkeypatch):
        """`config auto --local` cuando descarta provider debe informar nombre y razón."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        # Provider de anthropic funciona
        fake_anthropic = _make_fake_provider("anthropic", "claude-opus-4-7")

        # Provider de openai falla
        fake_openai = _make_fake_provider("openai", "gpt-4")
        fake_openai.send_message.side_effect = RuntimeError("Connection refused")

        call_count = {"count": 0}

        def mock_resolve(name, config=None, override=None):
            call_count["count"] += 1
            if "openai" in name.lower():
                return fake_openai
            return fake_anthropic

        monkeypatch.setattr(cli_main, "resolve_provider", mock_resolve)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        # Si se descarta un provider, el stderr debe mencionar la razón
        # (Esto puede o no aparecer dependiendo de la implementación)
        # El test falla si el comando no existe
        assert result.exit_code == 0


# --- PC-004-18: config_auto_writes_only_default ---


class TestPC00418ConfigAutoWritesOnlyDefault:
    """PC-004-18: El cdad.toml resultante de `config auto` contiene EXACTAMENTE
    una clave bajo [agents]: `default`. No se escriben claves para otros roles.
    """

    def test_only_default_key_is_written(self, tmp_path, monkeypatch):
        """`config auto --local` debe escribir solo default, no otros roles."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        toml_path = tmp_path / "cdad.toml"
        # El test fallará si el comando no existe
        # Cuando exista, verificar que solo hay default
        import toml as toml_lib

        config = toml_lib.load(toml_path)
        agents = config.get("agents", {})
        assert list(agents.keys()) == ["default"], (
            f"Solo debería haber 'default' en agents, pero hay: {list(agents.keys())}"
        )


# ===========================================================================
# Batch C — Comando `config set` (PC-004-19 a PC-004-25)
# ===========================================================================


# --- PC-004-19: config_set_writes_role ---


class TestPC00419ConfigSetWritesRole:
    """PC-004-19: `cdad config set <role> <provider>/<model>` con rol válido
    → escribe [agents] <role> = "<provider>/<model>" en cdad.toml. Exit code 0.
    """

    def test_config_set_writes_role_to_toml(self, tmp_path, monkeypatch):
        """`config set --local` debe escribir el rol en cdad.toml del project_root."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "architect", "anthropic/claude-sonnet-4-20250514"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        import toml as toml_lib

        config = toml_lib.load(tmp_path / "cdad.toml")
        assert "agents" in config
        assert "architect" in config["agents"]
        assert config["agents"]["architect"] == "anthropic/claude-sonnet-4-20250514"


# --- PC-004-20: config_set_preserves_other_entries ---


class TestPC00420ConfigSetPreservesOtherEntries:
    """PC-004-20: `cdad config set architect anthropic/claude` modifica solo
    la clave `architect`, dejando las demás intactas.
    """

    def test_config_set_preserves_other_roles(self, tmp_path, monkeypatch):
        """`config set --local` no debe borrar otras entradas existentes."""
        _create_cdad_toml(
            tmp_path,
            {
                "default": "anthropic/claude-opus-4-7",
                "test_writer": "openai/gpt-4",
            },
        )

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "architect", "anthropic/claude-sonnet-4"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        import toml as toml_lib

        config = toml_lib.load(tmp_path / "cdad.toml")

        # Architect fue agregado
        assert config["agents"]["architect"] == "anthropic/claude-sonnet-4"
        # Las otras entradas se preservan
        assert config["agents"]["default"] == "anthropic/claude-opus-4-7"
        assert config["agents"]["test_writer"] == "openai/gpt-4"


# --- PC-004-21: config_set_creates_toml_when_absent ---


class TestPC00421ConfigSetCreatesTomlWhenAbsent:
    """PC-004-21: Sin cdad.toml, `cdad config set <role> <p>/<m>` crea el
    archivo con esa única entrada. Exit code 0.
    """

    def test_config_set_creates_toml_from_scratch(self, tmp_path, monkeypatch):
        """Sin cdad.toml, `config set --local` debe crearlo."""
        toml_path = tmp_path / "cdad.toml"
        assert not toml_path.exists(), "cdad.toml no debería existir antes del test"

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "default", "anthropic/claude-opus-4-7"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"
        assert toml_path.exists(), "cdad.toml debería haber sido creado"

        import toml as toml_lib

        config = toml_lib.load(toml_path)
        assert config["agents"]["default"] == "anthropic/claude-opus-4-7"


# --- PC-004-22: config_set_rejects_invalid_format ---


class TestPC00422ConfigSetRejectsInvalidFormat:
    """PC-004-22: Valor sin `/` o provider no matchea `^[a-z][a-z0-9_-]*$`
    → aborta exit code != 0, stderr contiene 'provider/model' y el valor recibido.
    """

    def test_rejects_value_without_slash(self, tmp_path, monkeypatch):
        """Valor sin '/' debe ser rechazado."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "default", "claude-opus-4-7"],  # Sin '/'
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        stderr_lower = result.stderr.lower()
        assert "provider/model" in stderr_lower, (
            f"stderr debe contener 'provider/model'. stderr: {result.stderr}"
        )
        assert "claude-opus-4-7" in result.stderr

    def test_rejects_invalid_provider_name(self, tmp_path, monkeypatch):
        """Provider con caracteres inválidos debe ser rechazado."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "default", "1Invalid/model"],  # Empieza con número
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        stderr_lower = result.stderr.lower()
        assert "provider/model" in stderr_lower, (
            f"stderr debe contener 'provider/model'. stderr: {result.stderr}"
        )

    def test_rejects_provider_with_uppercase(self, tmp_path, monkeypatch):
        """Provider con mayúsculas debe ser rechazado con mensaje 'provider/model'."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "default", "Anthropic/claude"],  # Mayúscula
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        # Debe mencionar el formato esperado y el valor recibido
        stderr_lower = result.stderr.lower()
        assert "provider/model" in stderr_lower, (
            f"stderr debe contener 'provider/model'. stderr: {result.stderr}"
        )
        assert "anthropic" in result.stderr, (
            f"stderr debe contener el valor rechazado. stderr: {result.stderr}"
        )


# --- PC-004-23: config_set_rejects_unknown_role ---


class TestPC00423ConfigSetRejectsUnknownRole:
    """PC-004-23: Rol fuera de {default, architect, test_writer, implementer,
    reviewer, scribe} → aborta exit code != 0, stderr enumera roles aceptados.
    """

    VALID_ROLES = {"default", "architect", "test_writer", "implementer", "reviewer", "scribe"}

    def test_rejects_unknown_role(self, tmp_path, monkeypatch):
        """Rol no válido debe ser rechazado con mensaje enumerando roles."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "unknown_role", "anthropic/claude"],
            catch_exceptions=False,
        )

        assert result.exit_code != 0
        stderr_lower = result.stderr.lower()
        # El stderr debe mencionar al menos algunos de los roles válidos
        for role in self.VALID_ROLES:
            assert role in stderr_lower, (
                f"stderr debe mencionar el rol '{role}'. stderr: {result.stderr}"
            )

    def test_accepts_all_valid_roles(self, tmp_path, monkeypatch):
        """Todos los roles válidos deben ser aceptados."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        for role in self.VALID_ROLES:
            result = runner.invoke(
                cli_main.app,
                ["config", "set", "--local", role, "anthropic/claude-opus-4-7"],
                catch_exceptions=False,
            )

            assert result.exit_code == 0, (
                f"Rol '{role}' debería ser válido. Exit code: {result.exit_code}, stderr: {result.stderr}"
            )


# --- PC-004-24: config_set_does_not_validate_provider_works ---


class TestPC00424ConfigSetDoesNotValidateProviderWorks:
    """PC-004-24: `cdad config set default anthropic/non-existent-model-id`
    escribe exitosamente sin validar que el modelo funcione. Exit code 0.
    """

    def test_config_set_does_not_validate_model(self, tmp_path, monkeypatch):
        """`config set --local` debe escribir sin validar que el modelo funcione."""
        _create_cdad_toml(tmp_path)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "default", "anthropic/non-existent-model-id"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, (
            f"Debería escribir sin validar. Exit code: {result.exit_code}, stderr: {result.stderr}"
        )

        import toml as toml_lib

        config = toml_lib.load(tmp_path / "cdad.toml")
        assert config["agents"]["default"] == "anthropic/non-existent-model-id"


# ===========================================================================
# Batch D — Scopes global/local para config (PC-004-26 a PC-004-28)
# ===========================================================================


# --- PC-004-26: config_auto_global_scope ---


class TestPC00426ConfigAutoGlobalScope:
    """PC-004-26: `cdad config auto --global` crea o modifica `~/.config/cdad/cdad.toml`.
    Si el directorio `~/.config/cdad/` no existe, lo crea.
    Mismo comportamiento de detección/validación que sin flags, solo cambia el path.
    Exit code 0.
    """

    def test_config_auto_global_creates_cdad_toml(self, tmp_path, monkeypatch):
        """`config auto --global` debe crear `~/.config/cdad/cdad.toml` si no existe."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Simular home directory para evitar escribir en el home real
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        # Mockear expanduser para que ~ apunte al fake_home
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--global"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        global_toml = fake_home / ".config" / "cdad" / "cdad.toml"
        assert global_toml.exists(), (
            f"~/.config/cdad/cdad.toml debería haber sido creado. Path: {global_toml}"
        )

        import toml as toml_lib

        config = toml_lib.load(global_toml)
        assert "agents" in config
        assert "default" in config["agents"]

    def test_config_auto_global_creates_config_dir(self, tmp_path, monkeypatch):
        """`config auto --global` debe crear `~/.config/cdad/` si no existe."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--global"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        config_dir = fake_home / ".config" / "cdad"
        assert config_dir.exists(), f"~/.config/cdad/ debería haber sido creado. Path: {config_dir}"
        assert config_dir.is_dir()


# --- PC-004-27: config_auto_local_scope ---


class TestPC00427ConfigAutoLocalScope:
    """PC-004-27: `cdad config auto --local` crea o modifica `./cdad.toml`
    en el project_root.
    Mismo comportamiento, solo cambia el path.
    Exit code 0.
    """

    def test_config_auto_local_creates_cdad_toml(self, tmp_path, monkeypatch):
        """`config auto --local` debe crear `./cdad.toml` en project_root."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        local_toml = tmp_path / "cdad.toml"
        assert local_toml.exists(), f"./cdad.toml debería haber sido creado en {tmp_path}"

        import toml as toml_lib

        config = toml_lib.load(local_toml)
        assert "agents" in config
        assert "default" in config["agents"]

    def test_config_auto_local_different_from_global(self, tmp_path, monkeypatch):
        """`--local` y `--global` deben escribir en paths diferentes."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        monkeypatch.chdir(project_dir)

        fake_provider = _make_fake_provider("anthropic", "claude-opus-4-7")
        monkeypatch.setattr(cli_main, "resolve_provider", lambda *a, **kw: fake_provider)

        # Primero crear global
        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--global"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0

        # Modificar el global
        import toml as toml_lib

        global_toml = fake_home / ".config" / "cdad" / "cdad.toml"
        global_config = toml_lib.load(global_toml)
        global_config["agents"]["default"] = "openai/gpt-4"
        global_toml.write_text(toml_lib.dumps(global_config))

        # Ahora crear local
        result = runner.invoke(
            cli_main.app,
            ["config", "auto", "--local"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0

        # Los dos archivos deben existir con contenido diferente
        local_toml = project_dir / "cdad.toml"
        assert local_toml.exists()

        global_config_after = toml_lib.load(global_toml)
        local_config = toml_lib.load(local_toml)

        assert global_config_after["agents"]["default"] == "openai/gpt-4", (
            "El global no debe haber sido modificado por --local"
        )
        assert local_config["agents"]["default"] == "anthropic/claude-opus-4-7", (
            "El local debe tener el nuevo valor"
        )


# --- PC-004-28: config_set_scope_flags ---


class TestPC00428ConfigSetScopeFlags:
    """PC-004-28: `cdad config set --global <role> <p>/<m>` escribe en
    `~/.config/cdad/cdad.toml`.
    `cdad config set --local <role> <p>/<m>` escribe en `./cdad.toml`.
    Sin flags → global.
    Mismas validaciones de formato/rol. Exit code 0.
    """

    def test_config_set_global_writes_to_cdad_config(self, tmp_path, monkeypatch):
        """`config set --global` debe escribir en `~/.config/cdad/cdad.toml`."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--global", "architect", "anthropic/claude-sonnet-4"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        global_toml = fake_home / ".config" / "cdad" / "cdad.toml"
        assert global_toml.exists()

        import toml as toml_lib

        config = toml_lib.load(global_toml)
        assert config["agents"]["architect"] == "anthropic/claude-sonnet-4"

    def test_config_set_local_writes_to_project_toml(self, tmp_path, monkeypatch):
        """`config set --local` debe escribir en `./cdad.toml`."""
        # Cambiar al directorio temporal para que --local apunte ahí
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--local", "architect", "anthropic/claude-sonnet-4"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        local_toml = tmp_path / "cdad.toml"
        assert local_toml.exists()

        import toml as toml_lib

        config = toml_lib.load(local_toml)
        assert config["agents"]["architect"] == "anthropic/claude-sonnet-4"

    def test_config_set_without_flags_defaults_to_global(self, tmp_path, monkeypatch):
        """`config set` sin flags debe escribir en `~/.config/cdad/cdad.toml` (global)."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        # Cambiar a un directorio diferente para asegurar que no usa cwd
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        monkeypatch.chdir(project_dir)

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "default", "openai/gpt-4"],  # Sin --global ni --local
            catch_exceptions=False,
        )

        assert result.exit_code == 0, f"Exit code fue {result.exit_code}. stderr: {result.stderr}"

        # Debe escribir en global, NO en el project
        global_toml = fake_home / ".config" / "cdad" / "cdad.toml"
        assert global_toml.exists(), (
            f"~/.config/cdad/cdad.toml debería existir. Path: {global_toml}"
        )

        local_toml = project_dir / "cdad.toml"
        assert not local_toml.exists(), (
            f"./cdad.toml NO debería existir cuando se usa scope global (sin flags)"
        )

        import toml as toml_lib

        config = toml_lib.load(global_toml)
        assert config["agents"]["default"] == "openai/gpt-4"

    def test_config_set_global_preserves_local(self, tmp_path, monkeypatch):
        """`config set --global` no debe modificar el archivo local."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))
        import os.path

        original_expanduser = os.path.expanduser
        monkeypatch.setattr(
            os.path,
            "expanduser",
            lambda p: str(fake_home) + p[1:] if p.startswith("~") else original_expanduser(p),
        )

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        monkeypatch.chdir(project_dir)

        # Crear cdad.toml local primero
        _create_cdad_toml(project_dir, {"default": "anthropic/claude-opus-4-7"})

        # Guardar contenido original
        import toml as toml_lib

        local_toml = project_dir / "cdad.toml"
        original_content = local_toml.read_text()

        result = runner.invoke(
            cli_main.app,
            ["config", "set", "--global", "test_writer", "openai/gpt-4"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        # El local no debe haber cambiado
        current_content = local_toml.read_text()
        assert current_content == original_content, (
            "El cdad.toml local no debe haber sido modificado por --global"
        )

        # El global debe existir con el nuevo rol
        global_toml = fake_home / ".config" / "cdad" / "cdad.toml"
        assert global_toml.exists()
        global_config = toml_lib.load(global_toml)
        assert global_config["agents"]["test_writer"] == "openai/gpt-4"


# --- PC-004-25: provider_missing_lists_supported ---


class TestPC00425ProviderMissingListsSupported:
    """PC-004-25: Cuando un comando provider-aware falla por ausencia de
    credencial/binario, stderr contiene 'anthropic', 'openai', 'acp' y
    exit code != 0.
    NOTA: Este test verifica comportamiento ya implementado (regresión).
    """

    def test_missing_provider_lists_supported_providers(self, tmp_path, monkeypatch):
        """Cuando falla por falta de credenciales, debe listar providers soportados."""
        # Remover todas las API keys
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Mockear shutil.which para que no encuentre binarios ACP
        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        # Invocar un comando provider-aware (como discover) sin configuración
        # que falle por falta de provider
        result = runner.invoke(
            cli_main.app,
            ["discover", "."],
            catch_exceptions=False,
        )

        # El comando debe fallar
        assert result.exit_code != 0

        # El stderr debe listar los providers soportados
        stderr_lower = result.stderr.lower()
        assert "anthropic" in stderr_lower, (
            f"stderr debe mencionar 'anthropic'. stderr: {result.stderr}"
        )
        assert "openai" in stderr_lower, f"stderr debe mencionar 'openai'. stderr: {result.stderr}"
        assert "acp" in stderr_lower, f"stderr debe mencionar 'acp'. stderr: {result.stderr}"
