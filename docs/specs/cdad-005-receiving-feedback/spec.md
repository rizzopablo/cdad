# cdad-005: Protocolo de recepción de feedback (anti-sicofantía)

> Estado: DRAFT — pendiente de aprobación del usuario (Pablo).
> Fecha: 2026-09-02 · Origen: epic-001-superpowers-gaps (feature 1/5).
> Discovery: skill `receiving-code-review` de obra/superpowers leído completo
> (205 líneas) + verificación contra CDAD real: grep de
> "reacciona|push.?back|sicofant|aclaración" sobre stage-4-review.md,
> re-entry.md, anti-patterns.md, verdict-tuple.md y agents/cdad-implementer.md
> = 0 matches (02 Sep 2026). El reviewer EMITE veredicto (verdict-tuple); la
> RECEPCIÓN del feedback no está protocolizada.

## Descripción funcional

CDAD define cómo el reviewer emite un veredicto pero no cómo cualquier rol
(implementer, test-writer, architect) —ni el orquestador— debe RECIBIR
feedback: del reviewer (bloqueantes de Etapa 4), del usuario, o de un review
externo (comentarios en PR). Se incorpora un protocolo de recepción con
rigor técnico: sin respuestas performativas, verificación contra el código
real ANTES de implementar, push-back técnico con evidencia cuando el
feedback está equivocado, y clarificación total antes de implementar cuando
hay ítems ambiguos.

## Restricciones de diseño (del análisis del epic)

- **R1 — Dos lados del canal:** el protocolo aplica al orquestador cuando
  TRANSMITE feedback (íntegro, sin editar que suavice, al handoff packet) y
  al rol que lo RECIBE (secuencia obligatoria antes de implementar).
- **R2 — No debilita el aislamiento:** el feedback viaja por el handoff
  packet (regla §6 de state-passing); el receptor no lee el diff del reviewer
  ni sesiones ajenas.
- **R3 — No cambia el núcleo:** verdict-tuple, matriz de severidad y gates
  quedan intactos; el protocolo es el complemento de recepción del loop ya
  existente (priorizar fixes → suite verde tras cada fix).
- **R4 — Formato del repo:** la reference nueva incluye su tabla
  anti-racionalización y "cuándo NO aplica" (convención del epic).

## Contrato (postcondiciones numeradas)

**P1 — Reference nueva.** Existe `skills/cdad-cycle/references/receiving-feedback.md`
con: (a) secuencia obligatoria de 4 pasos — leer completo sin reaccionar →
restatear la postcondición/requirement en palabras propias → verificar contra
el código real → implementar un fix por vez con verificación; (b) lista de
respuestas prohibidas (agradecimientos, "tenés razón", agreement performativo
previo a verificación) y sus reemplazos; (c) regla de feedback multi-ítem
ambiguo: parar TODO y pedir aclaración antes de implementar ninguno;
(d) protocolo de push-back técnico: cuándo procede (rompe funcionalidad,
falta contexto, viola YAGNI, incorrecto para el stack, contradice decisiones
arquitectónicas) y cómo (evidencia citada, no defensa emocional); (e) chequeo
YAGNI con grep del codebase cuando el feedback pide "implementar bien algo";
(f) manejo de push-back incorrecto propio (corrección factual, sin
sobre-explicación); (g) tabla anti-racionalización; (h) sección "cuándo NO
aplica" (feedback del usuario sobre decisiones estratégicas: se ejecuta, no
se push-back-ea — la aprobación es indelegable).

**P2 — Loop de review.** `skills/cdad-cycle/references/stage-4-review.md`
(en el loop de fixes con bloqueantes) referencia el protocolo: el orquestador
transmite el feedback íntegro en el handoff packet (R1) y el implementer lo
recibe aplicando receiving-feedback.md antes de tocar código.

**P3 — Catálogo AP.** `skills/cdad-cycle/references/anti-patterns.md` agrega
**AP-16 — Respuesta performativa / implementación a ciegas** (formato del
catálogo: Síntoma / Por qué es malo / Corrección), citando la reference.

**P4 — Mapa de lectura.** `skills/cdad-cycle/SKILL.md` agrega
`receiving-feedback.md` a la tabla "Cómo leer las references"; y
`references/handoff-prompts.md` agrega al packet de fix/re-entry la línea de
transmisión íntegra del feedback (R1).

## Invariantes

- El protocolo no introduce etapas ni gates nuevos; es un contrato de
  conducta dentro del loop existente.
- El push-back técnico nunca bloquea la aprobación indelegable del usuario
  (contra decisiones estratégicas del usuario no hay push-back, hay ejecución
  o escalado).
- Ninguna otra reference ni agente se modifica (scope: los 4 archivos de P1-P4).

## Criterios de aceptación (verificables)

1. `receiving-feedback.md` existe y contiene las 8 piezas de P1 (checks grep
   por sección: secuencia, prohibidas, ambiguo, push-back, YAGNI,
   corrección, anti-racionalización, cuándo NO).
2. `stage-4-review.md` menciona `receiving-feedback` en su loop de fixes.
3. `anti-patterns.md` contiene `## AP-16` con las 3 sub-secciones del formato.
4. SKILL.md (tabla de lectura) y handoff-prompts.md mencionan el protocolo.
5. RED: checks definidos ANTES de editar y fallando sobre el estado actual.
6. Sin regresión: suite cdad-003 121/121 y checks cdad-004 10/10 siguen
   verdes tras GREEN.
