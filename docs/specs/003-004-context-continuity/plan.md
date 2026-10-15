---
feature_id: 003-004-context-continuity
feature_name: Memoria activa, checkpoints y reanudación automática
created_at: 2026-10-07
status: approved
approved_by: orchestrator (HITL delegation epic-003)
approved_at: 2026-10-07
---

# Plan — 003-004-context-continuity

> **Versión final** del borrador `architect-draft-001.md` con la disposición
> `review-draft-001-decision.md`: **4 tareas** (R5), sin `verify-checkpoint`
> (R1), sin subcomando `budget` propio (R3), `--max-bytes` calibrable (R4),
> proyección on-demand sin `ACTIVE.json` (O1), T4 sin dependencia de fixtures
> (O2) y un único escenario continuo (O4). El plan define el **contrato**, nunca
> el código (`stage-2-specification.md:115-119`); usa el bloque canónico
> `plan-tasks` de `planning-contract-draft.md` §4.1.

Principio transversal: **read-only** sobre el producto salvo
`.cdad/executions/<id>/continuity/**`; sin servicio; el juicio y la escritura
del state quedan en el orquestador. Tres contratos con nombre:
`continuity-checkpoint-v1` (T1), `reconcile-v1` (T2), `trigger-v1` (T3).

## 1. Tareas

### T1 — Checkpoint inmutable + memoria activa + `resume`
- **Resultado observable / postcondiciones:** P1, P2, P5, P7.
- **Alcance incluido/excluido:** L2 create-only content-addressed (cuerpo canónico
  = digest y `seq`), `prev_checkpoint_sha256`, `references[]` con digest; `begin`
  idempotente (cuerpo idéntico al head → no-op rc 0, clave
  `(execution_id, packet_id, attempt)`); proyección de memoria activa on-demand
  (no persistida) con `resume`, `--role` y `--max-bytes` (default 16 KiB, falla
  cerrado sin truncar). Excluido: reconciliación (T2), presupuesto/trigger (T3).
- **Consume:** state/execution (001); esquemas existentes (001/003); receipts de
  002 (para poblar `receipts[]`).
- **Produce:** `cdad-continuity-checkpoint` (`continuity-checkpoint-v1`).
- **Dependencias previas / condición de arranque:** ninguna; arranca el pipeline.
- **Archivos:** Create `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Create `scripts/cdad_continuity.py` (wrapper);
  Create `skills/cdad-cycle/assets/continuity-checkpoint.schema.json`;
  Create `skills/cdad-cycle/assets/active-record.schema.json`;
  Test `tests/test_003_004_t1_checkpoint.py`, `tests/test_003_004_t1_resume.py`.
- **Validación (focales):** los 4 negativos de tamper vía `resume`; round-trip
  determinista (mismo input → mismo digest); `begin` idéntico = no-op rc 0;
  `resume --role test-writer` no expone `implementation_roots` de la política;
  `--max-bytes` excedido → rc≠0 sin truncar.
- **Detener si:** V6 no se puede fijar sin ambigüedad, o el cap no se alcanza sin
  degradar información obligatoria → reacotar con el dueño.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — Write-ahead + `reconcile` + fixtures de la matriz
- **Resultado observable / postcondiciones:** P3, P8 (parte fixtures).
- **Alcance incluido/excluido:** `checkpoint` (write-ahead) y `reconcile` por
  `(execution_id, packet_id)` sobre receipts/journal (002), dispatch I8 y state;
  clasificación cerrada de §2 de la spec; **no** repite efecto con receipt; no
  falla por ausencia de `ACTIVE.json`. Fixtures deterministas de la matriz
  (crash/restart/split-brain/stale/autoridad vencida/tarea cerrada) + un
  escenario continuo legítimo. Excluido: cambio de state y de autoridad.
- **Consume:** `cdad-continuity-checkpoint` (`continuity-checkpoint-v1`, T1);
  `.cdad/runtime/results/**` y `materializations/**` (002); dispatches I8; state (001).
- **Produce:** `cdad-continuity-reconcile` (`reconcile-v1`).
- **Dependencias previas / condición de arranque:** T1 verde.
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Test `tests/test_003_004_t2_writeahead.py`,
  `tests/test_003_004_t2_reconcile.py`; fixtures bajo `tests/fixtures/003_004/**`.
- **Validación (focales):** los estados de §2 por fixtures —incluido `unknown`—
  etiquetados **simulación**; con receipt válido el CLI **no** ofrece repetir el
  efecto; `begin` divergente con la misma clave → conflicto/escalado sin
  sobrescribir; autoridad vencida no escribe checkpoint; cabezas divergentes →
  escalar; un flujo continuo legítimo no dispara intervención.
- **Regresión:** `tests/validate-consistency.sh`.
- **Detener si:** no se puede leer un receipt sin ambigüedad → `unknown`, escalar.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Trigger con unknowns + referencia operativa
- **Resultado observable / postcondición:** P6.
- **Alcance incluido/excluido:** `trigger` con perfil 200k/150k/120k leyendo el
  snapshot de presupuesto embebido en el checkpoint (`budget.source`); guía
  `references/continuity.md`. Excluido: subcomando `budget` propio (R3), medición
  de contexto nueva y lector de sesiones.
- **Consume:** `cdad-continuity-checkpoint` (`continuity-checkpoint-v1`, T1);
  `cdad_guard budget` (003) como fuente de intentos; tokens reportados por el
  runtime (si existen).
- **Produce:** `cdad-continuity-trigger` (`trigger-v1`).
- **Dependencias previas / condición de arranque:** T1 verde.
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_continuity.py`;
  Create `skills/cdad-cycle/references/continuity.md`;
  Test `tests/test_003_004_t3_trigger.py`.
- **Validación (focales):** sin contador/límite → `trigger: unknown` y
  `context_*: null` con `unknowns[]`; con contador y límite → `prepare`/`rotate`
  según la política; el presupuesto de intentos de una sesión nueva no se
  reinicia y se reporta con `source`.
- **Detener si:** se pretende un número sin fuente → prohibido (invariante 2).
- **Owner:** RED test-writer; GREEN implementer.

### T4 — Adopción real en un límite natural de tarea
- **Resultado observable / postcondición:** P8 (adopción).
- **Alcance incluido/excluido:** una **reconstrucción automática** de sesión en un
  límite natural de tarea; como 003-004 es la última feature del epic, se usa el
  propio desarrollo (rotación del orquestador entre T3 y el cierre, «entre tareas
  naturales del mismo desarrollo» según el brief), registrada en
  `continuity-ledger.md`. Excluido: terminar la feature antes para repetirla;
  benchmark; comparación A/B.
- **Consume:** `cdad-continuity-reconcile` (`reconcile-v1`, T2) y
  `cdad-continuity-trigger` (`trigger-v1`, T3); límite natural real.
- **Produce:** `continuity-ledger` (registro de adopción).
- **Dependencias previas / condición de arranque:** T2 y T3 verdes (O2: no
  depende de fixtures).
- **Archivos:** `docs/specs/003-004-context-continuity/continuity-ledger.md`.
- **Registro (campos obligatorios):** `situación | evidencia (file:line) |
  decisión | autoridad vigente | presupuesto (intentos/contexto o null) |
  falsas alarmas | retrabajo | pendiente`.
- **Validación (observable):** la reconstrucción conserva decisiones y
  aprobaciones, reconcilia trabajo en curso y continúa sin repetir la tarea
  confirmada (`plan.md:165-169`).
- **Owner:** orquestador.

## 2. Escenario continuo (único)

Además de los fixtures de fallo de T2, **un** escenario continuo **etiquetado
simulación**: varias llamadas y artefactos que progresan, un `reconcile` sin
efecto nuevo y una reconstrucción intermedia **no** disparan intervención ni
retrabajo; la evidencia queda en `continuity-ledger.md` de T4 (O4: sin escenario
global duplicado).

## 3. Estimaciones (rango, método, incertidumbre)

- Rango por unidad: **medio** (T1, T2), **bajo–medio** (T3), **bajo** (T4).
  Método: comparación cualitativa con ciclos similares de 003-002/003-003.
  Incertidumbre **alta** por V1–V6 (observabilidad del runtime).

## 4. Integración final

1. Suite completa del repo + los tres validadores (sin regresiones; deuda de CI
   declarada, convención vigente).
2. Adopción real en un límite natural con `continuity-ledger.md` (T4).
3. Spec y plan revisados juntos por sesión independiente antes de aprobar.

## 5. Incertidumbres / replanificación

- Si V1–V6 no se resuelven, reacotar con el dueño antes de expandir
  infraestructura; no asumir APIs (`plan.md:191-197`).
- Si una unidad crece más allá de su mini-ciclo, pasa a candidata a feature propia.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con fixtures deterministas etiquetados simulación; suite completa y validadores del repo al cierre; sin incidentes reales provocados; un único escenario continuo sin retrabajo",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "scripts/cdad_continuity.py", "skills/cdad-cycle/assets/continuity-checkpoint.schema.json", "skills/cdad-cycle/assets/active-record.schema.json", "tests/test_003_004_t1_checkpoint.py", "tests/test_003_004_t1_resume.py"], "focal_tests": ["tests/test_003_004_t1_checkpoint.py", "tests/test_003_004_t1_resume.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-continuity-reconcile", "contract": "reconcile-v1"}], "consume": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "tests/test_003_004_t2_writeahead.py", "tests/test_003_004_t2_reconcile.py", "tests/fixtures/003_004/**"], "focal_tests": ["tests/test_003_004_t2_writeahead.py", "tests/test_003_004_t2_reconcile.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "cdad-continuity-trigger", "contract": "trigger-v1"}], "consume": [{"artifact": "cdad-continuity-checkpoint", "contract": "continuity-checkpoint-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_continuity.py", "skills/cdad-cycle/references/continuity.md", "tests/test_003_004_t3_trigger.py"], "focal_tests": ["tests/test_003_004_t3_trigger.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "continuity-ledger", "contract": "n/a"}], "consume": [{"artifact": "cdad-continuity-reconcile", "contract": "reconcile-v1", "producer": "T2"}, {"artifact": "cdad-continuity-trigger", "contract": "trigger-v1", "producer": "T3"}], "depends_on": ["T2", "T3"], "parallel": [], "files": ["docs/specs/003-004-context-continuity/continuity-ledger.md"], "observable_checks": ["una reconstrucción automática real en un límite natural queda registrada en continuity-ledger.md con situación, evidencia file:line, decisión, autoridad vigente, presupuesto, falsas alarmas, retrabajo y pendiente"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh", "scripts/validate-subagents.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```

---

Status: Approved by orchestrator (HITL delegation epic-003) on 2026-10-07.
