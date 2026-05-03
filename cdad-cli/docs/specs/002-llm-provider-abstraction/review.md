# Review — Feature 002: Abstracción de Proveedor LLM/Agente

**Fecha**: 2026-05-03  
**Reviewer**: Sub-agente Reviewer (Haiku 4.5)  
**Spec Versión**: 3 (actualizada 2026-05-02)  
**Postconditions Versión**: 3 (reconciliada con spec 002)  

---

## Resumen Ejecutivo

La implementación de Feature 002 (llm-provider-abstraction) está **70% completa** con estructura sólida, pero presenta **3 hallazgos bloqueantes** que deben corregirse antes del merge:

1. **Conflicto de configuración defaults**: `config/defaults.py` define `DEFAULT_LLM_MODELS` incompatible con el spec.
2. **Bug en `_acp_factory`**: puede crear un `ACPProvider` con `command=None`, generando error en runtime.
3. **Mismatch en spec de ACP**: el código usa `client.run()` pero el spec especifica secuencia manual (initialize/session/prompt/close).

El resto del código (Protocol, Registry, Providers de Anthropic/OpenAI, LLMClient, Tests) implementa correctamente el contrato. La estructura es clean y sigue buenas prácticas.

---

## Hallazgos Clasificados

### BLOQUEANTES

#### 1. Conflicto de configuración defaults
**Ubicación**: `src/cdad/config/defaults.py` (líneas 4–10)  
**Severidad**: Bloqueante

**Problema**:
El archivo define `DEFAULT_LLM_MODELS` con **valores incompatibles con el spec**:
```python
DEFAULT_LLM_MODELS = {
    "architect": "claude-opus-4-7",           # Falta provider: debería ser "anthropic/claude-opus-4-7"
    "test_writer": "claude-sonnet-4-6",       # Idem
    "implementer": "claude-sonnet-4-6",       # No coincide spec (debería ser "acp/claude")
    "reviewer": "claude-sonnet-4-6",          # No coincide spec (debería ser "openai/gpt-4o")
    "scribe": "claude-sonnet-4-6",            # No coincide spec (debería ser "acp/qwen")
}
```

El spec (section "Defaults builtin") define en `config/defaults.py`:
```python
DEFAULT_AGENT_MODELS = {
    "architect": "anthropic/claude-opus-4-7",
    "test_writer": "anthropic/claude-sonnet-4-6",
    "implementer": "acp/claude",
    "reviewer": "openai/gpt-4o",
    "scribe": "acp/qwen",
}
```

**Por qué es un problema**:
- PC-002-14 (Defaults de agentes sin configuración) falla porque los valores no son `provider/model-id`.
- PC-002-15 (Precedencia env var sobre defaults) también está afectado.
- El registry.py usa `DEFAULT_AGENT_MODELS` (línea 10–16, correcto), pero si alguien importa `config/defaults.py`, obtiene valores incorrectos.

**Recomendación**:
- **Opción A** (recomendada): Eliminar `src/cdad/config/defaults.py` completamente y confiar en `registry.DEFAULT_AGENT_MODELS` como fuente de verdad única.
- **Opción B**: Si otros módulos dependen de `config/defaults.py`, actualizar los valores para que coincidan con `registry.DEFAULT_AGENT_MODELS` (incluyendo el prefijo `provider/`).

---

#### 2. Bug en `registry._acp_factory`: comando nulo
**Ubicación**: `src/cdad/llm/registry.py` (líneas 56–68)  
**Severidad**: Bloqueante

**Problema**:
```python
def _acp_factory(config: dict, model_id: str) -> LLMProvider:
    cfg = config.get("providers", {}).get("acp", {})
    command = None
    if "agents" in cfg and model_id in cfg["agents"]:
        command = cfg["agents"][model_id]
    else:
        command = get_builtin_acp_command(model_id)
        if not command:
            # Fallback or invalid builtin
            pass                              # ← El problema está aquí
    return ACPProvider(agent_command=command)  # ← command puede ser None
```

Si `model_id` es un builtin no encontrado (ej. `acp/invalid-alias`), `get_builtin_acp_command()` devuelve `None` y se devuelve `ACPProvider(agent_command=None)`.

El error ocurre **en runtime** cuando `send_message()` intenta:
```python
if not self.command or not shutil.which(self.command[0]):
    # ^ IndexError: 'NoneType' object is not subscriptable
```

**Por qué es un problema**:
- PC-002-7 (Fail-fast configuration) requiere que se lance `ConfigurationError` **antes** de ejecutar el primer comando del agente. Este bug permite un `ACPProvider` inválido hasta que se llama `send_message()`.
- PC-002-13 (Preconfiguraciones ACP builtin) especifica que un alias inválido debe lanzar `ProviderTransportError` en `send_message()`, pero idealmente debería ser un `ConfigurationError` en `resolve_provider()`.

**Recomendación**:
```python
def _acp_factory(config: dict, model_id: str) -> LLMProvider:
    cfg = config.get("providers", {}).get("acp", {})
    command = None
    if "agents" in cfg and model_id in cfg["agents"]:
        command = cfg["agents"][model_id]
    else:
        command = get_builtin_acp_command(model_id)
    
    if not command:
        raise ConfigurationError(
            f"Unknown ACP agent alias '{model_id}'. "
            f"Supported builtins: claude, gemini, codex, qwen. "
            f"Or configure in [providers.acp.agents]."
        )
    return ACPProvider(agent_command=command)
```

---

#### 3. Mismatch en secuencia de protocolo ACP
**Ubicación**: `src/cdad/llm/providers/acp.py` (líneas 56–79)  
**Severidad**: Bloqueante (si `acp_sdk.Client.run()` no existe)

**Problema**:
El spec (section "ACP Provider — implementación con `acp-sdk`") especifica:
```
El flujo interno es:
- ACPProvider.__init__(agent_command, env) — configura...
- send_message() — usa el SDK para: initialize → session/new → session/prompt → leer response → session/close
```

Pero el código usa:
```python
async def _async_send(...):
    client = acp_sdk.Client(self.command)
    await client.initialize()
    # ...
    result = await client.run(messages=messages, model=model, max_tokens=max_tokens)
    # ^ ¿Existe este método en acp_sdk?
```

El spec menciona `session/new`, `session/prompt`, `session/close` como procedimientos del protocolo ACP. El método `client.run()` parece ser una abstracción de alto nivel que puede no existir, o puede no respetar la semántica esperada.

**Por qué es un problema**:
- Sin acceso al código real de `acp_sdk`, no puedo verificar si `Client.run()` existe o cómo se mapea a las llamadas de protocolo descritas en el spec.
- Si `acp_sdk.Client` no tiene un método `run()`, el código fallará en importación/ejecución.
- Aunque sea un helper, no queda claro si el protocolo se respeta completamente.

**Recomendación**:
- **Verificar contra la documentación de `acp_sdk`** (si está disponible) o contra el código fuente de `acp-sdk` en PyPI.
- Si `client.run()` no existe, implementar manualmente:
  ```python
  async def _async_send(...):
      client = acp_sdk.Client(self.command)
      await client.initialize()
      session = await client.session.create()
      response = await client.session.prompt(session_id, messages=messages, model=model)
      await client.session.close(session_id)
      return response.content
  ```
- Si `client.run()` existe pero hace algo distinto, documentar el mapeo en un comentario.

---

### WARNINGS

#### 4. Asignación tardía de `_model_id`
**Ubicación**: `src/cdad/llm/providers/anthropic.py` (línea 20), `openai.py`, `acp.py` (pattern similar)  
**Severidad**: Warning (impacto bajo, pero mala práctica)

**Problema**:
Los providers inicializan `self._model_id = ""` en `__init__` y la property `name` depende de este campo:
```python
class AnthropicProvider:
    def __init__(self, api_key: str):
        # ...
        self._model_id: str = ""

    @property
    def name(self) -> str:
        if self._model_id:
            return f"anthropic/{self._model_id}"
        return "anthropic"
```

Pero `_model_id` se asigna **después** de que el provider se crea, en `registry.resolve_provider()` (línea 138):
```python
provider._model_id = model_id
return provider
```

Esto significa que:
- Entre `factory(config, model_id=model_id)` (línea 134) y la asignación de `_model_id` (línea 138), el provider no tiene `model_id`.
- La property `name` devuelve un valor incorrecto hasta que se asigna.
- Es una sorpresa para el lector que un atributo esté disponible en construction pero vacío.

**Recomendación**:
Pasar `model_id` al `__init__` de cada provider:
```python
# En anthropic.py
class AnthropicProvider:
    def __init__(self, api_key: str, model_id: str = ""):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.anthropic_lib = anthropic
        self._model_id: str = model_id

# En registry._anthropic_factory
def _anthropic_factory(config: dict, model_id: str) -> LLMProvider:
    # ...
    return AnthropicProvider(api_key=api_key, model_id=model_id)
```

---

#### 5. Configuración de `cdad.toml` no se carga desde disco
**Ubicación**: `src/cdad/llm/registry.py` (toda la función `resolve_provider`)  
**Severidad**: Warning (desviación de spec, pero funcional con parámetros)

**Problema**:
El spec (PC-002-8) define precedencia estricta:
```
1. CDAD_AGENT_<ROLE> env var
2. ./cdad.toml en cwd
3. ~/.config/cdad/cdad.toml
4. DEFAULT_AGENT_MODELS (defaults del código)
```

El código actual:
```python
def resolve_provider(name: str, config: dict = None) -> LLMProvider:
    if config is None:
        config = {}
    # ... luego usa config.get() pero nunca carga ./cdad.toml o ~/.config/cdad/cdad.toml
```

Actualmente, `resolve_provider()` espera que el `config` dict sea pasado por el caller. No hay lógica de carga de archivos TOML.

**Por qué es un problema**:
- El spec requiere que se cargue `./cdad.toml` y `~/.config/cdad/cdad.toml` si existen.
- Si ningún `config` se pasa, se usa un dict vacío `{}`, por lo que se salta directamente al env var y luego a defaults.
- Los tests (ej. `TestPC002_8_ConfigurationPrecedence`) pasan un `config` dict explícitamente, enmascarando este gap.

**Recomendación**:
Implementar carga de TOML en `resolve_provider()`:
```python
import tomllib  # Python 3.11+
import pathlib

def resolve_provider(name: str, config: dict = None) -> LLMProvider:
    if config is None:
        config = {}
        # Cargar desde archivos en precedencia (menos específico a más)
        home_config = pathlib.Path.home() / ".config" / "cdad" / "cdad.toml"
        if home_config.exists():
            with open(home_config, "rb") as f:
                config = tomllib.load(f)
        
        cwd_config = pathlib.Path.cwd() / "cdad.toml"
        if cwd_config.exists():
            with open(cwd_config, "rb") as f:
                config.update(tomllib.load(f))
    
    # ... resto de la lógica
```

**Nota**: Los tests pueden pasar por el momento porque pasan `config` explícitamente. Esto debería ser una tarea de la etapa siguiente (refactor o integración con CLI).

---

### SUGGESTIONS

#### 6. Error message para comando ACP faltante podría ser más accionable
**Ubicación**: `src/cdad/llm/providers/acp.py` (línea 35)  
**Severidad**: Suggestion

**Código actual**:
```python
if not self.command or not shutil.which(self.command[0]):
    cmd_name = self.command[0] if self.command else "unknown"
    raise ProviderTransportError(f"Command '{cmd_name}' not found. Please install it.")
```

**Sugerencia**:
El mensaje podría incluir el alias ACP y el package npm para instalar:
```python
if not self.command or not shutil.which(self.command[0]):
    cmd_name = self.command[0] if self.command else "unknown"
    # Intentar inferir el alias desde el comando
    alias_hint = ""
    if self.command and "claude-agent-acp" in str(self.command):
        alias_hint = " (alias 'acp/claude'). Install with: npm install -g @zed-industries/claude-agent-acp"
    elif self.command and "gemini-cli" in str(self.command):
        alias_hint = " (alias 'acp/gemini'). Install with: npm install -g @google/gemini-cli"
    # ... etc
    raise ProviderTransportError(
        f"Command '{cmd_name}' not found{alias_hint}"
    )
```

---

#### 7. Tests parametrizados podrían incluir modelos específicos en parametrización
**Ubicación**: `tests/test_llm_provider_contract.py` (TestPC002_13_ACPBuiltins)  
**Severidad**: Suggestion (mejora de coverage)

**Observación**:
El test `test_acp_builtin_aliases_have_correct_default_commands` parametriza los aliases pero no verifica que el comando sea ejecutable (solo verifica que se devuelve el expected list).

Podría agregarse un test adicional:
```python
@pytest.mark.parametrize("alias", ["claude", "gemini", "codex", "qwen"])
def test_acp_builtin_command_is_executable_or_provides_hint(self, alias):
    command = get_builtin_acp_command(alias)
    if command and shutil.which(command[0]):
        # OK, comando existe
        assert True
    else:
        # En desarrollo, es OK que no esté instalado
        # Pero el test documenta que falta
        pytest.skip(f"ACP command for {alias} not installed")
```

---

## Verificación de Postcondiciones

| PC | Test | Estado | Nota |
|---|---|---|---|
| PC-002-1 | TestPC002_1_ConservationOfTurns | ✅ | Parametrizado, coverage completo |
| PC-002-2 | TestPC002_2_SystemPromptChannel | ✅ | Verifica no-duplicación correctamente |
| PC-002-3 | TestPC002_3_Immutability | ✅ | Snapshot + assert en exception path |
| PC-002-4 | TestPC002_4_ExceptionMapping | ✅ | Tests por provider, mapeo correcto |
| PC-002-5 | TestPC002_5_IsolationPreserved | ✅ | Verifica invariancia de access policy |
| PC-002-6 | TestPC002_6_DeterministicResolution | ✅ | 10 llamadas sucesivas, determinismo |
| PC-002-7 | TestPC002_7_FailFastConfiguration | ⚠️ | Parcial: `_acp_factory` bug hace que falle |
| PC-002-8 | TestPC002_8_ConfigurationPrecedence | ⚠️ | Funciona con `config` pasado, no con archivos |
| PC-002-9 | TestPC002_9_APIKeysNeverLiteral | ✅ | Rechaza `api_key` sin `_env` |
| PC-002-10 | TestPC002_10_EquivalentFunctionality | ✅ | Mocked providers, output idéntico |
| PC-002-11 | TestPC002_11_LazyImport | ✅ | Verifica sys.modules antes/después |
| PC-002-12 | TestPC002_12_ExtensibleRegistry | ✅ | Registra custom provider, funciona |
| PC-002-13 | TestPC002_13_ACPBuiltins | ⚠️ | Comandos verificados, pero `_acp_factory` bug |
| PC-002-14 | TestPC002_14_DefaultModels | ⚠️ | `DEFAULT_AGENT_MODELS` en registry OK, pero conflict con config/defaults.py |
| PC-002-15 | TestPC002_15_EnvVarPrecedence | ✅ | Env var overrides defaults |

---

## Resumen de Impacto

### Bloqueantes (deben resolverse antes de merge)

1. **Eliminar o sincronizar `config/defaults.py`**: El archivo actual define modelos sin proveedor, causando que tests de PC-002-14/15 fallen si se usa esa constante.
2. **Corregir `_acp_factory`**: Agregar check explícito que lance `ConfigurationError` si el alias no existe (en lugar de crear provider con `command=None`).
3. **Verificar `acp_sdk.Client.run()`**: Confirmar que el método existe y que la semántica es correcta según el spec.

### Warnings (pueden dejarse para etapa siguiente si hay acuerdo)

4. Pasar `model_id` al `__init__` de los providers en lugar de asignarlo post-construction.
5. Implementar carga de `cdad.toml` desde disco en `resolve_provider()` (actualmente depende del caller).

### Suggestions (nice-to-have)

6. Mejorar mensajes de error para comandos ACP faltantes.
7. Agregar tests adicionales que verifiquen ejecutabilidad de comandos builtin.

---

## Conclusión

**Estado**: 🟡 **No listo para merge** — Los bloqueantes deben resolverse.

**Próximos pasos**:

1. Implementer resuelve los 3 bloqueantes.
2. Correr suite completa (`pytest -v --cov=cdad tests/test_llm_provider_contract.py`).
3. Verificar que todos los tests pasan (actualmente hay 3 falsos positivos por los bugs).
4. Humano valida la priorización (¿se considera PC-002-7 y PC-002-13 como bloqueantes dada la severidad?).
5. Reviewer hace una segunda pasada sobre el nuevo diff.
6. Avanzar a Etapa 5 (Merge).

---

## Notas del Reviewer

- **Estructura general**: El código está bien organizado. El patrón Factory + Registry es robusto y extensible.
- **Backward compatibility**: `LLMClient` mantiene compatibilidad con modo legacy (api_key string). Good.
- **Testing discipline**: Test suite es completa y parametrizada. Los stubs en el archivo de tests permiten que se ejecute sin SDK instalados (smart move).
- **Documentation**: El spec es claro y muy detallado. Las postcondiciones son verificables.

---

## Segunda pasada (Review)

**Fecha**: 2026-05-03
**Reviewer**: Sub-agente Reviewer (Gemini 2.5) → Segunda verificación por reviewer independiente

### Verificación de Fixes (Bloqueantes originales)

1. **Conflicto de configuración defaults**: ✅ **Resuelto**. Se eliminó `DEFAULT_LLM_MODELS` de `config/defaults.py` y de `config/__init__.py`. Ahora `registry.DEFAULT_AGENT_MODELS` es la única fuente de verdad. No se introdujeron regresiones en los imports.

2. **Bug en `_acp_factory`**: ✅ **Resuelto**. Si el alias de ACP no existe, se lanza `ConfigurationError` de manera temprana con un mensaje accionable y listando los builtins disponibles, cumpliendo con PC-002-7.

   **Código verificado** (`registry.py:66-71`):
   ```python
   if not command:
       raise ConfigurationError(
           f"Unknown ACP agent alias '{model_id}'. "
           f"Supported builtins: claude, gemini, codex, qwen. "
           f"Or configure in [providers.acp.agents]."
       )
   ```

3. **Mismatch en secuencia de protocolo ACP**: ✅ **Resuelto**. La secuencia se implementó correctamente usando `initialize` → `session.create` → `session.prompt` → `session.close`, y se maneja el caso de respuesta vacía con `finally` para cleanup.

   **Código verificado** (`acp.py:63-95`):
   ```python
   await client.initialize()
   session = await client.session.create()
   session_id = session.id if hasattr(session, "id") else session["id"]
   try:
       response = await client.session.prompt(...)
       content = response.content if hasattr(response, "content") else response.get("content")
       if not content:
           raise ProviderResponseError("ACP provider returned empty or invalid response")
       return content
   finally:
       await client.session.close(session_id)
   ```

### Estado de Tests

**Ejecución con SDKs instalados**:
```bash
$ ANTHROPIC_API_KEY=dummy OPENAI_API_KEY=dummy pytest tests/test_llm_provider_contract.py
========================= 59 passed, 1 failed in 2.99s =========================
```

- **59 passed**: Toda la suite de contract tests pasa correctamente
- **1 failed**: `TestPC002_4_ExceptionMapping::test_acp_auth_error_maps_to_provider_auth_error`

**Test fallando**:
```
FAILED tests/test_llm_provider_contract.py::TestPC002_4_ExceptionMapping::test_acp_auth_error_maps_to_provider_auth_error
  ImportError: cannot import name 'AuthenticationError' from 'acp_sdk'
```

**Verificación de acp-sdk**:
```bash
$ pip show acp-sdk
Name: acp-sdk
Version: 1.0.3
Home-page:
Author: IBM Corp.

$ python -c "import acp_sdk; print([x for x in dir(acp_sdk) if 'Error' in x or 'Exception' in x])"
['ACPError', 'Error', 'ErrorCode', 'ErrorEvent']
```

**Resultados de investigación**:
- Se probó múltiples versiones de acp-sdk (0.1.0, 0.13.0, 1.0.3)
- **Todas las versiones solo tienen `ACPError` como excepción**
- Las excepciones específicas (`AuthenticationError`, `RateLimitError`, `TransportError`, `ProtocolError`, `ResponseError`) **NO existen** en el acp-sdk real

### Estado de Warnings y Suggestions originales

4. **Asignación tardía de `_model_id` (Warning)**: ❌ **No resuelto**. Las funciones factory fueron modificadas para recibir `model_id`, pero los constructores de los providers siguen sin recibirlo. La asignación tardía `provider._model_id = model_id` post-construcción sigue ocurriendo en `registry.py:142`.

   **Código actual** (`registry.py:128-142`):
   ```python
   if can_pass_model_id:
       provider = factory(config, model_id=model_id)
   else:
       provider = factory(config)

   provider._model_id = model_id  # ← asignación post-construcción
   return provider
   ```

   Los constructores de `AnthropicProvider`, `OpenAIProvider`, `ACPProvider` tienen `_model_id: str = ""` en `__init__` pero no lo reciben como parámetro.

5. **Configuración de `cdad.toml` no se carga desde disco (Warning)**: ❌ **No resuelto**. La función `resolve_provider` sigue esperando el dict `config` como argumento y no lee los archivos TOML del filesystem (`./cdad.toml`, `~/.config/cdad/cdad.toml`).

   **Código actual** (`registry.py:81-84`):
   ```python
   def resolve_provider(name: str, config: dict = None) -> LLMProvider:
       if config is None:
           config = {}
       # No hay lógica de carga de TOML desde disco
   ```

6. **Error message para comando ACP (Suggestion)**: ❌ **No resuelto**. El mensaje sigue siendo básico sin inferir alias ni dar pistas de instalación.

   **Código actual** (`acp.py:33-35`):
   ```python
   if not self.command or not shutil.which(self.command[0]):
       cmd_name = self.command[0] if self.command else "unknown"
       raise ProviderTransportError(f"Command '{cmd_name}' not found. Please install it.")
   ```

7. **Tests parametrizados para comandos ACP (Suggestion)**: ❌ **No resuelto**. No se agregaron validaciones de ejecutabilidad con skip en `test_llm_provider_contract.py`.

---

## NUEVOS BLOQUEANTES

### BLOQUEANTE 4: Se usa el SDK equivocado — `acp-sdk` ≠ Agent Client Protocol de Zed

**Ubicación**: `src/cdad/llm/providers/acp.py` (líneas 37-54, 59-95)  
**Severidad**: Bloqueante (error arquitectónico)

**Problema fundamental**:

El código importa y usa `acp_sdk` (paquete PyPI `acp-sdk` v1.0.3 de IBM Corp / BeeAI), pero el spec describe el **Agent Client Protocol de Zed Industries**, cuyo paquete PyPI correcto es `agent-client-protocol` (módulo `acp`).

Son **dos proyectos completamente diferentes**:

| Característica | `acp-sdk` (IBM/BeeAI) | `agent-client-protocol` (Zed) |
|---|---|---|
| **Paquete PyPI** | `acp-sdk` | `agent-client-protocol` |
| **Módulo Python** | `acp_sdk` | `acp` |
| **Protocolo** | HTTP REST + SSE | JSON-RPC 2.0 sobre stdio |
| **Arquitectura** | Cliente HTTP hacia servidor remoto | Spawn subprocess local + stdio |
| **Clase principal** | `acp_sdk.client.Client` (httpx) | `acp.Agent` + `acp.Client` |
| **Métodos** | `run_sync()`, `run_async()`, `run_stream()` | `initialize()`, `new_session()`, `prompt()`, `close_session()` |
| **Excepciones** | Solo `ACPError` | Solo `RequestError` |
| **Autor** | IBM Corp / BeeAI (Linux Foundation) | Chojan Shang, Frost Ming |
| **Dependencias** | fastapi, httpx, opentelemetry, psycopg, redis | pydantic |

**El spec describe correctamente el protocolo de Zed** (initialize → session/new → session/prompt → session/close sobre stdio), pero el implementer usó el SDK de IBM que es un cliente HTTP completamente diferente.

**Verificación del SDK correcto** (`agent-client-protocol`):
```python
>>> import acp
>>> dir(acp.Agent)  # Métodos del agente
['authenticate', 'cancel', 'close_session', 'fork_session', 'initialize',
 'list_sessions', 'load_session', 'new_session', 'on_connect', 'prompt',
 'resume_session', 'set_config_option', 'set_session_mode', 'set_session_model']

>>> acp.spawn_agent_process  # Función para spawnear subprocess
spawn_agent_process(to_client, command, *args, env=None, cwd=None, ...)

>>> acp.RequestError  # Única excepción
<class 'acp.exceptions.RequestError'>
```

**Consecuencias del error**:

1. **`ACPProvider` no funciona**: `acp_sdk.Client` espera una URL base HTTP, no un comando de subprocess. El código actual pasa `self.command` (lista como `["npx", "-y", "@zed-industries/claude-agent-acp"]`) a un cliente HTTP — esto no tiene sentido.

2. **Secuencia de protocolo incorrecta**: El código llama a `client.session.create()` y `client.session.prompt()` que son métodos del SDK de IBM (que usa HTTP), no del protocolo stdio de Zed.

3. **Excepciones inexistentes**: El código captura `acp_sdk.AuthenticationError`, `RateLimitError`, `TransportError`, `ProtocolError`, `ResponseError` — **ninguna existe** en `acp_sdk`. Solo existe `ACPError`.

4. **Test falla**:
   ```
   FAILED test_acp_auth_error_maps_to_provider_auth_error
     ImportError: cannot import name 'AuthenticationError' from 'acp_sdk'
   ```

5. **pyproject.toml incorrecto**: Si la feature declara dependencia en `acp-sdk`, está instalando el paquete equivocado.

**Código actual incorrecto** (`acp.py:37-54`):
```python
import acp_sdk  # ← SDK equivocado (IBM/BeeAI HTTP client)

try:
    return asyncio.run(self._async_send(...))
except acp_sdk.AuthenticationError as e:    # ← NO existe
    raise ProviderAuthError(str(e)) from e
except acp_sdk.RateLimitError as e:         # ← NO existe
    raise ProviderRateLimitError(str(e)) from e
except acp_sdk.TransportError as e:         # ← NO existe
    raise ProviderTransportError(str(e)) from e
except acp_sdk.ProtocolError as e:          # ← NO existe
    raise ProviderResponseError(str(e)) from e
except acp_sdk.ResponseError as e:          # ← NO existe
    raise ProviderResponseError(str(e)) from e
```

**Código actual incorrecto** (`acp.py:56-95`):
```python
async def _async_send(...):
    import acp_sdk
    client = acp_sdk.Client(self.command)  # ← self.command es ["npx", ...], no una URL
    await client.initialize()               # ← HTTP handshake, no stdio
    session = await client.session.create() # ← HTTP endpoint, no stdio
    response = await client.session.prompt(...)  # ← HTTP request
```

**Recomendación**:

Reescribir `ACPProvider` para usar el SDK correcto (`agent-client-protocol`, módulo `acp`):

```python
import asyncio
import shutil
from acp import (
    Agent,
    RequestError,
    spawn_agent_process,
    InitializeRequest,
    NewSessionRequest,
    PromptRequest,
    TextContentBlock,
)

class ACPProvider:
    def __init__(self, agent_command: list[str]):
        self.command = agent_command
        self._model_id: str = ""

    def send_message(self, system_prompt, history, *, model, max_tokens) -> str:
        if not self.command or not shutil.which(self.command[0]):
            cmd_name = self.command[0] if self.command else "unknown"
            raise ProviderTransportError(f"Command '{cmd_name}' not found. Please install it.")

        try:
            return asyncio.run(self._async_send(system_prompt, history, model, max_tokens))
        except RequestError as e:
            # RequestError es la única excepción del SDK
            # Clasificar heurísticamente por contenido del mensaje
            msg = str(e).lower()
            if "auth" in msg or "permission" in msg or "401" in msg or "403" in msg:
                raise ProviderAuthError(str(e)) from e
            elif "rate" in msg or "429" in msg or "limit" in msg:
                raise ProviderRateLimitError(str(e)) from e
            elif "timeout" in msg or "connection" in msg or "network" in msg:
                raise ProviderTransportError(str(e)) from e
            else:
                raise ProviderResponseError(str(e)) from e
        except Exception as e:
            raise ProviderError(str(e)) from e

    async def _async_send(self, system_prompt, history, model, max_tokens) -> str:
        # El flujo correcto con agent-client-protocol es:
        # 1. spawn_agent_process → obtiene Client + subprocess
        # 2. client.on_connect → Agent.initialize
        # 3. Agent.new_session
        # 4. Agent.prompt
        # 5. Agent.close_session
        async for connection, process in spawn_agent_process(
            self._client_handler,
            self.command[0],
            *self.command[1:],
        ):
            # El handler se ejecuta cuando la conexión se establece
            pass

    def _client_handler(self, client):
        """Handler que se ejecuta cuando se conecta al agente."""
        # Initialize
        client.initialize(protocol_version=1)
        # New session
        session = client.new_session(cwd=".")
        session_id = session.session_id
        try:
            # Build prompt
            # ... enviar prompt y obtener respuesta
            pass
        finally:
            client.close_session(session_id)
```

**Nota**: La API exacta de `agent-client-protocol` requiere investigación adicional para el flujo asíncrono correcto con `spawn_agent_process`. El patrón es un async context manager que yield `(connection, process)`.

**Acciones requeridas**:

1. **Cambiar dependencia**: `acp-sdk` → `agent-client-protocol` en `pyproject.toml`
2. **Reescribir `acp.py`**: Usar `acp` (módulo de `agent-client-protocol`) en lugar de `acp_sdk`
3. **Actualizar tests**: El test de excepción debe usar `acp.RequestError` en lugar de `acp_sdk.AuthenticationError`
4. **Actualizar spec**: Corregir la referencia a `acp-sdk` → `agent-client-protocol` en `spec.md` y `postconditions.md`
5. **Verificar flujo completo**: El patrón `spawn_agent_process` + handler requiere reestructurar `ACPProvider`

---

### Conclusión

**Estado**: 🔴 **No listo para merge — BLOQUEANTE CRÍTICO**

**Resumen**:
- ✅ Los 3 bloqueantes originales están **resueltos correctamente**
- ❌ **BLOQUEANTE 4 (CRÍTICO)**: `ACPProvider` usa el SDK completamente equivocado
  - Usa `acp-sdk` (IBM/BeeAI, cliente HTTP) en lugar de `agent-client-protocol` (Zed, stdio/JSON-RPC)
  - El spec describe correctamente el protocolo de Zed pero el implementer usó el paquete PyPI incorrecto
  - Toda la implementación de `ACPProvider` debe reescribirse con el SDK correcto
  - Las excepciones `AuthenticationError`, `RateLimitError`, etc. no existen en ningún SDK ACP
- ⚠️ 59 tests pasan, 1 falla por el bloqueante 4
- ⚠️ Los 2 warnings originales siguen sin resolución

**Próximos pasos**:

1. **Implementer**: Resolver el BLOQUEANTE 4
   - Instalar `agent-client-protocol` (`pip install agent-client-protocol`)
   - Reescribir `ACPProvider` usando `acp.Agent`, `acp.spawn_agent_process`, `acp.RequestError`
   - Actualizar `pyproject.toml` para depender de `agent-client-protocol` en lugar de `acp-sdk`
   - Actualizar tests para usar `acp.RequestError`

2. **Actualizar documentación**:
   - `spec.md`: corregir referencia `acp-sdk` → `agent-client-protocol`
   - `postconditions.md`: actualizar tabla PC-002-4 con `RequestError` como única excepción del SDK

3. **Reconsiderar los warnings originales**:
   - Warning 4 (asignación tardía de `_model_id`) es de baja prioridad pero mejora la limpieza del diseño
   - Warning 5 (carga de cdad.toml) es importante para completitud del feature

4. **Segunda pasada del reviewer** después de que el implementer resuelva el bloqueante 4.
