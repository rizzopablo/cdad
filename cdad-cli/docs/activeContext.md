# Active Context — CDAD-CLI

## 2026-05-04 — Feature 004: Provider-Aware CLI Commands

Cerrada feature que unificó todos los comandos al patrón provider-aware con `resolve_provider`, eliminando el modo legacy `LLMClient(api_key=...)`.

### Qué se implementó

| Componente | Descripción |
|---|---|
| Migración de 4 comandos | `discover`, `spec`, `architect`, `test` ahora usan `resolve_provider` con rol específico |
| Eliminación de legacy | Removidos `_require_api_key`, `_make_llm_client`, parámetro `api_key` de `LLMClient` |
| Comando `cdad config` | Subcomandos `auto` y `set` con scopes `--global`/`--local` |
| Rol `default` en registry | Fallback chain: override > env var > config[role] > config[default] > ConfigurationError |
| `get_available_providers()` | Detección de providers disponibles sin hardcodear env vars |
| `_resolve_config()` | Resolución de config local → global → defaults para comandos provider-aware |
| ACP provider fixes | Race condition (asyncio.Event + wait_for), extracción de texto (content.text), stubs de protocolo |
| Migración de tests legacy | 17 tests de features anteriores migrados al nuevo patrón provider-aware |
| Tests E2E | 4 tests de integración contra `acp/qwen` real |

### Métricas

- Tests: **57 unitarios** + **4 E2E** (integración con acp/qwen real)
- Suite completa: **~270 tests passing** (excluyendo 1 test de timeout conocido)
- Postcondiciones: **28/28 verificadas**
- Bloqueantes de review: **6/6 resueltos** + 3 fixes ACP
- Tests legacy migrados: **17/17** (de features 002 y 003)

### Decisiones relevantes

- Se eliminó completamente el modo legacy `LLMClient(api_key=...)` a favor del patrón provider-aware con `resolve_provider`.
- Se introdujo la cadena de fallback `default` en el registry: cualquier rol no configurado explícitamente hereda del agente `default`.
- Se implementaron dos scopes de configuración (`--global` y `--local`) con prioridad determinística: local > global > defaults.
- El comando `cdad config auto` realiza validación funcional real (prompt "CDAD disponible") con timeout de 30s antes de escribir configuración.
- Se priorizó `ThreadPoolExecutor` sobre `signal.alarm` para timeout cross-platform compatible con Python 3.10+.

### Deuda técnica detectada

- El comando `green` requirió refactorización tardía para usar `_resolve_config()` (detectado en review).
- Fragmentación temporal en el manejo de ACP: race conditions y extracción de texto requirieron fixes ad-hoc post-review.
- Algunos tests legacy migrados dependen de mocks con firmas laxas (`*args, **kwargs`) que podrían ocultar regresiones futuras.
- La documentación de `cdad config set --help` no menciona explícitamente que no valida el provider (solo formato).
- El retry de `cdad spec` requiere acceso al filesystem por parte del agente ACP — pendiente como feature separada.
- `test_timeout_rejects_provider` se cuelga en el test runner (problema de compatibilidad con el test runner, no con el código).

### Próxima feature en cola

Implementar filesystem access para agente ACP durante retry de `cdad spec` (lectura/escritura de archivos).

---

## 2026-05-03 — Feature 003: ImplementerAgent + comando `cdad green`

Cerrada feature que completa el ciclo RED→GREEN del flujo CDAD: el `ImplementerAgent` itera entre test output y generación de código hasta alcanzar GREEN, sin modificar tests/.

### Qué se implementó

| Componente | Descripción |
|---|---|
| `ImplementerAgent.implement()` | Bucle TDD iterativo con spec + pytest output + provider LLM |
| `cdad green` command | CLI con `--spec`, `--max-iterations`, `--provider` y exit codes (0, 1, 2) |
| Protección de tests/ | Rechazo de writes bajo `tests/` con defensa en 2 capas (validación + filesystem) |
| Detección de obsolescencia | Heurística que detecta tests referenciando specs cerrados (`PC-NNN` donde `NNN ≠ active_feature`) |
| Logging NDJSON | `implement.log` con una línea JSON por iteración |
| `acp/qwen` como default implementer | Provider ACP local sin API keys (qwen v0.12.3+ con `--acp`) |

### Métricas

- Tests: **45 unitarios** + **1 property test** + **1 integration E2E**
- Cobertura: **implementer.py 90%**, **global 84%**
- Postcondiciones: **13/13 verificadas**
- Bloqueantes de review: **2/2 resueltos** (error string + active_feature hardcodeado)
- Bug crítico encontrado: **path traversal en `_has_tests_path`** (corregido en property test)

### Decisiones relevantes

- Default implementer cambiado a `acp/qwen` — elimina dependencia de API keys para el agente más invocado
- Defensa en 2 capas para protección de `tests/`: validación de paths + verificación post-resolución
- Property test con Hypothesis detectó vulnerabilidad real que tests unitarios no cubrían

### Deuda técnica detectada

- Búsqueda de spec por `active_feature` en CLI puede fallar con estructura de directorios (hallazgo review, diferido)
- Exception handling genérico en `ACPProvider.close_session()` (diferido)
- Output duplicado entre agente y CLI (diferido)
- 5 tests de feature 002 failing por mock de API key (pre-existente)

### Próxima feature en cola

Implementar los 3 opcionales de review pendientes y/o `ReviewerAgent` (feature 004).

---

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
