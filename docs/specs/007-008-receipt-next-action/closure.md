# Cierre 007-008-receipt-next-action

Fecha: 2026-10-26. Epic: `epic-007-reliable-cycle-operation`. Colección: 8/8.

## Resultado

El cierre de recibo deja de heredar la acción previa al despacho. Todo cierre **nuevo** escribe la
acción canónica:

> `recibo recibido mecánicamente; no repetir despacho/recepción; revisar el resultado sin presumir aprobación`

Conserva goal, autoridad, decisiones previas, incertidumbres, referencias, presupuesto, `changes`,
`evidence`, `receipt_checkpoint` y `prev`. No migra cierres históricos: sus bytes y digests quedan
intactos aunque muestren la acción vieja. No cambia identidad, idempotencia, `semantic_status` ni la
forma de `status`.

## Evidencia

- Contrato: `spec.md` (PC-01..PC-06 + AJ1–AJ4).
- RED: `tests/test_007_008_receipt_next_action.py` (`fbadfdc`), 17 casos, 15 en rojo por la acción
  heredada; los dos restantes protegen la no migración de historia y la acción de contextos no
  recibidos.
- GREEN: `af03944`, una línea en `_closing_body`; 115 casos focales verdes (007-008 + 007-003/004/007).
- Oráculos endurecidos: `45e1749` (snapshots de recibo/parts; `no_op` e identidad del replay) y
  `20a1762` (PC-02 compara la decisión mecánica completa de AJ4).
- Review: 2 rondas. Ronda 1 sin bloqueantes, 2 mejoras opcionales (cerradas en ronda 2); ronda 2 sin
  hallazgos pendientes.
- Suite completa: **1721 passed, 5 skipped, 1 failed** — `test_006_001_t2_wait_recovery.py::TestPd7…`,
  que **pasa aislado** (`1 passed`): es la contaminación entre tests ya declarada
  (`SUITE-CONTAMINATION`), no una regresión de esta unidad.
- Desplegado `20a1762` en HOME con respaldo previo.

## Recorrido feliz desde reposo (evidencia para el epic)

La unidad se abrió con el ciclo en reposo:

1. `status` = `next-unit`/`at-rest` → `open-unit`.
2. `prepare` (architect/discovery), `begin` (seq 1), `verify-begin`, despacho nativo, `record`
   verificado (`parent`/`moment`; `project` no evaluable por ser ancestro), `receive` con recibo
   válido y `checkpoint-receipt`.
3. `prepare` (architect/draft), `begin` (seq 3), `verify-begin`, despacho, `record`, `receive`; la
   cabeza queda en **seq 4** con el cierre enlazado al recibo.

Es el recorrido que el epic necesitaba observar: entrada desde reposo, despacho real, registro y
recepción, con continuidad vigente al terminar.

## Desviación de proceso declarada

Los despachos de **RED, GREEN y review** se hicieron con el subagente nativo, **sin paquete
renderizado** (`prepare`/`begin`/`record`/`receive`). No hay por tanto registro de continuidad de
esas subfases: su evidencia son los commits y los tests. No afecta al producto, pero es una
desviación del método y se declara.

## Límites

- Un cierre histórico con acción obsoleta sigue mostrándola: la unidad no reescribe historia.
- `SUITE-CONTAMINATION` vuelve a aparecer (un test, aislado verde); la auditoría de la suite sigue
  pendiente.
- El literal canónico se fija como contrato; cambiarlo será otra unidad.
