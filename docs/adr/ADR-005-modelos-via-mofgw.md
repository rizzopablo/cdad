# ADR-005: Modelos de los agentes CDAD vía mofgw (gateway propio)

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: Pablo (dueño del proyecto) + Ofap

## Contexto

ADR-001 eligió provider `bailian` directo ("no omniroute") para preservar el
override de modelo por etapa: omniroute rota modelos y rompería el invariante
reviewer ≠ implementer. El proyecto opera un gateway propio (mofgw,
`http://localhost:3369/v1`) que da resiliencia de proxy (failover). El tráfico
debe ir por el gateway, no directo al upstream.

## Opciones consideradas

### Opción A: Mantener bailian directo (status quo)
- Pros: cero cambios; decisión ya documentada en ADR-001.
- Contras: sin resiliencia de proxy; el tráfico no pasa por el gateway propio.

### Opción B: Swap provider a mofgw (recomendada)
- Pros: resiliencia del proxy (failover); mismo modelo id (deepseek-v4-pro,
  deepseek-v4-flash, glm-5.2, qwen3.7-plus); un solo punto de entrada.
- Contras: si mofgw no corre, los agentes fallan; cada deploy debe definir el
  provider si no usa mofgw (override por config `agent.<nombre>.model`).

### Opción C: Id pelado sin provider (descartada)
- Pros: aparente simplicidad de escritura.
- Contras: opencode requiere el formato `provider/model`; además hay colisión
  de ids entre bailian y mofgw → no resuelve.

## Decisión

Los 5 agentes CDAD usan `model: mofgw/<modelo>` (architect, test-writer,
implementer, reviewer, scribe). El orquestador sigue sin modelo fijo (lo elige
el usuario). La tabla "Familia modelo" del Contrato de roles queda
provider-agnóstica (nombres sin provider).

## Consecuencias

**Positivas:**
- Resiliencia del gateway (failover de proxy).
- Modelo id preservado por etapa; el invariante reviewer ≠ implementer
  (ADR-001) se mantiene (sujeto a la verificación pendiente).
- Un solo punto de entrada para el tráfico de modelos.

**Negativas / trade-offs:**
- Si mofgw no corre, los agentes fallan (dependencia de disponibilidad del
  gateway local).
- Cada deploy debe definir/overridear el provider si no usa mofgw (override por
  config `agent.<nombre>.model`).

**Neutrales:**
- La identidad por etapa se mantiene igual: mismos modelos, mismo mapeo rol →
  modelo; solo cambia el provider en el campo `model:`.

## Verificación pendiente

Confirmar que mofgw preserva la identidad del modelo en failover (no sustituye
silenciosamente por otro modelo), porque el invariante CDAD reviewer ≠
implementer (ADR-001) depende de que `qwen3.7-plus` y `deepseek-v4-flash`
lleguen como tales. Si mofgw rotara modelos como omniroute, ese invariante se
rompería.

## Notas

Supersede la cláusula de provider de ADR-001 (elección de bailian directo). La
asignación de modelos por etapa (ADR-001) no cambia.
