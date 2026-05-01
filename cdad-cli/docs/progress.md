# Progress — CDAD-CLI

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
| CLI commands (review, merge) | 🚧 | Placeholders implementados, sin lógica real |
| Memory Bank files (CDAD spec §2.5) | 🚧 | Generando documentation completa |

## Planned (Phase 1+)

| Feature | Prioridad | Notas |
|---|---|---|
| ImplementerAgent | Alta | Agente que implementa código para pasar tests (GREEN phase) |
| ReviewerAgent | Alta | Compara implementación contra spec |
| ScribeAgent | Media | Actualiza Memory Bank después de merge |
| `cdad status` | Media | Ya implementado pero puede mejorarse |
| `cdad red` completo | Media | Integración con ImplementerAgent |
| `cdad green` completo | Media | Validación automática de GREEN phase |
| Dogfooding | Alta | Usar cdad-cli para desarrollar cdad-cli v0.2 |
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
