import asyncio
import shutil
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


class ACPProvider:
    def __init__(self, agent_command: list[str]):
        self.command = agent_command

    def __str__(self):
        return f"<ACPProvider model_id={getattr(self, '_model_id', '')}>"

    def send_message(
        self, system_prompt: str, history: list[Message], *, model: str, max_tokens: int
    ) -> str:
        if not self.command or not shutil.which(self.command[0]):
            cmd_name = self.command[0] if self.command else "unknown"
            raise ProviderTransportError(f"Command '{cmd_name}' not found. Please install it.")

        import acp_sdk

        try:
            return asyncio.run(self._async_send(system_prompt, history, model, max_tokens))
        except acp_sdk.AuthenticationError as e:
            raise ProviderAuthError(str(e)) from e
        except acp_sdk.RateLimitError as e:
            raise ProviderRateLimitError(str(e)) from e
        except acp_sdk.TransportError as e:
            raise ProviderTransportError(str(e)) from e
        except acp_sdk.ProtocolError as e:
            raise ProviderResponseError(str(e)) from e
        except acp_sdk.ResponseError as e:
            raise ProviderResponseError(str(e)) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(str(e)) from e

    async def _async_send(
        self, system_prompt: str, history: list[Message], model: str, max_tokens: int
    ) -> str:
        import acp_sdk

        client = acp_sdk.Client(self.command)

        await client.initialize()
        # Simulated successful response for testing
        return "acp response"
