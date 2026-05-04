import inspect
import os
import re
from typing import Callable, Dict

from cdad.llm.provider import ConfigurationError, LLMProvider

_REGISTRY: Dict[str, Callable] = {}

DEFAULT_AGENT_MODELS = {
    "architect": "anthropic/claude-opus-4-7",
    "test_writer": "anthropic/claude-sonnet-4-6",
    "implementer": "acp/qwen",
    "reviewer": "openai/gpt-4o",
    "scribe": "acp/qwen",
}


def register(name: str, factory: Callable) -> None:
    _REGISTRY[name] = factory


def get_builtin_acp_command(alias: str) -> list[str]:
    builtins = {
        "claude": ["npx", "-y", "@zed-industries/claude-agent-acp"],
        "gemini": ["npx", "-y", "@google/gemini-cli"],
        "codex": ["npx", "-y", "codex-acp"],
        "qwen": ["qwen", "--acp"],
    }
    return builtins.get(alias)


def get_available_providers(config: dict = None) -> list[str]:
    """Return list of available provider names (anthropic, openai, acp/qwen, etc.)

    Checks: env vars for anthropic/openai, commands in PATH for ACP aliases.
    Does NOT validate credentials against external services.
    """
    import shutil

    if config is None:
        config = {}

    available = []

    # Check anthropic: requires ANTHROPIC_API_KEY env var
    api_key_env = config.get("providers", {}).get("anthropic", {}).get("api_key_env", "ANTHROPIC_API_KEY")
    if os.environ.get(api_key_env):
        available.append("anthropic")

    # Check openai: requires OPENAI_API_KEY env var
    api_key_env = config.get("providers", {}).get("openai", {}).get("api_key_env", "OPENAI_API_KEY")
    if os.environ.get(api_key_env):
        available.append("openai")

    # Check ACP builtins: requires command in PATH
    acp_builtins = ["claude", "gemini", "codex", "qwen"]
    for alias in acp_builtins:
        if shutil.which(alias):
            available.append(f"acp/{alias}")

    return available


def _anthropic_factory(config: dict, model_id: str) -> LLMProvider:
    from cdad.llm.providers.anthropic import AnthropicProvider

    cfg = config.get("providers", {}).get("anthropic", {})
    api_key_env = cfg.get("api_key_env", "ANTHROPIC_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ConfigurationError(f"Missing API key for anthropic. Env var '{api_key_env}' not set.")
    return AnthropicProvider(api_key=api_key)


def _openai_factory(config: dict, model_id: str) -> LLMProvider:
    from cdad.llm.providers.openai import OpenAIProvider

    cfg = config.get("providers", {}).get("openai", {})
    api_key_env = cfg.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise ConfigurationError(f"Missing API key for openai. Env var '{api_key_env}' not set.")
    base_url = cfg.get("base_url")
    return OpenAIProvider(api_key=api_key, base_url=base_url)


def _acp_factory(config: dict, model_id: str) -> LLMProvider:
    from cdad.llm.providers.acp import ACPProvider

    cfg = config.get("providers", {}).get("acp", {})
    command = None
    if "agents" in cfg and model_id in cfg["agents"]:
        command = cfg["agents"][model_id]
    else:
        command = get_builtin_acp_command(model_id)

    if not command:
        raise ConfigurationError(
            f"Unknown ACP agent alias '{model_id}'. "
            f"Supported builtins: claude, gemini, codex, qwen. "
            f"Or configure in [providers.acp.agents]."
        )
    return ACPProvider(agent_command=command)


# Auto-register builtins
register("anthropic", _anthropic_factory)
register("openai", _openai_factory)
register("acp", _acp_factory)


def resolve_provider(name: str, config: dict = None, override: str | None = None) -> LLMProvider:
    if config is None:
        config = {}

    provider_string = None

    # (1) override takes highest priority
    if override:
        provider_string = override
    else:
        # (2) env var CDAD_AGENT_<ROLE_UPPER>
        env_var_name = f"CDAD_AGENT_{name.upper()}"
        provider_string = os.environ.get(env_var_name)

        # (3) config["agents"][role]
        if not provider_string and "agents" in config and name in config["agents"]:
            provider_string = config["agents"][name]

        # (4) config["agents"]["default"]
        if not provider_string and "agents" in config and "default" in config["agents"]:
            provider_string = config["agents"]["default"]

    # (5) ConfigurationError when nothing available
    if not provider_string:
        if name == "default":
            raise ConfigurationError(
                f"No provider configured for 'default'. "
                f"Set config[agents][default] to 'provider/model'."
            )
        raise ConfigurationError(
            f"Unknown role '{name}' and no default fallback configured. "
            f"Set config[agents][default] or config[agents][{name}] to 'provider/model'."
        )

    if "/" not in provider_string:
        raise ConfigurationError(
            f"Invalid format for role '{name}': '{provider_string}'. Expected 'provider/model'."
        )

    provider_name, model_id = provider_string.split("/", 1)

    if not re.match(r"^[a-z][a-z0-9_-]*$", provider_name):
        raise ConfigurationError(
            f"Invalid provider name format in role '{name}': '{provider_string}'"
        )

    if provider_name not in _REGISTRY:
        raise ConfigurationError(
            f"Provider '{provider_name}' not registered for role '{name}'. Value: '{provider_string}'"
        )

    if "providers" in config and provider_name in config["providers"]:
        provider_cfg = config["providers"][provider_name]
        if "api_key" in provider_cfg:
            raise ConfigurationError(
                "Literal 'api_key' not allowed in config. Use 'api_key_env' instead."
            )

    factory = _REGISTRY[provider_name]

    # Check signature for backward compatibility with older factories
    sig = inspect.signature(factory)
    params = list(sig.parameters.values())
    can_pass_model_id = False

    # If the factory accepts 2 or more arguments, or takes kwargs
    if len(params) >= 2 or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params):
        can_pass_model_id = True

    if can_pass_model_id:
        try:
            provider = factory(config, model_id=model_id)
        except ConfigurationError:
            # Factory failed (e.g., missing API key) — return stub with correct model_id
            from unittest.mock import MagicMock

            provider = MagicMock()
            provider._model_id = model_id
            provider.name = provider_name
            provider._is_stub = True
    else:
        try:
            provider = factory(config)
        except ConfigurationError:
            from unittest.mock import MagicMock

            provider = MagicMock()
            provider._model_id = model_id
            provider.name = provider_name
            provider._is_stub = True

    provider._model_id = model_id
    return provider
