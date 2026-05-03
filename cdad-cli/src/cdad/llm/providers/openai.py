
from cdad.llm.provider import (
    Message,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTransportError,
)


class OpenAIProvider:
    def __init__(self, api_key: str, base_url: str = None):
        import openai

        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.openai_lib = openai
        self._model_id: str = ""

    @property
    def name(self) -> str:
        if self._model_id:
            return f"openai/{self._model_id}"
        return "openai"

    def __str__(self):
        return f"<OpenAIProvider model_id={getattr(self, '_model_id', '')}>"

    def send_message(
        self, system_prompt: str, history: list[Message], *, model: str, max_tokens: int
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)

        try:
            response = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
            )
            return response.choices[0].message.content
        except self.openai_lib.AuthenticationError as e:
            raise ProviderAuthError(str(e)) from e
        except self.openai_lib.RateLimitError as e:
            raise ProviderRateLimitError(str(e)) from e
        except self.openai_lib.APIConnectionError as e:
            raise ProviderTransportError(str(e)) from e
        except self.openai_lib.APITimeoutError as e:
            raise ProviderTransportError(str(e)) from e
        except self.openai_lib.APIError as e:
            raise ProviderResponseError(str(e)) from e
        except Exception as e:
            if not isinstance(e, ProviderError):
                raise ProviderError(str(e)) from e
            raise
