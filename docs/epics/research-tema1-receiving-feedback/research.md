# Tema 1: Recepción de feedback — investigación (02 Sep 2026)

> Fase 1 del ciclo de investigación: qué hace Superpowers, qué hacen otros,
> qué tiene CDAD, qué falta de verdad. Sin tocar código. Decisión cycle vs
> epic pendiente de la síntesis aprobada por Pablo.

## Fuentes revisadas

| Fuente                                                                                     | Qué aporta                                                                                                                          |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| obra/superpowers `receiving-code-review/SKILL.md` (205 líneas, leído completo)              | Secuencia READ→UNDERSTAND→VERIFY→EVALUATE→RESPOND→IMPLEMENT; respuestas prohibidas; ítems ambiguos → STOP; push-back con 6 criterios; YAGNI con grep; corrección factual del push-back propio; orden de implementación (bloqueantes→simples→complejos) |
| obra/superpowers `requesting-code-review/SKILL.md` (par receptor/emisor)                   | Cómo actuar sobre el feedback por severidad (Critical ya / Important antes de seguir / Minor después) + push-back con evidencia      |
| GitAuto — Review Response Guardrails (gitauto.ai, may 2026)                                 | Producción real: anti-sicofantía como guardrail del prompt de respuesta a review; justificación RLHF (compliance premiada); persistir reglas aprendidas en archivo de proyecto (GITAUTO.md) |
| Morricone — "Sycophancy-Free Coding" (dev.to, jul 2026)                                     | Hallazgos de diseño de skill anti-sicofantía: NO poner cláusula de salida (el modelo la explota al primer empujón); double-pushback; párrafo continuo > bullets (los bullets se leen como opciones excluyentes); **dilución en sesiones largas** → re-invocar el skill al final del contexto |
| Koushik — "Your AI Code Reviewer Is a Liar" (dev.to, jun 2026)                              | Del lado emisor: cold review sin contexto como ground truth; desafiar hallazgos en **sesión fresca** (no la misma); steelman antes de retractar; confidence rating por hallazgo; **contar reversals como yellow flag** de sycophancy |
| Ejentum adversarial review (dev.to, may 2026)                                               | Estructura anti-theater: cada hallazgo viene de un especialista con evidencia; arquitecto no inventa. CDAD ya tiene esto (two-layer) — confirma más que enseña |
| 0xcjl/anti-sycophancy (GitHub)                                                              | 3 capas (hook/SKILL/memoria persistente); cita ArXiv 2602.23971 "Ask Don't Tell"; valida dilución de reglas                          |

## Lo que CDAD YA tiene (verificado, no reinventar)

- Aislamiento por sesión: el receptor llega fresco → mitiga la dilución y el
  confirmation loop **estructuralmente** (superior a los skills de single-session).
- Confidence threshold en reviewer (≥80%, cdad-reviewer.md:53).
- Loop de fixes con severidad: bloqueantes → priorización por usuario → suite
  verde tras cada fix (stage-4-review.md:86-96) ≈ implementation order.
- Verdict-tuple + matriz de severidad (emisión).
- Anti-rationalization tables como formato del repo.
- Aprobación del usuario indelegable (limita el push-back: decisiones
  estratégicas no se discuten post-aprobación).

## Gap real (lo que falta)

- **Lado receptor**: nadie define cómo recibe el feedback el implementer (ni
  el orquestador que lo transmite). 0 matches en greps (02 Sep).
- **Reconsideración del reviewer**: ante push-back legítimo del implementer,
  no hay protocolo (riesgo espejo: el reviewer cede ante el push-back —
  reversal counting + steelman del artículo "Liar" aplican al reviewer CDAD).
- **Feedback externo (PR de GitHub)**: fuente no contemplada en el ciclo.
- **Persistencia de patrón aprendido**: cuando el feedback revela una regla
  reutilizable del proyecto → Memory Bank (análogo GITAUTO.md).

## Propuesta adaptada (borrador de síntesis)

Protocolo en dos lados del canal:

1. **Receptor** (reference nueva): secuencia de 4 pasos + prohibiciones +
   ítems ambiguos → STOP + YAGNI + orden por severidad. "Cuándo NO aplica":
   decisiones estratégicas ya aprobadas del usuario (se ejecutan o se escalan
   por otro canal, no se push-back-ean post-hoc).
2. **Transmisor** (orquestador): feedback íntegro en el handoff packet, sin
   editar que suavice; el packet re-invoca el protocolo (antídoto a la
   dilución: los tokens frescos viajan con la tarea — ventaja estructural
   CDAD explicitada).
3. **Reconsideración del reviewer**: ante push-back con evidencia, el
   reviewer aplica steelman ("¿cuál es el caso más fuerte de que el hallazgo
   sigue siendo válido dado este contexto?") y solo revierte con motivo
   escrito; 2+ reversals en una misma review = yellow flag → segunda pasada
   en sesión fresca (ya prevista en stage-4:89, ahora con criterio).
4. **AP-16** en el catálogo (respuesta performativa / implementación a ciegas).
5. Persistencia: patrón reutilizable → nota al scribe para systemPatterns
   (no edita el rol receptor inline).

## Decisión de forma (pendiente de Pablo)

Toca ~6 archivos y tiene dos contratos diferenciables (receptor /
reconsideración-reviewer). Opción A: **cycle standalone** con 1 feature
(cdad-005, alcance 5 archivos). Opción B: **epic chico de 2 features**
(005 recepción + 006 reconsideración-reviewer). La síntesis aprobada decide.
