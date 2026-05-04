# Spec 004: Provider-Aware CLI Commands

## Descripción funcional

Unificar los comandos `discover`, `spec`, `architect`, `test` de cdad-cli al patrón provider-aware que ya usa `green`, eliminando el modo legacy `LLMClient(api_key=...)` y la función `_require_api_key()`. Introducir el comando `cdad config` con dos subcomandos (`auto`, `set`) para gestión de providers sin editar `cdad.toml` a mano. Soporte de dos scopes: `--global` (`~/.config/cdad/cdad.toml`, configuración del usuario) y `--local` (`./cdad.toml` en project_root, configuración del proyecto). Por defecto, `config auto` y `config set` operan en scope global. Agregar el rol `default` al registry como fallback de cualquier rol no configurado explícitamente.

## Contrato

### Postcondición PC-004-01
**Name**: `discover_uses_resolve_provider`
**Description**: Cuando el usuario corre `cdad discover --feature "X"` con `cdad.toml` válido conteniendo `[agents] default = "<provider>/<model>"`, el comando llama a `resolve_provider(name="architect", config=<contenido cdad.toml>, override=None)` y construye el `LLMClient` con `provider=<instancia retornada>` y `model=<model_id>`. No se invoca `LLMClient(api_key=...)` en ningún path.
**Verification**: test

### Postcondición PC-004-02
**Name**: `spec_uses_resolve_provider`
**Description**: Cuando el usuario corre `cdad spec --name "X"` con `cdad.toml` válido, el comando llama a `resolve_provider(name="architect", config=<contenido>, override=None)` y construye `LLMClient(provider=<instancia>, model=<model_id>)`. No se invoca `LLMClient(api_key=...)`.
**Verification**: test

### Postcondición PC-004-03
**Name**: `architect_uses_resolve_provider`
**Description**: Cuando el usuario corre `cdad architect <target>` con `cdad.toml` válido, el comando llama a `resolve_provider(name="architect", ...)` y construye `LLMClient(provider=<instancia>, model=<model_id>)`. No se invoca `LLMClient(api_key=...)`.
**Verification**: test

### Postcondición PC-004-04
**Name**: `test_command_uses_test_writer_role`
**Description**: Cuando el usuario corre `cdad test <spec_name>` con `cdad.toml` válido, el comando llama a `resolve_provider(name="test_writer", ...)` (no `architect`) y construye `LLMClient(provider=<instancia>, model=<model_id>)`.
**Verification**: test

### Postcondición PC-004-05
**Name**: `commands_accept_provider_override`
**Description**: Los comandos `discover`, `spec`, `architect`, `test` aceptan un flag `--provider <provider/model>` que se propaga como `override` al `resolve_provider`. Cuando se pasa, sobrescribe la configuración de `cdad.toml` y la env var `CDAD_AGENT_<ROLE>`.
**Verification**: test

### Postcondición PC-004-06
**Name**: `commands_abort_without_config`
**Description**: Cuando el usuario corre cualquiera de `discover`, `spec`, `architect`, `test` y no existe configuración resuelta (ni `./cdad.toml` local ni `~/.config/cdad/cdad.toml` global, o existen pero no contienen la sección `[agents]` con clave `default` y el rol específico tampoco está configurado), el comando aborta con exit code 2, no invoca al LLM, y emite por stderr un mensaje que contiene literalmente la cadena `"cdad config auto"` y `"cdad config set"`.
**Verification**: test

### Postcondición PC-004-07
**Name**: `legacy_api_key_mode_removed`
**Description**: La clase `LLMClient` no acepta el parámetro `api_key` en su constructor. Llamar `LLMClient(api_key="x")` levanta `TypeError`. El atributo `LLMClient.client` no existe. Solo el constructor `LLMClient(provider=<LLMProvider>, model=<str>, max_tokens=<int>)` está soportado.
**Verification**: test

### Postcondición PC-004-08
**Name**: `legacy_helpers_removed_from_main`
**Description**: El módulo `cdad.cli.main` no exporta los símbolos `_require_api_key` ni `_make_llm_client`. Importar cualquiera de los dos levanta `ImportError`/`AttributeError`.
**Verification**: test

### Postcondición PC-004-09
**Name**: `default_role_resolves`
**Description**: `resolve_provider("default", config={"agents": {"default": "anthropic/claude-opus-4-7"}}, override=None)` devuelve una instancia de `AnthropicProvider` con `_model_id == "claude-opus-4-7"`. No levanta `ConfigurationError` por rol desconocido.
**Verification**: test

### Postcondición PC-004-10
**Name**: `unconfigured_role_falls_back_to_default`
**Description**: Cuando se llama `resolve_provider(role, config, override=None)` con `role ∈ {"architect", "test_writer", "implementer", "reviewer", "scribe"}`, y ese rol no está presente en `config["agents"]`, ni hay env var `CDAD_AGENT_<ROLE>` seteada, ni override, **y** `config["agents"]["default"]` está definido, el provider retornado es el que corresponde al string `default`.
**Verification**: test

### Postcondición PC-004-11
**Name**: `fallback_precedence_order`
**Description**: La precedencia de resolución por rol es, de mayor a menor: (1) `override` argumento; (2) env var `CDAD_AGENT_<ROLE_UPPER>`; (3) `config["agents"][role]`; (4) `config["agents"]["default"]`; (5) `ConfigurationError`. Cada nivel se evalúa solo si el anterior no está presente.
**Verification**: test

### Postcondición PC-004-12
**Name**: `config_auto_creates_toml_when_absent`
**Description**: Cuando el usuario corre `cdad config auto` sin `cdad.toml` en el scope objetivo, y al menos un provider candidato responde OK al prompt de validación dentro del timeout, el comando crea el archivo de configuración del scope con la sección `[agents]` conteniendo únicamente la clave `default = "<provider>/<model>"` correspondiente al provider seleccionado por prioridad. Scope por defecto: global (`~/.config/cdad/cdad.toml`). Con `--local`: `./cdad.toml` en el project_root. Con `--global`: explícitamente global. Exit code 0.
**Verification**: test

### Postcondición PC-004-13
**Name**: `config_auto_backups_existing_toml`
**Description**: Cuando el usuario corre `cdad config auto` y existe el archivo de configuración del scope objetivo (`./cdad.toml` para `--local`, `~/.config/cdad/cdad.toml` para `--global` o default), el archivo previo se renombra a `<archivo>.bak-<YYYYMMDDHHMM>` (timestamp UTC con minutos de precisión) **antes** de escribir el nuevo. Si el rename falla, el comando aborta con exit code != 0 y no escribe el nuevo archivo.
**Verification**: test

### Postcondición PC-004-14
**Name**: `config_auto_priority_order`
**Description**: Cuando `cdad config auto` tiene múltiples providers que responden OK a la validación, escribe en `default` el provider de mayor prioridad según este orden estricto: (1) `anthropic/<model>` si `ANTHROPIC_API_KEY` presente; (2) `openai/<model>` si `OPENAI_API_KEY` presente; (3) `acp/claude` si binario `claude` o npx wrapper disponible; (4) `acp/qwen` si binario `qwen` disponible. Cualquier otro ACP builtin (`gemini`, `codex`) solo es elegido si es el único que respondió OK.
**Verification**: test

### Postcondición PC-004-15
**Name**: `config_auto_precheck_aborts_when_nothing_available`
**Description**: Cuando `cdad config auto` no detecta ninguna API key (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY` ausentes) ni ningún binario ACP compatible (`claude`, `gemini`, `codex`, `qwen` no en PATH), el comando aborta con exit code != 0 antes de hacer cualquier llamada de validación. El mensaje stderr lista los providers compatibles que el usuario podría instalar/configurar (cadenas `"anthropic"`, `"openai"`, `"claude"`, `"qwen"` presentes en el output). No escribe ni hace backup de `cdad.toml`.
**Verification**: test

### Postcondición PC-004-16
**Name**: `config_auto_validates_with_real_call`
**Description**: Para cada provider candidato detectado en el pre-check, `config auto` realiza exactamente una llamada `provider.send_message` con un prompt que contiene la cadena literal `"CDAD"` y la palabra `"disponible"`. La llamada tiene timeout de 30 segundos por provider. Un provider se considera OK sii la llamada retorna respuesta no vacía dentro del timeout.
**Verification**: test

### Postcondición PC-004-17
**Name**: `config_auto_reports_discarded_providers`
**Description**: Cuando `config auto` descarta un provider candidato (timeout, excepción, respuesta vacía), imprime por stdout o stderr una línea conteniendo el nombre del provider y la razón (substring `"timeout"`, `"error"`, o el mensaje de la excepción). Continúa evaluando los providers restantes.
**Verification**: test

### Postcondición PC-004-18
**Name**: `config_auto_writes_only_default`
**Description**: El archivo de configuración resultante de `config auto` contiene exactamente una clave bajo `[agents]`: `default`. No se escriben claves para `architect`, `test_writer`, `implementer`, `reviewer`, `scribe`. Aplica a ambos scopes.
**Verification**: test

### Postcondición PC-004-19
**Name**: `config_set_writes_role`
**Description**: `cdad config set <role> <provider>/<model>` con `role ∈ {default, architect, test_writer, implementer, reviewer, scribe}` y formato válido escribe la asignación `[agents] <role> = "<provider>/<model>"` en el archivo del scope objetivo. Scope por defecto: global. Con `--local`: `./cdad.toml`. Con `--global`: explícitamente global. Exit code 0.
**Verification**: test

### Postcondición PC-004-20
**Name**: `config_set_preserves_other_entries`
**Description**: Cuando el archivo del scope objetivo ya contiene otras entradas en `[agents]` (ej. `default = "x/y"`, `implementer = "a/b"`) y secciones distintas a `[agents]`, ejecutar `cdad config set architect anthropic/claude-opus-4-7` (con el scope correspondiente) modifica únicamente la clave `architect` y deja todas las demás claves de `[agents]` y otras secciones del archivo intactas en valor (no necesariamente en formato/comentarios).
**Verification**: test

### Postcondición PC-004-21
**Name**: `config_set_creates_toml_when_absent`
**Description**: Cuando el archivo del scope objetivo no existe y el usuario corre `cdad config set <role> <provider>/<model>` con argumentos válidos, el comando crea el archivo con la sección `[agents]` conteniendo solo esa entrada. Para scope `--local`, crea `./cdad.toml` en el project_root. Para scope `--global` o default, crea `~/.config/cdad/cdad.toml` (creando directorios intermedios si es necesario). Exit code 0.
**Verification**: test

### Postcondición PC-004-22
**Name**: `config_set_rejects_invalid_format`
**Description**: `cdad config set <role> <value>` donde `value` no contiene `/` (ej. `"foobar"`) **o** la parte `provider` no matchea `^[a-z][a-z0-9_-]*$`, aborta con exit code != 0, no modifica `cdad.toml`, y el mensaje stderr contiene la cadena literal `"provider/model"` (formato esperado) y el valor recibido.
**Verification**: test

### Postcondición PC-004-23
**Name**: `config_set_rejects_unknown_role`
**Description**: `cdad config set <role> <provider>/<model>` con `role` fuera del conjunto `{default, architect, test_writer, implementer, reviewer, scribe}` aborta con exit code != 0, no modifica `cdad.toml`, y el mensaje stderr enumera los roles aceptados.
**Verification**: test

### Postcondición PC-004-24
**Name**: `config_set_does_not_validate_provider_works`
**Description**: `cdad config set default anthropic/non-existent-model-id` con formato válido escribe exitosamente la entrada en el archivo del scope objetivo aunque el modelo no exista realmente y aunque la env var `ANTHROPIC_API_KEY` no esté seteada. No realiza ninguna llamada de validación funcional. Exit code 0.
**Verification**: test

### Postcondición PC-004-25
**Name**: `provider_missing_lists_supported`
**Description**: Cuando un comando provider-aware (`discover`, `spec`, `architect`, `test`) intenta resolver un provider y falla por ausencia de credencial/binario (`ConfigurationError` desde `resolve_provider` por env var faltante o binario ACP no en PATH), el mensaje stderr contiene los nombres de providers compatibles (substrings `"anthropic"`, `"openai"`, `"acp"`) y exit code != 0.
**Verification**: test

### Postcondición PC-004-26
**Name**: `config_auto_global_scope`
**Description**: `cdad config auto --global` crea o modifica `~/.config/cdad/cdad.toml`. Si el directorio `~/.config/cdad/` no existe, lo crea. El comportamiento de detección, validación y escritura es idéntico al de `config auto` sin flags, solo cambia el path del archivo objetivo. Exit code 0.
**Verification**: test

### Postcondición PC-004-27
**Name**: `config_auto_local_scope`
**Description**: `cdad config auto --local` crea o modifica `./cdad.toml` en el project_root. El comportamiento de detección, validación y escritura es idéntico al de `config auto` sin flags, solo cambia el path del archivo objetivo. Exit code 0.
**Verification**: test

### Postcondición PC-004-28
**Name**: `config_set_scope_flags`
**Description**: `cdad config set --global <role> <provider>/<model>` escribe en `~/.config/cdad/cdad.toml`. `cdad config set --local <role> <provider>/<model>` escribe en `./cdad.toml`. Sin flags, escribe en global. Ambos flags respetan las mismas validaciones de formato, rol y no-validación de provider que la versión sin scope. Exit code 0.
**Verification**: test

## Invariantes verificables

1. **No hay path en `cdad.cli.main` que construya `LLMClient(api_key=...)`.** Verificable con grep AST sobre el módulo: no debe haber llamadas a `LLMClient` con argumento keyword `api_key`.

2. **`LLMClient.__init__` tiene un único parámetro de provider.** La firma es `__init__(self, provider: LLMProvider, *, model: str, max_tokens: int = ...)`. Verificable con `inspect.signature`.

3. **El rol `default` es válido en `resolve_provider`.** `resolve_provider("default", {"agents": {"default": "anthropic/x"}})` no levanta `ConfigurationError("Unknown role")`.

4. **Cadena de fallback determinística.** Para todo `role ∈ {architect, test_writer, implementer, reviewer, scribe}`, dado un `config` que solo define `agents.default`, `resolve_provider(role, config)` devuelve el mismo provider que `resolve_provider("default", config)`.

5. **`config auto` es idempotente bajo entorno estable.** Dos ejecuciones sucesivas de `cdad config auto` con el mismo conjunto de env vars y binarios disponibles producen el mismo valor de `default` (aunque cada una rote el archivo previo a `.bak-<timestamp>`).

6. **`config set` es idempotente.** `cdad config set <role> <p>/<m>` ejecutado dos veces consecutivas resulta en el mismo `cdad.toml` final que ejecutado una vez (excepto efectos colaterales de reescritura como pérdida de comentarios/orden, que pueden ocurrir solo en la primera).

7. **`config set` nunca borra entradas no relacionadas.** Para cualquier `cdad.toml` previo `T`, después de `cdad config set <role> <value>`, el conjunto de claves en `[agents]` distintas de `<role>` con sus valores es idéntico a `T`, y todas las secciones distintas de `[agents]` mantienen sus valores.

8. **`config auto` siempre crea backup si había archivo previo.** Si `cdad.toml` existe antes de `config auto`, después existe un archivo `cdad.toml.bak-<YYYYMMDDHHMM>` con el contenido byte-a-byte del original.

9. **Pre-check de `config auto` usa solo lectura de env y `shutil.which`.** No realiza ninguna llamada de red ni spawn de proceso ACP durante el pre-check (solo durante la fase de validación funcional). Verificable mockeando red y spawn.

10. **Resolución de config en comandos provider-aware.** Los comandos `discover`, `spec`, `architect`, `test`, `green` leen configuración en este orden: (1) `./cdad.toml` si existe (local); (2) `~/.config/cdad/cdad.toml` si existe (global); (3) `DEFAULT_AGENT_MODELS` del código. La fusión es shallow: keys locales ganan sobre globales para el mismo rol. Si ninguna fuente tiene `default` ni el rol específico, aborta con exit code 2.

## Criterios de aceptación

- [ ] Suite completa de tests verifica cada postcondición PC-004-01 a PC-004-25 con al menos un caso de éxito y, donde aplica, un caso de error.
- [ ] Cobertura de tests sobre `src/cdad/cli/main.py` (comandos migrados + grupo `config`) ≥ 85% líneas.
- [ ] Cobertura de tests sobre el cambio en `src/cdad/llm/registry.py` (rol `default` + fallback) ≥ 95% líneas.
- [ ] `pytest tests/test_cli.py tests/test_llm_client.py tests/cli/ tests/llm/` pasa sin errores ni warnings de deprecación.
- [ ] `grep -r "ANTHROPIC_API_KEY" src/cdad/cli/` retorna cero matches (la env var se accede solo desde `src/cdad/llm/registry.py` y/o `src/cdad/llm/providers/anthropic.py`).
- [ ] `grep -rn "_require_api_key\|_make_llm_client" src/cdad/` retorna cero matches.
- [ ] `grep -rn "api_key\s*=\s*api_key\|Anthropic(api_key" src/cdad/llm/client.py` retorna cero matches.
- [ ] `cdad --help` muestra `config` como comando disponible. `cdad config --help` muestra `auto` y `set` como subcomandos.
- [ ] Al correr `cdad config auto` en un entorno con solo `ANTHROPIC_API_KEY` seteada y respuesta válida del provider, el `cdad.toml` resultante contiene exactamente la línea (o equivalente toml) `default = "anthropic/<model>"` bajo `[agents]` y nada más en esa sección.
- [ ] Al correr `cdad config auto` en entorno limpio (sin keys, sin binarios ACP), exit code != 0 y el output menciona los 4 providers compatibles.
- [ ] Al correr `cdad discover --feature x` sin `cdad.toml`, exit code 2 y el output sugiere `cdad config auto` o `cdad config set`.
- [ ] Tests existentes en `tests/test_cli.py` que dependían del fixture `patched_llm` (firma `(api_key)`) están migrados a un fixture equivalente que mockea provider, y todos pasan.
- [ ] Tests existentes en `tests/test_llm_client.py` que construían `LLMClient(api_key="...")` están migrados a `LLMClient(provider=<mock>, model=...)` y todos pasan.
- [ ] El comando `cdad green` (no parte de esta feature) sigue funcionando sin cambios — sus tests `tests/cli/test_green.py` y `tests/integration/test_green_e2e.py` pasan sin modificación.
- [ ] La documentación de `cdad config auto --help` y `cdad config set --help` describe el comportamiento de prioridad, backup, validación con prompt, y el formato `provider/model`.

## Status: APPROVED (v2 — scope global/local añadido 2026-05-03)
