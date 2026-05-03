# Active Context — CDAD-CLI

## Feature 002: LLM Provider Abstraction (2026-05-03)

**Completada.** Abstracción de proveedores LLM para cdad-cli usando Protocol + Registry pattern.

### Qué se implementó

| Componente | Descripción |
|---|---|
| `LLMProvider` Protocol | Interface verificable para providers |
| Jerarquía de excepciones | `ProviderError`, `ProviderAuthError`, `ProviderRateLimitError`, `ProviderTransportError`, `ProviderResponseError`, `ConfigurationError` |
| `AnthropicProvider` | Wrapper de Anthropic SDK con mapeo de errores |
| `OpenAIProvider` | Wrapper de OpenAI SDK con `base_url` configurable (Azure, OpenRouter, Ollama) |
| `ACPProvider` | Agente ACP vía `agent-client-protocol` con protocolo completo: initialize → new_session → prompt → close_session |
| Registry | `register()` + `resolve_provider()` con precedencia: env var → config → defaults |
| Defaults mixtos | architect=anthropic, implementer=acp, reviewer=openai, scribe=acp/qwen |

### Métricas

- Tests: **60 passing** (feature 002), **158 total suite**
- Cobertura: **76%** (umbral era 78%, cerca)
- Postcondiciones: **15/15 verificadas**
- Bloqueantes resueltos: **4/4** (incluyendo corrección de paquete ACP)

### Decisiones

- Se usó `agent-client-protocol` (módulo `acp`) en vez de `acp-sdk` (que era de IBM/BeeAI)
- Python ≥ 3.11 requerido por `agent-client-protocol`
- Qwen soporta ACP (confirmado en Zed), no solo OpenAI-compatible

---

## Estado Anterior (Phase 1 MVP — 2026-05-01)

**Phase 1 MVP completado.** El CLI tiene 4 comandos funcionales y 2 agentes implementados. 88 tests pasando con 78% de cobertura.

### Qué funciona ahora

| Comando | Estado | Agente | Descripción |
|---|---|---|---|
| `cdad init` | ✅ Completo | — | Inicializa proyecto CDAD, detecta framework |
| `cdad spec` | ✅ Completo | ArchitectAgent | Genera specs con postcondiciones verificables |
| `cdad architect` | ✅ Completo | ArchitectAgent | Analiza código y recomienda mejoras |
| `cdad test` | ✅ Completo | TestWriterAgent | Genera tests pytest desde spec validada |
| `cdad red` | ⚠️ Scaffolding | — | Valida specs y ejecuta tests |
| `cdad green` | ⚠️ Scaffolding | — | Ejecuta tests y verifica GREEN |
| `cdad review` | 🚧 Placeholder | — | Pendiente: ReviewerAgent |
| `cdad merge` | 🚧 Placeholder | — | Pendiente: ScribeAgent |

### Presets activos

- **generic**: proyectos Python genéricos (detecta `pyproject.toml` / `setup.py`)
- **odoo**: addons de Odoo (detecta `__manifest__.py` / `__openerp__.py`)
- **django**: proyectos Django (detecta `manage.py`)

### Métricas

- Tests: **88 passing**
- Cobertura: **78%**
- Archivos de código fuente: ~25 archivos Python
- Agentes: 2 de 5 implementados
- Comandos: 4 completos, 4 scaffolding

### Próximo paso inmediato

Desarrollar `ImplementerAgent` y completar el ciclo RED→GREEN usando el propio CDAD-CLI (dogfooding).

### Riesgos actuales

1. **API Anthropic**: todos los agentes que usan LLM requieren `ANTHROPIC_API_KEY`. Sin ella, los comandos fallan silenciosamente.
2. **Validación de specs**: el SpecValidator es estricto pero puede rechazar specs válidas con formato ligeramente diferente.
3. **Cobertura al 78%**: faltan tests para comandos `red`/`green`/`review`/`merge` y para `PhaseManager`.

### Decisiones recientes

- Se eligió **context narrowing** sobre sandboxing para aislamiento de agentes (ADR-003)
- Se priorizó **ArchitectAgent + TestWriterAgent** como primer par de agentes (ciclo descubrimiento → spec → tests)
- Se estableció **pytest como validador de tests** (RED/GREEN se detecta por código de salida de pytest)
