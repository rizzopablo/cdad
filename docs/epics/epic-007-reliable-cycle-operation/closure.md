# Cierre — Epic 007 «Operación confiable del ciclo»

Fecha: 2026-10-26. Features: **8/8 cerradas**.

## Resultado

El recorrido serial de CDAD dejó de depender de diagnóstico externo y de prosa:

- **Entrada:** la vista compacta declara situación, siguiente operación con su script y referencia
  verificable a la aprobación vigente (007-001).
- **Recuperación:** un intento abandonado se dispone y `reconcile` deja de reportarlo irresoluble; el
  sucesor se prepara sin reconstrucción manual (007-002).
- **Continuidad en los bordes:** `begin`/`verify-begin` antes del despacho y `checkpoint-receipt` tras
  la recepción, con reparación de historia legada por `reanchor` explícito (007-003).
- **Terminación ≠ entrega:** `delivery` (`none | staged | received`) con tabla cerrada; ni `rc` ni
  `termination` acreditan recepción (007-004).
- **Recepción real:** un tramo entre proyectos atravesó el recorrido completo con la versión adoptada
  (007-005).
- **Retiro y republicación:** un paquete `prepared` que no se despachará se retira con motivo; los
  agentes derivados se republican sin `prepare` (007-006).
- **Suspender y reanudar:** una unidad se interrumpe en un borde seguro y se reanuda explícitamente,
  sin perder identidad ni repetir efectos (007-007).
- **Acción del cierre de recibo:** deja de heredar la orden previa al despacho (007-008).

## Criterios de aceptación

| Criterio | Estado | Evidencia / límite |
|---|---|---|
| Las features del plan, cerradas individualmente | **Cumplido** | 8/8 con `closure.md`; suite completa 1721 passed, 5 skipped, 1 failed aislado verde (`SUITE-CONTAMINATION`). |
| **Recorrido feliz desde reposo** | **Observado, con alcance declarado** | 007-008: `status` en reposo → `open-unit` → `prepare` → `begin` (seq 1) → `verify-begin` → despacho → `record` verificado → `receive` → `checkpoint-receipt`; segunda vuelta hasta cabeza seq 4. Los despachos de RED/GREEN/review se hicieron nativos, sin paquete (desviación declarada en el cierre de 007-008): el recorrido observado es el de entrada y despacho packetizado. |
| **Recorrido de fallo** | **No observado como uso real** | Mecanismo y contrato: 007-002 (disposición/reconcile) y 007-003/007-004 (continuidad y `delivery`), verificados en entorno controlado. No ocurrió naturalmente en un consumidor durante el epic. |
| **Señales** | **Cumplido por contrato y ejercido** | 007-004 define la tabla y los productores; 007-005 consumió `staged` por su valor y rechazó un transporte por identidad sin acreditarlo. No hay inventario completo de consumidores documentados. |
| **Precondición de la recepción** | **Cumplido** | Versión `538ec57` desplegada con autorización del dueño, respaldo previo y `COHERENT` en el consumidor. |
| **Recepción real** | **Cumplido con desviación aceptada** | 007-005: dos transportes; el primero rechazado por identidad, sin registro ni efectos. Declarado y aceptado; revocable por el dueño. |
| **Sin mecanismos duplicados** | **Cumplido** | No hay intentos, disposición, recibo ni almacén nuevos; el manifiesto de evidencia de 007-005 es evidencia, no mecanismo. |

## Retrospectiva

**Funcionó:** el gate por superficie (descubrió 29 tests de continuidad que los gates focales
ocultaban, incluida una regresión real); las rondas de review adversarial (cerraron escapes reales en
007-004 y 007-006 antes del cierre); la recepción real como unidad de evidencia; y la suspensión, que
permitió cambiar de unidad sin excepciones de arranque.

**No funcionó / a corregir:** la suite creció por historia y no por capacidad (≈134k líneas de tests
contra ≈21k de producto), con contaminación entre tests por HOME/XDG no aislados; los despachos de
roles se hicieron en varios casos sin paquete renderizado, con lo que su continuidad no quedó
registrada; y una postcondición (PC-03 de 007-005) se escribió sin ser observable, obligando a una
sustitución contractual.

## Deuda que se lleva

- **`SUITE-CONTAMINATION`** (media): tests verdes aislados y rojos en corridas grandes; auditoría por
  capacidad y aislamiento de entorno.
- **`SUSP-GUARD`, `SUSP-LOCK`, `SUSP-APPROVAL`, `SUSP-IDENTITY`**: límites declarados de la suspensión.
- **Despachos sin paquete:** la práctica de este epic no debe repetirse; el ciclo debe exigir paquete
  para cada subfase de rol.
- Heredadas: DT-8/F011, DT-9, `scope_validation: unknown`, W-U6-*, ausencia de CI.
