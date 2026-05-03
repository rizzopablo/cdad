from __future__ import annotations

from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ProviderError(Exception):
    """Base exception for all provider errors."""


class ProviderAuthError(ProviderError):
    """Authentication failure (401/403)."""


class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded (429)."""


class ProviderTransportError(ProviderError):
    """Network, timeout, or subprocess failure."""


class ProviderResponseError(ProviderError):
    """Unexpected response shape from provider."""


class ConfigurationError(Exception):
    """Invalid provider/agente configuration (missing key, unknown provider)."""


class LLMProvider(Protocol):
    name: str

    def send_message(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        """Envía la conversación al proveedor."""
        ...
