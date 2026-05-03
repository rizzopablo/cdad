from typing import Any, List

from cdad.llm.provider import (
    LLMProvider,
    Message,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTransportError,
)


class AnthropicProvider:
    def __init__(self, api_key: str):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.anthropic_lib = anthropic

    def __str__(self):
        return f"<AnthropicProvider model_id={getattr(self, '_model_id', '')}>"

    def send_message(
        self, system_prompt: str, history: list[Message], *, model: str, max_tokens: int
    ) -> str:
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt if system_prompt else None,
                messages=history,
            )
            return response.content[0].text
        except self.anthropic_lib.AuthenticationError as e:
            raise ProviderAuthError(str(e)) from e
        except self.anthropic_lib.RateLimitError as e:
            raise ProviderRateLimitError(str(e)) from e
        except self.anthropic_lib.APIConnectionError as e:
            raise ProviderTransportError(str(e)) from e
        except self.anthropic_lib.APIStatusError as e:
            raise ProviderResponseError(str(e)) from e
        except Exception as e:
            if not isinstance(e, ProviderError):
                raise ProviderError(str(e)) from e
            raise
