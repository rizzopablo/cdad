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
    """Client stub that captures session_update text from the agent.

    Implementa los métodos del protocolo Client que el agente puede llamar.
    Los métodos de filesystem retornan error ya que CDAD no expone filesystem al agente.
    """

    def __init__(self):
        self.text_parts: list[str] = []
        self._done = asyncio.Event()

    def on_connect(self, conn):
        pass

    async def session_update(self, session_id: str, update, **kwargs):
        # Extraer texto según el tipo de update
        # AgentMessageChunk tiene content.text (TextContentBlock)
        # AgentThoughtChunk tiene text directamente
        text = None

        if hasattr(update, "content"):
            # AgentMessageChunk: update.content es un ContentBlock (ej: TextContentBlock)
            content = update.content
            if hasattr(content, "text"):
                text = content.text
        elif hasattr(update, "text"):
            # AgentThoughtChunk: tiene text directamente
            text = update.text

        if text:
            self.text_parts.append(text)
            # Señalar que llegó contenido
            self._done.set()

    # Métodos del filesystem - CDAD no expone filesystem al agente
    async def read_text_file(self, path: str, session_id: str, **kwargs):
        """El agente solicita leer un archivo. CDAD no soporta esta operación."""
        raise NotImplementedError("Filesystem access not supported in CDAD")

    async def write_text_file(self, content: str, path: str, session_id: str, **kwargs):
        """El agente solicita escribir un archivo. CDAD no soporta esta operación."""
        raise NotImplementedError("Filesystem access not supported in CDAD")

    # Métodos de terminal - CDAD no expone terminal al agente
    async def create_terminal(self, command: str, session_id: str, **kwargs):
        """El agente solicita crear un terminal. CDAD no soporta esta operación."""
        raise NotImplementedError("Terminal access not supported in CDAD")

    async def kill_terminal(self, session_id: str, terminal_id: str, **kwargs):
        """El agente solicita matar un terminal. CDAD no soporta esta operación."""
        raise NotImplementedError("Terminal access not supported in CDAD")

    async def release_terminal(self, session_id: str, terminal_id: str, **kwargs):
        """El agente solicita liberar un terminal. CDAD no soporta esta operación."""
        raise NotImplementedError("Terminal access not supported in CDAD")

    async def terminal_output(self, session_id: str, terminal_id: str, **kwargs):
        """El agente solicita output de terminal. CDAD no soporta esta operación."""
        raise NotImplementedError("Terminal access not supported in CDAD")

    async def wait_for_terminal_exit(self, session_id: str, terminal_id: str, **kwargs):
        """El agente espera que un terminal termine. CDAD no soporta esta operación."""
        raise NotImplementedError("Terminal access not supported in CDAD")

    # Métodos de permisos - CDAD no implementa permissions interactivas
    async def request_permission(self, options, session_id: str, tool_call, **kwargs):
        """El agente solicita permiso para una operación. CDAD no soporta esta operación."""
        raise NotImplementedError("Interactive permissions not supported in CDAD")

    # Métodos de extensión - no soportados
    async def ext_method(self, method: str, params: dict, **kwargs):
        """Método de extensión no soportado."""
        raise NotImplementedError(f"Extension method '{method}' not supported")

    async def ext_notification(self, method: str, params: dict, **kwargs):
        """Notificación de extensión - ignorada silenciosamente."""
        pass


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

                # Esperar respuesta con timeout de 120s (los agentes pueden tardar)
                try:
                    await asyncio.wait_for(collector._done.wait(), timeout=120.0)
                except asyncio.TimeoutError:
                    raise ProviderResponseError(
                        f"ACP provider timed out after 120s. Command: {' '.join(self.command)}"
                    )

                # The agent sends response text via session_update callbacks,
                # which the _CollectingClient accumulates in collector.text_parts
                content = "".join(collector.text_parts)
                if not content.strip():
                    raise ProviderResponseError("ACP provider returned empty or invalid response")
                return content
            finally:
                try:
                    await conn.close_session(session_id)
                except Exception:
                    # Some ACP agents (e.g. qwen) don't support the session/close method.
                    # Swallow the error so it doesn't mask the actual response.
                    pass
