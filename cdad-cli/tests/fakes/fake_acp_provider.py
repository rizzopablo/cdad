from __future__ import annotations

from cdad.llm.provider import LLMProvider, Message


class FakeACPProvider(LLMProvider):
    """Fake LLMProvider for testing that returns scripted responses."""

    name: str = "acp_fake"

    def __init__(self, scripted_responses: list[str]):
        """Initialize with a list of responses to return in order."""
        self.responses = scripted_responses
        self.call_count = 0

    def send_message(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        """Return the next scripted response."""
        if self.call_count >= len(self.responses):
            raise IndexError(f"scripted_responses exhausted (called {self.call_count + 1} times)")
        resp = self.responses[self.call_count]
        self.call_count += 1
        return resp
