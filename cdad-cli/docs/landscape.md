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
