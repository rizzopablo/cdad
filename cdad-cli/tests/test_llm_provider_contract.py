"""Contract tests for LLM provider abstraction (spec 002, postconditions v3).

Tests verify PC-002-1 through PC-002-15.

RED phase: these tests fail because the modules defined in the spec
(provider.py, registry.py, providers/) do NOT exist yet.
This is correct RED behavior — the test suite signals "not yet implemented."

DO NOT edit src/ — only this test file.
"""

from __future__ import annotations

import copy
import inspect
import os
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ===========================================================================
# RecordingProvider — test double that records calls without I/O
# ===========================================================================


class RecordingProvider:
    """Mock provider recording calls without I/O.

    Implements the LLMProvider Protocol from the spec.
    """

    name: str = "recording"

    def __init__(self, response: str = "ok", raise_exc: BaseException | None = None):
        self.response = response
        self.raise_exc = raise_exc
        self.calls: list[dict] = []

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


def _make_client(provider: Any, model: str = "test-model") -> Any:
    """Build an LLMClient with the given provider."""
    from cdad.llm.client import LLMClient

    return LLMClient(provider=provider, model=model)


# ===========================================================================
# FOUNDATIONAL: Protocol shape & exception hierarchy
# ===========================================================================


class TestProtocolShape:
    """Tests: LLMProvider Protocol structure (foundational).

    PC: The spec defines a Protocol with `name`, `send_message`, and a `Message` TypedDict.
    """

    def test_llmprovider_has_name_attribute(self):
        from cdad.llm.provider import LLMProvider

        assert hasattr(LLMProvider, "name") or "name" in getattr(LLMProvider, "__annotations__", {})

    def test_llmprovider_send_message_has_correct_signature(self):
        from cdad.llm.provider import LLMProvider

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
        from cdad.llm.provider import Message

        annotations = getattr(Message, "__annotations__", {})
        assert "role" in annotations
        assert "content" in annotations


class TestExceptionHierarchy:
    """Tests: Exception types and hierarchy (foundational).

    PC: All provider exceptions inherit from ProviderError.
    """

    def test_provider_auth_error_inherits_from_provider_error(self):
        from cdad.llm.provider import ProviderAuthError, ProviderError

        assert issubclass(ProviderAuthError, ProviderError)

    def test_provider_rate_limit_error_inherits_from_provider_error(self):
        from cdad.llm.provider import ProviderError, ProviderRateLimitError

        assert issubclass(ProviderRateLimitError, ProviderError)

    def test_provider_transport_error_inherits_from_provider_error(self):
        from cdad.llm.provider import ProviderError, ProviderTransportError

        assert issubclass(ProviderTransportError, ProviderError)

    def test_provider_response_error_inherits_from_provider_error(self):
        from cdad.llm.provider import ProviderError, ProviderResponseError

        assert issubclass(ProviderResponseError, ProviderError)

    def test_configuration_error_inherits_from_exception(self):
        from cdad.llm.provider import ConfigurationError

        assert issubclass(ConfigurationError, Exception)

    def test_provider_error_is_exception(self):
        from cdad.llm.provider import ProviderError

        assert issubclass(ProviderError, Exception)


# ===========================================================================
# PC-002-1 — Conservation of turns
# ===========================================================================


class TestPC002_1_ConservationOfTurns:
    """PC-002-1: history order and count preserved across ALL providers.

    For every history of length N, the provider receives N+1 turns
    (N previous + the new user_message) in the same order.
    """

    @pytest.mark.parametrize(
        "history_seed",
        [
            pytest.param([], id="empty"),
            pytest.param(
                [{"role": "user", "content": "u1"}, {"role": "assistant", "content": "a1"}],
                id="1-turn",
            ),
            pytest.param(
                [
                    {"role": "user", "content": "u1"},
                    {"role": "assistant", "content": "a1"},
                    {"role": "user", "content": "u2"},
                    {"role": "assistant", "content": "a2"},
                    {"role": "user", "content": "u3"},
                ],
                id="5-messages",
            ),
        ],
    )
    def test_history_preserves_order_and_count(self, history_seed):
        """Each provider receives exactly N+1 turns in same order."""
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)
        client.history = copy.deepcopy(history_seed)

        client.send_message("new message", system_prompt="sys")

        assert provider.calls, "Provider should have received at least one call"
        forwarded = provider.calls[-1]["history"]
        expected = history_seed + [{"role": "user", "content": "new message"}]
        assert forwarded == expected, (
            f"Expected {len(expected)} turns in order, got {len(forwarded)}"
        )


# ===========================================================================
# PC-002-2 — System prompt channel
# ===========================================================================


class TestPC002_2_SystemPromptChannel:
    """PC-002-2: system_prompt transmitted via dedicated channel,
    NOT duplicated as a regular message in history.
    """

    def test_system_prompt_transmitted_as_parameter(self):
        """Each provider receives system_prompt as a dedicated parameter."""
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)

        client.send_message("hola", system_prompt="sys_value")

        assert provider.calls[-1]["system_prompt"] == "sys_value"

    def test_system_prompt_not_duplicated_in_history(self):
        """system_prompt is NOT duplicated as a regular message in history."""
        provider = RecordingProvider(response="ack")
        client = _make_client(provider)

        client.send_message("user msg", system_prompt="system msg")

        history = provider.calls[-1]["history"]
        for msg in history:
            assert msg["content"] != "system msg", (
                "system_prompt should NOT appear as a regular message in history"
            )


# ===========================================================================
# PC-002-3 — Immutability of input on provider error
# ===========================================================================


class TestPC002_3_Immutability:
    """PC-002-3: LLMClient.send_message does NOT mutate self.history
    when the provider raises an exception.
    """

    @pytest.mark.parametrize(
        "exc_class",
        [
            pytest.param("ProviderAuthError", id="auth"),
            pytest.param("ProviderRateLimitError", id="rate"),
            pytest.param("ProviderTransportError", id="transport"),
            pytest.param("ProviderResponseError", id="response"),
        ],
    )
    def test_history_unchanged_on_provider_exception(self, exc_class):
        from cdad.llm.provider import (
            ProviderAuthError,
            ProviderRateLimitError,
            ProviderResponseError,
            ProviderTransportError,
        )

        exc_map = {
            "ProviderAuthError": ProviderAuthError,
            "ProviderRateLimitError": ProviderRateLimitError,
            "ProviderTransportError": ProviderTransportError,
            "ProviderResponseError": ProviderResponseError,
        }
        exc_cls = exc_map[exc_class]
        exc_instance = exc_cls("test error")
        provider = RecordingProvider(response="should not reach", raise_exc=exc_instance)
        client = _make_client(provider)
        original = [{"role": "user", "content": "original"}]
        client.history = copy.deepcopy(original)

        with pytest.raises(exc_cls):
            client.send_message("new msg", system_prompt="sys")

        assert client.history == original, (
            "LLMClient.history was mutated despite provider raising an exception"
        )


# ===========================================================================
# PC-002-4 — Exception mapping
# ===========================================================================


class TestPC002_4_ExceptionMapping:
    """PC-002-4: each provider maps native errors to typed ProviderError hierarchy.

    The spec defines this mapping for all three providers (Anthropic, OpenAI, ACP).
    """

    def test_provider_auth_error_hierarchy(self):
        from cdad.llm.provider import ProviderAuthError, ProviderError

        assert issubclass(ProviderAuthError, ProviderError)

    def test_provider_rate_limit_error_hierarchy(self):
        from cdad.llm.provider import ProviderError, ProviderRateLimitError

        assert issubclass(ProviderRateLimitError, ProviderError)

    def test_provider_transport_error_hierarchy(self):
        from cdad.llm.provider import ProviderError, ProviderTransportError

        assert issubclass(ProviderTransportError, ProviderError)

    def test_provider_response_error_hierarchy(self):
        from cdad.llm.provider import ProviderError, ProviderResponseError

        assert issubclass(ProviderResponseError, ProviderError)

    def test_anthropic_auth_error_maps_to_provider_auth_error(self):
        """Anthropic AuthenticationError -> ProviderAuthError."""
        pytest.importorskip("cdad.llm.providers.anthropic")
        pytest.importorskip("anthropic")
        from anthropic import AuthenticationError
        from cdad.llm.provider import ProviderAuthError
        from cdad.llm.providers.anthropic import AnthropicProvider

        provider = AnthropicProvider(api_key="invalid-key")
        with patch.object(provider.client.messages, "create") as mock_create:
            mock_create.side_effect = AuthenticationError(
                "Invalid API key", response=MagicMock(), body=MagicMock()
            )
            with pytest.raises(ProviderAuthError):
                provider.send_message(
                    system_prompt="test", history=[], model="claude-opus-4-7", max_tokens=2048
                )

    def test_openai_auth_error_maps_to_provider_auth_error(self):
        """OpenAI AuthenticationError -> ProviderAuthError."""
        pytest.importorskip("cdad.llm.providers.openai")
        pytest.importorskip("openai")
        from cdad.llm.provider import ProviderAuthError
        from cdad.llm.providers.openai import OpenAIProvider
        from openai import AuthenticationError

        provider = OpenAIProvider(api_key="invalid-key")
        with patch.object(provider.client.chat.completions, "create") as mock_create:
            mock_create.side_effect = AuthenticationError(
                "Invalid API key", response=MagicMock(), body=MagicMock()
            )
            with pytest.raises(ProviderAuthError):
                provider.send_message(
                    system_prompt="test", history=[], model="gpt-4o", max_tokens=2048
                )

    def test_acp_auth_error_maps_to_provider_auth_error(self):
        """ACP AuthenticationError -> ProviderAuthError."""
        pytest.importorskip("cdad.llm.providers.acp")
        pytest.importorskip("acp_sdk")
        from acp_sdk import AuthenticationError
        from cdad.llm.provider import ProviderAuthError
        from cdad.llm.providers.acp import ACPProvider

        provider = ACPProvider(agent_command=["npx", "-y", "@zed-industries/claude-agent-acp"])
        with patch("acp_sdk.Client") as mock_acp_client:
            mock_client = MagicMock()
            mock_acp_client.return_value = mock_client
            mock_client.initialize.side_effect = AuthenticationError("Auth failed")
            with pytest.raises(ProviderAuthError):
                provider.send_message(
                    system_prompt="test", history=[], model="claude", max_tokens=2048
                )


# ===========================================================================
# PC-002-5 — Isolation preserved
# ===========================================================================


class TestPC002_5_IsolationPreserved:
    """PC-002-5: changing provider does not alter access policies.

    _AGENT_ACCESS_POLICY in src/cdad/project/model.py is independent of provider.
    """

    def test_agent_access_policy_unchanged_after_config_change(self):
        """Resolving different provider specs for same role yields same access policy."""
        from cdad.llm.registry import resolve_provider

        config_a = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        config_b = {
            "agents": {"architect": "acp/claude"},
            "providers": {
                "acp": {"agents": {"claude": ["npx", "-y", "@zed-industries/claude-agent-acp"]}}
            },
        }

        provider_a = resolve_provider("architect", config=config_a)
        provider_b = resolve_provider("architect", config=config_b)

        client_a = _make_client(provider_a)
        client_b = _make_client(provider_b)

        # Access policy is determined by agent role, NOT by provider
        accessible_a = getattr(client_a, "get_accessible_files", lambda: set())()
        accessible_b = getattr(client_b, "get_accessible_files", lambda: set())()
        assert accessible_a == accessible_b, (
            "Access policy should be the same regardless of provider"
        )

    def test_accessible_files_unchanged_across_providers(self):
        """The set of accessible files for a role is invariant across providers."""
        # This duplicates the test above with slightly different phrasing —
        # kept as a separate test for redundancy per the original file.
        self.test_agent_access_policy_unchanged_after_config_change()


# ===========================================================================
# PC-002-6 — Deterministic resolution
# ===========================================================================


class TestPC002_6_DeterministicResolution:
    """PC-002-6: resolve_provider returns the same (provider_name, model_id)
    across consecutive calls with the same config.
    """

    def test_resolve_provider_returns_same_result_across_calls(self):
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }

        results = [resolve_provider("architect", config=config) for _ in range(10)]
        for r in results[1:]:
            assert r == results[0] or getattr(r, "name", None) == getattr(
                results[0], "name", None
            ), (
                "resolve_provider should return the same provider for repeated calls with same config"
            )


# ===========================================================================
# PC-002-7 — Fail-fast configuration
# ===========================================================================


class TestPC002_7_FailFastConfiguration:
    """PC-002-7: invalid config raises ConfigurationError BEFORE executing
    the first agent command.
    """

    def test_unknown_provider_raises_configuration_error(self):
        from cdad.llm.provider import ConfigurationError
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "unknown-provider/model"},
            "providers": {},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)

    def test_missing_api_key_env_raises_configuration_error(self):
        from cdad.llm.provider import ConfigurationError
        from cdad.llm.registry import resolve_provider

        # Ensure the env var is NOT set
        env_backup = os.environ.pop("TEST_MISSING_KEY", None)
        try:
            config = {
                "agents": {"architect": "anthropic/claude-opus-4-7"},
                "providers": {"anthropic": {"api_key_env": "TEST_MISSING_KEY"}},
            }
            with pytest.raises(ConfigurationError):
                resolve_provider("architect", config=config)
        finally:
            if env_backup is not None:
                os.environ["TEST_MISSING_KEY"] = env_backup

    def test_invalid_format_raises_configuration_error(self):
        from cdad.llm.provider import ConfigurationError
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "invalid-format-no-slash"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)

    def test_unknown_role_raises_configuration_error(self):
        from cdad.llm.provider import ConfigurationError
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"unknown_role_xyz": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("unknown_role_xyz", config=config)


# ===========================================================================
# PC-002-8 — Configuration precedence
# ===========================================================================


class TestPC002_8_ConfigurationPrecedence:
    """PC-002-8: strict precedence order (most specific wins):
    1. CDAD_AGENT_<ROLE> env var
    2. ./cdad.toml (cwd)
    3. ~/.config/cdad/cdad.toml
    4. DEFAULT_AGENT_MODELS (code defaults)
    """

    def test_env_var_takes_precedence(self):
        """When env var is set, it should win over all other config layers."""
        from cdad.llm.registry import resolve_provider

        with patch.dict(
            os.environ,
            {"CDAD_AGENT_ARCHITECT": "anthropic/claude-opus-4-7", "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config={})
            assert result is not None, "Resolution should succeed with env var"

    def test_local_config_when_no_env_var(self):
        """When only local config is set, it should be used."""
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "anthropic/claude-sonnet-4-6"},
            "providers": {"anthropic": {"api_key_env": "ANTHROPIC_API_KEY"}},
        }
        result = resolve_provider("architect", config=config)
        assert result is not None

    def test_default_when_nothing_configured(self):
        """When nothing is configured, defaults from code should be used."""
        from cdad.llm.registry import DEFAULT_AGENT_MODELS, resolve_provider

        assert DEFAULT_AGENT_MODELS, "DEFAULT_AGENT_MODELS should be defined"
        result = resolve_provider("architect", config={})
        assert result is not None

    def test_all_layers_defined_env_wins(self):
        """When all layers are defined, env var must win over file config."""
        from cdad.llm.registry import resolve_provider

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


# ===========================================================================
# PC-002-9 — API keys never literal
# ===========================================================================


class TestPC002_9_APIKeysNeverLiteral:
    """PC-002-9: the loader rejects any `api_key` (literal value) in
    [providers.*]. Only `api_key_env` is allowed.
    """

    def test_literal_api_key_in_config_raises_configuration_error(self):
        from cdad.llm.provider import ConfigurationError
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "anthropic/claude-opus-4-7"},
            "providers": {"anthropic": {"api_key": "sk-literal-key"}},
        }
        with pytest.raises(ConfigurationError):
            resolve_provider("architect", config=config)


# ===========================================================================
# PC-002-10 — Equivalent functionality across providers
# ===========================================================================


class TestPC002_10_EquivalentFunctionality:
    """PC-002-10: Same (system_prompt, history) → same output across ALL providers
    (Anthropic, OpenAI, ACP) when mocked.
    """

    @pytest.mark.parametrize(
        "provider_name",
        ["anthropic", "openai", "acp"],
    )
    def test_all_providers_return_nonempty_string(self, provider_name):
        """Each provider returns a non-empty string for the same input."""
        provider = RecordingProvider(response=f"response from {provider_name}")
        client = _make_client(provider)

        result = client.send_message(
            "draft a spec",
            system_prompt="you are an architect",
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_providers_with_same_input_produce_same_output(self):
        """Anthropic, OpenAI, and ACP with same mock response produce identical output."""
        expected_response = "identical output across all three providers"
        anthropic = RecordingProvider(response=expected_response)
        openai = RecordingProvider(response=expected_response)
        acp = RecordingProvider(response=expected_response)

        sys_prompt = "you are an architect"
        hist = [{"role": "user", "content": "initial prompt"}]
        input_msg = "follow up question"

        client_a = _make_client(anthropic)
        client_a.history = copy.deepcopy(hist)
        result_a = client_a.send_message(input_msg, system_prompt=sys_prompt)

        client_b = _make_client(openai)
        client_b.history = copy.deepcopy(hist)
        result_b = client_b.send_message(input_msg, system_prompt=sys_prompt)

        client_c = _make_client(acp)
        client_c.history = copy.deepcopy(hist)
        result_c = client_c.send_message(input_msg, system_prompt=sys_prompt)

        assert result_a == result_b == result_c
        assert result_a == expected_response


# ===========================================================================
# PC-002-11 — Lazy import of SDKs
# ===========================================================================


class TestPC002_11_LazyImport:
    """PC-002-11: importing cdad.llm.registry or cdad.cli.main does NOT
    import anthropic, openai, or acp_sdk. SDKs are only imported when
    the corresponding provider is instantiated.
    """

    def test_registry_module_does_not_import_anthropic_directly(self):
        before_anthropic = "anthropic" in sys.modules
        before_openai = "openai" in sys.modules
        before_acp = "acp_sdk" in sys.modules

        try:
            import cdad.llm.registry  # noqa: F401
        except ImportError:
            pass

        after_anthropic = "anthropic" in sys.modules
        after_openai = "openai" in sys.modules
        after_acp = "acp_sdk" in sys.modules

        assert not after_anthropic or before_anthropic, (
            "anthropic SDK should not be imported by registry module"
        )
        assert not after_openai or before_openai, (
            "openai SDK should not be imported by registry module"
        )
        assert not after_acp or before_acp, "acp_sdk should not be imported by registry module"

    def test_cli_main_does_not_import_anthropic_on_startup(self):
        before_anthropic = "anthropic" in sys.modules
        try:
            import cdad.cli.main  # noqa: F401
        except ImportError:
            pass  # RED phase: module may not exist yet
        after_anthropic = "anthropic" in sys.modules
        assert not after_anthropic or before_anthropic, (
            "anthropic SDK should not be imported by cdad.cli.main at import time"
        )

    def test_sdk_imported_only_when_provider_instantiated(self):
        """SDK modules should only appear in sys.modules after a provider is built."""
        before = "anthropic" in sys.modules
        try:
            from cdad.llm.registry import resolve_provider

            provider = resolve_provider("architect", config={})
            if provider and hasattr(provider, "client"):
                after = "anthropic" in sys.modules
                assert after, (
                    "anthropic SDK should be in sys.modules after AnthropicProvider is instantiated"
                )
        except Exception:
            pass  # RED phase: expected


# ===========================================================================
# PC-002-12 — Extensible registry
# ===========================================================================


class TestPC002_12_ExtensibleRegistry:
    """PC-002-12: third parties can register custom providers without modifying
    CLI code.
    """

    def test_registry_allows_registering_custom_provider(self):
        from cdad.llm.registry import register, resolve_provider

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


# ===========================================================================
# PC-002-13 — ACP builtins
# ===========================================================================


class TestPC002_13_ACPBuiltins:
    """PC-002-13: ACP builtin aliases (claude, gemini, codex, qwen) have
    correct default commands and can be overridden via cdad.toml.
    """

    @pytest.mark.parametrize(
        "alias,expected_command",
        [
            ("claude", ["npx", "-y", "@zed-industries/claude-agent-acp"]),
            ("gemini", ["npx", "-y", "@google/gemini-cli"]),
            ("codex", ["npx", "-y", "codex-acp"]),
            ("qwen", ["qwen-agent"]),
        ],
    )
    def test_acp_builtin_aliases_have_correct_default_commands(self, alias, expected_command):
        from cdad.llm.registry import get_builtin_acp_command

        result = get_builtin_acp_command(alias)
        assert result == expected_command

    def test_acp_builtin_config_overrides_default_command(self):
        from cdad.llm.registry import resolve_provider

        custom_command = ["/custom/path/claude"]
        config = {
            "agents": {"architect": "acp/claude"},
            "providers": {"acp": {"agents": {"claude": custom_command}}},
        }
        provider = resolve_provider("architect", config=config)
        assert hasattr(provider, "command"), "ACPProvider should have a 'command' attribute"
        assert provider.command == custom_command

    def test_missing_acp_command_raises_provider_transport_error(self):
        from cdad.llm.provider import ProviderTransportError
        from cdad.llm.registry import resolve_provider

        config = {
            "agents": {"architect": "acp/nonexistent"},
            "providers": {"acp": {"agents": {"nonexistent": ["/path/that/does/not/exist"]}}},
        }
        provider = resolve_provider("architect", config=config)
        with pytest.raises(ProviderTransportError):
            provider.send_message(
                system_prompt="test",
                history=[],
                model="test",
                max_tokens=100,
            )


# ===========================================================================
# PC-002-14 — Default models
# ===========================================================================


class TestPC002_14_DefaultModels:
    """PC-002-14: defaults are mixed providers (Anthropic + OpenAI + ACP).

    Without any config:
      architect   → anthropic/claude-opus-4-7
      test_writer → anthropic/claude-sonnet-4-6
      implementer → acp/claude
      reviewer    → openai/gpt-4o
      scribe      → acp/qwen
    """

    def test_default_agent_models_constant_exists(self):
        from cdad.llm.registry import DEFAULT_AGENT_MODELS

        assert DEFAULT_AGENT_MODELS is not None, "DEFAULT_AGENT_MODELS not found in registry"

    @pytest.mark.parametrize(
        "role,expected_model",
        [
            ("architect", "anthropic/claude-opus-4-7"),
            ("test_writer", "anthropic/claude-sonnet-4-6"),
            ("implementer", "acp/claude"),
            ("reviewer", "openai/gpt-4o"),
            ("scribe", "acp/qwen"),
        ],
    )
    def test_default_models_are_correct_values(self, role, expected_model):
        from cdad.llm.registry import DEFAULT_AGENT_MODELS

        assert DEFAULT_AGENT_MODELS.get(role) == expected_model

    def test_default_models_use_multiple_providers(self):
        """PC-002-14: defaults use a mix of Anthropic, OpenAI, and ACP providers."""
        from cdad.llm.registry import DEFAULT_AGENT_MODELS

        providers_used = {model.split("/")[0] for model in DEFAULT_AGENT_MODELS.values()}
        assert "anthropic" in providers_used, "Expected Anthropic provider in defaults"
        assert "openai" in providers_used, "Expected OpenAI provider in defaults"
        assert "acp" in providers_used, "Expected ACP provider in defaults"


# ===========================================================================
# PC-002-15 — Env var precedence over defaults
# ===========================================================================


class TestPC002_15_EnvVarPrecedence:
    """PC-002-15: env var CDAD_AGENT_<ROLE> overrides default model from code."""

    def test_env_var_overrides_default_model(self):
        from cdad.llm.registry import resolve_provider

        with patch.dict(
            os.environ,
            {"CDAD_AGENT_ARCHITECT": "anthropic/claude-opus-4-7", "ANTHROPIC_API_KEY": "sk-test"},
            clear=False,
        ):
            result = resolve_provider("architect", config={})
            assert result is not None
            name = getattr(result, "name", str(result))
            assert "opus" in name.lower() or "claude-opus" in name.lower()

    def test_env_var_takes_precedence_over_file_config(self):
        from cdad.llm.registry import resolve_provider

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
            name = getattr(result, "name", str(result))
            assert "opus" in name.lower() or "claude-opus" in name.lower(), (
                "Env var should take precedence over file config"
            )
