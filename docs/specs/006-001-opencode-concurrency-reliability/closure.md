# Cierre de 006-001-opencode-concurrency-reliability

**Feature:** 006-001-opencode-concurrency-reliability · **Epic:** `epic-006-opencode-concurrency` (primera feature) ·
**Cerrada:** 2026-10-17 · **Contrato:** `spec.md` sha256 `dac418b98f938b23bd98ceec625c741cf1df601a3c178a2144ee48996415183b` (v2) ·
**Aprobación:** orquestador Claude bajo la HITL delegada del epic-006 (`docs/epics/epic-006-opencode-concurrency/execution.md`); Memory Bank aprobado por Pablo el 2026-10-17.

## 1. Qué entrega

Modo de ejecución explícito para la delegación OpenCode (`server` | `service` | `standalone`), con preflight, espera proporcional, correlación conservada en `timeout`, terminación del grupo de procesos e intento previo que falla cerrado. Con el servicio vivo ningún camino abre un `standalone` (INV-10). Decisión en **ADR-031**.

## 2. Gates

| Etapa | Evidencia |
|---|---|
| Construcción T1, T1b, T2, T3 | RED→GREEN por unidad (`t*-red.md`, `t*-green.md`) |
| Review formal | 3 bloqueantes, 5 opcionales, 3 abstenciones (`review.md`) |
| Review-fix | RED `17a7ca1` → GREEN `161c9ff` (`rf-red.md`, `rf-green.md`); focal y regresiones 81 passed, 1 skipped |
| Re-review | B1, B2, B3a, B3b y O1 cerrados; 0 bloqueantes (`rereview.md`) |
| Suite de cierre | 1 failed, 1079 passed, 5 skipped; la falla es DT-9 (verde aislada 5/5) (`execution.md`) |
| Memory Bank | `activeContext.md`, `progress.md`, `systemPatterns.md`, ADR-031 |

## 3. Abierto al cerrar

- **PD-6:** al cierre estaba BLOQUEADO por falta de la credencial; resuelto después del cierre (`execution.md`, «PD-6 en `mode: server`»): 3 despachos concurrentes `completed` sin servidores privados ni locks.
- **AC-7** pendiente del dueño.
- **Redespliegue en HOME** posterior al review-fix, a la orden del dueño.
- **Deuda:** DT-8, DT-9, O3–O5, opcional nuevo de la re-review, CLI `receive`/kind, falta de una vía CLI para fallar un paquete despachado.
