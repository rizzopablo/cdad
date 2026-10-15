# Cierre — 004-003-planning-procedures

Fecha: 2026-10-05. Orquestador: OpenCode (`cdad-orchestrator`), HITL delegada por
el dueño (registrado en `docs/.cdad-state.json`, `delegation_history`).

## Estado de tareas

| Tarea | Estado | Evidencia |
|---|---|---|
| T1 — contract-kind de plan borrador (PD-1) | cerrada | `review-t1.md`, `review-t1-rereview.md`; commits `1f51f03`…`b0acb03` |
| T2 — subfase y paquete de plan-review (PD-2/3/4/9) | cerrada | `review-t2.md`, `review-t2-rereview.md`; `019eee6`, `f12b478`, `1cb2732` |
| T3 — checks mecánicos de plan (AC-3) | cerrada | `review-t3.md`; `9f43d65`, `6257431` |
| T4 — plan de validación por unidad (PD-8/PD-11) | cerrada | `review-t4.md`, `review-t4-rereview.md`; `5126c75`…`afbb776` |
| T5 — equivalencia y re-entry (G1–G3) | cerrada | `review-t5.md`; `cf8963a`, `b881235` |
| T6 — F4 co-ubicados | **condicional/no ejecutada** | Decisión D3: fuera del camino feliz de este repo (`test_roots:["tests"]`); deuda para el primer consumidor Go |
| T7 — recorrido instalado real (PD-13) | cerrada | `evidence/t7-journey.md` |

## Verificación de criterios de aceptación

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| AC-1 | PD-1–PD-13 trazadas a pruebas de comportamiento; negativos que no fabrican aprobación ni publican para contratos no soportados | ✓ | `test-audit.md` (35/35 mapeados, 0 superfluos) |
| AC-2 | Un plan borrador se revisa **sin** volverse aprobado, desde sesión distinta, sobre producto instalado | ✓ | `t2_plan_review` (render instalado byte-idéntico); T7 preparó el `plan-review` rc=0; el plan de 003-002 sigue `draft` |
| AC-3 | Fixtures (sin productor, ciclo, contrato incompatible, paralelismo inválido) contra los checks reales | ✓ | `t3_plan_checks` (4 negativos + control); verificado por el reviewer de T3 con 10 sondas |
| AC-4 | La regla de equivalencia se ejercita con un flujo consecutivo | ✓ por disposición | Uso real registrado en el ciclo (suites 331/333/338/340/345/353/356/364 **citadas**, no re-ejecutadas, con identidad de árbol) + T7. `plan.md` trazado; residual declarado: PD-5/PD-6 no tienen enforcement ejecutable |
| AC-5 | Go co-ubicado y ciclo sin código con comprobación observable declarada | ✓ | `t4_validation_fields` (`GO_TASKS`, `NOCODE_WITH_CHECKS_TASKS`) |
| AC-6 | La sesión de replan de 003-002 produce dictamen y cambios concretos sin reimplementar 003-002 | ✓ | `evidence/t7-journey.md`; F1/F2 aplicados (plan re-valida, sha `781994fb…`); F3–F6 abiertos a epic-003 |
| AC-7 | Los validadores pasan | **eximido por decisión del dueño** | ver abajo |
| AC-8 | Limitaciones aceptadas declaradas; UNKNOWN permanece UNKNOWN | ✓ | `review-second-look.md`; deuda consolidada abajo |

### Decisión del dueño sobre AC-7 (HITL delegada, 2026-10-05)

`make validate` en `287f6c7` = **141 PASS / 2 FAIL**, ambos **preexistentes** a la
feature y **no implicados** por ningún archivo de su diff:

- **F011-A — drift de los mirrors de `$HOME`** (`scripts/validate-subagents.sh`):
  la copia instalada en `~/.claude` y `~/.config/opencode` carece incluso de
  contenido de features previas (T1/T2/T4 de 004-001/004-002). **No es resoluble
  por regla del proyecto**, que prohíbe instalar CDAD en HOME real; la evidencia
  de promulgación válida es la **instalación en raíz aislada** con
  `install.sh --check` **PASS (303 grupos)** (`evidence/t7-journey.md`).
- **F011-B — A3** (`validate-odoo-specialization.sh`) marca la palabra contenida
  en un identificador de `tests/test_role_packets.py` (archivo intacto desde
  `c50f521`, 004-002) y ruido transitorio de `__pycache__` de las corridas.

**Resolución:** AC-7 se **exime** para esta feature con la justificación
precedente; los dos fallos quedan como **deuda priorizada** con dueño asignado
(acotar el patrón A3 a palabra completa; excluir `__pycache__`; decidir la
política de reinstalación de mirrors de `$HOME`). Se descarta fabricar un verde
local que no corresponda al medidor real.

## Evidencia de cierre

- **Suite completa en worktree fijado** `287f6c7` (`make staging` + `env -u TMPDIR
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q -p no:cacheprovider`):
  **364 passed** (620.78 s). Re-verificada por el reviewer de la segunda mirada:
  **364 passed**.
- **Instalación aislada:** `install.sh --force` rc=0 (`Verify: PASS — 11 cdad
  agents`) + `install.sh --check` **PASS (303 grupos)**; el producto instalado
  contiene T1 (12 hits `draft-plan`), T2 (`reviewer-plan-review.md`), T4 (14 hits
  `plan-tasks`) y T5 (5 hits de equivalencia).
- **Brecha D8 cerrada:** el paquete v2 del **architect** se preparó por primera
  vez (`contract_kind: approved-epic-plan`) — imposible antes del registro I2 y
  del soporte de contrato de T1.

## Deuda priorizada (ninguna rompe el camino feliz)

T1: F3, F4, F5 · T2: O1 (newline), O2 (=O-D), O3 · T4: F-C (parcial), F-E · T5:
F4/F5 (etiqueta del co-dueño SKILL), F6 (comparadores concretos de equivalencia) ·
Segunda mirada: O-A…O-H · T7→003-002: F3–F6 de `review-plan-001` · T6/F4
condicional para el primer consumidor Go · F011-A/B.

## Límites declarados

- PD-5/PD-6 (equivalencia y re-entry) **no tienen enforcement ejecutable**: son
  disciplina del orquestador verificada por revisión, no un mecanismo. La
  propuesta de un mecanismo futuro pertenece a 003-002/003-003.
- El recorrido de T7 se hizo sobre el **draft** de 003-002; su aprobación
  pertenece al ciclo de epic-003 (suspendido).
