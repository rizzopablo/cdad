"""LLMClient - wrapper around LLMProvider with backward compatibility."""

from __future__ import annotations

from typing import Any

from cdad.llm.provider import Message, ProviderError

# For backward compatibility with tests that mock Anthropic directly
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


class LLMClient:
    """Wrapper around LLMProvider for agent interactions."""

    def __init__(
        self,
        provider: Any = None,
        model: str = "claude-opus-4-7",
        *,
        api_key: str = None,
        max_tokens: int = 2048,
    ):
        """Initialize LLMClient.

        Args:
            provider: LLMProvider to use. If string, assumed api_key for legacy compat.
            model: Model to use.
            api_key: Anthropic API key (legacy mode).
            max_tokens: Maximum tokens for response.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.history: list[Message] = []

        if isinstance(provider, str) and api_key is None:
            api_key = provider
            provider = None

        if api_key is not None:
            self.api_key = api_key
            self.provider = None
            if Anthropic is not None:
                self.client = Anthropic(api_key=api_key)
            else:
                self.client = None
        else:
            self.api_key = None
            self.client = None
            self.provider = provider

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send message and get response."""
        if self.provider is None:
            # Legacy mode
            self.history.append({"role": "user", "content": message})
            messages = list(self.history)
            system = system_prompt if system_prompt else None
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
            )
            response_text = response.content[0].text
            self.history.append({"role": "assistant", "content": response_text})
            return response_text
        else:
            history_snapshot = list(self.history)
            self.history.append({"role": "user", "content": message})

            try:
                response_text = self.provider.send_message(
                    system_prompt,
                    list(self.history),
                    model=self.model,
                    max_tokens=self.max_tokens,
                )
            except ProviderError:
                self.history = history_snapshot
                raise

            self.history.append({"role": "assistant", "content": response_text})
            return response_text

    def get_history(self) -> list[Message]:
        """Get conversation history."""
        return list(self.history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = []
