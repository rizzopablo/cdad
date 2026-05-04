"""Tests for LLMClient - wrapper around LLM providers."""

from unittest.mock import MagicMock

from cdad.llm.client import LLMClient


class TestLLMClientClass:
    """Test LLMClient integration with LLM providers."""

    def test_initializes_with_provider(self):
        """LLMClient initializes with provider instance."""
        fake_provider = MagicMock()
        client = LLMClient(provider=fake_provider, model="claude-opus-4-7")
        assert client.provider == fake_provider
        assert client.model == "claude-opus-4-7"

    def test_initializes_with_custom_model(self):
        """LLMClient accepts custom model."""
        fake_provider = MagicMock()
        client = LLMClient(provider=fake_provider, model="claude-sonnet-4-6")
        assert client.model == "claude-sonnet-4-6"

    def test_sends_message_and_receives_response(self):
        """LLMClient sends message and receives response via provider."""
        fake_provider = MagicMock()
        fake_provider.send_message.return_value = "Response text"

        client = LLMClient(provider=fake_provider, model="claude-opus-4-7")
        result = client.send_message("Test message")

        assert result == "Response text"
        # Verify provider.send_message was called with correct args
        fake_provider.send_message.assert_called_once()
        call_args = fake_provider.send_message.call_args
        assert call_args.kwargs.get("model") == "claude-opus-4-7"

    def test_maintains_conversation_history(self):
        """LLMClient maintains conversation history."""
        fake_provider = MagicMock()
        fake_provider.send_message.return_value = "Response"

        client = LLMClient(provider=fake_provider, model="claude-opus-4-7")
        client.send_message("First message")
        client.send_message("Second message")

        history = client.get_history()
        assert len(history) >= 2

    def test_clear_history(self):
        """LLMClient can clear conversation history."""
        fake_provider = MagicMock()
        client = LLMClient(provider=fake_provider, model="claude-opus-4-7")
        client.history = [{"role": "user", "content": "test"}]

        client.clear_history()
        assert client.get_history() == []

    def test_uses_correct_model(self):
        """LLMClient uses specified model in API calls."""
        fake_provider = MagicMock()
        fake_provider.send_message.return_value = "Response"

        client = LLMClient(provider=fake_provider, model="custom-model")
        client.send_message("Test")

        # Verify the model was passed to the provider call
        call_args = fake_provider.send_message.call_args
        assert call_args.kwargs["model"] == "custom-model"

    def test_get_history_returns_messages(self):
        """LLMClient returns conversation history."""
        fake_provider = MagicMock()
        client = LLMClient(provider=fake_provider, model="claude-opus-4-7")
        client.history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        history = client.get_history()
        assert len(history) == 2
        assert history[0]["content"] == "Hello"
