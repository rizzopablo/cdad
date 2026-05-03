"""Tests for registry postconditions from spec 003-implementer-agent.

CICLO 1: PC-003-10, PC-003-11, PC-003-12

RED phase: these tests MUST fail because the implementation does not exist yet.
DO NOT edit src/ — only this test file.
"""

from __future__ import annotations

import inspect

import pytest

from cdad.llm.registry import (
    DEFAULT_AGENT_MODELS,
    get_builtin_acp_command,
    resolve_provider,
)

# ===========================================================================
# PC-003-10 — Default de implementer es "acp/qwen"
# ===========================================================================


class TestPC003_10_ImplementerDefault:
    """PC-003-10: El default de DEFAULT_AGENT_MODELS["implementer"] es "acp/qwen".

    El spec de feature 003 cambia el placeholder "acp/claude" a "acp/qwen"
    porque qwen-coder tiene la mejor relación costo/calidad para codegen
    iterativo y el usuario tiene qwen v0.12.3 instalado.
    """

    def test_implementer_default_is_acp_qwen(self):
        assert "implementer" in DEFAULT_AGENT_MODELS, (
            "DEFAULT_AGENT_MODELS debe tener clave 'implementer'"
        )
        assert DEFAULT_AGENT_MODELS["implementer"] == "acp/qwen", (
            f"El default de implementer debe ser 'acp/qwen', "
            f"got '{DEFAULT_AGENT_MODELS['implementer']}'"
        )


# ===========================================================================
# PC-003-11 — Builtin qwen retorna ["qwen", "--acp"]
# ===========================================================================


class TestPC003_11_QwenBuiltinAcpCommand:
    """PC-003-11: El builtin qwen en get_builtin_acp_command retorna ["qwen", "--acp"].

    Verificado contra qwen v0.12.3+ que expone el flag --acp nativamente.
    """

    def test_qwen_builtin_returns_qwen_with_acp_flag(self):
        result = get_builtin_acp_command("qwen")
        assert result == ["qwen", "--acp"], (
            f"El builtin qwen debe retornar ['qwen', '--acp'], got {result}"
        )


# ===========================================================================
# PC-003-12 — resolve_provider acepta override
# ===========================================================================


class TestPC003_12_ResolveProviderOverride:
    """PC-003-12: resolve_provider acepta parámetro override: str | None = None.

    Si se pasa, tiene precedencia sobre env/config/defaults.
    """

    def test_resolve_provider_signature_accepts_override(self):
        """El parámetro override debe existir en la firma con default None."""
        sig = inspect.signature(resolve_provider)
        params = sig.parameters
        assert "override" in params, (
            f"resolve_provider debe tener parámetro 'override'. "
            f"Parámetros actuales: {list(params.keys())}"
        )
        override_param = params["override"]
        assert override_param.default is None, (
            f"override debe tener default None, got {override_param.default!r}"
        )

    def test_override_takes_precedence_over_env_var(self, monkeypatch):
        """Cuando se pasa override, tiene precedencia sobre CDAD_AGENT_* env var."""
        monkeypatch.setenv("CDAD_AGENT_IMPLEMENTER", "anthropic/claude-sonnet-4-6")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-dummy-anthropic")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy-openai")

        # override debe ganar sobre env var
        provider = resolve_provider("implementer", override="openai/gpt-4o")

        # Verificamos que es OpenAI, no Anthropic (del env var)
        assert provider.__class__.__name__ == "OpenAIProvider", (
            f"override debe seleccionar OpenAI, got {provider.__class__.__name__}"
        )

    def test_override_takes_precedence_over_config(self, monkeypatch):
        """Cuando se pasa override, tiene precedencia sobre config file."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy-openai")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-dummy-anthropic")

        config = {
            "agents": {"implementer": "anthropic/claude-sonnet-4-6"},
            "providers": {},
        }

        # override debe ganar sobre config
        provider = resolve_provider("implementer", config=config, override="openai/gpt-4o")

        # Verificamos que es OpenAI, no Anthropic (del config)
        assert provider.__class__.__name__ == "OpenAIProvider", (
            f"override debe seleccionar OpenAI, got {provider.__class__.__name__}"
        )

    def test_override_takes_precedence_over_default(self, monkeypatch):
        """Cuando se pasa override, tiene precedencia sobre DEFAULT_AGENT_MODELS."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy-openai")
        # Sin env var CDAD_AGENT_IMPLEMENTER, sin config
        # El default sería acp/qwen (cuando PC-003-10 esté GREEN)

        provider = resolve_provider("implementer", override="openai/gpt-4o")

        # Verificamos que es OpenAI, no el default
        assert provider.__class__.__name__ == "OpenAIProvider", (
            f"override debe seleccionar OpenAI, got {provider.__class__.__name__}"
        )

    def test_resolve_without_override_uses_normal_chain(self, monkeypatch):
        """Sin override (None), la cadena env > config > defaults funciona como antes."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-dummy-openai")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-dummy-anthropic")

        # Caso 1: env var gana
        monkeypatch.setenv("CDAD_AGENT_IMPLEMENTER", "anthropic/claude-opus-4-7")
        provider = resolve_provider("implementer", override=None)
        assert provider.__class__.__name__ == "AnthropicProvider"

        # Caso 2: config gana cuando no hay env var
        monkeypatch.delenv("CDAD_AGENT_IMPLEMENTER", raising=False)
        config = {
            "agents": {"implementer": "openai/gpt-4o"},
            "providers": {},
        }
        provider = resolve_provider("implementer", config=config, override=None)
        assert provider.__class__.__name__ == "OpenAIProvider"

        # Caso 3: default gana cuando no hay env var ni config
        # Nota: cuando PC-003-10 esté GREEN, el default será acp/qwen
        # Por ahora el default es acp/claude, así que probamos con ACP
        provider = resolve_provider("implementer", config={}, override=None)
        assert provider.__class__.__name__ == "ACPProvider"
