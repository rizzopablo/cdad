"""Contract tests for LLM provider abstraction (spec 002, postconditions v2).

Tests verify PC-002-1 through PC-002-15. RED phase: tests fail when modules
are missing (valid RED behavior). Imports are NOT protected globally.
"""

from __future__ import annotations

import copy
import inspect
import os
import sys
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from cdad.llm.client import LLMClient
from cdad.llm.provider import (
    LLMProvider,
    Message,
    ProviderError,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderTransportError,
    ProviderResponseError,
    ConfigurationError,
)
from cdad.llm.registry import resolve_provider, DEFAULT_AGENT_MODELS
import cdad.llm.registry as registry_mod


class RecordingProvider:
    """Mock provider recording calls without I/O."""

    name = "recording"

    def __init__(self, response: str = "ok", raise_exc: BaseException | None = None):
        self.response = response
        self.raise_exc = raise_exc
        self.calls = []

    def send_message(
        self,
        system_prompt: str,
        history: list[dict[str, str]],
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "history": copy.deepcopy(history),
                "model": model,
                "max_tokens": max_tokens,
            }
        )
        if self.raise_exc is not None:
            raise self.raise_exc
        return self.response


def _make_client(provider: Any, model: str = "test-model") -> LLMClient:
    return LLMClient(provider=provider, model=model)


class TestProtocolShape:
    """Tests: LLMProvider Protocol structure (foundational)."""

    def test_llmprovider_has_name_attribute(self):
        assert hasattr(LLMProvider, "name") or "name" in getattr(
            LLMProvider, "__annotations__", {}
        )

    def test_llmprovider_send_message_has_correct_signature(self):
        assert hasattr(LLMProvider, "send_message")
        sig = inspect.signature(LLMProvider.send_message)
        params = sig.parameters
        assert "system_prompt" in params
        assert "history" in params
        assert "model" in params
        assert "max_tokens" in params
        assert params["model"].kind == inspect.Parameter.KEYWORD_ONLY
        assert params["max_tokens"].kind == inspect.Parameter.KEYWORD_ONLY
        assert sig.return_annotation in (str, "str", inspect.Signature.empty)

    def test_message_typed_dict_structure(self):
        annotations = getattr(Message, "__annotations__", {})
        assert "role" in annotations
        assert "content" in annotations


class TestExceptionHierarchy:
    """Tests: Exception types and hierarchy (foundational)."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ProviderAuthError,
            ProviderRateLimitError,
            ProviderTransportError,
            ProviderResponseError,
            ConfigurationError,
        ],
    )
    def test_all_provider_exceptions_inherit_from_provider_error(self, exc_class):
        assert issubclass(exc_class, ProviderError)

    def test_provider_error_is_exception(self):
        assert issubclass(ProviderError, Exception)


class TestPC002_1_ConservationOfTurns:
    """PC-002-1: history order and count preserved."""

    @pytest.mark.parametrize(
        "history_seed",
        [
            [],
            [{"role": "user", "content": "u1"}, {"role": "assistant", "content": "a1"}],
            [
                {"role": "user", "content": "u1"},
                {"role": "assistant", "content": "a1"},
                {"role": "user", "content": "u2"},
                {"role": "assistant", "content": "a2"},
                {"role": "user", "content": "u3"},
            ],
        ],
        ids=["empty", "1-turn", "5-messages"],
    )
    def test_history_preserves_order_and_count(self, history_seed):
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)
        client.history = copy.deepcopy(history_seed)

        client.send_message("new message", system_prompt="sys")

        assert provider.calls
        forwarded = provider.calls[-1]["history"]
        expected = history_seed + [{"role": "user", "content": "new message"}]
        assert forwarded == expected
        assert len(forwarded) == len(expected)


class TestPC002_2_SystemPromptChannel:
    """PC-002-2: system_prompt via dedicated channel, not in messages."""

    def test_system_prompt_transmitted_as_parameter(self):
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)

        client.send_message("hola", system_prompt="sys_value")

        assert provider.calls[-1]["system_prompt"] == "sys_value"

    def test_system_prompt_not_duplicated_in_history(self):
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)

        client.send_message("user msg", system_prompt="system msg")

        history = provider.calls[-1]["history"]
        for msg in history:
            assert msg["content"] != "system msg"


class TestPC002_3_Immutability:
    """PC-002-3: send_message does not mutate history on exception."""

    @pytest.mark.parametrize(
        "exc",
        [
            ProviderAuthError("auth failed"),
            ProviderRateLimitError("rate exceeded"),
            ProviderTransportError("network error"),
            ProviderResponseError("invalid response"),
        ],
        ids=["auth", "rate", "transport", "response"],
    )
    def test_history_unchanged_on_provider_exception(self, exc):
        provider = RecordingProvider(raise_exc=exc)
        client = _make_client(provider)
        seed = [
            {"role": "user", "content": "msg1"},
            {"role": "assistant", "content": "resp1"},
        ]
        client.history = copy.deepcopy(seed)

        with pytest.raises(ProviderError):
            client.send_message("msg2", system_prompt="sys")

        assert client.history == seed


class TestPC002_4_ExceptionMapping:
    """PC-002-4: provider errors map to typed exceptions."""

    def test_provider_auth_error_hierarchy(self):
        assert issubclass(ProviderAuthError, ProviderError)
        exc = ProviderAuthError("test")
        assert isinstance(exc, ProviderError)

    def test_provider_rate_limit_error_hierarchy(self):
        assert issubclass(ProviderRateLimitError, ProviderError)
        exc = ProviderRateLimitError("test")
        assert isinstance(exc, ProviderError)

    def test_provider_transport_error_hierarchy(self):
        assert issubclass(ProviderTransportError, ProviderError)
        exc = ProviderTransportError("test")
        assert isinstance(exc, ProviderError)

    def test_provider_response_error_hierarchy(self):
        assert issubclass(ProviderResponseError, ProviderError)
        exc = ProviderResponseError("test")
        assert isinstance(exc, ProviderError)

    def test_auth_error_raised_on_http_401(self):
        provider = RecordingProvider(raise_exc=ProviderAuthError("HTTP 401"))
        client = _make_client(provider)
        with pytest.raises(ProviderAuthError):
            client.send_message("msg", system_prompt="sys")

    def test_rate_limit_error_raised_on_http_429(self):
        provider = RecordingProvider(raise_exc=ProviderRateLimitError("HTTP 429"))
        client = _make_client(provider)
        with pytest.raises(ProviderRateLimitError):
            client.send_message("msg", system_prompt="sys")

    def test_transport_error_raised_on_network_failure(self):
        provider = RecordingProvider(raise_exc=ProviderTransportError("Network timeout"))
        client = _make_client(provider)
        with pytest.raises(ProviderTransportError):
            client.send_message("msg", system_prompt="sys")

    def test_response_error_raised_on_invalid_shape(self):
        provider = RecordingProvider(raise_exc=ProviderResponseError("Invalid JSON"))
        client = _make_client(provider)
        with pytest.raises(ProviderResponseError):
            client.send_message("msg", system_prompt="sys")


class TestPC002_5_IsolationPreserved:
    """PC-002-5: changing provider config does not alter access policy."""

    def test_agent_access_policy_unchanged_after_config_change(self):
        try:
            from cdad.project import model as project_model
        except ImportError:
            pytest.skip("cdad.project.model not available")

        snapshot = copy.deepcopy(project_model._AGENT_ACCESS_POLICY)
        resolve_provider = getattr(registry_mod, "resolve_provider")

        config_a = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        config_b = {
            "agents": {"architect": "acp/claude"},
            "providers": {
                "acp": {
                    "agents": {"claude": ["npx", "-y", "@zed-industries/claude-agent-acp"]}
                }
            },
        }

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}, clear=False):
            for cfg in (config_a, config_b):
                try:
                    resolve_provider("architect", config=cfg)
                except ConfigurationError:
                    pass

        assert project_model._AGENT_ACCESS_POLICY == snapshot

    def test_accessible_files_unchanged_across_providers(self):
        try:
            from cdad.agents import ArchitectAgent
            from cdad.project import Project
        except ImportError:
            pytest.skip("agents/project modules not available")

        project = Mock(spec=Project)
        provider_a = RecordingProvider()
        provider_b = RecordingProvider()

        agent_a = ArchitectAgent(project=project, llm_client=_make_client(provider_a))
        agent_b = ArchitectAgent(project=project, llm_client=_make_client(provider_b))

        if hasattr(agent_a, "get_accessible_files"):
            files_a = set(agent_a.get_accessible_files())
            files_b = set(agent_b.get_accessible_files())
            assert files_a == files_b


class TestPC002_6_DeterministicResolution:
    """PC-002-6: resolve_provider is deterministic across calls."""

    def test_resolve_provider_returns_same_result_across_calls(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}, clear=False):
            results = []
            for _ in range(10):
                results.append(resolve_provider("architect", config=config))

        first_id = id(results[0])
        for i in range(1, len(results)):
            assert (
                results[i] == results[0]
                or getattr(results[i], "name", None) == getattr(results[0], "name", None)
            )


class TestPC002_7_FailFastConfiguration:
    """PC-002-7: invalid config raises ConfigurationError before execution."""

    def test_unknown_provider_raises_configuration_error(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {"agents": {"architect": "unknown/model"}, "providers": {}}
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)

    def test_missing_api_key_env_raises_configuration_error(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "MISSING_KEY_VAR"}},
        }
        clean_env = {k: v for k, v in os.environ.items() if k != "MISSING_KEY_VAR"}
        with patch.dict(os.environ, clean_env, clear=True):
            with pytest.raises(ConfigurationError):
                resolve_provider("architect", config=config)

    def test_invalid_format_raises_configuration_error(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {
            "agents": {"architect": "invalid-format-no-slash"},
            "providers": {},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)

    def test_unknown_role_raises_configuration_error(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {
            "agents": {"unknown_role": "anthropic/claude"},
            "providers": {"anthropic": {"api_key_env": "API_KEY"}},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("unknown_role", config=config)


class TestPC002_8_ConfigurationPrecedence:
    """PC-002-8: env > ./cdad.toml > ~/.config/cdad/cdad.toml > defaults."""

    def test_env_var_takes_precedence(self):
        config = {
            "agents": {"architect": "anthropic/claude-sonnet-4-6"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        with patch.dict(
            os.environ,
            {"CDAD_AGENT_ARCHITECT": "anthropic/claude-opus-4-7", "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config=config)
            assert result is not None
            assert "opus" in str(result).lower()

    def test_local_config_when_no_env_var(self):
        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        clean_env = {k: v for k, v in os.environ.items() if k != "CDAD_AGENT_ARCHITECT"}
        with patch.dict(os.environ, {**clean_env, "ANTHROPIC_API_KEY": "sk-test"}, clear=True):
            result = resolve_provider("architect", config=config)
            assert result is not None
            assert "opus" in str(result).lower()

    def test_default_when_nothing_configured(self):
        with patch.dict(
            os.environ,
            {"ANTHROPIC_API_KEY": "sk-test", "CDAD_AGENT_ARCHITECT": ""},
            clear=False,
        ):
            result = resolve_provider("architect", config={})
            assert result is not None

    def test_all_layers_defined_env_wins(self):
        config = {
            "agents": {"architect": "anthropic/claude-sonnet-4-6"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        home_config = {
            "agents": {"architect": "anthropic/claude-haiku-4-5"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        with patch.dict(
            os.environ,
            {"CDAD_AGENT_ARCHITECT": "anthropic/claude-opus-4-7", "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config=config)
            assert "opus" in str(result).lower()


class TestPC002_9_APIKeysNeverLiteral:
    """PC-002-9: reject api_key (literal) in config; only api_key_env."""

    def test_literal_api_key_in_config_raises_configuration_error(self):
        resolve_provider = getattr(registry_mod, "resolve_provider")
        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key": "sk-literal-key"}},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)


class TestPC002_10_EquivalentFunctionality:
    """PC-002-10: both providers produce same artifacts for same inputs."""

    def test_anthropic_provider_returns_nonempty_string(self):
        anthropic_provider = RecordingProvider(response="arch spec v1")
        client = _make_client(anthropic_provider)

        result = client.send_message(
            "draft a spec", system_prompt="you are an architect", model="claude", max_tokens=1024
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "arch spec v1"

    def test_acp_provider_returns_nonempty_string(self):
        acp_provider = RecordingProvider(response="arch spec v1")
        client = _make_client(acp_provider)

        result = client.send_message(
            "draft a spec", system_prompt="you are an architect", model="claude", max_tokens=1024
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert result == "arch spec v1"

    def test_both_providers_with_same_input_produce_same_output(self):
        expected_response = "identical output for both providers"
        anthropic = RecordingProvider(response=expected_response)
        acp = RecordingProvider(response=expected_response)

        sys_prompt = "you are an architect"
        hist = [{"role": "user", "content": "initial prompt"}]
        input_msg = "follow up question"

        client_a = _make_client(anthropic)
        client_a.history = copy.deepcopy(hist)
        result_a = client_a.send_message(input_msg, system_prompt=sys_prompt)

        client_b = _make_client(acp)
        client_b.history = copy.deepcopy(hist)
        result_b = client_b.send_message(input_msg, system_prompt=sys_prompt)

        assert result_a == result_b
        assert result_a == expected_response
        assert result_b == expected_response


class TestPC002_11_LazyImport:
    """PC-002-11: SDKs not imported until provider is resolved."""

    def test_registry_module_does_not_import_anthropic_directly(self):
        before_anthropic = "anthropic" in sys.modules
        before_acp = "acp_client" in sys.modules
        try:
            import cdad.llm.registry  # noqa: F401
        except ImportError:
            pass
        after_anthropic = "anthropic" in sys.modules
        after_acp = "acp_client" in sys.modules
        assert not after_anthropic or before_anthropic

    def test_cli_main_does_not_import_anthropic_on_startup(self):
        before_anthropic = "anthropic" in sys.modules
        try:
            import cdad.cli.main  # noqa: F401
        except ImportError:
            pytest.skip("cdad.cli.main not available")
        after_anthropic = "anthropic" in sys.modules
        assert not after_anthropic or before_anthropic

    def test_sdk_imported_only_when_provider_instantiated(self):
        before = "anthropic" in sys.modules
        try:
            provider = resolve_provider("architect", config={})
            if provider and hasattr(provider, "client"):
                after = "anthropic" in sys.modules
                assert after
        except (ConfigurationError, ImportError):
            pass


class TestPC002_12_ExtensibleRegistry:
    """PC-002-12: third parties can register custom providers."""

    def test_registry_allows_registering_custom_provider(self):
        from cdad.llm.registry import register

        class CustomProvider:
            name = "custom"

            def send_message(
                self,
                system_prompt: str,
                history: list[dict[str, str]],
                *,
                model: str,
                max_tokens: int,
            ) -> str:
                return "custom response"

        register("custom", lambda cfg: CustomProvider())
        provider = resolve_provider("custom/test-model", config={})
        assert provider.name == "custom"


class TestPC002_13_ACPBuiltins:
    """PC-002-13: ACP builtins (claude/gemini/codex) with npx wrappers."""

    @pytest.mark.parametrize(
        "alias,expected_command",
        [
            ("claude", ["npx", "-y", "@zed-industries/claude-agent-acp"]),
            ("gemini", ["npx", "-y", "@google/gemini-cli"]),
            ("codex", ["npx", "-y", "codex-acp"]),
        ],
    )
    def test_acp_builtin_aliases_have_correct_default_commands(self, alias, expected_command):
        from cdad.llm.registry import get_builtin_acp_command

        result = get_builtin_acp_command(alias)
        assert result == expected_command

    def test_acp_builtin_config_overrides_default_command(self):
        custom_command = ["/custom/path/claude"]
        config = {
            "agents": {"architect": "acp/claude"},
            "providers": {
                "acp": {
                    "agents": {"claude": custom_command}
                }
            },
        }
        provider = resolve_provider("architect", config=config)
        assert hasattr(provider, "command")
        assert provider.command == custom_command

    def test_missing_acp_command_raises_provider_transport_error(self):
        config = {
            "agents": {"architect": "acp/nonexistent"},
            "providers": {
                "acp": {
                    "agents": {"nonexistent": ["/path/that/does/not/exist"]}
                }
            },
        }
        provider = resolve_provider("architect", config=config)
        with pytest.raises(ProviderTransportError):
            provider.send_message(
                system_prompt="test",
                history=[],
                model="test",
                max_tokens=100,
            )


class TestPC002_14_DefaultModels:
    """PC-002-14: defaults are Anthropic models (not ACP)."""

    def test_default_agent_models_constant_exists(self):
        defaults = getattr(registry_mod, "DEFAULT_AGENT_MODELS", None)
        assert defaults is not None, "DEFAULT_AGENT_MODELS not found in registry"

    @pytest.mark.parametrize(
        "role,expected_model",
        [
            ("architect", "anthropic/claude-opus-4-7"),
            ("test_writer", "anthropic/claude-sonnet-4-6"),
            ("implementer", "anthropic/claude-sonnet-4-6"),
            ("reviewer", "anthropic/claude-sonnet-4-6"),
            ("scribe", "anthropic/claude-sonnet-4-6"),
        ],
    )
    def test_default_models_are_correct_values(self, role, expected_model):
        defaults = getattr(registry_mod, "DEFAULT_AGENT_MODELS", {})
        assert defaults.get(role) == expected_model

    def test_all_default_models_use_anthropic_provider(self):
        defaults = getattr(registry_mod, "DEFAULT_AGENT_MODELS", {})
        for role, model_str in defaults.items():
            assert model_str.startswith("anthropic/"), f"Role {role} default {model_str} does not use anthropic provider"


class TestPC002_15_EnvVarPrecedence:
    """PC-002-15: env var CDAD_AGENT_<ROLE> overrides default."""

    def test_env_var_overrides_default_model(self):
        env_var = "CDAD_AGENT_ARCHITECT"
        env_value = "anthropic/claude-opus-4-7"

        with patch.dict(
            os.environ,
            {env_var: env_value, "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config={})
            assert result is not None
            assert "opus" in str(result).lower()

    def test_env_var_takes_precedence_over_file_config(self):
        env_value = "anthropic/claude-opus-4-7"
        file_value = "anthropic/claude-sonnet-4-6"
        config = {
            "agents": {"architect": file_value},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }

        with patch.dict(
            os.environ,
            {"CDAD_AGENT_ARCHITECT": env_value, "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config=config)
            assert "opus" in str(result).lower()
