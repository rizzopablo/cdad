---
epic_id: epic-017-suite-performance
epic_name: Rendimiento de la suite
created_at: 2026-11-06
approved_by: <owner>
approved_at: 2026-11-06
---

<!-- cdad:plan-anchors
{"history": ["Cambios al plan"], "authorization": ["Autoridad"]}
-->

# Epic 017: Rendimiento de la suite

## Resumen

La suite completa tarda entre **56 y 76 minutos** (siete corridas registradas en
`.cdad/evidence/`) y **~71 minutos** en el gate del epic 016, con **1.989 tests**.
El total está medido; la atribución por archivo, no. Este epic produce la línea
base instrumentada, la atribución de costos y la optimización de la preparación,
con paralelismo solo si se demuestra seguro. **No poda tests**: la poda fue
`013-003` y el plan del epic 013 declara que poda y velocidad son promesas
separadas.

## Alcance

Entra:

- Instrumentación de la corrida (`--durations`, XML por test) y línea base
  repetible: comando, selección, entorno y duración.
- Atribución de costos por archivo y por test, consistente con el total medido.
- Optimización de la preparación (fixtures, staging, cachés por proceso) con
  antes/después medido.
- Paralelismo solo si la medición lo justifica y la seguridad se demuestra
  (aislamiento por test y cachés sin estado compartido); si no se demuestra, se
  declara y no se aplica.
- Presupuesto de propiedades solo si la medición muestra que domina el costo.

No entra:

- Poda, sustitución o consolidación de tests (fue `013-003`; su piloto no
  confirmó redundancia podable en el lote B1).
- Reescribir contratos cerrados (005-013, 008-002, 008-006, 013-003, 016-003).
- Acreditación semántica de la suite, clasificador de equivalencias, gate
  universal de mutación.
- Cambiar la forma de verificar el contrato: las mismas garantías, más rápidas.
- Publicar y desplegar (reservado al dueño).

## Features

| # | Feature | Resultado | Depende de |
|---|---|---|---|
| 1 | `017-001-suite-performance` | Línea base, atribución de costos y optimización de la preparación; paralelismo solo si hace falta y se demuestra seguro | — |

## Criterios de aceptación del epic

- [ ] Línea base medida y registrada (comando, selección, entorno, duración),
  repetible sobre la misma revisión.
- [ ] Atribución por archivo y por test publicada; la suma de las partes cuadra
  con el total medido.
- [ ] Optimización aplicada con antes/después medido y suite verde, sin cambios
  en las garantías.
- [ ] Paralelismo: solo con evidencia de seguridad y sin alterar el aislamiento;
  si no se demuestra, se declara y no se aplica.
- [ ] Sin poda de tests ni cambios en contratos cerrados.
- [ ] Cierre con suite completa verde atribuible, según la política de evidencia
  vigente.

## Autoridad

Aprueba el plan el dueño. Ejecuta el orquestador dentro del mandato registrado;
publicar y desplegar quedan reservados al dueño.

## Relación con `013-004-suite-performance`

`013-004` quedó `queued` en `epic-013-test-criterion`, cerrado el 2026-11-02 con la
nota «no abierta: decisión del dueño». El CLI no reabre unidades de epics cerrados
(015-002 D3) y este plan no reescribe ese contrato: retoma su alcance con un id
nuevo. La fila histórica del plan 013 se conserva. Antes de abrir esta unidad se
cerró la precondición de `docs/suite-maintenance.md` (quién registra `validate`
en «Mantener»).

## Cambios al plan

- 2026-11-06 — creación del borrador.
