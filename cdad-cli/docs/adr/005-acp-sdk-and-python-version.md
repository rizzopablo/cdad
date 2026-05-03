# ADR-005: Selección de SDK ACP y versión mínima de Python

**Fecha**: 2026-05-03
**Estado**: Aceptado
**Feature**: 002-llm-provider-abstraction

## Contexto

El spec 002 requiere soporte para Agent Client Protocol (ACP) como proveedor de LLM para agentes externos (Claude Code, Gemini CLI, Codex, Qwen).

Inicialmente el spec mencionaba `acp-sdk` como SDK Python. Durante la segunda pasada de review se descubrió que el nombre del paquete era incorrecto.

## Decisión

Se usa `agent-client-protocol` (módulo `acp`), no `acp-sdk`.

**Razón**: `acp-sdk` en PyPI es un proyecto de IBM/BeeAI — es un cliente HTTP para servidores ACP remotos, NO un cliente stdio para spawnear subprocesses locales.

El SDK correcto es `agent-client-protocol` que implementa el protocolo de Zed Industries con:
- `acp.spawn_agent_process()` para spawnear subprocesses
- `acp.Agent` con métodos: `initialize()`, `new_session()`, `prompt()`, `close_session()`
- `acp.RequestError` como única excepción

### Consecuencias

- **Python mínimo elevado a 3.11** (requerido por `agent-client-protocol`)
- El spec 002 fue corregido para reflejar el nombre correcto del paquete
- Extra de instalación: `cdad[acp]` instala `agent-client-protocol`
- El ACPProvider implementa el protocolo completo: initialize → new_session → prompt → close_session

## Alternativas consideradas

1. **Implementar ACP manualmente en Python puro** → descartada: SDK ya existe y es estable
2. **Usar `acp-sdk` (IBM)** → descartada: no implementa el protocolo stdio que necesitamos
3. **Wrapper sobre CLI** → descartada: ACP es más rico que comunicación por línea de comandos
