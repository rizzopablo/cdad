# Project Brief — CDAD-CLI

## ¿Qué es?

CDAD-CLI es un orquestador de línea de comandos escrito en Python que implementa la metodología **Contract-Driven AI Development (CDAD)**. Coordina agentes de IA aislados para construir software de forma iterativa utilizando especificaciones, tests y validación automática.

**Principio central**: cada agente solo ve los archivos relevantes a su rol (aislamiento por *context narrowing*). Los contratos (especificaciones con postcondiciones verificables) son la fuente de verdad que garantiza la disciplina del proceso.

## Alcance

### Fase 1 MVP (completada — 2026-05-01)

- CLI autónoma sin dependencia de IDE (independiente de OpenCode/Claude Code)
- 4 comandos operativos: `init`, `spec`, `architect`, `test`
- 2 agentes implementados: ArchitectAgent, TestWriterAgent
- Registro de presets: `generic`, `django`, `odoo`
- Validadores: SpecValidator, TestValidator
- 88 tests pasando, 78% de cobertura

### Fase 1+ (planificada)

- Comandos: `red`, `green`, `review`, `merge` (scaffolding existente, implementación pendiente)
- ImplementerAgent, ReviewerAgent, ScribeAgent (clases base listas)
- Workflow completo CDAD de extremo a extremo

### No incluido (fuera de alcance actual)

- Integración con editores/IDE específicos
- Soporte para lenguajes no-Python en el análisis de código
- UI gráfica o web
- Multi-agente simultáneo (orquestación secuencial actual)

## Restricciones

| Restricción | Racional |
|---|---|
| Python ≥ 3.9 | Público objetivo: desarrolladores Python/Odoo |
| Sin dependencias de IDE | CDAD debe funcionar en cualquier entorno |
| Aislamiento por contexto | Los agentes no ven archivos fuera de su rol |
| Specs como fuente de verdad | Sin postcondiciones verificables → no hay progreso |
| Tests deben fallar primero (RED) | Garantiza que los tests verifican comportamiento nuevo |

## Estado Actual

- **Versión**: 0.1.0
- **Último hito**: Phase 1 MVP completado (2026-05-01)
- **88 tests** pasando, **78% coverage**
- **Stack**: Typer (CLI), Anthropic SDK (LLM), pytest (tests)
- **CDAD aplicándose a sí mismo**: siguiente iteración usará el propio CLI para desarrollar nuevas features
