---
feature_id: 003-implementer-agent
feature_name: ImplementerAgent + cdad green
created_at: 2026-05-03
approved_by: rizzopablo
approved_at: 2026-05-03
---

# Spec: ImplementerAgent + comando `cdad green`

## Descripción funcional

El `ImplementerAgent` es el agente responsable de cerrar el ciclo RED→GREEN del flujo CDAD. Recibe un spec aprobado y una suite de tests RED, y genera/modifica código bajo `src/` hasta que la suite completa esté GREEN. Itera evaluando los resultados de pytest, ajustando código, y deteniéndose cuando alcanza GREEN, agota intentos, o detecta sospecha de tests obsoletos. El comando `cdad green` orquesta el agente desde la CLI.

El agente **nunca modifica archivos bajo `tests/`**. Si sospecha que un test es obsoleto (ej. referencia postcondiciones de specs ya cerrados), reporta la sospecha al orquestador para que un humano decida si vuelve al `TestWriterAgent`.

## Contrato (firma e invariantes)

**Firma del agente:**

```python
class ImplementerAgent(BaseAgent):
    def implement(
        self,
        spec_path: Path,
        max_iterations: int = 5,
        provider_override: str | None = None,
    ) -> ImplementResult: ...

    # Heredados de BaseAgent (abstractos), implementados acá:
    def get_accessible_files(self) -> list[Path]: ...
    def get_system_prompt(self) -> str: ...
```

**Tipo `ImplementResult`** (dataclass):

```python
@dataclass
class ImplementResult:
    success: bool
    iterations_used: int
    files_modified: list[Path]
    final_test_output: str
    error: str | None
    obsolescence_suspicions: list[ObsolescenceSuspicion]

@dataclass
class ObsolescenceSuspicion:
    test_path: Path
    reason: str         # ej. "references_closed_spec"
    evidence: str       # snippet o referencia textual
```

**Comando CLI:**

```
cdad green [--spec PATH] [--max-iterations N] [--provider STR]
```

- `--spec`: si se omite, usa `active_feature` de `.cdad-state.json`.
- `--max-iterations`: default 5.
- `--provider`: ej. `acp/qwen`, `anthropic/claude-opus-4-7`. Override de máxima prioridad sobre la cadena env→toml→defaults.

**Cadena de resolución del provider** (de mayor a menor prioridad):

1. Argumento `--provider` del CLI (`provider_override` en el agente).
2. Variable de entorno `CDAD_AGENT_IMPLEMENTER`.
3. Sección `[agents]` en `cdad.toml`, clave `implementer`.
4. `DEFAULT_AGENT_MODELS["implementer"]` (= `"acp/qwen"` tras esta feature).

**Postcondiciones (numeradas y verificables):**

1. Si la suite de tests está GREEN antes de cualquier iteración, retorna `ImplementResult(success=True, iterations_used=0, files_modified=[], obsolescence_suspicions=[])`.
2. Si tras una o más iteraciones la suite alcanza GREEN, retorna `success=True` con `iterations_used > 0` y `files_modified` listando todos los paths bajo `src/` creados o modificados.
3. Si tras `max_iterations` iteraciones la suite sigue RED, retorna `success=False` con `error="max_iterations_reached"` y `final_test_output` conteniendo el output del último `pytest`.
4. Si el agente intenta escribir un path bajo `tests/`, el agente NO aplica el cambio y retorna `success=False` con `error="test_modification_forbidden:<path>"` y registra el intento en `implement.log`.
5. Si el agente, tras al menos una iteración fallida, identifica heurísticamente un test que referencia postcondiciones de specs cerrados (formato `PC-NNN-X` donde `NNN ≠ active_feature_number`) cuyo comportamiento contradice el spec activo, agrega una entrada a `obsolescence_suspicions` y retorna `success=False` con `error="test_obsolescence_suspected"`.
6. Si el spec en `spec_path` no existe o no es válido (sin postcondiciones), el agente lanza `SpecNotFoundError` o `InvalidSpecError`. NO ejecuta tests ni invoca al provider.
7. Si el provider falla con `ProviderError` (de feature 002), el agente captura, retorna `success=False` con `error="provider_error: <message>"` y `iterations_used` reflejando los intentos previos exitosos.
8. El agente registra cada iteración en `docs/specs/<feature-id>/implement.log` en formato **NDJSON** (una línea JSON por iteración) con campos fijos: `timestamp` (ISO 8601), `iteration` (int), `pytest_passed` (int), `pytest_failed` (int), `files_modified` (list[str]), `provider_call_duration_s` (float), `notes` (str).
9. El agente imprime progreso a stdout en tiempo real (al menos: inicio de iteración, resultado de pytest resumido, archivos modificados).
10. El default de `DEFAULT_AGENT_MODELS["implementer"]` es `"acp/qwen"`.
11. El builtin `qwen` en `get_builtin_acp_command` retorna `["qwen", "--acp"]` (verificado contra `qwen` v0.12.3+ que expone el flag `--acp` nativamente).
12. La función `resolve_provider` acepta un parámetro adicional `override: str | None = None`. Si se pasa, tiene precedencia sobre env, config y defaults.
13. El comando `cdad green` retorna exit code `0` si `success=True`, `1` si `success=False` por `max_iterations_reached` o `test_obsolescence_suspected`, `2` si error de configuración (provider no resoluble, spec no encontrado, API key faltante, `--spec` omitido y `.cdad-state.json` ausente o sin `active_feature`).
14. El campo `requires-python` en `pyproject.toml` se actualiza a `">=3.11"` (ya requerido por feature 002 vía ACP SDK pero pendiente de reconciliar).

## Invariantes verificables

- ∀ ejecución del agente: ningún archivo bajo `tests/` (ni `tests/**/*.py`, ni `conftest.py` bajo `tests/`) es modificado, creado, o eliminado por el agente. Validable con property test que invoca `implement()` con secuencias arbitrarias de respuestas del fake provider y verifica el árbol de `tests/` post-ejecución.
- ∀ ejecución que retorna `success=True`: la suite `pytest` retorna exit code 0.
- ∀ ejecución: `iterations_used ≤ max_iterations`.
- ∀ ejecución que retorna `success=True`: cada path en `files_modified` está bajo `src/`.

## Criterios de aceptación

- [ ] Test unitario para cada una de las 14 postcondiciones pasa.
- [ ] Property test con 100 secuencias random de respuestas del `FakeACPProvider` verifica el invariante "no toca tests/".
- [ ] Cobertura de líneas en `src/cdad/agents/implementer.py` ≥ 90%.
- [ ] Cobertura global de la suite ≥ 80%.
- [ ] Test de integración (marcado `@pytest.mark.integration`, opt-in) ejecuta el comando `cdad green` contra una mini-spec de juguete usando `qwen --acp` real y verifica que la suite quede GREEN.
- [ ] Comando `cdad green` ejecutable y documentado en `cdad --help`.
- [ ] Archivo `implement.log` se genera correctamente bajo `docs/specs/<feature-id>/` en formato NDJSON parseable.

## Out of scope

- **Refactor automático del código generado**. El agente busca GREEN, no calidad estructural. El refactor queda para Etapa 4 (Review) que puede levantar bloqueantes y devolverlos a un humano. Una `004-refactor-agent` futura podría automatizarlo.
- **Retry strategies sofisticadas**: backoff exponencial, prompts variantes por iteración, switching de provider en runtime. Cada iteración usa el mismo provider y el mismo prompt template.
- **Auto-fallback de provider** si el provider configurado no está disponible. El agente falla con mensaje claro; el humano decide.
- **Paralelismo / concurrencia**: el agente es estrictamente secuencial. Una sola invocación al provider a la vez.
- **Métricas de calidad del código**: complejidad ciclomática, duplicación, etc. Out of scope.
- **Auto-corrección de tests obsoletos**. El agente solo reporta sospechas; el humano decide.
- **Modificación de archivos fuera de `src/`**: no toca `pyproject.toml` (excepto la actualización puntual de PC 14), `docs/`, `.cdad-state.json`, ni nada fuera de `src/`.

## Notas de implementación

### Justificación del cambio de default a `acp/qwen`

Feature 002 dejó `implementer: "acp/claude"` como placeholder. Esta feature lo cambia a `"acp/qwen"` por: (a) qwen-coder es el modelo CLI con mejor relación costo/calidad para tareas de codegen iterativo a la fecha; (b) usar ACP local (`qwen --acp`) elimina dependencia de API keys cloud para el agente más invocado del flujo; (c) el usuario tiene `qwen` v0.12.3 instalado y validado en su entorno de desarrollo. Documentar como ADR-006 al cerrar la feature.

### `FakeACPProvider` — interface mínima

Para tests unitarios y property tests:

```python
class FakeACPProvider(LLMProvider):
    def __init__(self, scripted_responses: list[str]): ...
    # Cada call a complete() consume una respuesta de la lista en orden.
    # Si se agotan, lanza IndexError (test mal configurado).
    # Implementa la misma interfaz que LLMProvider de feature 002.
```

### Bucle de iteración

Cada iteración: (a) corre `pytest` capturando stdout/stderr y exit code, (b) si RED, construye prompt con spec + tests + output de pytest + listado de archivos en `src/`, (c) invoca al provider, (d) parsea respuesta extrayendo cambios de archivos (formato esperado: bloques de código con header `### file: src/foo.py`), (e) **valida que ningún path esté bajo `tests/`** antes de aplicar, (f) aplica cambios al filesystem, (g) repite.

### Detección de obsolescencia

Heurística simple: regex sobre el contenido de los tests fallidos buscando referencias `PC-NNN-X` con `NNN ≠ active_feature_number`. No es garantía, es señal. El humano decide.

### Reemplazo de `_make_llm_client` legacy

El CLI actual tiene `_make_llm_client(api_key)` que crea un cliente Anthropic legacy. `cdad green` NO lo usa: invoca directamente `resolve_provider("implementer", override=...)` del registry. Documentar para que features futuras hagan migración progresiva del resto de comandos al registry.

### Manejo del state file ausente

Si `--spec` se omite y `docs/.cdad-state.json` no existe, o existe pero `active_feature` es `null`, el CLI imprime mensaje claro: `"No active feature. Pass --spec PATH or initialize a feature first."` y retorna exit code 2.

## Contexto técnico

### Módulos que toca

- **Crea**:
  - `src/cdad/agents/implementer.py` — agente.
  - `src/cdad/cli/green.py` — comando.
  - `tests/agents/test_implementer.py` — tests unitarios.
  - `tests/cli/test_green.py` — tests del comando.
  - `tests/fakes/fake_acp_provider.py` — fake determinista (si no existe ya en conftest).
- **Modifica**:
  - `src/cdad/llm/registry.py` — cambia default `implementer`, builtin `qwen`, agrega parámetro `override` a `resolve_provider`.
  - `src/cdad/cli/__init__.py` (o `main.py`) — registra comando `green`.
  - `pyproject.toml` — `requires-python = ">=3.11"`.

### Dependencias del runtime

- `pytest` ya disponible.
- `agent-client-protocol` ya disponible (feature 002).
- `qwen` CLI v0.12.3+ con flag `--acp` (verificado).

### Convenciones

- Tipos en todas las firmas públicas (mypy strict).
- Excepciones tipadas, no `Exception` genérico.
- Tests unitarios usan fakes deterministas, no mocks de comportamiento.
- Tests de integración con `@pytest.mark.integration`, skipean si `qwen` no instalado.

### Gotchas

- `pytest` debe correrse desde la raíz del proyecto (ya validado en feature 001 con `TestValidator`).
- El parsing de respuesta del LLM puede ser frágil; documentar formato esperado en docstring del agente.
- `_AGENT_ACCESS_POLICY` en `project/model.py` ya tiene la entrada `"implementer": {"specs": True, "tests": True, "src": True, "discovery": False}` — coherente con la intención.

---

Status: Approved by rizzopablo on 2026-05-03
