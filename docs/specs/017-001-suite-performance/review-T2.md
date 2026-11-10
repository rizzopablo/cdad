# Review T2 — 017-001-suite-performance

**Revisión examinada:** `613b3722`, junto con el test `eaeff429` y el GREEN previo.  
**Dictamen:** T2 **no pasa el gate**: el transporte sintético funciona, pero faltan los intervalos reales y la calibración que exige la tarea. No constituye una aprobación; la decisión corresponde al responsable.

## Hallazgo 1 — Faltan las marcas y la calibración de los recorridos reales

**Severidad:** Required  
**Verdict:** BLOCKING · **Bucket:** m

**Evidencia y ubicación.** El plan exige que T2 demuestre intervalos reales y entregue `calibration.md` con selección, revisión y contraste esperado/observado (`docs/specs/017-001-suite-performance/plan.md:283-305`). La spec exige específicamente preparación real dentro de `call` en los recorridos candidatos y establece que un ejemplo sintético no la sustituye (`spec.md:223-235`).

Sin embargo:

- Los casos de `tests/test_017_001_suite_operations.py:64-95` crean escenarios sintéticos con nombres de operaciones reales.
- La búsqueda de la costura de marcas en `tests/conftest.py`, `tests/product_staging.py` y los tests de recovery, continuity, U1, U3, U4 y documental identificados en el mapeo no encontró marcas.
- En `docs/specs/017-001-suite-performance/performance/` solo está `operation-scope.json`; no está `calibration.md`.

**Consecuencia.** Los cuatro tests verdes demuestran transporte en escenarios sintéticos, no que puedan medirse los constructores reales ni los demás intervalos comprometidos. Tampoco existe contraste recuperable de ocurrencias, relaciones y ramas esperadas frente a las observadas. No puede acreditarse T2 ni usarse esa evidencia para habilitar la base.

**Corrección y cierre verificable.** Instrumentar las fronteras reales mediante los responsables autorizados, conservar las transiciones y aserciones existentes, y ejecutar las selecciones focales comprometidas. Materializar la calibración con revisión, selección y contraste esperado/observado, incluidos contexto, ramas y anidamiento.

## Hallazgo 2 — El diagnóstico omite selecciones declaradas dentro de operaciones

**Severidad:** Required  
**Verdict:** BLOCKING · **Bucket:** m

**Evidencia y ubicación.** `committed_exercised_families()` solo consulta `family["selection"]`; si falta, descarta la familia (`scripts/cdad-suite.py:998-1033`). El registro aplicado incluye, por ejemplo, la familia `u3-disposable-product` sin selección a nivel de familia, pero su operación `u3.contract-staging` declara `selection: "C-U3"` (`performance/operation-scope.json`, familia `u3-disposable-product`).

**Consecuencia.** Si se ejecuta un nodeid de `C-U3` sin capturar ninguna operación y no hay otra familia coincidente, la regla acotada puede dejar el perfil como `complete` pese a que el alcance aplicado identifica un recorrido comprometido ejercitado. La ausencia de captura puede confundirse con medición válida.

**Corrección y cierre verificable.** Resolver las selecciones aplicables también en el nivel de operación, respetando sus estados y la regla acotada del encargo. Verificar con el registro real: un nodeid de `C-U3` sin captura debe quedar `incomplete`; una selección que no ejercita recorridos comprometidos debe conservar el comportamiento T1.

## Verificación independiente

| Comando | Resultado |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` | `4 passed in 12.00s` |
| Mismo comando sobre `tests/test_017_001_suite_profile.py` | `17 passed in 28.97s` |
| Mismo comando sobre `tests/test_008_002_suite_evidence.py tests/test_008_005_ci_gate.py` | `24 passed in 22.67s` |
| `PYTHONDONTWRITEBYTECODE=1 python3 scripts/cdad-suite.py validate` | `status: ok`; 2015 nodeids recolectados; timing `pending` |

El commit `613b3722` modifica únicamente `scripts/cdad-suite.py` y `scripts/cdad_suite_observer.py`; no modifica tests. La revisión no modificó archivos. Al inicio y al cierre figuraba `docs/.cdad-state.json` modificado, preexistente. No se ejecutó la suite completa: esta revisión utilizó las focales y la regresión solicitadas.

## Abstentions

- No acredito fidelidad de marcas, contexto compartido, ramas ni conteos **en recorridos reales**: faltan las marcas y la calibración descritas en el hallazgo 1.
- Las focales ejecutadas no prueban por sí solas todas las rutas de fallo de captura ni toda la semántica de `close`; no afirmo cobertura completa de esas propiedades.
- No se verificó exhaustivamente la tabla de decisiones actuales frente a todos los ADR.
