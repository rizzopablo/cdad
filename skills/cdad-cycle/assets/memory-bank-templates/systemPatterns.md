# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto. Este archivo se carga al inicio de cada sesión de agente.

## Capas y boundaries

<TODO: describir las capas arquitectónicas del proyecto y qué importa de qué. Ejemplo:

- `domain/` — lógica de negocio pura, no importa de adapters/ ni framework/
- `adapters/` — integraciones con sistemas externos
- `framework/` — wiring del framework, importa de domain y adapters
- `presentation/` — controllers/views, importa de framework
>

## Convenciones de código

### Naming

<TODO>

### Organización de archivos

<TODO>

### Errores y excepciones

<TODO: ¿excepciones tipadas? ¿result types? ¿qué se logea?>

## Patrones del framework

<TODO: cómo se usa el mecanismo de extensión del framework principal — herencia, hooks, signals, plugins. Qué patrones se prefieren y cuáles se evitan.>

## Convenciones de tests

- **Framework**: <TODO>
- **Estructura**: <TODO: tests unitarios en X, integración en Y, E2E en Z>
- **Fixtures**: <TODO: cómo se construyen, qué patrón se usa>
- **Property tests**: <TODO si aplica: librería usada, dónde van>

## Tooling enforcement

<TODO: linters, type checkers, import-linter, pre-commit hooks. Qué corre en CI.>

## Anti-patrones del proyecto

<TODO: cosas que históricamente este proyecto evita por buenas razones. Documentar el motivo.>

---

Última actualización: <YYYY-MM-DD>
