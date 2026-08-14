# ADR-005: Modelos de los agentes CDAD vía mofgw (gateway propio)

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: el usuario (dueño del proyecto) + el orquestador

## Contexto

ADR-001 eligió provider `bailian` directo ("sin proxy router") para preservar el
override de modelo por etapa: el proxy router rota modelos y rompería el invariante
reviewer ≠ implementer. El proyecto opera un gateway propio (mofgw,
`http://<GATEWAY_URL>/v1`) que da resiliencia de proxy (failover). El tráfico
debe ir por el gateway, no directo al upstream.

## Opciones consideradas

### Opción A: Mantener bailian directo (status quo)
- Pros: cero cambios; decisión ya documentada en ADR-001.
- Contras: sin resiliencia de proxy; el tráfico no pasa por el gateway propio.

### Opción B: Swap provider a mofgw
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

## Razones

1. Resiliencia del proxy vía gateway propio: el tráfico de modelos pasa por
   mofgw (failover), no directo al upstream bailian; el proyecto ya opera ese
   gateway y es la ruta de salida deseada.
2. Mismo modelo id por etapa preserva el invariante reviewer ≠ implementer:
   el id (deepseek-v4-flash, qwen3.7-plus, etc.) no cambia al swap de provider,
   solo el prefijo `mofgw/`.
3. El formato `provider/model` de opencode obliga a elegir provider — mofgw es
   el elegido para este deploy; cada deploy que no lo use debe overridear la
   config `agent.<nombre>.model`.

## Consecuencias

**Positivas:**
- Resiliencia del gateway (failover de proxy).
- Modelo id preservado por etapa; el invariante reviewer ≠ implementer
  (ADR-001) se mantiene (verificación realizada 2026-08-05).
- Un solo punto de entrada para el tráfico de modelos.

**Negativas / trade-offs:**
- Si mofgw no corre, los agentes fallan (dependencia de disponibilidad del
  gateway local).
- Cada deploy debe definir/overridear el provider si no usa mofgw (override por
  config `agent.<nombre>.model`).

**Neutrales:**
- La identidad por etapa se mantiene igual: mismos modelos, mismo mapeo rol →
  modelo; solo cambia el provider en el campo `model:`.

## Verificación (realizada 2026-08-05)

El dueño del proyecto confirmó que mofgw preserva la identidad del modelo en
failover (no sustituye silenciosamente por otro modelo). Por lo tanto, el
invariante CDAD reviewer ≠ implementer (ADR-001) se mantiene: `qwen3.7-plus`
(reviewer) y `deepseek-v4-flash` (implementer) no se intercambian.

## Notas

Supersede la cláusula de provider de ADR-001 (elección de bailian directo). La
asignación de modelos por etapa (ADR-001) no cambia.
