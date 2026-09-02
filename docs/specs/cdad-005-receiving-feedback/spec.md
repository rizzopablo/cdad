# cdad-005: Protocolo de recepción de feedback (anti-sicofantía)

> Estado: DRAFT — pendiente de aprobación del usuario (Pablo).
> Fecha: 2026-09-02 · Origen: investigación superpowers-gaps tema 1
> (docs/epics/research-tema1-receiving-feedback/research.md). Decisión de
> forma: cycle standalone (aprobado por Pablo 02 Sep 2026).

## Descripción funcional

CDAD define cómo el reviewer EMITE un veredicto (verdict-tuple, severidad,
confidence ≥80%) pero no cómo se RECIBE feedback — del reviewer (bloqueantes
de Etapa 4), del usuario, o de un review externo (PR). La sicofantía (RLHF)
hace que los agentes respondan con agreement performativo e implementen a
ciegas; también afecta al reviewer ante push-back (capitula). Se incorpora el
protocolo de recepción en dos lados del canal, aprovechando la ventaja
estructural de CDAD: sesiones aisladas llegan frescas y el handoff packet
re-invoca las reglas (antídoto a la dilución de contexto documentada).

## Restricciones de diseño (de la investigación aprobada)

- **R1 — Dos lados del canal:** el protocolo aplica al orquestador cuando
  TRANSMITE (feedback íntegro en el handoff packet, sin editar que suavice)
  y al rol que RECIBE (secuencia obligatoria antes de implementar).
- **R2 — Sin cláusulas de salida:** las reglas del protocolo se redactan
  sin "si el usuario insiste, cedé" — el compliance nativo (RLHF) ya cede
  solo; la cláusula explícita acelera la capitulación (hallazgo Morricone,
  verificado empíricamente en su A/B).
- **R3 — Núcleo intacto:** verdict-tuple, matriz de severidad, confidence
  threshold y gates no se modifican.
- **R4 — Aprobación indelegable:** contra decisiones estratégicas ya
  aprobadas por el usuario NO hay push-back post-hoc; la objeción técnica va
  antes de la aprobación (brainstorm socrático, etapas 1-2). En el protocolo:
  esas decisiones se ejecutan o se escalan por otro canal.
- **R5 — Alcance cerrado:** 5 archivos (P1-P5). Nada más.

## Contrato (postcondiciones numeradas)

**P1 — Reference del protocolo.** Existe
`skills/cdad-cycle/references/receiving-feedback.md` con:
(a) secuencia obligatoria del receptor: leer completo sin reaccionar →
restatear el requisito en palabras propias → verificar contra el código real
→ implementar de a un fix con verificación (orden: bloqueantes → simples →
complejos, suite verde tras cada uno); (b) lista de respuestas prohibidas
(agradecimientos, "tenés razón", agreement performativo pre-verificación) y
sus reemplazos factuales; (c) feedback multi-ítem con ítems ambiguos → parar
TODO y pedir aclaración antes de implementar ninguno; (d) push-back técnico:
cuándo procede (rompe funcionalidad / falta contexto / YAGNI con grep /
incorrecto para el stack / legacy / contradice decisión arquitectónica) y
cómo (evidencia citada, sin defensa emocional), con destino según la fuente:
reviewer → reconsideración con veredicto re-emitido; desacuerdo persistente
→ media el usuario; (e) chequeo YAGNI con grep del codebase cuando el
feedback pide "implementar bien algo"; (f) corrección factual del push-back
propio incorrecto (sin sobre-explicación); (g) matriz de fuente del feedback
(usuario trusted-ejecutar / reviewer verificar / PR externo escéptico);
(h) persistencia: patrón reutilizable detectado → nota al scribe para
systemPatterns, nunca edición de memoria inline; (i) ventaja estructural
documentada: packet re-invoca el protocolo (dilución) y sesión fresca
(confirmation loop); (j) tabla anti-racionalización; (k) sección "cuándo NO
aplica" (R4); (l) prohibición de cláusulas de salida en reglas propias (R2).

**P2 — Transmisión en el loop de review.**
`skills/cdad-cycle/references/stage-4-review.md` (loop de fixes con
bloqueantes): referencia el protocolo con la regla del transmisor — el
orquestador pega el feedback íntegro del reviewer (y del usuario) en el
handoff packet, sin editar que suavice, y el packet ordena al receptor
aplicar receiving-feedback.md antes de tocar código.

**P3 — AP-16.** `skills/cdad-cycle/references/anti-patterns.md` agrega
**AP-16 — Respuesta performativa / implementación a ciegas** (formato del
catálogo: Síntoma / Por qué es malo / Corrección) citando la reference.

**P4 — Mapa de lectura + handoff.** `skills/cdad-cycle/SKILL.md` agrega
`receiving-feedback.md` a la tabla "Cómo leer las references";
`references/handoff-prompts.md` agrega al packet de fix/re-entry la regla de
transmisión íntegra (R1) y la invocación del protocolo.

## Invariantes

- El protocolo no introduce etapas, gates ni roles nuevos.
- El push-back técnico nunca posterga ni condiciona la aprobación indelegable
  del usuario (R4).
- Scope: los 4 archivos de P1-P4. Ningún otro archivo del repo se modifica.
- La reconsideración del reviewer ante push-back (steelman/reversals) queda
  documentada en la reference como regla de conducta del reviewer citada
  desde verdict-tuple.md, SIN modificar el formato del veredicto (R3).

## Criterios de aceptación (verificables)

1. `receiving-feedback.md` existe con las 12 piezas de P1 (checks grep por
   sección).
2. `stage-4-review.md` menciona `receiving-feedback` en el loop de fixes con
   la regla del transmisor.
3. `anti-patterns.md` contiene `## AP-16` con las 3 sub-secciones del formato
   del catálogo.
4. SKILL.md (tabla de lectura) y handoff-prompts.md mencionan el protocolo.
5. `verdict-tuple.md` referencia la conducta de reconsideración (steelman /
   reversal counting) sin cambiar el formato del veredicto.
6. RED: checks definidos ANTES de editar y fallando sobre el estado actual.
7. Sin regresión: suite cdad-003 121/121 y checks cdad-004 10/10 verdes tras
   GREEN.
