"""LLMClient - wrapper around Anthropic SDK for Claude interactions."""

from typing import List, Dict
from anthropic import Anthropic


class LLMClient:
    """Wrapper around Anthropic SDK for LLM interactions."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-7"):
        """Initialize LLMClient.

        Args:
            api_key: Anthropic API key.
            model: Model to use (default: claude-opus-4-7).
        """
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.history: List[Dict[str, str]] = []

    def send_message(self, message: str, system_prompt: str = "") -> str:
        """Send message to Claude and get response.

        Args:
            message: User message to send.
            system_prompt: Optional system prompt for the message.

        Returns:
            Response text from Claude.
        """
        # Add user message to history
        self.history.append({"role": "user", "content": message})

        # Build messages for API call
        messages = self.history.copy()

        # Call Claude API
        system = system_prompt if system_prompt else None
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=messages,
        )

        # Extract response text
        response_text = response.content[0].text

        # Add assistant response to history
        self.history.append({"role": "assistant", "content": response_text})

        return response_text

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history.

        Returns:
            List of message dictionaries with role and content.
        """
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history = []
