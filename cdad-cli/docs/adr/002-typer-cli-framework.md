# ADR-002: Typer como Framework de CLI

**Fecha**: 2026-01-15  
**Estado**: Aceptado  
**Contexto**: CDAD-CLI §2.5, Phase 1 MVP

## Contexto

Se necesitaba un framework para construir la interfaz de línea de comandos de cdad-cli. El CLI debe soportar:
- Múltiples comandos con subcomandos
- Argumentos opcionales y requeridos
- Help text automático
- Validación de tipos
- Posibilidad de async en el futuro

## Decisión

Usar **Typer 0.9.0** como framework de CLI.

## Racional

1. **API más limpia**: decoradores declarativos con type hints nativos de Python
2. **Help automático**: genera documentación de `--help` desde type hints y docstrings
3. **Integración de tipos**: valida tipos de argumentos automáticamente (no necesita validación manual)
4. **Soporte async**: Typer soporta comandos async nativamente (útil para agentes concurrentes en futuro)
5. **Basado en Click**: hereda la madurez y estabilidad de Click sin la verbosidad

## Alternativas Rechazadas

### argparse (stdlib)
- **Pro**: sin dependencias, disponible en Python stdlib
- **Contra**: API verbosa y anticuada; sin validación de tipos; help text limitado; sin soporte para subcomandos elegantes

### Click
- **Pro**: maduro, estable, usado por muchos proyectos (incluido Flask)
- **Contra**: API más verbosa que Typer; type hints no integrados naturalmente; más boilerplate por comando
- **Nota**: Typer usa Click internamente; se gana la abstracción sin perder capacidades

### argparse + custom parser
- **Pro**: control total, sin dependencias
- **Contra**: reinventar la rueda; más código para mantener; más bugs potenciales

## Consecuencias

- **Positivas**: código de CLI más legible y mantenible; type hints sirven para validación y documentación; async disponible cuando se necesite
- **Negativas**: dependencia de Typer (que depende de Click); Typer 0.9.0 es relativamente joven pero estable
- **Mitigación**: `click<8.2` fijado en dependencias para evitar breaking changes
