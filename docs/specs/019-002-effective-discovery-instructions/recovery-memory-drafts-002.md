## 0. Intake validation (route C)

| Check | Command | Result |
|---|---|---|
| Spec sha256 vs contracted | `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` | `cd61455c…1f0382` — matches |
| Request + packet | `python3 scripts/cdad_packet.py validate-packet --request …/REQUEST.json --packet …/PACKET.md` | `rc=0`, no diagnostic |
| Same with execution context | `… --execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json` | `rc=0`; `schema_version: 2` (v2, admissible for route C) |
| Identification block vs canonical render | `cdad_packet.py render --route C --request …` compared in-process to the received block | byte-identical (758 vs 757 chars = trailing newline only) |

No inline packet body was supplied — only the identification block, which is what route C allows. `write_scope` is empty: I modified nothing, committed nothing (`git status --porcelain` = pre-existing ` M docs/.cdad-state.json` + pre-existing `?? …/recovery-memory-drafts-001.md`). State observed: `active_feature: 019-002…`, `current_stage: merge`, feature `in-progress`, no `closure.md` for epic 019 → **feature not closed, epic OPEN**.

**Inputs read:** the approved spec (PC-1..PC-7, supersession, `deferred-hardening`), `recovery-memory-drafts-001.md` (prior drafts), `recovery-exercise-review.md`, `recovery-contextual-review-003.md`, `recovery-execution-progress.md`, `recovery-exercise-record.md`, `recovery-delivery-{red,green}.md`, `recovery-approval.md`, `recovery-readme-maintenance-decision.md`, `docs/{activeContext,progress,systemPatterns}.md`, `docs/.cdad-state.json`.

**Declared deviation (approved):** anchored deltas — the changed region with its insertion/replacement anchor, not a transcription of 9 762 lines of untouched history.

---

## 1. ACTIVE_CONTEXT — `docs/activeContext.md` (insertion: after line 6, before `## 2026-11-15 — Feature: 019-003…`; nothing existing changes)

```markdown
## 2026-11-16 — Feature: 019-002-effective-discovery-instructions

**Implementación y revisión independientes aceptadas; cierre formal NO registrado.** Epic 019 (`epic-019-discovery-dialogue`), orden **3/3**, la última. Producto: activación del diseño de discovery aprobado en instrucciones canónicas y consumidores efectivos, más la entrega de la consulta y el reposo. Aceptada bajo la HITL delegada del epic; **el cierre de feature, la suite completa y el mantenimiento de README siguen pendientes**, y el epic **sigue abierto**.

**Reconstrucción.** Baseline elegido por el dueño: `bc922c04` (producto y tests); restauración en `e2e67620` y `49b3feec`, conservando el bundle histórico de Git y los tests retirados. Sobre esa base la reconstrucción fue mínima y con RED/GREEN independientes: PC-4 en `dbb15fbd`/`cbd7828a` (17 tests en verde) y PC-5 en `62224ee7`/`02ff945a` (105 tests de regresión de `status`/`open-unit`/idle-history). La producción semántica `d415cc1b`, con las correcciones `5bb788dc` y `54b40d76`, regeneró los agentes de ambos runtimes.

**Revisión.** Tres rondas contextuales independientes: 001 (3 bloqueantes), 002 (1) y 003 (**sin bloqueantes nuevos en su alcance**). El ejercicio de uso real de PC-7 **completó su turno 4** (exit 0, transporte) en un proyecto descartable —no es una sandbox— con los hashes candidatos congelados antes de ejecutar; la evaluación independiente (`recovery-exercise-review.md`) lo declara **supported within declared limits**: respuesta parcial, default no aceptado, corrección autorizada que gobierna, incertidumbre que impide readiness, consulta previa al borrador, borrador no aprobado y revisión independiente. **No** acredita PC-4/PC-5, el cierre ni el cumplimiento universal de agentes. Los intentos fallidos se conservan como tales: la consulta que cargó una ruta como identificador de skill y el paquete de 6083 bytes frente a 6084 canónicos, rechazado antes de redactar.

**Decisiones relevantes.** *La consulta vuelve porque la tabla canónica lo admite, no porque un adaptador lo permita*: `role-report` para architect/brainstorm se resuelve en `_allowed_kinds` de `skills/cdad-cycle/scripts/cdad_result.py`, y las rutas nativa y OpenCode derivan de esa tabla; precio, reemplazar la expectativa obsoleta de rechazo en `tests/test_006_005_u7_scribe_role_report.py`; beneficio, una sola casa y ninguna cardinalidad global de partes inventada. *La prohibición del orquestador es autoría de producto y tests*: puede investigar, leer código y ejecutar el producto, y una corrección formal trivial vive solo en una presentación corregida separada y atribuida, mientras `_apply_copy` conserva el destino idéntico y rechaza la divergencia (`cdad_result.py:971–984`), sin tocar el original, su recibo ni la copia canon del diario. *El reposo no es un modelo de estado nuevo*: `status` aplica la misma comprobación de coherencia que `open-unit` antes de recomendar abrir, convierte `done`/`null` en diagnóstico y sigue read-only. *La verificación retiene la estrategia de 019-003* (método por promesa): el registro rígido de diálogo y las cuotas de escenarios de los PC-4/PC-11 anteriores quedan **superseded**, y sus observaciones fallidas o incompletas siguen siendo evidencia histórica, no logros.

**Verificación y límites.** Solo resta la **suite completa de `tests/`** (se corre contra `tests/`; se excluye `examples/idea_log/tests/test_idea_log.py`, que exige entorno Odoo). Evidencia ejecutable registrada: 17 tests (`cbd7828a`) y 105 (`02ff945a`). **F011 / `install.sh --check` sigue rojo por drift de instalación** (instalado ≠ candidato): excluido del alcance aceptado y **no verde**. Sin despliegue ni publicación.

**Deuda detectada.** **(1)** Suite completa pendiente y obligatoria por defecto en el cierre de epic. **(2)** Cuatro regresiones **preexistentes** de README reproducidas en el candidato (`4 failed, 3 passed` sobre `tests/test_005_006_t4_readme.py` y `tests/test_005_006_t6_owner_reviewfix.py`; log en `.cdad/orchestration/epic-019/recovery-readme-baseline.log`); disposición: asignación separada y acotada a `README.md` tras el snapshot de suite, con `2de6e72b` como evidencia y no como instrucción de replay. **(3)** F011 sin causa aislada. **(4)** Defecto **procedimental** visible: el registro de review-fix-013 se lanzó en segundo plano y falló con `active_packet mismatch: id`; no se fabricó recibo, el informe original se conservó (`recovery-handoff-fix.md`) y la revisión cerró el hallazgo sobre el diff real de `54b40d76`. **(5)** En el proyecto descartable, `projectbrief.md` quedó desactualizado frente a decisiones ya resueltas —hallazgo **opcional**, solo importa si ese proyecto se continúa. **(6)** `deferred-hardening` del spec con su disposición: *cumplimiento universal y cobertura exhaustiva de escenarios* —fuera de la promesa acotada—; *enforcement semántico o de aprobación automático* —sin necesidad demostrada—; *diagnóstico `--check` de la instalación y despliegue* —trabajo operativo separado, no prometido acá—; *limpieza documental y regresión no relacionadas* —fuera del delta—. Ninguna de las cuatro aplaza una postcondición comprometida.

**Siguiente en la cola.** No hay otra feature abierta: resta el **cierre de `019-002`** (suite completa de `tests/`, inventario vivo, Memory Bank) y el **cierre del epic 019**, condicionado a esa suite, al mantenimiento acotado de README y al registro formal. Publicación y despliegue siguen reservados al dueño.
```

*(15 lines, ≤25. Corrected against the prior draft: turn 4 no longer "shown as pending"; PC-7 recorded as bounded journey assented by its independent assessment, not as pending; only the full `tests/` suite remains; the 33/76 counts are dropped instead of misattributed; 17/105 kept; optional 3.b/ADR-index cleanup dropped.)*

---

## 2. PROGRESS — `docs/progress.md` (replacement: lines 5–15, the `## In progress` block; line 16 blank and everything from `Historical note retained below…` untouched)

```markdown
## In progress

**Active epic: `epic-019-discovery-dialogue` — plan approved by Pablo, 2026-11-15.**
`019-001-discovery-dialogue-contract` y `019-003-contract-verification-strategy` **cerradas el 2026-11-15** (detalle en `## Done`). `019-002-effective-discovery-instructions` (orden **3/3**, la última) tiene **implementación y revisión independientes aceptadas** bajo la HITL delegada del epic, con el ejercicio de uso real completado y evaluado como *supported within declared limits*; su **cierre formal todavía no está registrado**: restan la suite completa de `tests/`, las cuatro regresiones **preexistentes** de README y el cierre del epic. **No se declara** suite verde, coherencia de instalación (`F011` sigue rojo), despliegue, publicación ni cierre de epic; publicar y desplegar siguen reservados al dueño. Detalle en el entry de `activeContext.md` y en `docs/specs/019-002-effective-discovery-instructions/`. Plan: `docs/epics/epic-019-discovery-dialogue/plan.md`.
```

*(4 lines, ≤12. The feature is NOT moved to `## Done`: closure is not registered. What changes is the premise — "suspendida y a reanudar" → accepted, closure pending. The `## Done` bullet will be built from the materialized closure, not from this draft.)*

---

## 3. SYSTEM_PATTERNS — `docs/systemPatterns.md` (insertion: after line 641, end of `### Suite instrumentada y lote paralelo fail-closed (epic 017, 2026-11-08)`, before `## Palanca \`write: ask\``)

```markdown
### Diálogo de discovery efectivo — consulta entregable y reposo coherente (epic 019, 2026-11-16)

- **La consulta del architect vuelve porque la tabla canónica lo admite, no porque un adaptador lo permita.** `architect`/`brainstorm` entrega un `role-report` resuelto en `_allowed_kinds` de `cdad_result.py`, y las rutas nativa y OpenCode derivan de esa tabla; los kinds de borrador quedan rechazados ahí. Motivo: sin un kind entregable la consulta no regresa y el descubrimiento se interrumpe. Precio declarado: se reemplazó la expectativa obsoleta de rechazo en `tests/test_006_005_u7_scribe_role_report.py`, y no se impuso cardinalidad global de partes. Base: `019-002` PC-4, `cbd7828a`.
- **La prohibición del orquestador cubre producto y tests; la corrección formal trivial va aparte.** El orquestador conduce el diálogo, investiga, lee código y ejecuta el producto; puede mostrar una corrección de forma en una **presentación corregida** nombrada aparte, con autoría original y atribución de la corrección, mientras `_apply_copy` conserva un destino idéntico y rechaza la divergencia (`cdad_result.py:971–984`). El original, su recibo y la copia canon del diario quedan intactos; un defecto sustantivo vuelve al rol responsable. Base: `019-002` PC-3.
- **El reposo se comprueba antes de recomendar, con el chequeo que ya existía.** `status` aplica la misma validación de coherencia que `open-unit` antes de devolver `next-unit`; `done`/`null` produce `diagnosis` con el texto del error, sin recomendación de abrir ni afirmación de reposo, y `status` sigue read-only, sin vocabulario de estado nuevo. Base: `019-002` PC-5, `02ff945a`.
- **La verificación retiene la estrategia por promesa y no reinstala obligaciones superadas.** El método por promesa de `019-003` gobierna la evidencia (contextual, ejecutable o combinada, por postcondición). El registro rígido de diálogo y las cuotas de escenarios previas quedan **superseded**; sus observaciones fallidas siguen siendo evidencia histórica y no se reescriben como éxito. Base: `spec.md` §Supersession.
- **Límites que esta convención no convierte en garantías.** La igualdad de bytes y la coherencia contextual no demuestran conducta de agentes reales ni cumplimiento universal; el ejercicio PC-7 es evidencia acotada de candidato en un proyecto descartable, no despliegue ni benchmark; `F011` / `install.sh --check` sigue rojo por drift de instalación y no se declara verde. Normativo en `docs/specs/019-002-effective-discovery-instructions/spec.md` (PC-1..PC-7).
```

*(7 lines, ≤15. The prior draft's optional 3.b — ADR-index note cleanup, 019-003 debt — is **omitted** as instructed.)*

---

## ADR — **No ADR suggested**

No new architectural decision: `role-report` for architect/brainstorm is a row in the existing canonical kind table (both adapters already derive from it), and resting coherence reuses `_validate_idle_coherence` with no new state vocabulary, mechanism, gate or permission change. Normative homes are `cdad_result.py`, `cdad_packet.py` and the spec. If the owner wanted a record anyway, the candidate would be one ADR with Confidence **Medium** (mechanism demonstrated by focused tests and contextual review, not by live agent behaviour).

## R6 — `deferred-hardening` carried (not omitted)

Carried in Draft 1 "Deuda detectada (6)" and to be carried into the `closure.md` the orchestrator materializes: universal compliance/exhaustive scenario coverage (outside the bounded promise); automatic semantic/approval enforcement (no demonstrated need); installed `--check` diagnosis and deployment (separate operational work, F011 red); unrelated documentation and regression cleanup (outside the delta, includes the four README regressions). None postpones a committed postcondition; no new policy is required.

## Evidence report

- **Modified files:** none. **Commit:** none. Drafts only — approval is the owner's, materialization and git are the orchestrator's.
- **Exact commands and output:**
  - `sha256sum docs/specs/019-002-effective-discovery-instructions/spec.md` → `cd61455c3a5b799cdbfa0d29b5c08fbe8eddc1bd601f69869baa6eb00a1f0382`
  - `python3 scripts/cdad_packet.py validate-packet --request …/scribe-memory-002/REQUEST.json --packet …/PACKET.md` → rc 0, empty diagnostic
  - same with `--execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json` → rc 0 (`schema_version: 2`)
  - `python3 scripts/cdad_packet.py render --route C --request …` → rc 0; in-process byte comparison with the received identification block: **identical** (difference = trailing newline only)
  - `git status --porcelain` → ` M docs/.cdad-state.json`, `?? docs/specs/019-002-effective-discovery-instructions/recovery-memory-drafts-001.md` (both pre-existing)
- **Not done by me:** no test was run, no suite, no `install.sh --check`; every count above is attributed to the document that recorded it. I do not claim full-suite green, installation coherence, deployment, publication or epic closure.

## Limits (PD-15)

Drafts are not approval and not a commit. One anchored-edit deviation, declared: no verbatim replay of 9 762 lines. I flagged but deliberately did not draft anything about the `ADR-009` row/status mismatch (outside 019-002's evidence). Date used `2026-11-16` as in the prior draft and the state's UTC `last_updated`; local time of this session is still 2026-11-15 — if the owner prefers local dates, that single label changes and nothing else.