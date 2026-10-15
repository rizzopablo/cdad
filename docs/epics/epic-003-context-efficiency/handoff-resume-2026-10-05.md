# Handoff de reanudación — epic-003-context-efficiency

Fecha: 2026-10-05. Autorizado por el usuario en sesión: «reactiva epic-003 y
registra tu mandato de orquestación con criterio HITL para su alcance aprobado.
No heredes silenciosamente delegaciones anteriores.»

Este handoff es la **reconciliación**, no una restauración ciega del snapshot de
suspensión (`handoff-suspension.md`, 2026-09-24). Es el **único punto de entrada
vigente** del epic-003: `handoff.md` apunta acá, y `handoff-suspension.md` es
histórico.

---

## 0. Estado vigente (actualizado 2026-10-06: 003-002 CERRADA)

> **Leer esto primero.** §4 y §5 de abajo son el registro de la reanudación (histórico:
> decían «spec en draft» y «arrancar T1»); están cumplidas. El estado real es este.

| Elemento | Estado real |
|---|---|
| Spec 003-002 | **aprobada** (`spec.md`, `status: approved`, 2026-10-05) |
| Plan 003-002 | **aprobado** (`plan.md`); F3/F4/F5/F6 y las 4 marcas VERIFY resueltas |
| T1 `receive` | **cerrada** (review + review-fix + re-review) |
| T2 `materialize` | **cerrada** (review + review-fix + re-review) |
| T3 `run-python-unittest` / `validate-run-evidence` | **cerrada** (3 rondas de review-fix; remedio de clase `5c76fee`) |
| T4 integración | **cerrada** (guards `41b1663` → `d7ffbcc` → F1 → `aabb614`/`b0f9ade` → re-review focal) |
| **003-002-artifact-tools** | **CERRADA (2026-10-06)** — `docs/specs/003-002-artifact-tools/closure.md`; P1–P6 implementadas y verificadas |
| Gate de cierre | Suite **439 passed** en `8f5aaa7` (608.67 s, árbol limpio) + validadores **141 PASS / 2 FAIL preexistentes ajenos** |
| Integración | Verificada por 2 vías: producto instalado en raíz aislada (6 guards) y **primer uso real** (`receive`+`materialize`, bytes idénticos, idempotente; CAS del Memory Bank) |
| Memory Bank | `docs/activeContext.md`, `docs/progress.md`, `docs/systemPatterns.md` actualizados y **materializados por el flujo con CAS**; **ADR-014** (recepción/materialización/aprobación separadas) aceptado |
| State | `current_stage: idle`, `active_feature: null`, sin binding de ejecución (convención de fin de feature, verificada en `137698c`/`4f79a1a`) |
| Versión operativa | **`2ec12a7`** (raíz `<home>/.cache/cdad-adopted-2ec12a7`, consumidor verificado); la enmienda declarada de la calibración quedó **retirada** (entra en la versión) |
| Deuda priorizada | `closure.md` §6 — destaca: `README.md` sin clasificar en la política (**decisión del dueño pendiente**); `observation_status=unknown` no ejercitado |
| 003-003 / 003-004 | **queued** — no se implementan por anticipado |

**Siguiente acción — abrir 003-003 (`003-003-progress-guards`) sin ampliar su alcance:**

1. Registrar la feature como activa en el state: `epic_features[003-003].status =
   "in-progress"`, `active_feature = "003-003-progress-guards"`, `current_stage =
   "discovery"` (la convención que usó la reactivación de 003-002).
2. Abrir su **ejecución v2**: `cdad_packet.py prepare --project-root <repo>
   --new-execution` con la autoridad del epic (`execution.md`). Sin esa ejecución, el
   state queda en `idle` y no hay binding que validar.
3. Stage 1 (Discovery) con delegación real: arquitecto → gate → spec/plan aprobados →
   ciclo TDD con revisión independiente.
4. **No** implementar 003-003 ni 003-004 por anticipado; el alcance de 003-003 sigue
   siendo el del epic aprobado.

---

## 1. Reconciliación: snapshot congelado vs. estado actual

| Elemento | Snapshot 2026-09-24 | Estado actual (2026-10-05) | Disposición |
|---|---|---|---|
| `active_epic` | epic-003 | epic-004 (cerrado hoy) | epic-003 pasa a activo |
| `epic_stage` | `features-loop` | `features-loop` | se conserva |
| `active_feature` | `null` | 003-002-artifact-tools | se fija |
| `stack` | `null` | `null` | se conserva (este repo no es proyecto Odoo) |
| 003-001-role-packets | done (2026-09-18) | done | **no se reabre** |
| 003-005-claude-code-packets | done (2026-09-18) | done | **no se reabre** |
| 003-002-artifact-tools | queued, drafts no aprobados | **plan replanificado y revisado**; spec aún draft | entra al ciclo |
| 003-003-progress-guards | queued | queued | no se toca |
| 003-004-context-continuity | queued | queued | no se toca |
| Autoridad HITL | Codex (suspendida, **no heredada**) | nueva delegación (ver §3) | re-registrada |
| Estado del state | congelado en `24d37f0` | el state lo administró epic-004 | reconciliado acá |

**No se restauró el JSON de delegación antiguo** (habría reactivado la autoridad de
Codex sin nueva autorización).

## 2. Qué cambió en epic-004 y afecta a 003

1. **Runtime de paquetes v2.** `prepare` escribe REQUEST/PACKET + binding de state
   en `.cdad/`; los agentes de proyecto se publican en `.opencode/agents/` (I9) con
   la política del proyecto. 003-002 debe construir sobre **v2**, no sobre el flujo
   v1 que asumían los drafts del 2026-09-18.
2. **Política del proyecto y adaptadores** (ADR-012, `docs/cdad-policy.json`): los
   scopes de cada rol derivan de la política; el guard de Claude Code y el
   clasificador la cargan al ejecutarse.
3. **Contrato de plan borrador** (ADR-013) y **plan de validación por unidad**
   obligatorio (`planning-contract-draft.md` §4/§4.1): todo plan de 003-002 debe
   llevar su bloque `plan-tasks`.
4. **Requisitos de orquestación proporcional** (004-003): validación proporcional,
   reutilización de evidencia vigente, delegación por unidades coherentes.
5. **Versión operativa adoptada** (`docs/runtime-adopted-version.md`): commit
   `8cb6580`, raíz aislada, ámbito de proyecto. Los agentes de 003-002 corren con
   esa versión.
6. **Reparto de modelos vigente** (práctica del proyecto, ADR-007): architect,
   implementer y scribe en `mofgw/deepseek-v4.1-flash`; test-writer y reviewer en
   `mofgw/glm-5.3-flash`. **ADR-010** (modelo único para epic-003) sigue vigente
   como *permiso*, no se invoca: usar familias distintas es más estricto que lo
   que habilita y mantiene el invariante reviewer≠implementer.
7. **Garantías de 001/005 preservadas**: 004 fue aditivo; ninguna de sus tres
   features retiró garantías de 003-001/003-005 (verificado en el cierre de
   epic-004, §6).

## 3. Autoridad HITL re-registrada (nueva, no heredada)

| Campo | Valor |
|---|---|
| delegated_to | OpenCode orchestrator (agente `cdad-orchestrator`) |
| requested_by | usuario |
| requested_at | 2026-10-05 |
| scope | `epic-003-context-efficiency`: alcance del epic aprobado, specs, priorización de reviews, aprobaciones de Memory Bank y gates para sus features pendientes (003-002, 003-003, 003-004) e integración |
| expires | cierre, cancelación o revocación del epic |
| publication | sin push automático |
| source | `docs/epics/epic-003-context-efficiency/execution.md` |

Límites expresos (los mismos de la delegación original + los del mandato actual):
- No concede autoridad de publicación.
- No autoriza a tocar instalaciones globales en HOME.
- El alcance estratégico (nuevos alcances, cambios de frontera del epic, cierre del
  epic) sigue siendo del usuario.
- **No implementa 003-003 ni 003-004** por anticipado.

## 4. Estado de 003-002 al reanudar — **HISTÓRICO** (superado por §0)

> Registro de lo que había al reanudar. La spec ya está aprobada y T1–T3 están
> cerradas: nada de esta sección queda pendiente salvo lo que §0 marca.

- **Spec**: `docs/specs/003-002-artifact-tools/spec-draft.md` — **draft no
  aprobado** del 2026-09-18. Postcondiciones P1–P6. → hoy: `spec.md` aprobada.
- **Plan**: `docs/specs/003-002-artifact-tools/plan.md` — replanificado al contrato
  vigente y **revisado** por sesión independiente (004-003 T7):
  - **F1 y F2 (bloqueantes) aplicados** (el bloque omitía el validador; faltaban las
    regresiones del instalador).
  - **F3–F6 abiertos** (precisión, no defectos observables): F3 protocolo de
    serialización T2/T3 · F4 wording de la referencia en state · F5 `.gitignore`
    probablemente no-op · F6 incertidumbre VERIFY del state schema.
  - **F3 y F6 resueltos el 2026-10-05**; F4 y F5 pendientes de decisión.
  - Las cuatro marcas VERIFY quedaron resueltas (ver la sección "Incertidumbres del
    plan resueltas" del plan).
  - La **propiedad del state** quedó declarada: el orquestador es el único escritor;
    `receive`/`materialize`/`run-evidence` no lo tocan.
- **Pendiente para construir** (al reanudar): reconciliar y aprobar la spec;
  aprobar el plan; resolver F4/F5. → **todo cumplido**; ver §0.

## 5. Siguiente acción al reanudar — **HISTÓRICO** (cumplida)

> Estos tres pasos se ejecutaron el 2026-10-05 (spec reconciliada y aprobada; plan
> aprobado; ejecución v2 abierta; T1–T3 cerradas). La siguiente acción vigente está
> en §0.

1. Reconciliar `spec-draft.md` con los contratos vigentes y entregarla como texto
   final para aprobación del dueño (delegado).
2. Aprobar spec y plan; registrar ambas aprobaciones en el state.
3. Abrir la ejecución v2 de 003-002 y arrancar T1 (AUDIT/RED) con delegación real y
   revisión independiente.

## 6. Continuidad (lo que todo handoff debe dejar persistido)

- **Versión operativa**: `2ec12a7` en raíz aislada, ámbito de proyecto
  (`docs/runtime-adopted-version.md`); consumidor verificado; enmienda de calibración
  retirada (ya está en la versión).
- **Tarea y estado**: 003-002 **cerrada**; state en `idle` sin binding de ejecución;
  003-003 y 003-004 en `queued`.
- **Decisiones**: la calibración de la review
  (`docs/owner-decision-review-calibration-2026-10-05.md`, precisada en
  `skills/cdad-cycle/references/stage-4-review.md`); ADR-014; la desviación de
  `README.md` (decisión del dueño pendiente).
- **Evidencia**: `docs/specs/003-002-artifact-tools/{spec,plan,closure}.md`,
  `review-t1..t4*.md`, `supervision-record.md`, `dispatch-ledger.md`;
  `epics/epic-003-context-efficiency/evidence-utility-2026-10-05.md`.
- **Pendientes**: abrir 003-003 (§0); deuda priorizada de 003-002 (`closure.md` §6);
  decisión del dueño sobre `README.md` en la política.
- **Siguiente acción**: ver §0.
