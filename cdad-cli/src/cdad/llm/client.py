"""LLMClient - wrapper around LLMProvider."""

from __future__ import annotations

from typing import Any

from cdad.llm.provider import Message, ProviderError


class LLMClient:
    """Wrapper around LLMProvider for agent interactions."""

    def __init__(
        self,
        provider: Any = None,
        *,
        model: str = "claude-opus-4-7",
        max_tokens: int = 2048,
    ):
        """Initialize LLMClient.

        Args:
            provider: LLMProvider instance to use.
            model: Model to use.
            max_tokens: Maximum tokens for response.
        """
        self.model = model
        self.max_tokens = max_tokens
        self.history: list[Message] = []
        self.provider = provider

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send message and get response."""
        if self.provider is None:
            raise ValueError("LLMClient requires a provider to send messages")

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
