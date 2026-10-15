---
feature_id: 003-003-progress-guards
feature_name: Guards de progreso y recuperación acotada
created_at: 2026-10-06
status: pending-approval
approved_by: pending
approved_at: pending
---

# Plan — 003-003-progress-guards

> **Versión final** del borrador `architect-draft-001.md` (7 tareas) con la
> **fusión 7→5** de `review-draft-001.md` (§2b): `T1+T2→T1`, `T3→T2`,
> `T4+T5→T3`, `T6→T4`, `T7→T5`. Se corrigen F2 (citas), O1 (`steps:300`),
> O2 (preflight lee la política) y O3 (dedup explícito). Unidades pequeñas y
> coherentes; cada una con su plan de validación
> (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4/§4.1).
> Complejidad: interfaces nuevas + varios dominios (runtime, permisos, estado) ⇒
> plan revisado por sesión independiente junto con la spec
> (`planning-contract-draft.md:163-167`). El architect no aprueba su propuesta.

Principio transversal: **read-only**; sin servicio; el juicio en el orquestador.
La estrategia común de validación se declara una vez (`@validation_strategy`).

## 1. Fusión 7→5 (trazabilidad del borrador)

| Tarea final | Origen (borrador) | Postcondiciones | Por qué es segura |
|---|---|---|---|
| **T1** Núcleo de traza + clasificación de repetición/polling | T1 + T2 | P1, P2, P7 | Misma superficie (`cdad_guard.py`) y misma DB de sesiones; "repetición improductiva" y "legítimo que progresa" son el mismo truco de separación |
| **T2** Pre-flight de capacidad/permisos + acotado de rechazos | T3 | P3 | Dominio policy/permisos aislado; se queda sola |
| **T3** Presupuesto durable + eventos + tabla de escalado | T4 + T5 | P4, P5 | Comparten el canal de escritura (`guards/`) y el paquete de escalado consulta el presupuesto |
| **T4** Fixtures de trazas + generalidad + simulación declarada | T6 | P6, P8 (generalidad) | Product owner test-writer (inquilino correcto) |
| **T5** Integración en un límite de tarea real + registro de uso | T7 | P7 (dedup), P8 (adopción) | Owner orquestador, dueño distinto; es el gate del epic |

Cuidado: **T4 y T5 no se fusionan** (`T5.owner = "orquestador"`): es la
validación de "capacidad aplicada en un desarrollo real"
(`handoff-architect-001.md:54-56`). El pipeline es serializado
(`parallel: []`): T1–T5 comparten `skills/cdad-cycle/scripts/cdad_guard.py`
y no se despachan en paralelo sobre el mismo archivo.

## 2. Estrategia de validación (declarada una vez)

- **Focales** por unidad: `env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
  sobre el test focal de cada tarea.
- **Trazas grabadas** (fixtures deterministas) para todo escenario de fallo; los
  fallos provocados se etiquetan explícitamente **simulación**.
- **No se provocan incidentes reales** en proyectos reales; no se repite un
  desarrollo completo (`plan.md:173-176`).
- **Suite completa + validadores** del repo al cierre
  (`tests/validate-consistency.sh`, `tests/validate-odoo-specialization.sh`,
  `scripts/validate-subagents.sh`); ausencia de CI declarada como deuda.
- **Prueba de trabajo legítimo progresivo** (global, §4) en verde y **sin
  intervención**.

## 3. Tareas

### T1 — Núcleo de traza + clasificación de repetición/polling

- **Resultado observable / postcondiciones:** P1, P2, P7. `observe` detecta
  repeticiones equivalentes sin progreso con regla explícita y evidencia de
  equivalencia; un polling válido (condición/deadline/cadencia) no se corta y al
  vencer escala una vez; un trabajo legítimo y progresivo continúa sin intervención.
- **Alcance incluido / excluido:** traza `trace-v1`, núcleo determinista de
  repetición y clasificación de polling/no-alarma. Excluido: pre-flight (T2),
  presupuesto/escalado (T3), fixtures formales (T4).
- **Consume:** DB OpenCode read-only (scan:21-54); `dispatches/*.json`; state;
  artefactos/git como señal de progreso. (Externos al plan.)
- **Produce:** `cdad-guard-trace` (contrato `trace-v1`) y `cdad-guard-poll`
  (`poll-v1`).
- **Dependencias previas / condición de arranque:** ninguna; arranca el pipeline.
- **Archivos (propuestos):** Create `skills/cdad-cycle/scripts/cdad_guard.py`;
  Create wrapper `scripts/cdad_guard.py`; Create
  `skills/cdad-cycle/assets/guard-trace.schema.json`; Test
  `tests/test_003_003_t1_repetition.py`, `tests/test_003_003_t1_polling.py`.
- **Validación (focales/simulación/no-alarma):** focales de bucle equivalente
  (incidente 2.073), progreso real y nueva hipótesis; **simulación** etiquetada en
  el escenario de bucle. Prueba de trabajo legítimo: el encargo progresivo no
  dispara intervención.
- **Detener si:** V1/V2/V5 no se resuelven ⇒ declarar límite, no asumir.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — Pre-flight de capacidad/permisos + acotado de rechazos

- **Resultado observable / postcondición:** P3. Rechazos prevalidados contra
  política+rol o acotados; sin loop ilimitado de la misma llamada denegada.
- **Alcance incluido / excluido:** pre-flight determinista (lectura) y acotado de
  rechazos. Excluido: cambio de autoridad; auto-grant/auto-harden.
- **Consume:** `docs/cdad-policy.json` (**lectura**, O2), mapa de rol, execution
  context; `error.type=="permission.rejected"` (scan:46); `cdad-guard-trace`
  (`trace-v1`) de T1.
- **Produce:** `cdad-guard-preflight` (contrato `preflight-v1`).
- **Dependencias previas / condición de arranque:** T1 (traza).
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_guard.py`; Test
  `tests/test_003_003_t2_preflight.py`. `docs/cdad-policy.json` **no** figura en
  `files`: es una entrada de lectura, no una escritura (O2); así se evita una
  regresión cross-feature.
- **Validación (focales):** deny de operación legítima (defecto del producto),
  deny fuera de rol (correcto), variantes de ruta mediadas por patrón (V6;
  `t7-live-walk.md:38-66`). **Invariante:** ningún auto-grant/auto-harden.
- **Detener si:** la política no puede expresarse sin un motor de reglas general.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Presupuesto durable + eventos + tabla de escalado

- **Resultado observable / postcondiciones:** P4, P5. Cada recuperación consume
  presupuesto y emite receipt/evento; reanudar no reinicia; ambigüedad/`unknown`
  devuelve paquete breve con tabla cerrada evento→acción y sin decisión semántica
  encubierta.
- **Alcance incluido / excluido:** presupuesto durable, `guard-event.schema.json`,
  tabla cerrada de acciones y escalado. Excluido: checkpoints/reconstrucción de
  003-004 (D10).
- **Consume:** execution context (001), receipt/journal (002), dispatch I8,
  `cdad-guard-trace` (`trace-v1`) de T1.
- **Produce:** `cdad-guard-budget` (`budget-v1`) y `cdad-guard-escalation`
  (`escalation-v1`).
- **Dependencias previas / condición de arranque:** T1.
- **Archivos:** Modify `skills/cdad-cycle/scripts/cdad_guard.py`; Create
  `skills/cdad-cycle/assets/guard-event.schema.json`; Test
  `tests/test_003_003_t3_budget.py`, `tests/test_003_003_t3_escalation.py`.
  Escritura **solo** bajo `.cdad/executions/<id>/guards/**` (nunca
  `docs/.cdad-state.json`).
- **Validación (focales):** restart/sesión nueva no reinician contadores;
  reconciliación de 002 antes de retry (D7); caso ambiguo → escalar; caso sin
  señal → `unknown`; no se fabrica outcome.
- **Frontera:** interfaces keyed por `execution_id`, sin truncar contratos, que
  no obstaculizan 003-004 (D10).
- **Owner:** RED test-writer; GREEN implementer.

### T4 — Fixtures de trazas + generalidad + simulación declarada

- **Resultado observable / postcondiciones:** P6, P8 (parte generalidad). Fixtures
  cubren bucle, progreso, polling, flaky y crash; tests Go co-ubicados y un ciclo
  sin código; fallos provocados **etiquetados simulación**.
- **Alcance incluido / excluido:** fixtures deterministas y cobertura de
  generalidad. Excluido: repetir un desarrollo completo; provocar incidentes
  reales.
- **Consume:** `cdad-guard-trace` (`trace-v1`) y `cdad-guard-poll` (`poll-v1`) de
  T1; `cdad-guard-preflight` (`preflight-v1`) de T2; `cdad-guard-budget`
  (`budget-v1`) y `cdad-guard-escalation` (`escalation-v1`) de T3.
- **Produce:** `cdad-guard-fixtures` (contrato `fixtures-v1`).
- **Dependencias previas / condición de arranque:** T1, T2, T3 verdes.
- **Archivos:** Test `tests/test_003_003_t4_fixtures.py`; fixtures bajo
  `tests/fixtures/003_003/**`.
- **Validación (focales + observable):** `focal_tests` deterministas;
  `observable_checks` para el ciclo sin código ("un ciclo sin código con progreso
  no recibe intervención") y tests Go co-ubicados.
- **Regresión:** `tests/validate-consistency.sh` sin regresiones.
- **Owner:** RED test-writer; GREEN implementer.

### T5 — Integración en un límite de tarea real + registro de uso

- **Resultado observable / postcondiciones:** P7 (dedup), P8 (adopción). Adopción
  real con `guards-ledger.md` y de-dup de incidentes.
- **Alcance incluido / excluido:** registro de uso real en un límite de tarea del
  epic. Excluido: rehacer la tarea; benchmark.
- **Consume:** `cdad-guard-fixtures` (`fixtures-v1`) de T4; límite de tarea real
  del epic.
- **Produce:** `cdad-guard-adoption` (contrato `adoption-v1`).
- **Dependencias previas / condición de arranque:** T4.
- **Archivos:** `docs/specs/003-003-progress-guards/guards-ledger.md`.
- **Registro (O3 — campos obligatorios):** `situación | evidencia (file:line) |
  decisión | falsas alarmas | costo | pendiente | dedup_key | cambio_relevante`.
  **Clave de dedup explícita:**
  `dedup_key = canon(incident_kind, fingerprint_canónico, execution_id, packet_id)`.
  Solo se re-alerta si cambia el **token de relevancia** (digest de progreso en
  git/artefacto/state) o la clase de la huella; un incidente sin cambio relevante
  no vuelve a alertar (`handoff-architect-001.md:45`).
- **Validación (observable):** un límite de tarea real queda registrado en
  `guards-ledger.md` con su `dedup_key`; falsas alarmas con su causa.
- **Regresión:** los tres validadores del repo sin regresiones.
- **Owner:** orquestador.

## 4. Prueba de trabajo legítimo progresivo (global)

Además de los fixtures de fallo, un escenario continuo: un encargo simulado
**etiquetado simulación** que progresa en varias llamadas y artefactos **no**
dispara ninguna intervención; la evidencia queda en `guards-ledger.md` con
falsas alarmas = 0 registradas (P7). Es el contrapeso de no-alarma de todo el
pipeline.

## 5. Estimaciones (rangos, método declarado, incertidumbre)

- Rango por unidad: **bajo–medio** (T1, T3, T4), **medio** (T2, T5). Método:
  comparación cualitativa con ciclos de tamaño similar de 003-002/004-003.
  Incertidumbre: **alta** por V1–V6 (observabilidad del runtime).

## 6. Integración final

1. Suite completa del repo + los tres validadores (sin regresiones; deuda de CI
   declarada, convención vigente).
2. Adopción en un límite de tarea real del epic con `guards-ledger.md`.
3. `plan.md` y `spec.md` revisados juntos por sesión independiente antes de
   aprobar (interfaces nuevas + límites de confianza).

## 7. Incertidumbres / replanificación

- Si **V1–V6** no se resuelven, reacotar el alcance explícitamente con el dueño
  antes de expandir infraestructura (`plan.md:193-197`) — no asumir APIs.
- Si una unidad crece más allá de su mini-ciclo, pasa a candidata a feature propia.

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) + trazas grabadas etiquetadas simulación; suite completa y validadores del repo al cierre; no se provocan incidentes reales; escenario global de trabajo legítimo progresivo sin intervención",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "cdad-guard-trace", "contract": "trace-v1"}, {"artifact": "cdad-guard-poll", "contract": "poll-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "scripts/cdad_guard.py", "skills/cdad-cycle/assets/guard-trace.schema.json", "tests/test_003_003_t1_repetition.py", "tests/test_003_003_t1_polling.py"], "focal_tests": ["tests/test_003_003_t1_repetition.py", "tests/test_003_003_t1_polling.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-guard-preflight", "contract": "preflight-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "tests/test_003_003_t2_preflight.py"], "focal_tests": ["tests/test_003_003_t2_preflight.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "cdad-guard-budget", "contract": "budget-v1"}, {"artifact": "cdad-guard-escalation", "contract": "escalation-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}], "depends_on": ["T1"], "parallel": [], "files": ["skills/cdad-cycle/scripts/cdad_guard.py", "skills/cdad-cycle/assets/guard-event.schema.json", "tests/test_003_003_t3_budget.py", "tests/test_003_003_t3_escalation.py"], "focal_tests": ["tests/test_003_003_t3_budget.py", "tests/test_003_003_t3_escalation.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "cdad-guard-fixtures", "contract": "fixtures-v1"}], "consume": [{"artifact": "cdad-guard-trace", "contract": "trace-v1", "producer": "T1"}, {"artifact": "cdad-guard-poll", "contract": "poll-v1", "producer": "T1"}, {"artifact": "cdad-guard-preflight", "contract": "preflight-v1", "producer": "T2"}, {"artifact": "cdad-guard-budget", "contract": "budget-v1", "producer": "T3"}, {"artifact": "cdad-guard-escalation", "contract": "escalation-v1", "producer": "T3"}], "depends_on": ["T1", "T2", "T3"], "parallel": [], "files": ["tests/test_003_003_t4_fixtures.py", "tests/fixtures/003_003/**"], "focal_tests": ["tests/test_003_003_t4_fixtures.py"], "observable_checks": ["tests Go co-ubicados y un ciclo sin código cubiertos y deterministas"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T5", "produce": [{"artifact": "cdad-guard-adoption", "contract": "adoption-v1"}], "consume": [{"artifact": "cdad-guard-fixtures", "contract": "fixtures-v1", "producer": "T4"}], "depends_on": ["T4"], "parallel": [], "files": ["docs/specs/003-003-progress-guards/guards-ledger.md"], "observable_checks": ["un límite de tarea real queda registrado en guards-ledger.md con su dedup_key"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh", "scripts/validate-subagents.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```
