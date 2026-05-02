# Design 002: Abstracción de Proveedor LLM/Agente

Acompaña a `spec.md`. Detalla decisiones técnicas y mapeo a archivos. No es contractual; la spec sí lo es.

## 1. Mapa de cambios

```
cdad-cli/
├── cdad.toml.example                          [NUEVO] config de referencia
├── pyproject.toml                             [MOD]   extras [anthropic|openai|acp]
├── src/cdad/
│   ├── config/
│   │   ├── defaults.py                        [MOD]   sin model IDs hardcoded
│   │   └── loader.py                          [NUEVO] resolución de cdad.toml
│   ├── llm/
│   │   ├── client.py                          [MOD]   delega en LLMProvider
│   │   ├── provider.py                        [NUEVO] Protocol + Message + excepciones
│   │   ├── registry.py                        [NUEVO] register/resolve
│   │   └── providers/
│   │       ├── __init__.py                    [NUEVO]
│   │       ├── anthropic_provider.py          [NUEVO] extracto del client.py actual
│   │       ├── openai_provider.py             [NUEVO]
│   │       └── acp_provider.py                [NUEVO]
│   └── cli/main.py                            [MOD]   _make_llm_client usa registry
└── tests/
    ├── test_llm_client.py                     [MOD]   mockea LLMProvider, no Anthropic
    ├── test_provider_anthropic.py             [NUEVO]
    ├── test_provider_openai.py                [NUEVO]
    ├── test_provider_acp.py                   [NUEVO]
    ├── test_provider_conformance.py           [NUEVO] suite común para los 3
    └── test_config_loader.py                  [NUEVO]
```

## 2. `LLMProvider` Protocol

Decisión: usar `typing.Protocol` (estructural) en vez de `ABC` (nominal).

- Compatible con duck typing existente en tests (`MagicMock(spec=...)`).
- Permite que un usuario añada un provider externo sin importar nuestra base class.
- Coherente con el patrón ya usado por `BaseAgent` (que es ABC, pero `LLMClient` se inyecta vía duck typing en los tests).

Excepciones (`src/cdad/llm/provider.py`):

```python
class ProviderError(Exception): ...
class ProviderAuthError(ProviderError): ...
class ProviderRateLimitError(ProviderError): ...
class ProviderTransportError(ProviderError): ...
class ProviderResponseError(ProviderError): ...
class ConfigurationError(Exception): ...
```

## 3. Mapeo por provider

### 3.1 AnthropicProvider

Extracción mecánica de `client.py` actual. Mapeo:

| Concepto interno | API Anthropic |
|---|---|
| `system_prompt` | parámetro `system=` |
| `history` | parámetro `messages=` (ya en formato `{role, content}`) |
| respuesta | `response.content[0].text` |

Errores: capturar `anthropic.AuthenticationError` → `ProviderAuthError`; `RateLimitError` → `ProviderRateLimitError`; `APIConnectionError` → `ProviderTransportError`; `APIStatusError` con shape inesperado → `ProviderResponseError`.

### 3.2 OpenAIProvider

```python
client = OpenAI(api_key=..., base_url=...)
resp = client.chat.completions.create(
    model=model,
    max_tokens=max_tokens,
    messages=[{"role": "system", "content": system_prompt}, *history],
)
return resp.choices[0].message.content
```

`base_url` opcional habilita Azure OpenAI, OpenRouter, Ollama, vLLM, LM Studio, etc. sin código adicional. Documentado en `cdad.toml.example`.

### 3.3 ACPProvider

ACP (https://agentclientprotocol.com) es un protocolo JSON-RPC sobre stdio donde el CLI actúa como **cliente** y un agente externo (Claude Code, Gemini CLI, agentes Zed) actúa como **servidor**.

Estrategia:

1. **Inicialización perezosa**: el subproceso se lanza al primer `send_message`. Comando configurable: `command = ["claude", "--acp"]`.
2. **Sesión persistente**: tras `initialize`, se llama `session/new` una vez. El `session_id` queda guardado en `self._session_id`.
3. **Por turno**: se envía `session/prompt` con el último mensaje de usuario. El system prompt se inyecta:
   - Si la implementación ACP soporta `meta.system`, se usa esa vía.
   - Si no, se prepone como primer turno de usuario en la sesión inicial (degradación documentada).
4. **Recolección**: stream de notificaciones `session/update` se acumula en buffer hasta `stop_reason`. Texto plano concatenado se devuelve.
5. **Cierre**: el subproceso se cierra al destruir el `LLMClient` (registrado vía `atexit` o context manager opcional).

Limitación conocida: ACP es naturalmente streaming/multi-turn con tool-use. Esta primera iteración expone una vista *blocking & text-only* sobre el protocolo. Streaming/tool-use → spec futura.

Errores: subproceso muerto → `ProviderTransportError`; respuesta JSON-RPC con `error` → `ProviderResponseError`; método inicial fallido → `ProviderAuthError` (incluye trust/permissions).

## 4. Registry y resolución

`src/cdad/llm/registry.py`:

```python
ProviderFactory = Callable[[ProviderConfig], LLMProvider]

_REGISTRY: dict[str, ProviderFactory] = {}

def register(name: str, factory: ProviderFactory) -> None: ...
def resolve(name: str, config: ProviderConfig) -> LLMProvider: ...
def list_builtin_acp_agents() -> dict[str, str]: ...  # devuelve {alias: comando}
```

Registro al import en `providers/__init__.py`. Importaciones de SDK son lazy dentro de cada factory (los extras no instalados no rompen el import).

### Preconfiguraciones ACP builtin

En `providers/__init__.py`, se registran cuatro aliases ACP con comandos por defecto:

```python
# Preconfiguraciones ACP builtin
_BUILTIN_ACP_AGENTS = {
    "claude": ["claude", "--acp"],      # DEFAULT para todos los agentes
    "gemini": ["gemini-cli", "--acp"],
    "qwen": ["qwen-agent", "--acp"],
    "opencode": ["opencode", "--acp"],
}

for alias, cmd in _BUILTIN_ACP_AGENTS.items():
    factory = lambda cfg, cmd=cmd: ACPProvider(cmd, config=cfg)
    registry.register(f"acp/{alias}", factory)
```

En `config/defaults.py`:
```python
DEFAULT_AGENT_MODELS = {
    "architect": "acp/claude",
    "test_writer": "acp/claude",
    "implementer": "acp/claude",
    "reviewer": "acp/claude",
    "scribe": "acp/claude",
}
```

El usuario puede:
1. Usar directamente: `agents.implementer = "acp/claude"` (sin toml, sin env var custom).
2. Sobrescribir en `cdad.toml`:
   ```toml
   [providers.acp.claude]
   command = ["/custom/path/claude", "--acp", "--model=opus"]
   ```
   El loader sobrescribe la preconfiguration con la custom.
3. Registrar un alias nuevo:
   ```toml
   [providers.acp.my-agent]
   command = ["my-agent", "--acp"]
   ```

Resolución desde `cli/main.py:_make_llm_client(role)`:

```python
spec = config.agents[role]                       # "acp/claude"
provider_name, model = spec.split("/", 1)       # provider_name="acp/claude", model=(unused)
provider_cfg = config.providers.get(provider_name)  # None si no en toml; registry.resolve lo maneja
provider = registry.resolve(provider_name, provider_cfg or {})
return LLMClient(provider, model=model or alias)  # model usado para tracing/logs
```

**Ventaja de builtin ACP**: el usuario no necesita escribir `cdad.toml` para usar `acp/claude`. El registro global lo hace transparente. Los comandos pueden ser sobrescritos si el CLI está en ruta no estándar.

## 5. Loader de configuración

Precedencia (la más específica gana):

1. CLI flag (`--provider anthropic/claude-opus-4-7`, futuro).
2. Env var `CDAD_AGENT_<ROLE>` (e.g. `CDAD_AGENT_ARCHITECT=openai/gpt-4o`).
3. `./cdad.toml` (cwd).
4. `~/.config/cdad/cdad.toml`.
5. `defaults.py` → `DEFAULT_AGENT_MODELS` (todos los roles → `acp/claude`).

API keys SIEMPRE vienen de env vars; `cdad.toml` sólo declara el *nombre* de la env var (`api_key_env`). Nunca se persisten secretos en archivos de proyecto.

Validación al arranque: el loader construye un `ResolvedConfig` y verifica que cada provider referenciado en `[agents]` esté registrado y tenga sus credenciales. Falla con `ConfigurationError` accionable antes de instanciar agentes.

## 6. Tests

### 6.1 Suite de conformidad (`test_provider_conformance.py`)

Parametrizada sobre los tres providers con SDK/subproceso mockeado. Verifica las invariantes de la spec:

- preserva orden de `history`,
- system prompt llega por canal correcto,
- excepciones específicas se mapean a `ProviderError` subclasses,
- no muta el `history` de entrada,
- return es `str` no vacío.

### 6.2 Tests por provider

- `test_provider_anthropic.py`: refactor de `test_llm_client.py` actual; mocks a nivel `anthropic.Anthropic`.
- `test_provider_openai.py`: `@patch("cdad.llm.providers.openai_provider.OpenAI")`.
- `test_provider_acp.py`: mock de `subprocess.Popen` y stdin/stdout JSON-RPC; cubre handshake, prompt, error de subproceso muerto.

### 6.3 Tests de loader

`test_config_loader.py`: precedencia, env var, archivo ausente, provider desconocido, API key faltante.

## 7. Migración

Sin breaking changes para los agentes. `LLMClient` mantiene firma. Pasos:

1. **PR 1** — Introducir `LLMProvider`, `AnthropicProvider` y registry. `LLMClient` delega en `AnthropicProvider` cuando se construye con un `api_key` (compatibilidad). Tests existentes pasan.
2. **PR 2** — Loader de configuración + `cdad.toml`. `_make_llm_client` consulta loader. `defaults.py` queda agnóstico.
3. **PR 3** — `OpenAIProvider` + tests + extras `pyproject.toml`.
4. **PR 4** — `ACPProvider` + tests + extras.
5. **PR 5** — Eliminar el shim de compatibilidad de `LLMClient(api_key=...)`. Documentar en CHANGELOG.

## 8. Decisiones rechazadas

- **LiteLLM**: librería que ya unifica ~100 providers. Pro: cero código. Contra: dependencia pesada, opacidad de errores, no cubre ACP (es un protocolo, no una API), no encaja con el principio CDAD de "infraestructura mínima auditable".
- **CrewAI/LangChain adapters**: orientados a orquestación con tool-use; sobre-ingeniería para nuestra superficie de un solo `send_message` text-in/text-out.
- **ABC en lugar de Protocol**: requeriría que providers externos hereden de nuestra clase, contraria al espíritu pluggable.
- **Configuración 100% por env vars**: insuficiente para mapear `agents.<role> → provider/model` legible y diffeable.
