import asyncio
import shutil

from cdad.llm.provider import (
    Message,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderTransportError,
)


class _CollectingClient:
    """Client stub that captures session_update text from the agent."""

    def __init__(self):
        self.text_parts: list[str] = []

    def on_connect(self, conn):
        pass

    async def session_update(self, session_id: str, update, **kwargs):
        # AgentMessageChunk / AgentThoughtChunk have a .text attribute
        text = getattr(update, "text", None)
        if text:
            self.text_parts.append(text)


class ACPProvider:
    def __init__(self, agent_command: list[str]):
        self.command = agent_command
        self._model_id: str = ""

    @property
    def name(self) -> str:
        if self._model_id:
            return f"acp/{self._model_id}"
        return "acp"

    def __str__(self):
        return f"<ACPProvider model_id={getattr(self, '_model_id', '')}>"

    def send_message(
        self, system_prompt: str, history: list[Message], *, model: str, max_tokens: int
    ) -> str:
        if not self.command or not shutil.which(self.command[0]):
            cmd_name = self.command[0] if self.command else "unknown"
            raise ProviderTransportError(f"Command '{cmd_name}' not found. Please install it.")

        import acp

        try:
            return asyncio.run(self._async_send(system_prompt, history, model, max_tokens))
        except acp.RequestError as e:
            # RequestError es la única excepción del SDK acp (agent-client-protocol).
            # Clasificación heurística basada en el contenido del mensaje.
            msg = str(e).lower()
            if "auth" in msg or "permission" in msg or "401" in msg or "403" in msg:
                raise ProviderAuthError(str(e)) from e
            elif "rate" in msg or "429" in msg or "limit" in msg:
                raise ProviderRateLimitError(str(e)) from e
            elif "timeout" in msg or "connection" in msg or "network" in msg:
                raise ProviderTransportError(str(e)) from e
            else:
                raise ProviderResponseError(str(e)) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(str(e)) from e

    async def _async_send(
        self, system_prompt: str, history: list[Message], model: str, max_tokens: int
    ) -> str:
        import acp

        collector = _CollectingClient()

        async with acp.spawn_agent_process(
            collector,
            self.command[0],
            *self.command[1:],
        ) as (conn, _process):
            # Initialize connection
            await conn.initialize(protocol_version=1)

            # Create new session
            session_resp = await conn.new_session(cwd=".")
            session_id = session_resp.session_id

            try:
                # Build prompt content blocks
                prompt_blocks = []
                if system_prompt:
                    # System prompt goes in as a text block at the beginning
                    prompt_blocks.append(acp.text_block(system_prompt))
                for msg in history:
                    prompt_blocks.append(acp.text_block(msg["content"]))

                # Send prompt
                await conn.prompt(
                    prompt=prompt_blocks,
                    session_id=session_id,
                )

                # The agent sends response text via session_update callbacks,
                # which the _CollectingClient accumulates in collector.text_parts
                content = "".join(collector.text_parts)
                if not content:
                    raise ProviderResponseError("ACP provider returned empty or invalid response")
                return content
            finally:
                await conn.close_session(session_id)
