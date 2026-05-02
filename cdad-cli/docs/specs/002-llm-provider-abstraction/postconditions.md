# Postconditions 002: Abstracción de Proveedor LLM/Agente

**Versión**: 2 (actualizada 2026-05-02, post-Etapa 1 Descubrimiento)
**Reconciliada con**: `spec.md` (updated 2026-05-02)
**Cambios respecto a v1**: Eliminadas PC sobre OpenAI (fuera de scope); eliminados aliases qwen/opencode (sin ACP documentado); corregidos comandos ACP a npx wrappers; corregidos defaults a Anthropic.

Material directo para `TestWriterAgent`. Cada postcondición se traduce a uno o más tests. La numeración se reutiliza como `PC-002-<n>` en los nombres de tests. Las PC eliminadas se marcan como ~~strikethrough~~ para preservar referencia histórica.

## PC-002-1 — Conservación de turnos

Para todo `history: list[Message]` de longitud N pasado a `LLMClient.send_message(user_message, system_prompt)`:

- el `LLMProvider` subyacente recibe exactamente `N+1` turnos (los N previos más el `user_message`),
- en el mismo orden,
- con los mismos `role` y `content` que el input.

**Test**: parametrizado sobre **ambos** providers (Anthropic, ACP) con `history` de longitudes 0, 1, 5; capturar el call al mock e inspeccionar argumentos.

## PC-002-2 — System prompt por canal de sistema

Para cada provider, `system_prompt` se transmite a través del canal de sistema nativo:

- **Anthropic**: argumento `system=` de `messages.create`.
- **ACP**: se transmite en el payload de `session/prompt` como parte del prompt (el agente ACP recibe el system prompt en el contexto de la sesión).

`system_prompt` NO aparece duplicado como turno `user`/`assistant` en `messages`/`history`.

**Test**: por provider, llamar con `system_prompt="X"` y verificar que aparece en el canal correcto y NO en la lista de mensajes regulares.

## PC-002-3 — Inmutabilidad del input

`LLMClient.send_message` no muta `self.history` cuando el provider lanza una excepción:

```python
client = LLMClient(provider=failing_provider, model="m")
client.history = [{"role": "user", "content": "a"}]
snapshot = list(client.history)
with pytest.raises(ProviderError):
    client.send_message("b")
assert client.history == snapshot
```

## PC-002-4 — Mapeo de excepciones

Cada provider mapea errores nativos a la jerarquía `ProviderError`:

| Causa | Excepción esperada |
|---|---|
| Credencial inválida (HTTP 401/403, ACP `auth_required`/`unauthenticated`) | `ProviderAuthError` |
| Rate limit (HTTP 429, ACP rate-limited) | `ProviderRateLimitError` |
| Red, timeout, subproceso muerto | `ProviderTransportError` |
| Respuesta con shape inesperado / JSON-RPC error | `ProviderResponseError` |
| Config inválida (provider no registrado, env var faltante) | `ConfigurationError` |

**Test**: por provider, simular cada condición y `pytest.raises` la subclase específica (no sólo `ProviderError`).

## PC-002-5 — Aislamiento preservado

Para todo `role` y todo `provider/model` válido:

```python
agent = ArchitectAgent(project, llm_client=LLMClient(provider, model))
files_a = set(agent.get_accessible_files())
agent2 = ArchitectAgent(project, llm_client=LLMClient(other_provider, other_model))
files_b = set(agent2.get_accessible_files())
assert files_a == files_b
```

Cambiar el provider no altera `_AGENT_ACCESS_POLICY` ni los archivos accesibles.

## PC-002-6 — Determinismo de resolución

Dado un `cdad.toml` y un entorno fijos, `registry.resolve("architect")` devuelve el mismo `(provider_name, model_id)` en N llamadas consecutivas.

**Test**: invocar 100 veces y assert sobre igualdad estructural.

## PC-002-7 — Fail-fast de configuración

Construir la configuración del agente lanza `ConfigurationError` cuando:

- `agents.<role>` referencia un `provider` no registrado en el registry,
- el provider requiere `api_key_env` y la env var no está definida o está vacía,
- el formato del valor no coincide `^[a-z][a-z0-9_-]*\/.+$`,
- una clave en `[agents]` no es uno de los roles conocidos (`architect|test_writer|implementer|reviewer|scribe`).

El error incluye en el mensaje: nombre del rol, valor ofensivo y campo/env var faltante.

**Test**: tabla parametrizada con un caso por condición; verificar tanto la clase como un fragmento del mensaje.

## PC-002-8 — Precedencia de configuración

Orden estricto (más específico gana):

1. `CDAD_AGENT_<ROLE>` env var
2. `./cdad.toml` en cwd
3. `~/.config/cdad/cdad.toml`
4. `DEFAULT_AGENT_MODELS` (defaults del código)

**Test**: cuatro escenarios donde sólo una capa define el valor; el quinto donde todas lo definen y se verifica la ganadora.

## PC-002-9 — API keys nunca persisten en archivos de proyecto

Inspección estática: el loader rechaza cualquier clave `api_key` (sin `_env`) en `[providers.*]` con `ConfigurationError`. Sólo `api_key_env` está permitido.

**Test**: cargar un toml con `api_key = "sk-..."` literal y verificar `ConfigurationError` con mensaje sobre uso de `api_key_env`.

## PC-002-10 — Equivalencia funcional ante el agente

Para **ambos** providers, dado un mismo `(system_prompt, history)` y un mismo string mockeado de respuesta, `ArchitectAgent.draft_spec(...)` y `TestWriterAgent.write_tests(...)` producen la misma salida observable (mismo string devuelto, mismas escrituras a disco).

**Test**: parametrizado sobre providers con respuesta mockeada constante; comparar artefactos de salida.

## PC-002-11 — Lazy import de SDKs

Importar `cdad.llm.registry` o `cdad.cli.main` NO importa `anthropic` ni `acp_sdk` ni lanza ningún subproceso. Los SDKs se importan sólo al construir el provider correspondiente.

**Test**: usar `sys.modules` antes/después de importar `cdad.cli.main`; assert que `anthropic` no esté presente hasta resolver explícitamente un provider Anthropic.

## PC-002-12 — Registro extensible

```python
from cdad.llm import registry
from cdad.llm.provider import LLMProvider

class FakeProvider:
    name = "fake"
    def send_message(self, system_prompt, history, *, model, max_tokens) -> str:
        return "ok"

registry.register("fake", lambda cfg: FakeProvider())
assert registry.resolve("fake", {}).send_message("", [], model="x", max_tokens=1) == "ok"
```

**Test**: garantiza que registrar un provider de terceros funciona sin tocar código del CLI.

## PC-002-13 — Preconfiguraciones ACP builtin

Para cada alias builtin ACP (`claude`, `gemini`, `codex`):

- `registry.resolve("acp/<alias>", {})` devuelve un `ACPProvider` configurado con el comando por defecto.
- El comando por defecto usa **npx wrappers** de Zed:

| Alias | Comando builtin |
|---|---|
| `acp/claude` | `["npx", "-y", "@zed-industries/claude-agent-acp"]` |
| `acp/gemini` | `["npx", "-y", "@google/gemini-cli"]` |
| `acp/codex` | `["npx", "-y", "codex-acp"]` |

- El usuario puede sobrescribir con `cdad.toml`:
  ```toml
  [providers.acp.claude]
  command = ["/custom/path/to/claude-agent-acp"]
  ```
  y `registry.resolve("acp/claude", custom_config)` usa el custom en lugar del builtin.
- Si el comando builtin no existe en `PATH` (npx no disponible), `ACPProvider` lanza `ProviderTransportError` con sugerencia clara del paquete a instalar.

**Test**: tabla parametrizada con los tres aliases; verificar que sin `cdad.toml` se usan defaults, y que `cdad.toml` sobrescribe. Test de fallback: simular que el comando no existe y capturar el mensaje de error de ayuda.

## ~~PC-002-14 — Default `acp/claude` sin configuración~~ ~~ELIMINADA~~

**Eliminada** — spec.md actualizada define defaults como `anthropic/claude-opus-4-7` y `anthropic/claude-sonnet-4-6`, no `acp/claude`.

## PC-002-14 — Defaults de agentes sin configuración

Sin `cdad.toml`, sin env vars, sin flags CLI, los defaults son:

| Rol | Default |
|---|---|
| `architect` | `anthropic/claude-opus-4-7` |
| `test_writer` | `anthropic/claude-sonnet-4-6` |
| `implementer` | `anthropic/claude-sonnet-4-6` |
| `reviewer` | `anthropic/claude-sonnet-4-6` |
| `scribe` | `anthropic/claude-sonnet-4-6` |

**Test**: sin config externa, llamar `resolve("architect")` y verificar `("anthropic", "claude-opus-4-7")`. Ídem para cada rol.

## PC-002-15 — Precedencia: env var sobrescribe default

Dado `DEFAULT_AGENT_MODELS = {"architect": "anthropic/claude-opus-4-7"}` y `CDAD_AGENT_ARCHITECT=acp/claude`:

- `resolve("architect")` devuelve `"acp/claude"`, no el default.

**Test**: setear env var, llamar resolver, verificar que gana sobre default.
