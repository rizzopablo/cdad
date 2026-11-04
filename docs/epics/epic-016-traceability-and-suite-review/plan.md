---
epic_id: epic-016-traceability-and-suite-review
epic_name: Trazabilidad contrato→test y revisión completa de la suite
created_at: 2026-11-03
approved_by: Pablo
approved_at: 2026-11-03
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 016: Trazabilidad contrato→test y revisión completa de la suite

## Resumen

Dos necesidades del dueño, hoy sin cubrir: (1) saber qué promesa del contrato protege cada test, para detectar
contratos sin verificador y para poder optimizar la suite; (2) revisar la suite completa, hoy 1972 tests, que se
construyó por acumulación sin una revisión de conjunto.

La revisión se hace por tramos del 20%, empezando por los tests más nuevos, con control entre tramos. La trazabilidad
se introduce hacia adelante (tests nuevos) y se completa por demanda mientras la revisión avanza: cada test revisado
queda vinculado a su contrato. No hay relleno masivo ni normalización retroactiva del formato de las specs.

Insumos: `docs/planning/test-evidence-and-traceability-proposal-2026-11-02.md` (§3.B, §3.C, §3ter opinión del
architect), `docs/specs/008-002-suite-by-capability/{suite-inventory.json,pc-map.json}`, `docs/suite-maintenance.md`.

## Alcance

Entra:
- Formato mínimo y verificable del vínculo test→contrato→promesa, en un registro por unidad separado del inventario
  (que clasifica) y del mapa de PC (que guarda genealogía).
- Chequeo mecánico: referencias que resuelven, nodeids que existen, promesas sin verificador declarado.
- Informe de huecos sobre specs cerradas, con relleno por demanda del tramo en curso.
- Revisión de la suite en tramos del 20%, del más nuevo al más viejo, con auditoría barata de todos y verificación caras
  solo para candidatos; medición de costo en el primer tramo y decisión registrada entre tramos.
- Poda o consolidación, solo si un tramo lo justifica y como unidad propia.

No entra:
- Relleno de los ~1972 tests de una vez ni por agentes en masa (produciría vínculos nominales).
- Normalizar el formato de postcondiciones de las specs existentes (los IDs nuevos sí son estables).
- Gate universal de mutación ni campaña de propiedades sobre toda la suite.
- Reescribir contratos cerrados.
- Publicar y desplegar (reservado al dueño).

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `016-001-contract-test-link` | Formato y registro del vínculo test→contrato→promesa, con validación mecánica; aplicado a los tests nuevos y al primer tramo revisado | — |
| 2 | `016-002-gap-report` | Informe reproducible de promesas de specs cerradas sin verificador declarado, con exclusión justificada admitida | 1 |
| 3 | `016-003-suite-review-tranche-1` | Primer tramo (20% más nuevo): auditoría de cada test, verificación de candidatos, costo medido y decisión registrada sobre continuar | 1 |

## Contratos entre features

- **Vocabulario:** 016-001 define el formato del vínculo y las disposiciones que usan los tramos; 016-002 y 016-003 lo consumen.
- **Un solo dueño del dato:** el inventario sigue clasificando; el registro nuevo guarda el vínculo; no se duplican campos.
- **La auditoría de un tramo produce altas de vínculo**, no un informe aparte que se descarta.
- **Costo antes que escala:** el tramo 1 mide antes de comprometer los siguientes.

## Criterios de aceptación del epic

- Un test nuevo declara su vínculo y el sistema lo verifica mecánicamente; un vínculo roto se detecta.
- Existe un informe de promesas sin verificador sobre specs cerradas, reproducible.
- El tramo 1 cierra con: tests revisados, disposición por test, costo medido y decisión explícita sobre continuar.
- Nada de esto bloquea el ciclo normal cuando el proyecto no usa el registro (compatibilidad hacia atrás).
- Suite completa de cierre por el gate atribuible.

## Autoridad

Aprueba el dueño el plan y, por épica, el alcance del mandato operativo. Publicar y desplegar reservados al dueño.

## Cambios al plan

Ninguno todavía.
