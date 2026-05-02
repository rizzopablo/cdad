# Landscape — CDAD-CLI

## Conocimiento del Terreno

### API Anthropic

- **SDK**: `anthropic>=0.40.0`
- **Modelo por defecto**: `claude-opus-4-7` (architect), `claude-sonnet-4-6` (otros agentes)
- **Autenticación**: variable de entorno `ANTHROPIC_API_KEY`
- **Endpoint**: Messages API (`client.messages.create()`)
- **Parámetros clave**: `max_tokens=2048`, `system` prompt por agente
- **Historial**: `LLMClient` mantiene `history: List[Dict]` por sesión (no persistente entre invocaciones CLI)
- **Rate limits**: no implementados aún; si se exceden, el comando falla con excepción no capturada

**Lecciones aprendidas**:
- Los system prompts deben ser específicos por rol para evitar que el LLM "invente" comportamientos fuera del agente
- El historial de conversación es volátil (se pierde al terminar el proceso CLI) — suficiente para retry loops dentro de un comando, pero no para continuidad entre sesiones

### pytest

- **Versión**: 7.4.0
- **Uso en CDAD**: TestValidator ejecuta `python -m pytest tests/ -v --tb=no`
- **Detección RED/GREEN**: cuenta strings ` PASSED` y ` FAILED` en el output
- **Coverage**: pytest-cov 4.1.0, 78% en Phase 1 MVP
- **Timeout**: 30 segundos por ejecución de tests

**Lecciones aprendidas**:
- Parsear output de pytest con regex es frágil pero funcional para MVP
- El código de retorno de pytest (0 = todos pasan) es más fiable que parsear output
- `--tb=no` acelera la ejecución pero elimina información de debugging

### Framework Detection

| Framework | Archivos manifest | Orden en registry |
|---|---|---|
| Odoo | `__manifest__.py`, `__openerp__.py` | 1º (más específico) |
| Django | `manage.py` | 2º |
| Generic | `setup.py`, `pyproject.toml` | 3º (fallback) |

**Principio**: los frameworks más específicos se evalúan primero. Si un proyecto tiene `__manifest__.py` Y `manage.py`, se detecta como Odoo (primero en el registry).

### Typer

- **Versión**: 0.9.0
- **Uso**: CLI framework principal
- **Ventajas**: type hints → validación automática, `--help` generado, subcomandos naturales
- **Limitación**: `click<8.2` forzado como dependencia para compatibilidad

### python-frontmatter

- **Versión**: 1.0.0
- **Uso**: parsea frontmatter YAML en archivos markdown (specs)
- **Permite**: metadata en specs (título, autor, fecha) separada del contenido

### Toml

- **Versión**: 0.10.2
- **Uso**: lee `pyproject.toml` para nombre del proyecto
- **Alternativa**: Python 3.11+ tiene `tomllib` nativo, pero se soporta 3.9

### Markdown-it-py

- **Versión**: 3.0.0
- **Uso**: parseo de markdown para extracción de secciones en specs
- **Nota**: SpecValidator actualmente usa regex directamente, no markdown-it-py

---

## Agentes CLI Externos (ACP y modos programáticos)

**Fecha de investigación**: 2026-05-02

### ACP (Agent Client Protocol)

- **Qué es**: Protocolo estandarizado (JSON-RPC 2.0 sobre stdio) para comunicación entre editores/IDEs y agentes de IA autónomos. Similar a LSP pero para agentes.
- **Transporte local**: El editor spawn ea el agente como subprocess; comunicación vía stdin/stdout con JSON-RPC.
- **Transporte remoto**: HTTP/WebSocket (en desarrollo).
- **Repositorio**: https://github.com/zed-industries/agent-client-protocol
- **SDKs oficiales**: TypeScript (`@agentclientprotocol/sdk`), Rust, Python (`acp-sdk`), Kotlin, Java.
- **Python SDK**: `pip install acp-sdk` — **requiere Python ≥ 3.11** (cdad-cli soporta ≥ 3.9, esto es un constraint importante).
- **Especificación completa**: https://agentclientprotocol.com/get-started

#### Métodos JSON-RPC clave

| Método | Dirección | Propósito |
|---|---|---|
| `initialize` | Cliente → Agente | Handshake: `clientInfo`, `clientCapabilities`, `protocolVersion` |
| `authenticate` | Cliente → Agente | Autenticación si el agente lo requiere |
| `session/new` | Cliente → Agente | Crea sesión, retorna `sessionId`. Requiere `cwd` y opcionalmente `mcpServers` |
| `session/prompt` | Cliente → Agente | Envía `ContentBlock[]` al agente. Retorna `PromptResponse` con `stopReason` |
| `session/update` | Agente → Cliente | Notificación streaming: chunks de texto, tool calls, estado |
| `session/list` | Cliente → Agente | Lista sesiones existentes |
| `session/resume` | Cliente → Agente | Reanuda sesión sin retransmitir historial |
| `session/close` | Cliente → Agente | Cierra sesión y libera recursos |
| `session/cancel` | Cliente → Agente | Notificación para abortar operación en curso |
| `session/request_permission` | Agente → Cliente | El agente solicita autorización para operación sensible |
| `fs/read_text_file` | Agente → Cliente | El agente lee archivo del filesystem |
| `fs/write_text_file` | Agente → Cliente | El agente escribe archivo |
| `terminal/create` | Agente → Cliente | El agente ejecuta comando en terminal |

#### ContentBlock types

- `text`: Texto plano o Markdown
- `image`/`audio`: Base64 con `mimeType`
- `resource_link`: URI a recurso externo
- `resource`: Contenido embebido (`EmbeddedResource`)

### Agentes soportados por Zed (referencia de integración)

Zed es el editor de referencia que implementa ACP. Gestiona los agentes como **subprocesses** vía npm wrappers:

| Agente | Package npm | Comando base | Autenticación |
|---|---|---|---|
| `claude-acp` | `@zed-industries/claude-agent-acp` | Incluido vendored | `/login` en thread, o `ANTHROPIC_API_KEY` nativa |
| `gemini` | `@google/gemini-cli` | `@google/gemini-cli` | `GEMINI_API_KEY` o Login Google |
| `codex-acp` | `codex-acp` | `codex-acp` | ChatGPT login, `CODEX_API_KEY` o `OPENAI_API_KEY` |

**Nota crítica**: Estos son **npm wrappers**, no flags nativas de los CLIs. El wrapper implementa ACP y delega al agente real. Para un agente custom, Zed usa:
```json
{ "command": "node", "args": ["~/path/to/agent", "--acp"], "env": {} }
```

### CLIs individuales — modos programáticos

#### Claude CLI (`claude`)
- **Modo programático**: `claude -p --output-format stream-json --input-format stream-json --replay-user-messages`
- **NO tiene flag `--acp` nativo** — la comunicación es JSON línea a línea, no JSON-RPC completo.
- **Autenticación**: `ANTHROPIC_API_KEY` o login interactivo (`/login`)
- **Modelos**: `--model` flag (ej. `claude -m claude-sonnet-4-6`)
- **System prompt**: soportado vía API

#### Gemini CLI (`gemini`)
- **Modo programático**: `gemini -p "prompt" --output-format json`
- **Modo streaming**: `gemini -p "prompt" --output-format stream-json`
- **Modelos**: `gemini -m gemini-2.5-flash`
- **NO implementa ACP directamente** — el package npm `@google/gemini-cli` es el que actúa como ACP agent.
- **Autenticación**: `GEMINI_API_KEY` o `GOOGLE_AI_API_KEY`

#### Codex CLI (`codex`)
- **Instalación**: `npm install -g @openai/codex` o `brew install --cask codex`
- **Modo programático**: vía `codex-acp` npm wrapper para ACP
- **Autenticación**: ChatGPT login, `CODEX_API_KEY`, o `OPENAI_API_KEY`

#### Qwen CLI (`qwen`)
- **Estado ACP**: No aparece en el registry de Zed ni en documentación ACP oficial.
- **Modo programático**: Pendiente de investigar (no hay documentación pública disponible en las fuentes consultadas).
- **Probable**: requiere verificar si `qwen` soporta `--output-format json` o similar.

### Implicaciones para Spec 002

1. **La suposición original de `--acp` flag nativo es incorrecta.** Los CLIs no tienen un flag `--acp` universal. Zed usa npm wrappers para implementar ACP.
2. **Opciones viables para cdad-cli:**
   - **Opción A**: Usar los npm wrappers (`@zed-industries/claude-agent-acp`, `@google/gemini-cli`, `codex-acp`) como subprocesses que hablan ACP por stdio. Requiere Node.js instalado.
   - **Opción B**: Implementar el protocolo ACP en Python puro (spawn subprocess + JSON-RPC manual por stdio). Más complejo pero sin dependencia de Node.js.
   - **Opción C**: Usar los modos programáticos nativos de cada CLI (no-ACP, comunicación simplificada: enviar prompt por stdin, leer respuesta de stdout). Menos potente pero más simple.
   - **Opción D (híbrida)**: Mantener `AnthropicProvider` directo (SDK), agregar `ACPProvider` para agentes ACP-compliant (vía npm wrappers o Python impl), y agregar `CLISubprocessProvider` para modos programáticos nativos.
3. **Python SDK constraint**: `acp-sdk` requiere Python ≥ 3.11. cdad-cli soporta ≥ 3.9 actualmente. **Decisión (2026-05-02): elevar a Python ≥ 3.11** y usar `acp-sdk` oficial en lugar de implementación manual. Se documenta en ADR-005.
4. **Qwen**: No tiene soporte ACP documentado. Fuera del scope de Spec 002. Si se necesita soporte para Qwen, requerirá investigación de su protocolo nativo (spec futura).
