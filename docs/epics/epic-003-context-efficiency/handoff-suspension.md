# Handoff de suspensión — epic-003-context-efficiency

Fecha: 2026-09-24. Snapshot documental previo a la activación de
`epic-004-single-source-planning` (procedimiento §6, paso 1 de la corrección
del architect). La reanudación de 003 se hará por **reconciliación**, no por
restauración ciega de este snapshot.

## Estado congelado de epic 003

- `active_epic: epic-003-context-efficiency` · `epic_stage: features-loop` ·
  `active_feature: null` · `current_stage: idle` · `stack: null`
- Features: `003-001-role-packets` **done** (2026-09-18) ·
  `003-005-claude-code-packets` **done** (2026-09-18) ·
  `003-002-artifact-tools` queued (drafts en
  `docs/specs/003-002-artifact-tools/{discovery,spec,plan}-draft.md`, no
  aprobados) · `003-003-progress-guards` queued ·
  `003-004-context-continuity` queued.
- Contexto de continuation de las features en cola:
  [remaining-features-handoff.md](remaining-features-handoff.md).
- Presupuesto y objetivos del epic: [plan.md](plan.md) (objetivo 200k por
  feature; <100k aspiración posterior); medición mínima en
  [planning contract](../epic-004-single-source-planning/planning-contract-draft.md).

## Decisiones vigentes al momento de la suspensión

- 001 y 005 están **cerradas**; no se reabren. Sus contratos son la base de
  004, con enmiendas que ese epic cierre.
- [ADR-010](../../adr/ADR-010-modelo-unico-mvp-epic-003.md) sigue limitado a
  epic-003/OpenCode con vencimiento; el criterio de modelo único del recorrido
  final de aceptación requiere enmienda explícita o se conserva (señalado en
  la revisión C0 de GPT, pendiente de presentar formalmente).
- Ajustes de 003 realizados por GPT (2026-09-24): requisitos de recepción de
  evidencia, detección de fricción/incidentes y continuidad de decisiones
  entre sesiones, en los documentos de 003 (sin commit propio aún — quedan
  dentro del árbol de trabajo documental).
- ADR-011 afecta a 003-002/003/004 (supervisión proporcional, fricción
  observada) — ver mapa de impacto en la
  [enmienda C0](../epic-004-single-source-planning/c0-amendment-supervised-autonomy-2026-09-24.md).

## Delegación HITL vigente (texto literal del state pre-activación)

```json
"hitl_delegation": {
  "delegated_to": "Codex (orquestador y HITL delegado)",
  "requested_by": "usuario",
  "requested_at": "2026-09-17",
  "scope": "epic-003-context-efficiency: alcance, specs, priorización de reviews, aprobaciones de Memory Bank y gates para sus cuatro features e integración",
  "expires": "cierre, cancelación o revocación del epic",
  "publication": "sin push automático",
  "source": "docs/epics/epic-003-context-efficiency/execution.md"
}
```

**No se hereda en 004.** Al activar 004 pasa a `delegation_history` con nota
`status: suspended`. La reanudación de 003 requiere re-registro de autoridad
con confirmación explícita del usuario.

## Congelación

- Commit que congela el state pre-activación: `24d37f0` (aprobación de
  spec/plan 004-001 + corrección del architect). El commit inmediato posterior
  (este archivo + execution.md de 004) no toca el state.
- La activación (única escritura del state) se registra en `epic_history` con
  referencia a ese commit y a este snapshot.

## Reanudación (contrato, no ejecución)

1. Entrada: este handoff + diff git del state en el momento de la suspensión +
   `epic_history`.
2. Reconciliación: comparar progreso conservado con el estado actual; los
   cambios de 004 que afecten a 003 (nuevo runtime de paquetes, política de
   capacidades, R13) se declaran en el handoff de reanudación.
3. Re-registro de la autoridad HITL de 003 con **confirmación explícita del
   usuario** (no restaurar el JSON antiguo: reactivaría la delegación de
   Codex sin nueva autoridad).
4. Nueva entrada en `epic_history` con la evidencia de reconciliación.
