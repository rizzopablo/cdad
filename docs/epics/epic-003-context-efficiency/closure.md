# Cierre — epic-003-context-efficiency

Fecha: 2026-10-08. Orquestador: Claude Code, bajo la delegación HITL de epic-003. **Aprobación del
dueño:** "De acuerdo, avanza con eso" (2026-10-08), sobre la lista de decisiones que incluía cerrar el
epic con la enmienda; la aplicación se difirió al cierre de 003-007. Se cierra como **fase de
infraestructura del MVP** con la enmienda de `closure-amendment-draft.md`, que se actualizó con los
resultados de 003-007 después de la aprobación. Si el dueño no está de acuerdo, se reabre.

## 1. Features
| Feature | Cierre | Entrega |
|---|---|---|
| 003-001-role-packets | 2026-09-18 | Paquetes por rol y subfase |
| 003-005-claude-code-packets | 2026-09-18 | `prepare` y consumidores en Claude Code |
| 003-002-artifact-tools | 2026-10-06 | `cdad_result`: recepción idempotente, receipts, materialización con CAS |
| 003-003-progress-guards | 2026-10-07 | `cdad_guard`: repeticiones, rechazos, preflight (sobre fixtures) |
| 003-004-context-continuity | 2026-10-07 | `cdad_continuity`: checkpoints content-addressed, `resume`, `reconcile`, `trigger` |
| 003-006-runtime-adoption | 2026-10-08 | Cableado en el ciclo, `cdad-activate.py`, RU-1/RU-2, v5/v6 |
| 003-007-living-continuity | 2026-10-08 | Referencias `contract`/`living`, `record`, append de checkpoint, unidad despachable, sonda 2 |

## 2. Criterios
Ver la tabla de `closure-amendment-draft.md`. Resumen: 1, 3 y 4 cumplidos; 2 enmendado (modelos por
rol en lugar de un único modelo; presupuesto no medible); 5 y 6 parciales, con límites declarados
(sin lector de sesiones, sin CI, sin medición de contexto).

## 3. Evidencia de integración
- **Suite de cierre del epic:** ver la cifra en la sección 5, corrida por el orquestador en un worktree
  fijado al HEAD de cierre de 003-007, con `make staging` previo.
- **Uso real de punta a punta (003-006 y 003-007):** `prepare` → despacho → `receive` →
  materialización con CAS → `begin`/`checkpoint` → rotación con `resume`, con modelos por rol
  (DeepSeek construye; GLM escribe tests y revisa).
- **Validadores:** 141/2 en el repo (F011 y A3, preexistentes).

## 4. Pendiente para el dueño
Activar la v7 (`ce09ed0`); confianza de carpeta de Claude Code y copias viejas en HOME; prioridad de la
deuda del próximo epic (lector de sesiones, medición de contexto, CI, ANON-1, MIX-V6V7, R2-STAGE,
POLICY-CLASS). Detalle en `closure-amendment-draft.md`.

## 5. Gate final
- Suite completa: **599 passed (727 s)**, corrida por el orquestador en un worktree fijado a `350a93c`
  con `make staging` previo. Después de ese commit solo cambió documentación. Reproduce la cifra que
  informó el implementer en T4 (`1f5fdac`).
- Validadores: 141 PASS / 2 FAIL (F011 y A3, preexistentes). Sin CI.
