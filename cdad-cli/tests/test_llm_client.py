"""Tests for LLMClient - wrapper around Anthropic SDK."""

from unittest.mock import MagicMock, patch
from cdad.llm.client import LLMClient


class TestLLMClientClass:
    """Test LLMClient integration with Anthropic API."""

    @patch("cdad.llm.client.Anthropic")
    def test_initializes_with_api_key(self, mock_anthropic_class):
        """LLMClient initializes with API key."""
        mock_anthropic_class.return_value = MagicMock()
        client = LLMClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "claude-opus-4-7"

    @patch("cdad.llm.client.Anthropic")
    def test_initializes_with_custom_model(self, mock_anthropic_class):
        """LLMClient accepts custom model."""
        mock_anthropic_class.return_value = MagicMock()
        client = LLMClient(api_key="test-key", model="claude-sonnet-4-6")
        assert client.model == "claude-sonnet-4-6"

    @patch("cdad.llm.client.Anthropic")
    def test_sends_message_and_receives_response(self, mock_anthropic_class):
        """LLMClient sends message and receives response."""
        # Mock the Anthropic client
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock the message response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response text")]
        mock_client.messages.create.return_value = mock_response

        client = LLMClient(api_key="test-key")
        result = client.send_message("Test message")

        assert result == "Response text"

    @patch("cdad.llm.client.Anthropic")
    def test_maintains_conversation_history(self, mock_anthropic_class):
        """LLMClient maintains conversation history."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        client = LLMClient(api_key="test-key")
        client.send_message("First message")
        client.send_message("Second message")

        history = client.get_history()
        assert len(history) >= 2

    @patch("cdad.llm.client.Anthropic")
    def test_clear_history(self, mock_anthropic_class):
        """LLMClient can clear conversation history."""
        mock_anthropic_class.return_value = MagicMock()
        client = LLMClient(api_key="test-key")
        client.history = [{"role": "user", "content": "test"}]

        client.clear_history()
        assert client.get_history() == []

    @patch("cdad.llm.client.Anthropic")
    def test_uses_correct_model(self, mock_anthropic_class):
        """LLMClient uses specified model in API calls."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response

        client = LLMClient(api_key="test-key", model="custom-model")
        client.send_message("Test")

        # Verify the model was passed to the API call
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["model"] == "custom-model"

    @patch("cdad.llm.client.Anthropic")
    def test_get_history_returns_messages(self, mock_anthropic_class):
        """LLMClient returns conversation history."""
        mock_anthropic_class.return_value = MagicMock()
        client = LLMClient(api_key="test-key")
        client.history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        history = client.get_history()
        assert len(history) == 2
        assert history[0]["content"] == "Hello"
