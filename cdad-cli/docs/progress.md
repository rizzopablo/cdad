# Progress — CDAD-CLI

## Completed (Feature 002 — 2026-05-03)

| Feature | Estado | Notas |
|---|---|---|
| `LLMProvider` Protocol | ✅ | `src/cdad/llm/provider.py` |
| Jerarquía de excepciones tipadas | ✅ | 6 clases en `provider.py` |
| `AnthropicProvider` | ✅ | Con mapeo de errores nativos |
| `OpenAIProvider` | ✅ | Con `base_url` configurable |
| `ACPProvider` | ✅ | Con protocolo completo (initialize→session→prompt→close) |
| Registry + resolución | ✅ | `src/cdad/llm/registry.py` |
| Defaults mixtos (3 providers) | ✅ | `registry.DEFAULT_AGENT_MODELS` |
| 60 tests para feature 002 | ✅ | 15 postcondiciones verificadas |

## Completed (Phase 1 MVP — 2026-05-01)

| Feature | Estado | Notas |
|---|---|---|
| Project initialization (`cdad init`) | ✅ | Crea estructura de directorios, detecta framework |
| Preset registry (generic, django, odoo) | ✅ | Detección automática por archivos manifest |
| ArchitectAgent — discover() | ✅ | Genera discovery de requirements |
| ArchitectAgent — draft_spec() | ✅ | Genera specs con postcondiciones |
| ArchitectAgent — analyze() | ✅ | Analiza código existente |
| ArchitectAgent — recommend() | ✅ | Genera recomendaciones priorizadas |
| SpecValidator | ✅ | Valida specs (postcondiciones, métodos de verificación, lenguaje vago) |
| TestWriterAgent — write_tests() | ✅ | Genera tests pytest desde spec validada |
| TestValidator | ✅ | Ejecuta pytest y detecta RED/GREEN |
| ProjectModel | ✅ | Lee estructura de proyecto, detecta framework, navega specs |
| LLMClient | ✅ | Wrapper de Anthropic SDK con historial de conversación |
| PhaseManager | ✅ | Detecta fase actual y sugiere siguiente comando |
| CLI commands (init, spec, architect, test) | ✅ | Implementación completa con Typer |
| CLI commands (red, green) | ✅ | Scaffolding funcional sin agentes dedicados |
| BaseAgent (clase abstracta) | ✅ | Base para todos los agentes |
| 88 tests | ✅ | 78% de cobertura |

## In Progress

| Feature | Estado | Notas |
|---|---|---|
| Memory Bank files | 🚧 | Documentación de feature 002 completada |

## Planned (Phase 1+)

| Feature | Prioridad | Notas |
|---|---|---|
| Dogfooding | Alta | **Iniciado con feature 002** — usar cdad-cli para desarrollar cdad-cli v0.2 |
| ReviewerAgent | Alta | Review de feature 002 fue exitoso; automatizar como agente |
| ScribeAgent | Media | Actualizar Memory Bank automáticamente después de merge |
| Soporte async | Baja | Typer soporta async; podría paralelizar agentes |
| Presets adicionales | Baja | FastAPI, Flask, otros frameworks Python |

## Blocked

Ninguna feature bloqueada actualmente.

## Dependencies entre features

```
cdad init
  ↓
cdad discover (ArchitectAgent)
  ↓
cdad spec (ArchitectAgent + SpecValidator)
  ↓
cdad test (TestWriterAgent) ←— requiere spec válida
  ↓
cdad red (TestValidator)
  ↓
cdad green (TestValidator) ←— requiere ImplementerAgent (pendiente)
  ↓
cdad review (ReviewerAgent) ←— pendiente
  ↓
cdad merge (ScribeAgent) ←— pendiente
```
