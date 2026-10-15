# Decisiones del dueño — 004-003 (2026-10-05)

Aprobadas en sesión OpenCode del orquestador, tras presentar
`architect-draft-001.md` y sus decisiones abiertas. Registradas por el
orquestador; la aprobación del dueño es la autoridad (ADR-011).

| # | Decisión | Resolución aprobada |
|---|---|---|
| D1 | Soporte de contrato para plan borrador | Implementar `draft-plan` nativo en T1; el handoff legacy queda solo como transición. |
| D2 | Alcance de la revisión de plan | Por disparador (complejo / interfaz nueva / paralelismo) + obligatoria para el plan del epic y el replan de 003-002. |
| D3 | F4 (scopes del test-writer con tests co-ubicados) | **Fuera del camino feliz de este repo** (`test_roots:["tests"]`): T6 queda condicional y F4 se registra como deuda priorizada para el primer consumidor Go o co-ubicado. |
| D4 | Dueño canónico de la regla de equivalencia | `re-entry.md` edita una vez; `stage-4-review.md` y `SKILL.md` referencian. |
| D5 | Métricas de 004-003 | Registro en artefactos existentes (supervision-record + dispatch-ledger); UNKNOWN declarado; sin plataforma de telemetría. |
| D6 | Modelo del rol de revisión de plan | El del reviewer (`mofgw/glm-5.3-flash`), familia ≠ implementer/architect. |
| D7 | Autoridad de aprobación del contract-kind borrador | El dueño aprueba alcance; el dictamen técnico es separado. |

## Preguntas de materialización resueltas

1. **Archivos sin commitear previos a este traspaso.** Revisados sus diffs
   (solo añaden la referencia cruzada a `efficient-orchestration-requirements.md`
   en `plan.md` del epic, `planning-contract-draft.md` y `handoff-architect-001.md`).
   Aprobado commitearlos con pathspec, sin push.
2. **`plan.md` del epic con `Status: Draft` (línea 357).** Resuelto por
   evidencia: el frontmatter del archivo declara `status: active` y
   `activated_at: 2026-09-24`, y el propio archivo marca las secciones
   posteriores como estado **previo** a la activación (nota de reconciliación,
   líneas 10-17 y 26-31). `_contract_for` (`cdad_packet.py:869-882`) devuelve la
   ruta del plan del epic y no valida su estado de aprobación. **Sin cambios.**
