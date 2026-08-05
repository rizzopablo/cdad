# Memory Bank — cdad-001-validate-subagents

## 2026-08-05 — Feature: cdad-001-validate-subagents

### Qué se validó
Ciclo CDAD real con sub-agentes nativos opencode (delegación end-to-end):
- **Runtime:** 5/5 agentes `cdad-*` instalados y descubribles (config in-memory 19 entries, verificado vía `/config` del server).
- **Repo:** `install.sh --check` 11/11 PASS (byte-compare repo↔runtime).
- **Artefactos por etapa:** spec.md (architect), tests/ (test-writer), impl.diff (implementer), review.md (reviewer), memory-bank.md (scribe) — todos materializados en `docs/specs/cdad-001-validate-subagents/artifacts/`.
- **Delegación real de reviewer:** corrió con `bailian/qwen3.7-plus` (modelo distinto al implementer, ADR-001 respetado), produjo review completa: **0 bloqueantes, 5 opcionales, veredicto PASS**.
- **Delegación real de scribe:** corrió con `bailian/deepseek-v4-pro`, produjo draft ADR-003 completo.

### Decisiones relevantes
1. **F1 (BLOCKER) resuelto:** reviewer/scribe son read-only por diseño (anti-confirmation-bias) → NO pueden escribir sus artefactos. Decisión final: **el orquestador materializa los artefactos desde el output del delegate** (rechazado el scoped-write: opencode 1.18.4 trata `write` como objeto/allowlist como `write: deny` catch-all → task rechazado). Ver ADR-003.
2. **task vs delegate:** read-only → `delegate` (async, background); write-capable → `task`. opencode rechaza `task` con agentes read-only. Documentado en `references/opencode-delegation.md`.
3. **Reviewer prompt alineado:** entrega review como texto final (no "Write review.md"); el orquestador materializa `review.md`.

### Deuda técnica detectada (5 opcionales del reviewer) — TODOS RESUELTOS ✅
1. ✅ Spec §3.3/T4 alineados al criterio `git apply --check --reverse` (divergencia documentada en spec §3.3 y review.md) — aplicado en el propio spike.
2. ✅ `set -euo pipefail` alineado con install.sh:12 — manejo de errores manual convertido a if-forms (compatible con -e).
3. ✅ Condición redundante `! -x` eliminada — solo `-f` (bash no requiere +x).
4. ✅ `fail()` escribe a stderr (`>&2`) — T2 sigue PASS (mergea 2>&1).
5. ✅ Frontmatter validado en Etapa 1 (`description:` presente por agente) + narrativa §6 corregida (frontmatter en Etapa 1, byte-compare en Etapa 2).

### 2026-08-05 — Iteración: reviewer findings #2-#5 aplicados
- Fixes aplicados a `scripts/validate-subagents.sh` (4 cambios): set -euo pipefail, simplificación ! -x, fail() → stderr, frontmatter check en Etapa 1.
- Spec §6 narrativa corregida (frontmatter + byte-compare: dónde se cubre cada uno).
- impl.diff regenerado contra base 6a5cf9a (estado actual de la implementación).
- Verificación: `validate-subagents.sh` PASS 5/5 etapas + `tests/run_all.sh` 5/5 PASS (T1-T5, idempotencia incluida).

### Próxima feature en cola
- Phase 4 task pendiente: "Ajustar prompts/permisos/modelos según empiria" (los 5 opcionales del reviewer son los candidatos).
- Luego Phase 6 cierre: cerrar fase en project-tracker.

---

## ADR-003: El orquestador materializa los artefactos de los sub-agentes CDAD read-only

- **Status**: Accepted
- **Date**: 2026-08-05
- **Deciders**: Ofap (build orchestrator) + sub-agentes CDAD
- **Confianza**: Alta

### Contexto

Los roles CDAD (architect, test-writer, implementer, reviewer, scribe) se
definieron como sub-agentes nativos con permisos read-only (ADR-001): no pueden
editar archivos ni correr comandos de escritura. Eso garantiza aislamiento de
sesión y anti-confirmation-bias, pero significa que ninguno de ellos puede
persistir su propio output. El resultado de cada etapa (spec, tests, impl.diff,
review, memory-bank) debe ser escrito por quien sí tiene permisos de escritura:
el orquestador. El validator de esta feature (cdad-001, Etapa 3) asume que los
5 artefactos existen en `docs/specs/<feature>/artifacts/`, materializados por
el orquestador desde los outputs read-only de cada rol.

### Opciones consideradas

#### Opción A: Sub-agentes read-only + orquestador materializa sus artefactos
- Pros: preserva el aislamiento/anti-bias de ADR-001; el artefacto queda bajo
  control del orquestador que tiene el contexto completo; el validator puede
  enumerarlos por etapa.
- Contras: el orquestador debe serializar/transcribir el output; riesgo de
  pérdida si el output no llega completo.

#### Opción B: Roles write-capable que escriben sus propios artefactos
- Pros: cada rol persiste su artefacto sin intermediario.
- Contras: rompe el aislamiento de sesión de ADR-001; el mismo rol podría
  auto-validarse su artefacto (vuelve el sesgo que se quería eliminar).

#### Opción C: Harness externo que persiste por rol
- Pros: enforcement determinista.
- Contras: sobre-ingeniería para el MVP (ya descartada en ADR-001).

### Decisión

El orquestador (build orchestrator) materializa los artefactos de cada rol CDAD
read-only en `docs/specs/<feature>/artifacts/`. Routing complementario: los
sub-agentes read-only se invocan con `delegate` (async, background); los
write-capable con `task` (preserva undo/branching).

### Razones

1. Preserva el aislamiento de sesión y el anti-confirmation-bias de ADR-001.
2. El orquestador tiene el contexto completo para transcribir outputs parciales.
3. El validator (Etapa 3) depende de que los 5 artefactos existan en un dir
   plano por feature — materializarlos en el orquestador satisface ese contrato.

### Consecuencias

**Positivas:**
- Contrato de artefactos estable y verificable por `validate-subagents.sh`.
- Roles siguen read-only (copias de seguridad contra auto-validación sesgada).

**Negativas / trade-offs:**
- El orquestador es punto único de transcripción de output; si un rol termina
  con output incompleto, el artefacto puede quedar incompleto.

**Neutrales:**
- El routing `delegate` vs `task` depende de los permisos del rol (read-only →
  delegate; write-capable → task).

### Notas

Evidencia directa en esta feature: `scripts/validate-subagents.sh` Etapa 3
enumera `spec.md` (architect), `tests/` (test-writer), `impl.diff`
(implementer), `review.md` (reviewer) y `memory-bank.md` (scribe) — este último
fue materializado vía este flujo (drafts parciales del scribe + completado por
el orquestador).
