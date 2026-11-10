# Epic 017 — Integration

**Epic:** `epic-017-suite-performance`. **Fecha:** 2026-11-08.
**Revisión de integración:** `bf0e7483` (la misma que cerró la feature 017-001).

## Contexto: un epic de una sola feature

El plan declara **una** unidad: `017-001-suite-performance`. Por eso no hay
criterios *entre* features que verificar: no existen dos features que
intercambien salida. Lo que sí exige integración real es el encuentro entre las
piezas que la feature toca y el resto del sistema, y eso **no** lo cubre ninguna
focal: solo aparece al correr la suite completa, y en particular al correrla en
paralelo.

## Criterios del epic contra evidencia

| Criterio del plan | Estado | Evidencia |
|---|---|---|
| Línea base medida y registrada, repetible sobre la misma revisión | ✅ | `performance/baseline.json` (4994.27 s, 2029 passed + 5 skipped, `7426438b`) |
| Atribución por archivo y por test publicada; la suma de las partes cuadra con el total | ✅ | `reconcile` (preparación 448.90 s + resto 4002.51 s = 4451.41 s; `sum_S_test` 4451.41 s), `tests/test_017_001_suite_reconcile.py` |
| Optimización aplicada con antes/después medido y suite verde, sin cambios en las garantías | ✅ con matiz | la optimización de **preparación** quedó demostrada como inexistente (0/76 instalaciones compartibles); se aplicó la de **pared** (paralela): 4459 → 2593.15 s, −41.84 % |
| Paralelismo: solo con evidencia de seguridad y sin alterar el aislamiento | ✅ | 2059 nodeids sin diferencias, `family_verifiable: true`, 0 huérfanos con 20 transitorios, canario limpio (`incomplete: []`) |
| Sin poda de tests ni cambios en contratos cerrados | ✅ | `review-final-tests.md` (17 archivos ajenos auditados, sin debilitamiento); contratos 005-013/008-002/008-006/013-003/016-003 intactos |
| Cierre con suite completa verde atribuible | ✅ | `--all` sobre `bf0e7483`: 2054 passed + 5 skipped, 0 failed, serial y paralela; `validate` rc=0, 2059 nodeids |

## Comprobaciones de integración (no focales)

Estas son las verificaciones que **solo** tienen sentido a nivel de sistema y
que se corrieron sobre la revisión de integración:

1. **Suite completa serial y paralela sobre la misma revisión**, con el árbol
   limpio en ambas y comparación de resultados por nodeid: 2059 vs 2059, 0
   diferencias. Es la comprobación de que el lote no cambia el significado de la
   suite.
2. **`validate` en el momento de cierre** (el que declara
   `docs/suite-maintenance.md`): rc=0, `status: ok`, 2059 nodeids.
3. **Encuentro del runner con los tests del instalador y del consumidor
   aislado**, que son los que más escriben en disco. Es donde aparecieron los
   defectos de la sección siguiente.
4. **Reversibilidad**: `close` no cambió de comportamiento (comparación AST en
   `review-T6-005`), de modo que el camino serial sigue disponible si el lote
   paralelo no se considera seguro en un entorno dado.

## Hallazgos de la integración

Todos aparecieron **al integrar**, no en las focales, y todos quedaron
corregidos con test:

- **Interferencia entre workers por scratch dentro del checkout.**
  `tests/test_010_004_t5_e2e.py` copiaba el producto completo (~19 000
  archivos, ~450 MB) dentro de `.cdad/tmp` del repositorio. Con dos workers, el
  canario del checkout de un worker veía el árbol del otro crecer y
  desaparecer, y rechazaba la corrida. Era un rechazo **correcto**: el árbol
  efectivamente cambiaba durante la corrida. La corrección no fue debilitar el
  canario sino sacar el scratch del checkout (`03c22039`).
- **El veredicto del canario dependía del `mtime`.** El churn legítimo de
  directorios bajo `.cdad/tmp` movía el `mtime` máximo sin cambiar un byte, y la
  corrida se descartaba con contenido idéntico. Se pasó a veredicto por
  contenido (`6645a340`).
- **Timeouts de liveness fuera de convención.** Los meta-tests que lanzan el
  runner anidado usaban 120 s donde la familia usa 300 s; bajo la carga de la
  suite completa uno murió (`2981f9aa`).
- **Cuatro huecos de integridad del veredicto** (familia no acreditable,
  canario tomado antes de la limpieza, barrido incompleto silenciado, evidencia
  reutilizable entre invocaciones), corregidos en `474064e7` y verificados con
  sondas independientes.

Lección de integración: el runner nuevo convive con 2059 tests escritos sin
saber de él. La integración no consistió en unirlos, sino en descubrir qué
supuestos de esos tests (escribir cerca del checkout, usar raíces temporales
dentro del árbol) chocaban con un observador que fotografía el árbol.

## Deuda técnica detectada

- `close` no instrumenta la carga del host ni toma canario del checkout; la
  pierna serial del contrato de T7 queda con esas dos condiciones **no
  demostradas** y así se declara. Mejora pendiente.
- El resto del tiempo (89.9 %) sigue **desconocido**: no se clasifica por
  descarte.
- El paralelismo vive en `scripts/cdad-suite.py` de este proyecto, no como
  capacidad del ciclo CDAD; para reutilizarlo en otros proyectos hay que
  promoverlo (workers configurables, reglas de tests paralelizables,
  declaración de aislamiento por módulo).
- La huella del checkout no ve cambios de modo ni directorios vacíos.

## Estado

`integration.md` existe y está commiteado; los criterios del epic quedan
verificados con la evidencia citada. Corresponde el cierre del epic (Memory
Bank consolidado + `closure.md` del epic + registro en `epic_history`).
