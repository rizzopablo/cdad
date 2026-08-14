# ADR-003: El orquestador materializa los artefactos de los sub-agentes CDAD read-only

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: el orquestador + sub-agentes CDAD
- **Confianza**: Alta

## Contexto

Los roles CDAD (architect, test-writer, implementer, reviewer, scribe) se
definieron como sub-agentes nativos con permisos read-only (ADR-001): no pueden
editar archivos ni correr comandos de escritura. Eso garantiza aislamiento de
sesión y anti-confirmation-bias, pero significa que ninguno de ellos puede
persistir su propio output. El resultado de cada etapa (spec, tests, impl.diff,
review, memory-bank) debe ser escrito por quien sí tiene permisos de escritura:
el orquestador. El validator de esta feature (cdad-001, Etapa 3) asume que los
5 artefactos existen en `docs/specs/<feature>/artifacts/`, materializados por
el orquestador desde los outputs read-only de cada rol.

## Opciones consideradas

### Opción A: Sub-agentes read-only + orquestador materializa sus artefactos
- Pros: preserva el aislamiento/anti-bias de ADR-001; el artefacto queda bajo
  control del orquestador que tiene el contexto completo; el validator puede
  enumerarlos por etapa.
- Contras: el orquestador debe serializar/transcribir el output; riesgo de
  pérdida si el output no llega completo.

### Opción B: Roles write-capable que escriben sus propios artefactos
- Pros: cada rol persiste su artefacto sin intermediario.
- Contras: rompe el aislamiento de sesión de ADR-001; el mismo rol podría
  auto-validarse su artefacto (vuelve el sesgo que se quería eliminar).

### Opción C: Harness externo que persiste por rol
- Pros: enforcement determinista.
- Contras: sobre-ingeniería para el MVP (ya descartada en ADR-001).

## Decisión

El orquestador (build orchestrator) materializa los artefactos de cada rol CDAD
read-only en `docs/specs/<feature>/artifacts/`. Routing complementario: los
sub-agentes read-only se invocan con `delegate` (async, background); los
write-capable con `task` (preserva undo/branching).

## Razones

1. Preserva el aislamiento de sesión y el anti-confirmation-bias de ADR-001.
2. El orquestador tiene el contexto completo para transcribir outputs parciales.
3. El validator (Etapa 3) depende de que los 5 artefactos existan en un dir
   plano por feature — materializarlos en el orquestador satisface ese contrato.

## Consecuencias

**Positivas:**
- Contrato de artefactos estable y verificable por `validate-subagents.sh`.
- Roles siguen read-only (copias de seguridad contra auto-validación sesgada).

**Negativas / trade-offs:**
- El orquestador es punto único de transcripción de output; si un rol termina
  con output incompleto, el artefacto puede quedar incompleto.

**Neutrales:**
- El routing `delegate` vs `task` depende de los permisos del rol (read-only →
  delegate; write-capable → task).

## Notas

Evidencia directa en esta feature: `scripts/validate-subagents.sh` Etapa 3
enumera `spec.md` (architect), `tests/` (test-writer), `impl.diff`
(implementer), `review.md` (reviewer) y `memory-bank.md` (scribe) — este último
fue materializado vía este flujo (drafts parciales del scribe + completado por
el orquestador).
