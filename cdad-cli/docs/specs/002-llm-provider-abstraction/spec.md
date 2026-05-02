# Spec 002: Abstracción de Proveedor LLM/Agente

**Estado**: Draft (actualizado 2026-05-02, post-Etapa 1 Descubrimiento)
**Fecha**: 2026-05-02
**Referencias**: `docs/landscape.md` (sección "Agentes CLI Externos"), `docs/adr/003-context-narrowing-isolation.md`, ADR-004 (pendiente)

## Descripción funcional

`cdad-cli` debe permitir que cada agente (Architect, TestWriter, Implementer, Reviewer, Scribe) opere contra cualquier proveedor LLM o agente compatible, sin acoplamiento al SDK de un vendor específico. El usuario configura, por agente, qué proveedor y modelo usar mediante el formato `provider/model-id`. La implementación actual está acoplada a `anthropic.Anthropic` en `src/cdad/llm/client.py`, lo cual contradice el principio de agnosticismo de la metodología.

Los proveedores soportados en esta spec son dos:

1. **Anthropic** — API REST nativa vía Anthropic SDK (`messages.create`). Mantiene compatibilidad con la implementación actual.
2. **ACP** — Agent Client Protocol (https://agentclientprotocol.com) sobre stdio/JSON-RPC 2.0; permite delegar a agentes externos como Claude Code, Gemini CLI, y Codex. **Implementación propia en Python** (no se usa `acp-sdk` porque requiere Python ≥ 3.11 y cdad-cli soporta ≥ 3.9).

### Finding de Etapa 1 Descubrimiento (corrección crítica)

La spec original asumía que los CLIs tienen un flag nativo `--acp`. La investigación revela que **esto es incorrecto**:

- Los CLIs (`claude`, `gemini`, `codex`) **no tienen** flag `--acp` nativo.
- Zed usa **npm wrappers** (`@zed-industries/claude-agent-acp`, `@google/gemini-cli`, `codex-acp`) que implementan ACP y spawn ean el agente real como subprocess.
- `claude` tiene modo programático (`-p --output-format stream-json`) pero **no es ACP** — es JSON línea a línea simplificado.
- `qwen` no tiene soporte ACP documentado.

**Decisión de diseño**: `ACPProvider` usa `acp-sdk` (Python SDK oficial del protocolo ACP). Esto implica **elevar el mínimo de Python a 3.11** (de 3.9). Se documenta en ADR-005. Los comandos de los agents apuntan directamente al binario/package que implementa ACP por stdio.

**Para los agents disponibles en Zed**, los comandos de spawn eo son:
- **claude-acp**: `npx -y @zed-industries/claude-agent-acp` (o ruta al binario instalado)
- **gemini**: `npx -y @google/gemini-cli` (el package npm ES el agente ACP)
- **codex-acp**: `npx -y codex-acp`

**Qwen**: Sin soporte ACP documentado. Fuera del alcance de esta spec. Si se necesita soporte para Qwen, requerirá investigación de su protocolo nativo (spec futura).

## Contrato (firma e invariantes)

### Tipo `Message`

```python
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str
```

### Excepciones tipadas

```python
class ProviderError(Exception):
    """Base exception for all provider errors."""

class ProviderAuthError(ProviderError):
    """Authentication failure (401/403)."""

class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded (429)."""

class ProviderTransportError(ProviderError):
    """Network, timeout, or subprocess failure."""

class ProviderResponseError(ProviderError):
    """Unexpected response shape from provider."""

class ConfigurationError(ProviderError):
    """Invalid provider/agente configuration (missing key, unknown provider)."""
```

### Protocol `LLMProvider`

```python
class LLMProvider(Protocol):
    name: str  # identificador estable: "anthropic" | "acp"

    def send_message(
        self,
        system_prompt: str,
        history: list[Message],
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        """
        Envía la conversación al proveedor y devuelve el texto plano de la
        respuesta del asistente.

        Postcondiciones:
          - El return es str y no vacío cuando el proveedor responde con éxito.
          - El orden de `history` se preserva al transmitirlo al proveedor.
          - `system_prompt` se transmite como instrucción del sistema.
          - No se filtra ninguna API key ni credencial al return.
          - Errores del proveedor se traducen a excepciones tipadas:
              * ProviderAuthError       (auth failure)
              * ProviderRateLimitError  (429)
              * ProviderTransportError  (red, timeout, subproceso muerto)
              * ProviderResponseError   (shape inesperado)

        Invariantes:
          - send_message es idempotente respecto a `history` (no muta el input).
          - Llamadas con la misma (system_prompt, history, model) son válidas
            consecutivamente; el provider no acumula estado oculto que cambie
            la semántica observable del próximo call.
        """
```

### Refactor de `LLMClient`

```python
class LLMClient:
    def __init__(self, provider: LLMProvider, model: str, *, max_tokens: int = 2048): ...
    def send_message(self, user_message: str, system_prompt: str = "") -> str: ...
```

`LLMClient` mantiene la **API pública existente**. Los `BaseAgent` y subclases **NO se modifican** en su interfaz pública.

### Configuración (`cdad.toml`)

```toml
[providers.anthropic]
api_key_env = "ANTHROPIC_API_KEY"

[providers.acp]
# Comando base para spawn ear agentes ACP.
# Se puede usar npx, ruta directa, o wrapper.
default_command = ["npx", "-y"]

# Preconfiguraciones ACP builtin (aliases de agents conocidos).
# El usuario puede referenciarlos como "acp/claude", "acp/gemini", "acp/codex".
[providers.acp.agents]
claude  = ["@zed-industries/claude-agent-acp"]
gemini  = ["@google/gemini-cli"]
codex   = ["codex-acp"]

[agents]
architect   = "anthropic/claude-opus-4-7"
test_writer = "anthropic/claude-sonnet-4-6"
implementer = "acp/claude"
reviewer    = "anthropic/claude-sonnet-4-6"
scribe      = "anthropic/claude-sonnet-4-6"
```

**Defaults builtin**:

```python
# En config/defaults.py
DEFAULT_AGENT_MODELS = {
    "architect": "anthropic/claude-opus-4-7",
    "test_writer": "anthropic/claude-sonnet-4-6",
    "implementer": "anthropic/claude-sonnet-4-6",
    "reviewer": "anthropic/claude-sonnet-4-6",
    "scribe": "anthropic/claude-sonnet-4-6",
}
```

Resolución (precedencia): CLI flag → env var `CDAD_AGENT_<ROLE>` → `./cdad.toml` → `~/.config/cdad/cdad.toml` → `DEFAULT_AGENT_MODELS`.

**Formato de provider string**: `"<provider_name>/<model_or_agent_id>"`. El proveedor se parsea del string hasta el primer `/`. Si no hay `/`, se asume el default del provider.

### ACP Provider — implementación con `acp-sdk`

`ACPProvider` usa el SDK oficial de Python (`acp-sdk`, requiere Python ≥ 3.11):

1. Instala el SDK: `pip install acp-sdk`
2. Usa el cliente asíncrono del SDK para comunicar con el agente subprocess
3. El comando del agente se configura por alias (ej. `acp/claude` → `npx -y @zed-industries/claude-agent-acp`)
4. El SDK maneja: spawn del subprocess, handshake `initialize`, gestión de sesiones, envío de prompts, recepción de responses via JSON-RPC sobre stdio

El flujo interno es:
- `ACPProvider.__init__(agent_command, env)` — configura el comando de spawn eo y variables de entorno
- `send_message()` — usa el SDK para: initialize → session/new → session/prompt → leer response → session/close
- Las excepciones del SDK se mapean a las tipadas del Protocol (`ProviderTransportError`, etc.)

## Invariantes verificables (property test material)

1. **Conservación de turnos**: para cualquier `history` de longitud N pasado a `LLMClient.send_message`, el provider concreto recibe exactamente esos N turnos en el mismo orden, más el `system_prompt` por canal de sistema.
2. **No-mutación**: `LLMClient.send_message` no modifica el `history` interno cuando el provider lanza excepción.
3. **Aislamiento preservado**: cambiar `agents.<role>` en `cdad.toml` no altera `_AGENT_ACCESS_POLICY` (`src/cdad/project/model.py`); los archivos accesibles por cada rol son independientes del provider.
4. **Resolución determinista**: dado un `cdad.toml` válido, `resolve_provider("architect")` devuelve el mismo `(provider_name, model_id)` en llamadas sucesivas.
5. **Fail-fast de configuración**: `provider/model-id` con `provider` no registrado, o sin la API key requerida en el entorno, lanza `ConfigurationError` antes de ejecutar el primer comando del agente.
6. **Equivalencia funcional**: para ambos providers (Anthropic, ACP), dada la misma `(system_prompt, history)` mockeada, los `BaseAgent` existentes (`ArchitectAgent`, `TestWriterAgent`) producen los mismos artefactos de salida sin cambios en su código.

## Criterios de aceptación

- [ ] `LLMProvider` Protocol definido en `src/cdad/llm/provider.py` con tipos exportados (`Message`, excepciones tipadas).
- [ ] `AnthropicProvider` implementa el Protocol y pasa los tests de conformidad.
- [ ] `ACPProvider` implementa el Protocol: spawn ea subprocess, comunica JSON-RPC por stdio, maneja initialize/session/prompt.
- [ ] Tests de conformidad comunes: una suite de tests parametrizados que prueba las postcondiciones del Protocol contra cualquier implementación registrada.
- [ ] Registry (`src/cdad/llm/registry.py`) permite registrar y resolver providers por nombre.
- [ ] `cdad.toml` se carga desde `cwd`, `~/.config/cdad/cdad.toml` y env (`CDAD_CONFIG`); precedencia documentada y testeada.
- [ ] `_make_llm_client(role)` en `cli/main.py` consulta el registry y NO menciona `Anthropic` por nombre.
- [ ] Suite `pytest` verde con cobertura ≥ 78% (línea base Phase 1).
- [ ] Tests existentes de `BaseAgent`, `ArchitectAgent`, `TestWriterAgent` pasan SIN modificación de los agentes (sólo se ajustan los mocks/fixtures).
- [ ] `pyproject.toml` expone extras opcionales: `cdad[anthropic]`, `cdad[acp]`. La instalación base no requiere SDKs de proveedor innecesarios.
- [ ] Mensajes de error de configuración inválida son accionables: incluyen el nombre del provider/agente afectado y el campo faltante.
- [ ] ADR-004 documenta la decisión de diseño: Protocol + registry, findings de descubrimiento sobre flags `--acp`.
- [ ] ADR-005 documenta la decisión de elevar Python mínimo a 3.11 (requerido por `acp-sdk`).
- [ ] **Qwen queda fuera del scope** — se documenta en ADR-004 como limitación conocida, con plan para spec futura.

## Out of scope

- Streaming de respuestas (SSE/event stream).
- Tool / function calling y multi-turn tool-use loops.
- Batching de requests.
- Caching de respuestas y persistencia de conversaciones.
- Telemetría de costo/tokens por provider.
- UI/TUI para gestionar credenciales.
- Soporte de modelos multimodales (imágenes, audio).
- Migración automática de `cdad.toml` desde formatos previos.
- Fallback automático entre providers ante fallo.
- **Soporte para Qwen** — no tiene ACP documentado. Spec futura si se necesita.
- **OpenAI como provider directo** — se elimina de esta spec porque no es necesario para el uso actual (los agentes se usan vía CLI, no vía API directa).
