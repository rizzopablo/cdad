# Revisión T6 — 017-001-suite-performance

**Veredicto: T6 no pasa el gate.** El paralelismo tiene una justificación preliminar de rendimiento, pero **no queda acreditado como seguro para la corrida final con `--workers 2`**. Hay defectos del runner y faltan evidencias necesarias para sostener las afirmaciones de PC-10. No apruebo ni modifico el producto.

## Hallazgos bloqueantes

### 1. Un worker sin archivos ejecuta pytest sin selección

**Required · Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:1634–1647`, se lanza un proceso por cada grupo, incluso si el grupo está vacío. `_parallel_worker_argv()` añade los nodeids al final; para un grupo vacío, invoca pytest **sin nodeids**, lo que activa su selección predeterminada.

**Consecuencia:** una selección focal con menos archivos que workers puede disparar trabajo no solicitado —potencialmente la suite completa— y producir resultados o escrituras fuera de la selección declarada. No ejecuté esa reproducción porque podría iniciar precisamente la suite completa.

**Cierre verificable:** no lanzar pytest para grupos vacíos, o rechazar la combinación antes de lanzar hijos; comprobar con una selección de un archivo y dos workers que solo se ejecutan los nodeids pedidos.

### 2. Las paredes por worker y el solapamiento pueden ser incorrectos

**Required · Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:1670–1672`, el runner espera los hijos **en orden** y calcula la pared al volver de cada `wait()`. Si un worker posterior termina antes que uno anterior, su pared incluye el tiempo que el padre pasó esperando al anterior. `overlap_s` se calcula a partir de esas paredes (`:1720`), por lo que también queda afectado.

**Consecuencia:** el informe puede atribuir al paralelismo un solapamiento y unas paredes por worker que no ocurrieron. La pared total se mide por separado; el defecto afecta la descomposición y la interpretación publicadas.

**Cierre verificable:** registrar el instante real de finalización de cada proceso y comprobarlo con workers de duraciones deliberadamente desiguales, incluido el caso en que el segundo termine primero.

### 3. `orphans: 0` no es evidencia de ausencia de huérfanos

**Required · Verdict: BLOCKING · Bucket: h**

`children_terminated` comprueba únicamente los procesos pytest directos; `orphans` se fija incondicionalmente en cero (`scripts/cdad-suite.py:1748–1750`). Además, si falla la apertura de evidencia o el lanzamiento de un worker posterior (`:1649–1662`), no se ve una limpieza de los hijos ya lanzados.

**Consecuencia:** el agregado puede declarar ausencia de huérfanos sin haberla comprobado y, ante un error parcial de lanzamiento, dejar procesos ejecutándose. Esto no acredita la garantía concurrente de PC-10.

**Cierre verificable:** gestionar y esperar los procesos lanzados también en las rutas de error; aportar una comprobación real de descendientes y una prueba que fuerce un fallo tras lanzar el primer worker.

### 4. El inventario no acredita la seguridad de la selección final

**Required · Verdict: BLOCKING · Bucket: h**

`performance/parallelism.md:130–139` afirma que los archivos que usan puertos quedan fuera hasta demostrar aislamiento, pero no los enumera. La selección final registrada es `--all` (`:94`). Hay consumidores de puertos en `tests/test_006_001_t3_integration.py:302–310`, `tests/test_006_001_reviewfix.py:197–198` y `tests/test_006_001_t1_selection.py:304–305,339–343`. Algunos usan puertos efímeros; su existencia no demuestra por sí sola una colisión, pero sí contradice que baste la evidencia de la muestra de seis archivos para caracterizar toda la suite.

Además, el canario de mi corrida declaró como alcance directorios de configuración y entradas de primer nivel de HOME, **no** `build/` ni `.cdad/` del checkout, pese a la afirmación de `parallelism.md:136`.

**Consecuencia:** no está demostrado que `--all` evite recursos compartidos peligrosos ni que el canario detecte modificaciones del checkout.

**Cierre verificable:** inventariar los consumidores de la selección final y demostrar su aislamiento o decidir explícitamente su tratamiento; verificar con evidencia adecuada el checkout y demás recursos compartidos. Resolver la tensión con `--all` sin recortar cobertura silenciosamente.

### 5. Los resultados publicados no están respaldados aquí por evidencia cruda accesible

**Required · Verdict: BLOCKING · Bucket: h**

`parallelism.md:106–128` publica las cifras de 837,2 s, 666,3 s y 552,0 s y señala `evidence/017-001-t6-parallel2` y `…parallel2b`. Esas rutas no estaban presentes en la raíz del repositorio durante la revisión; tampoco encontré esos JSON entre los archivos versionados. Por ello no pude contrastar sus valores, nodeids, revisión ni carga del host.

Por separado, `parallelism.md:118–120` identifica la diferencia entre trabajo paralelo y pared serial como “preparación duplicada por worker”. Esa resta, por sí sola, no mide ni atribuye el costo de reconstrucción de cachés: también puede reflejar otras diferencias de ejecución o contención.

**Consecuencia:** no se puede verificar independientemente el beneficio publicado ni el costo específico exigido por PC-10. El defecto de medición del hallazgo 2 también afecta la confianza en el solapamiento publicado.

**Cierre verificable:** facilitar los `parallel.json`, perfiles y evidencia serial correspondientes; contrastar revisión, selección, carga y métricas; medir o declarar no medido el costo de reconstrucción de cachés, sin atribuirle toda la diferencia por resta.

## Verificación independiente

- Intake Route C: `validate-request` y `validate-packet` terminaron con **rc=0**; el render de identificación coincide y el contexto es **v2**.
- En `HEAD 9ed567ceb88d0716099909240e1c24ffb9d2198e`, ejecuté la focal T6 y los siete archivos focales T1/T2/T3 y regresiones indicados:
  `python3 -m pytest tests/test_017_001_suite_parallel.py tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_external.py tests/test_008_002_suite_evidence.py -q` → **54 passed en 90,82 s**.
- `python3 scripts/cdad-suite.py validate` → **rc=0**, `status: ok`.
- Reejecuté `parallel --workers 2` y `close` con los dos nodeids de tranche1 y tranche2 usados por el oráculo. Ambos devolvieron **rc=0**, con **2 passed, 0 failed, 0 skipped**. El paralelo informó pared total **2,432 s**, trabajo **0,020 s**, solapamiento **0,118 s** y canario sin delta. Evidencia temporal: `~/<workspace>/tmp/review-t6-xebE44/`.
- El diff de `scripts/cdad-suite.py` desde el padre de `10dfae99` muestra el subcomando paralelo como adición; no observé cambios al cuerpo de `close`.
- No modifiqué archivos del producto ni hice commit. Al inicio y al final, `git status --short` mostró `M docs/.cdad-state.json`, preexistente para esta revisión.

## Abstentions

- **Cifras de las corridas de 57 tests:** no puedo confirmarlas ni rechazarlas sin los archivos de evidencia cruda mencionados.
- **Ausencia real de huérfanos y seguridad de toda la suite:** no quedan demostradas por los campos del agregado ni por la muestra focal.
- **Suite completa:** no la ejecuté; los 54 tests focales verdes no acreditan su resultado ni autorizan inferirlo.
