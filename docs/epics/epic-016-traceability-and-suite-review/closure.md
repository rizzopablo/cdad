# Closure — epic-016-traceability-and-suite-review

**Cerrado:** 2026-11-04. No publicado ni desplegado (reservado al dueño).

## 1. Resultado

El epic entrega las dos capacidades que el dueño pidió para dejar de acumular tests a ciegas: saber **qué promesa
del contrato protege cada test** y **revisar la suite completa por tramos** sin relleno masivo ni poda a ciegas.

- **Trazabilidad hacia adelante y por demanda.** Existe un registro JSON por unidad, validado por una CLI autónoma
  que resuelve obligaciones por marcadores reales `cdad:pc` o por índice legacy, sin mezclar ambos universos y sin
  escribir ni ejecutar tests. Un test nuevo declara su vínculo y un vínculo roto o una obligación sin verificador
  se detectan mecánicamente. El registro no reemplaza al inventario (que clasifica) ni al mapa de PC (que guarda
  genealogía): cada dato tiene un solo dueño.
- **Informe de huecos reproducible.** `gap-report` parte del estado (cierres registrados, fila actual por encima de
  sus copias históricas), distingue «no indexado» de «hueco», agrupa por promesa y admite exclusiones justificadas
  que no inflan la cobertura ni borran el hueco subyacente. Salida determinista por stdout, códigos 0/1/2.
- **Revisión del primer tramo, con costo y decisión.** El 20 % más nuevo de la suite (398 de 1 988 nodeids, 36
  módulos, 25 contratos) quedó auditado fila por fila, con disposición R2, evidencia recuperable y revisión
  semántica independiente. El costo se midió y la decisión de continuar quedó registrada con cambios explícitos de
  método.
- **Comportamiento vigente del sistema intacto.** Ninguna de las tres features agrega un gate al ciclo de un
  proyecto sin registro; la compatibilidad está medida por verificadores, no afirmada.

## 2. Criterios de aceptación del plan

| Criterio | Estado | Evidencia |
| --- | --- | --- |
| Un test nuevo declara su vínculo y el sistema lo verifica mecánicamente; un vínculo roto se detecta | ✅ | 016-001 cerrada: `cdad_contract_links.py validate` (0/1/2, JSON determinista) + 11 verificadores; review independiente con 2 bloqueantes corregidos y verificados |
| Existe un informe de promesas sin verificador sobre specs cerradas, reproducible | ✅ | 016-002 cerrada: `gap-report` determinista, 5 verificadores, universo desde el estado; 4 bloqueantes del review corregidos y verificados |
| El tramo 1 cierra con tests revisados, disposición por test, costo medido y decisión explícita sobre continuar | ✅ | 016-003 cerrada: 398 filas en `tranche-1/audit.json` (398 `Mantener`, 0 candidatos), `costs.json` con totales y proyección, `decision.md` autorizada |
| Nada de esto bloquea el ciclo normal cuando el proyecto no usa el registro | ✅ | 016-001 PC-7 y 016-002 PC-9 con verificadores propios; ninguno de los tres contratos introduce un gate nuevo |
| Suite completa de cierre por el gate atribuible | ✅ | `scripts/cdad-ci-gate.py --base origin/main`, commit `4c543721`, árbol limpio: **1 989 passed, 0 failed, 5 skipped**, verde atribuible |

## 3. Evidencia

- **Gate:** `.cdad/local/gate-20261104T051729363892Z-3050014-fbd7fdcc` (`gate.json` + `suite-report.md`), base `116ef8cf`, commit `4c543721`, árbol
  limpio, un solo intento `finished`, `rc` 0, ~71 min de reloj. Detalle en `integration.md`.
- **016-001:** 11 verificadores (`test_016_001_contract_test_link.py`), registro con `mode`/`coverage`/
  `obligations`; suite de la feature no realizada (recomendada) — la cubre este gate.
- **016-002:** 5 verificadores (`test_016_002_gap_report.py`); `validate` de 016-001 intacto; suite de la feature
  no realizada (recomendada) — la cubre este gate.
- **016-003:** `tranche-1/{selection,collection,audit}.json` (398 de 1 988 nodeids, reproducible byte a byte),
  `tranche-1/{costs.json,decision.md,report.md,experiments/}`, tres pasadas de revisión independiente
  (`review.md` rechazado, `review-r2.md` rechazado, `review-r3.md` **aprobado con observaciones** con la
  aritmética al decimal), 6 fixes posteriores (H1 `0b6046a9`, H2/B1/B2/O1/O2 `6bdbb854`, O3/O4 `afbb4c2e`,
  N1/N2/N3 `8805eaff`) y POST-AUDIT de cierre `94c86e80`.
- **Costo del tramo 1:** 398 tests en 17 actividades de auditoría (7 081,8 s ≈ 17,79 s/test), 353,6 s de revisión
  independiente, 1 304,6 s de preparación compartida con 90,1 s de solapamiento declarado, 8 692,5 s agregados por
  unión de intervalos, 9 643,7 s de reloj; 2 716 861 tokens de entrada, 702 509 de salida y 92,9 M de lectura de
  caché; proyección del resto 29 986,6 s ≈ 8,3 h declarada como cota alta.
- **Inventario vivo:** `cdad-suite.py validate` → `ok` (1 994 nodeids, 238 módulos, 31 entradas de mapa).

## 4. Deuda declarada

- **El epic no revisa la suite completa:** entrega el método y el primer tramo. La decisión registrada autoriza el
  tramo 2 con cambios de método (registro por unidad en la misma pasada, objetivo generado por script, auditoría
  dirigida por promesa, materializador que descarta sólo repeticiones byte-idénticas), con revisión si el costo se
  aparta más de 30 % de la proyección. Los tramos 2–5 quedan fuera de este cierre.
- **Cero candidatos deja el costo experimental sin calibrar** (S1/S2/S3 registradas en
  `tranche-1/experiments/suspicions.json`, sin promoverlas ni descartarlas). La ausencia de candidatos no acredita
  redundancia universal ni autoriza poda.
- **N3:** seis filas del tramo citan fragmentos que viven en un test hermano que no ejecutan (declaradas con sus
  nodeids en `report.md` §2). **N2:** el bloque de cierre usa el rótulo `ses_orquestador_cierre` sin id de sesión
  del runtime; sus tokens se declaran «no disponibles», no cero. **O2:** falta decidir si la lectura de caché
  (92,9 M tokens) entra en la noción de costo que el dueño quiere gobernar.
- **Proyección lineal y por cota alta:** no descuenta el ahorro esperado de los cambios de método del tramo 2.
- **Nada desplegado:** el registro, el `gap-report` y el revisor de tramos existen en el repo y **no** en el árbol
  instalado del HOME. Publicar y desplegar siguen reservados al dueño; el instalador no se ejecutó en este cierre.
- **Dos huecos de clasificación de `surface` detectados al cerrar** (preexistentes, fuera del alcance de este
  epic): la raíz `findings/` no está en la política de rutas y un archivo no-`.py` bajo `tests/` se trata como
  superficie de producto en vez de activo de test. No afectan al epic con su base propia, pero hacen rojo
  `surface` en cualquier corrida contra una base de publicación que no contenga esas rutas. Merecen una unidad
  propia si se quiere que el gate funcione indistintamente contra `origin/main`.
- **Límites del método, ya declarados en las closures de cada feature:** la comprobación es estructural (no
  acredita ejecución ni pertinencia semántica), la antigüedad individual de cada protección y la demostración
  universal de redundancia siguen fuera de alcance.

## 5. Cambios al plan

Ninguno: las tres features planificadas se entregaron como estaban definidas. El alcance de la revisión por tramos
se detuvo donde el plan lo fijó —tramo 1 con costo y decisión— y lo que sigue es trabajo posterior autorizado por
`docs/specs/016-003-suite-review-tranche-1/tranche-1/decision.md`, no una ampliación de este epic.

## 6. Siguiente

Tramo 2 de la revisión (decisión ya registrada y acotada), y —sólo por decisión del dueño— publicación del árbol
y despliegue al HOME.
