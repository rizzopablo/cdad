# Test Audit Report — 004-provider-aware-cli

## Comportamiento que cambia (resumen)
- **Eliminación del modo legacy `api_key`**: `LLMClient` ya no acepta `api_key` en su constructor. Las funciones de utilidad `_require_api_key` y `_make_llm_client` han sido removidas de `cdad.cli.main` (PC-004-07, PC-004-08).
- **Resolución de providers**: Los comandos usan `resolve_provider(role, config, override)` para instanciar su proveedor. Hay un nuevo rol `default` y un orden estricto de precedencia: override > env var > config específico de rol > config `default` (PC-004-09, PC-004-10, PC-004-11).
- **Nuevo comando `cdad config`**: Subcomandos `auto` y `set` para manejar scopes `--global` (`~/.config/cdad/cdad.toml`) y `--local` (`./cdad.toml`), con creación y backup de los archivos de configuración (PC-004-12 a PC-004-24, PC-004-26 a PC-004-28).

## Tests modificados

### Fixture `patched_llm` en `tests/test_cli.py`
- **Archivo**: `cdad-cli/tests/test_cli.py`
- **Cambio**: El fixture `patched_llm` mockea `_make_llm_client` con un `api_key`. Esta función fue eliminada. Debe actualizarse para mockear `resolve_provider` (o similar) y devolver un `LLMClient` construido con un `MockProvider`.
- **Spec ref**: PC-004-01 a PC-004-05, PC-004-08
- **Nueva expectativa**: Los tests de los comandos `discover`, `spec`, `architect` y `test` deben interactuar con un provider resuelto por `resolve_provider` sin fallos.
- **Estrategia**: Reemplazar `monkeypatch.setattr(cli_main, "_make_llm_client", ...)` por un mock de `resolve_provider` que retorne un proveedor mockeado válido.

### `tests/test_cli.py::TestArchitectCommand::test_requires_api_key`
- **Archivo**: `cdad-cli/tests/test_cli.py`
- **Cambio**: El test verifica que sin API key, el output menciona `ANTHROPIC_API_KEY`.
- **Spec ref**: PC-004-06, PC-004-25
- **Nueva expectativa**: Sin proveedor configurado, el comando aborta con exit code 2, y menciona `"cdad config auto"`, `"cdad config set"`, `"anthropic"`, `"openai"`, etc.
- **Estrategia**: Actualizar aserciones sobre `result.exit_code == 2` y verificar mención a `config auto` y providers soportados.

### Suite de `tests/test_llm_client.py` (7 tests)
- **Archivo**: `cdad-cli/tests/test_llm_client.py`
- **Cambio**: Instanciaciones de `LLMClient(api_key="test-key")`.
- **Spec ref**: PC-004-07
- **Nueva expectativa**: `LLMClient(provider=<mock>, model=...)`.
- **Estrategia**: Crear un `MockProvider` para pasar como dependencia en la inicialización de `LLMClient` en todos los tests y asegurar que `api_key` no se pase (o valide que lance un `TypeError` si se pasa).

### Suite de `tests/test_llm_provider_contract.py` (4 tests)
- **Archivo**: `cdad-cli/tests/test_llm_provider_contract.py`
- **Cambio**: Tests sobre precedencia vieja/variables de entorno.
- **Spec ref**: PC-004-11
- **Nueva expectativa**: Validar la nueva precedencia: `override` > `CDAD_AGENT_<ROLE_UPPER>` > `config["agents"][role]` > `config["agents"]["default"]` > `ConfigurationError`.
- **Estrategia**: Actualizar casos de test para que validen explícitamente el nuevo comportamiento de fallback en `resolve_provider`.

### Suite de `tests/cli/test_green.py` (4 tests)
- **Archivo**: `cdad-cli/tests/cli/test_green.py`
- **Cambio**: Utiliza la resolución de config cambiada; el comando `green` asimila el pattern.
- **Spec ref**: PC-004-25, Invariante 10
- **Nueva expectativa**: Debe funcionar usando resolución `local` > `global` (shallow merge). Los comportamientos de exit code deben mantenerse.
- **Estrategia**: Asegurar en los fixtures de test (como `temp_project_with_spec`) la existencia de una configuración válida (ej. `cdad.toml` local con un provider mock) para evitar que aborte prematuramente por `ConfigurationError`.

### `test_resolve_without_override_uses_normal_chain` en `tests/llm/test_registry.py`
- **Archivo**: `cdad-cli/tests/llm/test_registry.py`
- **Cambio**: Validaba resolución sin override; debe contemplar rol default.
- **Spec ref**: PC-004-09, PC-004-10
- **Nueva expectativa**: Incluir a `default` en la validación del fallback de la cadena normal si falla la env var o config específico.
- **Estrategia**: Actualizar los aserciones de mock para verificar la prioridad de la clave `default`.

## Tests nuevos a escribir
- Tests unitarios y de integración para el nuevo comando `cdad config auto` y comportamiento `--global`/`--local`, garantizando backup, jerarquía (Anthropic, OpenAI, Claude, Qwen) e interacciones timeout (PC-004-12 a PC-004-18, PC-004-26, PC-004-27).
- Tests unitarios para el subcomando `cdad config set` validando manipulación de roles, formato esperado y `--global`/`--local` sin tocar llaves ajenas (PC-004-19 a PC-004-24, PC-004-28).

## Tests sin cambios (untouched)
- `tests/test_cli.py::TestInit`: Todo el grupo de comandos `init` sigue inalterado ya que no consume provider.
- `tests/test_cli.py::TestStatus`: Sigue inalterado.
- Tests puramente orientados a validadores de spec/tests (`test_spec_validator.py`, `test_test_validator.py`, `test_contract_validator.py`).
- Pruebas del modelo de proyecto (`test_project_model.py`) u orquestadores (`test_phase_manager.py`) donde el proveedor LLM se inyecta externamente y no se inicializa con credenciales duras.

## Regression Risk Assessment
⚠️ **Risk**: Alto.
- **Justificación**: El cambio remueve el camino original y central de inyección de LLMs (`LLMClient(api_key=...)`) que es base para todos los comandos principales en CDAD. Errores al migrar los fixtures impactarán transversalmente en toda la suite, provocando falsos negativos. Además, una resolución incorrecta de local vs. global scopes en `cdad.toml` puede llevar a comportamiento imprevisto si un entorno local no está correctamente configurado durante las pruebas.

## Gate de Test Audit
- [x] Cada test modificado justificado en spec.md
- [x] Tests untouched listados explícitamente
- [x] Regression risk assessment completado
