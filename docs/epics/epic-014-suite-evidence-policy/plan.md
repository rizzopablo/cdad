---
epic_id: epic-014-suite-evidence-policy
epic_name: Política de evidencia de suite completa
created_at: 2026-11-02
approved_by: Pablo
approved_at: 2026-11-02
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 014: Política de evidencia de suite completa

## Resumen

Corregir la generalización de ADR-041: la exclusión de la suite completa respondía
al costo de CDAD y se convirtió en norma del producto. Defaults nuevos: durante el
ciclo, focal + regresión proporcional; al cerrar feature, suite completa
**recomendada** (omisión registrada con motivo); al cerrar epic, **obligatoria por
defecto** (omisión solo con dispensa expresa del dueño, registrada con motivo).
La aprobación de esta política autoriza la corrida ordinaria de cierre de epic.

Insumos: `docs/planning/test-evidence-and-traceability-proposal-2026-11-02.md`
(§3.A, §3bis, §3ter — opinión del architect).

## Alcance

Entra:
- Nuevo ADR que supersede solo la cláusula de autorización/defaults de ADR-041
  (contribución y obligaciones Odoo se conservan).
- Hogar canónico `skills/cdad-cycle/references/stage-3-tdd.md` y sus consumidores
  (legacy, paquetes, roles en `sources/`, cdad-epic, skills Odoo, docs de proyecto),
  con regeneración (`make agents`).
- Tratamiento de rojos/skips/inestables en la corrida de cierre; costo declarado por
  proyecto (sin CI: ejecución local atribuible).

No entra:
- Trazabilidad contrato→test, revisión de la suite, poda (epic posterior).
- Reescribir contratos cerrados (005-013, 008-002, 008-006, 013-*).
- Regularizar retroactivamente el cierre del 013 (cerró bajo directiva registrada).
- Publicar y desplegar (reservado al dueño).

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `014-001-suite-evidence-defaults` | Defaults por momento vigentes en la norma y en todos sus consumidores, coherentes entre rutas legacy y por paquetes, regenerados | — |
| 2 | `014-002-pd10-window-drift` | Corrige el único rojo que reveló la primera suite completa desde el epic 013: `test_pd10_installed_cli_paths_in_t1_wiring_points` (ventana por número de línea desfasada) | 1 |

## Criterios de aceptación del epic

- Rutas legacy y por paquetes transmiten los mismos defaults.
- Ninguna fuente sigue exigiendo autorización expresa para la corrida de cierre de epic.
- Cierre del epic con suite completa (gate atribuible, `scripts/cdad-ci-gate.py`).
- Cambios en `sources/` + regeneración; doctrina y `make agents` sin deriva.

## Autoridad

Aprueba el dueño: «Si, vamos con A» (2026-11-02), sobre la propuesta y la opinión
del architect. Publicar y desplegar reservados al dueño.

## Cambios al plan

- 2026-11-02: la corrida completa de cierre (1947 passed, 5 skipped, 1 failed; commit e9969d9e) mostró un rojo
  preexistente del epic 013 (falla en `c4271693`, pasa en `0eab565c`). Se añade la feature 2 para corregirlo; la
  suite completa se repite al final. Aprobado por HITL delegada.
