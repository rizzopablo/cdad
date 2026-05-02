# System Patterns — CDAD-CLI

## Agent Pattern

Todos los agentes heredan de `BaseAgent` (`src/cdad/agents/base.py`), una clase abstracta que define:

```python
class BaseAgent(ABC):
    @abstractmethod
    def get_accessible_files(self) -> List[Path]: ...
    @abstractmethod
    def get_system_prompt(self) -> str: ...
    def invoke(self, user_message: str) -> str: ...
    def get_context(self) -> str: ...
```

**Principio**: cada agente solo ve archivos relevantes a su rol. Esto se implementa por *context narrowing* (no sandboxing). El sistema confía en que el agente respete sus instrucciones; los validadores (`SpecValidator`, `TestValidator`) detectan violaciones de contrato.

**Agentes implementados**:

| Agente | Archivos accesibles | Prompt clave |
|---|---|---|
| ArchitectAgent | README, docs/, specs existentes | "Eres un arquitecto de software experto en CDAD" |
| TestWriterAgent | specs, tests existentes, pyproject.toml | "Eres un ingeniero de tests senior escribiendo pytest" |

**Agentes planificados**: ImplementerAgent, ReviewerAgent, ScribeAgent.

## CLI Pattern

CLI construida con **Typer** (`src/cdad/cli/main.py`). Cada comando sigue la misma estructura:

1. **Parsear argumentos** → Typer decoradores `@app.command()`
2. **Cargar proyecto** → `_load_project()` → `ProjectModel`
3. **Validar prerequisitos** → API key, archivos existentes
4. **Invocar agente** → Instanciar agente con `ProjectModel` + `LLMClient`
5. **Escribir resultado** → Archivo en `docs/` o `tests/`
6. **Reportar estado** → `typer.echo()` con emojis para feedback visual

**Patrón de factory**: `_make_llm_client()` permite monkey-patching en tests para evitar llamadas reales a la API.

## Preset Pattern

Los frameworks se detectan mediante un registro de presets (`src/cdad/presets/__init__.py`):

```python
REGISTRY: list[Preset] = [ODOO, DJANGO, GENERIC]
```

Cada `Preset` define:
- `manifest_files`: archivos que identifican el framework en el root
- `source_dirs`: directorios de código fuente convencionales
- `test_dirs`: directorios de tests convencionales

**Primera coincidencia gana** — por eso ODOO y DJANGO están antes de GENERIC.

## Validator Pattern

Los validadores son clases stateless que devuelven dataclasses de resultado:

```python
@dataclass
class SpecValidationResult:
    is_valid: bool
    postconditions: List[Postcondition]
    errors: List[str]
```

**SpecValidator**:
- Extrae sección `## Postconditions` con regex
- Parsea cada postcondición (**Name**, **Description**, **Verification**)
- Rechaza lenguaje vago (`properly`, `correctly`, etc.)
- Valida método de verificación contra lista permitida

**TestValidator**:
- Ejecuta `pytest` como subprocess
- Parsea output para contar PASSED/FAILED
- Devuelve `TestResult(passed, failed, errors)`

## ProjectModel Pattern

`ProjectModel` es el modelo central del dominio:

- Lee `pyproject.toml` para nombre del proyecto
- Detecta framework via `Preset.matches()`
- Lista specs (`docs/specs/*.md`) y tests (`tests/test_*.py`)
- Navega Memory Bank (`AGENTS.md`)

## PhaseManager Pattern

Máquina de estados finita con transiciones predefinidas:

```
none → discovery → spec → red → green → review → merge
```

Cada fase sabe cuál es la siguiente. `PhaseManager.suggest_next_command()` devuelve el comando CLI recomendado.
