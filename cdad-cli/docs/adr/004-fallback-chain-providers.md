---
status: accepted
date: 2026-05-03
deciders: feature-004-team
---

# ADR-004: Fallback Chain para Resolución de Providers

## Contexto

Los comandos CLI (`discover`, `spec`, `architect`, `test`) necesitaban un mecanismo para resolver providers sin requerir configuración explícita por cada rol. El spec v1 requería configuración individual, generando fricción para usuarios con setups simples (un solo provider para todos los roles).

## Decisión

Se introdujo el rol especial `default` en el registry con semántica de fallback:

1. Precedencia: `override` > env var `CDAD_AGENT_<ROLE>` > `config["agents"][role]` > `config["agents"]["default"]` > `ConfigurationError`
2. El rol `default` es válido en `resolve_provider()` y se resuelve como cualquier otro provider.
3. Los comandos `config auto` y `config set` permiten asignar a `default`, pero no pre-poblan otros roles.

## Consecuencias

**Positivas:**

- Configuración mínima viable: un solo `default = "anthropic/claude-opus-4-7"` soporta todos los roles.
- Retrocompatibilidad: setups existentes con roles explícitos siguen funcionando.
- Predecibilidad: la precedencia es estricta, documentada y verificable (Invariante 4).

**Negativas:**

- Riesgo de sorpresa: un usuario puede esperar comportamiento diferenciado por rol pero obtener el fallback silencioso.
- Complejidad en debugging: el origen de un provider resuelto requiere trazar 4 niveles de precedencia.
- No hay warnings cuando se activa fallback (aunque el spec lo permita, es una UX debt).

## Alternativas consideradas

- **Requerir configuración explícita por rol**: rechazada por fricción excesiva para setups homogéneos.
- **Herencia por prefijo (`architect.*`)**: rechazada por complejidad en parsing y merge de TOML.
- **Configuración jerárquica nested**: rechazada por sobre-diseño; el 90% de casos se cubren con flat + default.
