# ADR-001: Modelo distinto por etapa CDAD (sub-agentes especializados)

- **Status**: Accepted
- **Date**: 2026-08-03
- **Deciders**: Pablo Rizzo + Ofap

> Nota (2026-08-05): la elección de provider directo a bailian fue superseded por ADR-005 — los modelos ahora corren vía mofgw.

## Contexto

CDAD recomienda explícitamente que cada etapa corra con perfil cognitivo adecuado y que el reviewer use un modelo distinto al implementer (anti-confirmation-bias). Con opencode/chamber el flujo funcionaba, pero todo pasaba por el agente `coder` con un solo modelo: no se podía asignar modelo por etapa. El TDD anti-trampa perdía fuerza (el mismo agente/modelo escribe test e implementación). Se necesitaban agentes especializados por etapa con `model` override por agente.

## Opciones consideradas

### Opción A: Un solo agente `coder` para todo (status quo)
- Pros: cero configuración, cero mantenimiento.
- Contras: sin modelo distinto por etapa; reviewer == implementer (mismo modelo); TDD anti-trampa es solo disciplina de prompt, no estructural.

### Opción B: Sub-agentes nativos de OpenCode, uno por rol CDAD, con model override
- Pros: aislamiento de sesión nativo (sub-agentes no ven contexto del padre); modelo fijo por etapa; permisos por glob; compatibilidad con el skill cdad-cycle existente.
- Contras: configuración adicional; dependencia del runtime (OpenCode); deuda de mantenimiento de N archivos de agente.

### Opción C: Framework externo de orquestación (harness)
- Pros: enforcement determinista de colusión.
- Contras: sobre-ingeniería para el MVP; research plan lo desaconsejó para MVP ("no necesita hash-chain ni framework externo").

## Decisión

Crear 5 sub-agentes OpenCode nativos (`cdad-architect`, `cdad-test-writer`, `cdad-implementer`, `cdad-reviewer`, `cdad-scribe`) en el repo fuente con `model: bailian/<modelo>` por agente, instalados via `install.sh`.

## Razones

1. Data empírica de Pablo: deepseek codea bien ("en general en todo"); lo más difícil es hacer buenos tests (→ rigor: glm-5.2 para test-writer).
2. Regla no-negociable CDAD: reviewer ≠ implementer en familia de modelo. Implementer = deepseek-v4-flash, reviewer = qwen3.7-plus (familias distintas).
3. Provider `bailian` directo (sin proxy router): el proxy router rota modelos y rompería el override. Verificado: los 4 modelos existen en bailian directo.
4. Asignación: architect+scribe = deepseek-v4-pro (razonador fuerte), test-writer = glm-5.2 (rigor), implementer = deepseek-v4-flash (productivo barato), reviewer = qwen3.7-plus.

## Consecuencias

**Positivas:**
- Modelo distinto por etapa, enforceable por runtime.
- Reviewer con familia distinta al implementer (anti-confirmation-bias).
- El skill cdad-cycle puede delegar vía Task (`subagent_type: cdad-<rol>`).

**Negativas / trade-offs:**
- HONESTIDAD: la asignación de modelos es intuición + data empírica, NO benchmarks verificados. Ajustar con experimentación (Fase 4).
- deepseek-v4-pro en architect + scribe = caro en 2 roles.
- bailian directo sin rotación: riesgo de 429 en uso intensivo (fallback documentado en opencode-delegation.md).

**Neutrales:**
- Coexistencia con coder/build (cada proyecto elige).
- refactorer es sub-modo de implementer (no agente dedicado).

## Notas

Research base: research plan (phase-4-complete). Verdict 4.1: "TDD anti-trampa NO efectivo (mismo agente/modelo)".
