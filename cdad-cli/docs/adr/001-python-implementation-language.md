# ADR-001: Python como Lenguaje de Implementación

**Fecha**: 2026-01-15  
**Estado**: Aceptado  
**Contexto**: CDAD-CLI §2.5, Phase 1 MVP

## Contexto

Se necesitaba elegir un lenguaje de implementación para cdad-cli, un orquestador de agentes de IA que coordina desarrollo de software mediante especificaciones con contratos verificables.

**Requisitos**:
- Ejecutarse como CLI independiente (sin IDE)
- Analizar código Python (AST parsing)
- Integrarse con pytest para validación de tests
- Comunicarse con API de Anthropic (Claude)
- Ser desarrollado por el propio cdad-cli en iteraciones futuras (dogfooding)

## Decisión

Implementar cdad-cli en **Python 3.9+**.

## Racional

1. **Público objetivo**: desarrolladores Python/Odoo que ya tienen entornos Python configurados
2. **Análisis AST nativo**: Python tiene `ast` module en stdlib para parsear código Python sin dependencias externas
3. **Integración pytest**: los tests generados por agentes son nativamente compatibles con validación
4. **SDK Anthropic maduro**: excelente documentación, type hints, manejo de errores
5. **Dogfooding inmediato**: cdad-cli v0.1 puede desarrollar cdad-cli v0.2 porque ambos son Python

## Alternativas Rechazadas

### Go
- **Pro**: binarios independientes, rápido, bueno para CLI
- **Contra**: infraestructura excesiva para un CLI I/O-bound; no tiene parsing AST de Python nativo; distribución a usuarios Python sería más compleja

### TypeScript
- **Pro**: buen tooling, ecosystem npm grande, async nativo
- **Contra**: sin parsing AST de Python; distribución más compleja para usuarios Python-centric; requiere Node.js como dependencia runtime

### Rust
- **Pro**: rendimiento, seguridad de memoria, binarios independientes
- **Contra**: overhead de compilación durante desarrollo iterativo CDAD; curva de aprendizaje empinada para agentes de IA; tiempo de compilación ralentiza el ciclo RED→GREEN

### Bash
- **Pro**: disponible en cualquier Unix, sin dependencias
- **Contra**: sin abstracciones; frágil para orquestación compleja de workflows; imposible de analizar con AST; difícil de testear

## Consecuencias

- **Positivas**: desarrollo rápido, integración nativa con herramientas Python, dogfooding inmediato
- **Negativas**: dependencias de Python gestionadas por usuario final; performance inferior a Go/Rust (no relevante para CLI I/O-bound)
- **Mitigación**: `pyproject.toml` con dependencias claras; instalación con `pip install -e ".[dev]"`
