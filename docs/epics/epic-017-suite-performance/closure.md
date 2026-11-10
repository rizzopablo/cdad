# Epic epic-017-suite-performance — Closure

**Cerrado:** 2026-11-08 · **1/1 features** · **no publicado ni desplegado** (reservado al dueño).
**Duración:** 2026-11-06 (plan aprobado) → 2026-11-08 (2 días).
**Revisión de cierre:** `bf0e7483c0403b545760efbcb0134cd958d31a30`.

## Summary

El epic atacó un problema medido pero no atribuido: la suite completa tardaba entre 56 y 76 minutos con
~1989 tests y nadie sabía dónde se iba el tiempo. Entregó la suite **instrumentada**, una **base
reproducible**, atribución y conciliación sin cifras ficticias, y un **lote paralelo** con veredicto
*fail-closed* que bajó la pared de 4459 s a 2593.15 s (−41.84 %) sin cambiar un solo resultado por nodeid.
La optimización de preparación, en cambio, quedó demostrada como **inexistente**: 0 de 76 instalaciones
son compartibles.

## Features delivered

| Orden | Feature | Cierre | Resultado observable |
|---|---|---|---|
| 1 | `017-001-suite-performance` | 2026-11-08 | suite instrumentada, base reproducible, `reconcile` reproducible y `parallel` con veredicto fail-closed: 4459 s → 2593.15 s con equivalencia exacta por nodeid |

## Acceptance criteria (plan §Criterios de aceptación, los seis)

| # | Criterio | Estado |
|---|---|---|
| 1 | Línea base medida y registrada (comando, selección, entorno, duración), repetible sobre la misma revisión | ✅ `performance/baseline.json`/`.md`: **4994.27 s**, 2029 passed + 5 skipped, revisión `7426438b`, con metadatos de §4.1 y reconstruible desde los crudos |
| 2 | Atribución por archivo y por test publicada; la suma de las partes cuadra con el total medido | ✅ `reconcile` sobre la corrida serial final: preparación **448.90 s** + resto **4002.51 s** = 4451.41 s = `sum_S_test`; `R_pytest` 7.12 s, `R_exterior` 0.47 s, cota de redondeo 1.03 s, `status: complete` |
| 3 | Optimización aplicada con antes/después medido y suite verde, sin cambios en las garantías | ✅ **con matiz**: la optimización de **preparación** quedó demostrada como inexistente (**0 de 76** instalaciones compartibles: 47 acción bajo prueba, 29 mixtas) y **no se aplicó**; la optimización de **pared** es la paralela, con antes/después sobre la misma revisión y resultados idénticos |
| 4 | Paralelismo: solo con evidencia de seguridad y sin alterar el aislamiento; si no se demuestra, se declara y no se aplica | ✅ **demostrado antes de aplicar**: `family_verifiable: true`, **0 huérfanos con 20 transitorios**, canario de configuración y del checkout limpios (`incomplete: []`, 20 607 archivos), `HOME`/`XDG`/`TMPDIR` por worker y evidencia sin colisiones |
| 5 | Sin poda de tests ni cambios en contratos cerrados | ✅ `review-final-tests.md`: 17 archivos ajenos auditados sin debilitamiento; contratos 005-013, 008-002, 008-006, 013-003 y 016-003 intactos |
| 6 | Cierre con suite completa verde atribuible, según la política de evidencia vigente | ✅ `--all` sobre `bf0e7483`: **2054 passed + 5 skipped, 0 failed** en serial y paralela; `validate` `status: ok` con 2059 nodeids sobre la misma revisión |

## Brief retrospective

### What worked well

- **Medir antes de decidir.** La auditoría de las 76 invocaciones de `install.sh` evitó construir una caché
  de preparación que habría dejado de ejecutar transiciones verificadas: el resultado «0 de 76» es un
  hallazgo, no un fracaso.
- **El veredicto estricto encontró los defectos.** Los cuatro rechazos de corrida (dos por canario, uno
  por liveness, uno por evidencia reutilizable) y el hallazgo de scratch compartido salieron de exigir
  integridad, no de revisar a ojo: el runner se corrigió cuatro veces **con test** antes de acreditar.
- **Equivalencia por nodeid como condición, no como cortesía.** El objetivo exigía ≥ 15 % **y** conjuntos
  idénticos por nodeid; eso impidió presentar un total igual como equivalencia demostrada en las corridas
  descartadas.

### What got complicated

- **La integración fue el trabajo real.** Cuatro defectos del runner y cuatro huecos de integridad del
  veredicto aparecieron **al correr la suite completa**, no en las focales: scratch de test dentro del
  checkout, veredicto por `mtime`, timeouts de liveness fuera de convención y evidencia reutilizable entre
  invocaciones. Ninguno era visible en una selección pequeña.
- **Tres corridas completas descartadas** antes del par válido, cada una con su causa reproducida. Se
  conservan como historia del diagnóstico y **no acreditan nada**.

### Lessons for future epics

- Un runner que observa el árbol exige una **regla de diseño de tests** (raíces propias, sin escrituras al
  checkout) que hoy no viaja en los encargos: es la primera pieza de la unidad pendiente de promoción.
- Cuando el objetivo de rendimiento depende de una operación desconocida, la regla de §4.4 («focal
  adicional antes de modificar») es la que evita optimizar por intuición; aquí evitó tocar la preparación.
- Un par de medición con runner corregido **no hereda** la validez del par anterior, aunque las cifras
  mejoren: el de `83674246` (30.92 %) no se usa.

## Technical debt carried forward

- **Carga del host y canario del checkout no instrumentados en la pierna serial de `close`**: las dos
  condiciones del contrato de T7 quedan **no demostradas** allí y así se declaran (sustitutos: mismo
  commit, `dirty: 0` en ambos, resultados idénticos por nodeid y paredes seriales consistentes en cuatro
  corridas: 4235, 4239, 4370 y 4459 s, ±5 %).
- **El resto (89.9 %) sigue desconocido.** No se clasifica por descarte ni se le atribuye costo.
- **El lote paralelo no es capacidad de CDAD**: vive en `scripts/cdad-suite.py` de este proyecto.
  Promoverlo exige workers configurables en la herramienta del ciclo, reglas de tests paralelizables y
  declaración de aislamiento por módulo: unidad nueva, no abierta.
- **La huella del checkout no ve cambios de modo ni directorios vacíos**; sí detecta altas, bajas y
  cambios de contenido.
- **Un solo host y una repetición por régimen**: sin significancia estadística.
- **`deferred-hardening` de la spec §9, conservados con su disposición** (R6; ninguno aplaza una promesa
  comprometida): campaña estadística multi-host → no se hace, se informan condiciones y límites; profiler
  universal → no se construye, el resto queda desconocido; optimización de toda caché existente → no se
  migra (0 de 76 compartibles); reducción de presupuestos de propiedades → no se aplica ni se propone;
  garantía universal de confinamiento → no se promete, el canario tiene los límites declarados; poda,
  reescritura de contratos y publicación → excluidas por el contrato del epic.
- **El epic no autoriza poda ni publicación.**

## Architectural decisions made

- **ADR-043: Lote paralelo por archivo con veredicto fail-closed** — `docs/adr/ADR-043-lote-paralelo-por-archivo-veredicto-fail-closed.md` (aceptado por delegación del dueño al cierre del epic).
- No hubo otros ADR durante el epic: la instrumentación de `close` y la identidad contable de §4.4 están
  gobernadas por la spec aprobada de la unidad.

## Final notes

El par de `83674246` (30.92 %) queda en los artefactos como **historia del diagnóstico** y nunca como
evidencia. `comparison.json` y `.cdad/tmp/017-001-final-evidence/` contienen exclusivamente el par vigente
de `bf0e7483`; los crudos están en `evidence/017-001-final4/{serial,parallel}`. Publicar y desplegar
siguen reservados al dueño, y nada de este epic se publicó.
