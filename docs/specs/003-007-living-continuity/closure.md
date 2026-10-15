# Cierre — 003-007-living-continuity

**Cerrada:** 2026-10-08, por el orquestador bajo la delegación HITL de epic-003. La abrió el dueño
el mismo día tras la revisión externa de Codex ("De acuerdo, avanza con eso"). Es la última feature
de epic-003.

## Qué entrega
- **Clases de referencia declaradas por el escritor** (`contract` / `living`; ausente → `contract`).
  `contract` bloquea con path y digests; `living` informa `changed`/`missing` y no bloquea. El CLI
  nunca clasifica por ruta (`b1e56e9`, ADR-018).
- **Proyección de autoridad del state** con `fields` (`hitl_delegation`, `approver`, `execution`).
  Falla cerrado al escribir si el archivo no es JSON o la proyección queda vacía.
- **`checkpoint` ≠ `begin`:** `record` en todo body nuevo; un checkpoint con la clave del head
  apendea un eslabón; un `begin` divergente sigue fallando cerrado (`f466ed9`).
- **Legado por comparación:** un body sin `record` (anterior a 003-007) informa en vez de bloquear.
- **Regla de encargo reconciliada** (unidad despachable) y **cableado de continuidad** con clases;
  `resume` declarado de solo lectura y primer paso al retomar (`1f5fdac`, `42f9904`).
- **Regla de gates nueva** (aprobada por el dueño): el implementer corre focales y módulos tocados;
  suite completa solo al cierre o si toca instalador, staging o renderer.

## Postcondiciones
| P | Estado | Evidencia |
|---|---|---|
| P1–P4, P8 | ✅ | T1: 14 focales, review T1 sin bloqueantes (6 sondas del reviewer) |
| P5, P6 | ✅ | T2: review T2 sin bloqueantes; append real en T3 (seq 8 → 9) |
| P7 | ✅ con límite | Fixture legado real; en uso real, v7 reanuda los stores de 003-004, 003-006 y 003-007. **Límite:** el legado informa también decisiones cambiadas que en un checkpoint nuevo serían `contract` |
| P9 | ✅ | `continuity-ledger.md`: rotación real con `resume` v7 tras escrituras vivas, sin escrituras de la sesión; contrato y autoridad editados en una copia → rc 1 |
| P10 | ✅ | T4 + review T4 (mutación: 4 fallos); **sonda 2**: el orquestador regenerado invoca `resume`/`reconcile` sin que se los nombren (tras 18 lecturas de orientación) |

## Gate
- Suite completa **599 passed** en `1f5fdac` (T4 GREEN; la primera corrida dio un fallo inestable
  en un test de 003-002, deuda `FLAKY-002-T3`). Después solo cambió documentación; gate de cierre:
  tests que leen `continuity.md` + `test_003_007_*` = **66 passed**.
- **Suite de cierre del orquestador: 599 passed (727 s)** en un worktree fijado a `350a93c` con
  `make staging`; reproduce la cifra del implementer.
- Validadores en el repo: **141 PASS / 2 FAIL** (F011 y A3, preexistentes).
- Sin CI. Suites completas en la feature: 3 del implementer en T4 (gate 598/1 por el test inestable,
  línea base con stash 589 passed para descartarlo, re-corrida 599 passed) más la de cierre del
  orquestador; frente a 7 en 003-006.

## Versión
v7 instalada en raíces aisladas (`2ed4c8d` para T3, `ce09ed0` con T4; Check PASS) e invocada por
ruta explícita. **El repo sigue activado en v6 (`abcd4d3`).** Activar la versión de cierre es
decisión del dueño. Mientras convivan las versiones, usar una sola versión del CLI por ejecución
(deuda `MIX-V6V7`).

## Deuda
`debt.md`. Media: MIX-V6V7, R2-STAGE, POLICY-CLASS. Baja: T2-R1, CKPT-FORK, T1-N1..N3, T2-N1,
T4-F2, FLAKY-002-T3.
