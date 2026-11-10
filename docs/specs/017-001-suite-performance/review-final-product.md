# Revisión de producto — unidad 2 de 3

**Dictamen: no apto para aceptación en esta unidad.** Encontré bloqueantes que permiten declarar aceptado un lote sin acreditar la finalización de sus procesos o sin detectar cambios persistentes del checkout. Este informe no constituye aprobación.

## Hallazgos bloqueantes

### 1. El lote puede aceptarse sin que la garantía de subreaper esté activa

**Required · Verdict: BLOCKING · Bucket: h**

En `scripts/cdad-suite.py:2265` se intenta activar el subreaper, pero si falla solo se añade una nota (`:2538–2544`). El veredicto de `:2633–2655` no exige que esté activo ni que la comprobación de huérfanos haya sido posible.

Un descendiente que cambió de sesión puede quedar reparentado fuera del runner cuando falla `prctl`; el barrido por PPID y grupo puede entonces no verlo. Aun así, con pytest verde, el resultado puede ser `accepted`. La misma ruta acepta el lote cuando el barrido de `/proc` no está disponible.

**Consecuencia:** se puede presentar como limpio un lote que dejó actividad viva, sin satisfacer PC-10.

**Cierre verificable:** impedir la aceptación cuando no pueda acreditarse la comprobación de familia; verificar el fallo de activación del subreaper y la indisponibilidad del barrido, además del caso normal.

### 2. El canario final se toma antes de terminar de comprobar la familia

**Required · Verdict: BLOCKING · Bucket: h**

`cmd_parallel()` toma el canario final en `scripts/cdad-suite.py:2414–2430`, pero la búsqueda, espera de gracia y eventual limpieza de descendientes se realizan después (`:2457–2524`). Un descendiente todavía vivo puede escribir en `build/` o `.cdad/` después de la fotografía, terminar durante la gracia y dejar el lote aceptado con un cambio persistente no observado.

**Consecuencia:** el veredicto puede afirmar que el checkout no cambió cuando sí cambió durante la actividad residual del lote.

**Cierre verificable:** finalizar y comprobar la familia antes del snapshot final y del veredicto; demostrar el descarte con un descendiente que escriba después de terminar su worker y termine dentro de la gracia.

### 3. La huella trata errores de lectura como contenido estable

**Required · Verdict: BLOCKING · Bucket: h**

`checkout_canary_snapshot()` omite rutas cuyo `lstat` falla y sustituye un hash fallido por el literal `"unreadable"` (`scripts/cdad-suite.py:1556–1577`). `_canary_walk()` también omite silenciosamente directorios inaccesibles (`:706–714`). Si una ruta permanece inaccesible en ambas fotografías, su contenido puede cambiar sin alterar la huella ni impedir `accepted`.

**Consecuencia:** la igualdad del canario se presenta como ausencia de cambios incluso cuando no se pudo leer la zona protegida.

**Cierre verificable:** registrar la incompletitud del barrido y descartar o impedir acreditar la corrida cuando no pueda leerse una entrada relevante; comprobar tanto el caso ilegible como uno legible sin cambios.

### 4. Se reutiliza el directorio de evidencia de workers anteriores

**Required · Verdict: BLOCKING · Bucket: h**

`cmd_parallel()` acepta un directorio existente y crea `worker-N` con `exist_ok=True` (`scripts/cdad-suite.py:2239–2241, 2274–2280`). Sobrescribe algunos logs, pero no reserva un intento nuevo ni elimina los artefactos anteriores antes de ejecutar. Si la corrida nueva no produce XML o sumidero —por ejemplo, por un fallo temprano—, `:2370–2379` puede leer archivos de la corrida previa y asociar mediciones antiguas con la nueva.

**Consecuencia:** la evidencia de trabajo y preparación deja de ser atribuible inequívocamente al intento, contraviniendo INV-1 e INV-6.

**Cierre verificable:** reservar evidencia exclusiva por invocación o rechazar un destino previamente ocupado; comprobar que un fallo temprano nunca incorpore XML o perfil anteriores.

## Contraste de las correcciones e invariantes solicitados

- **Workers vacíos:** `cmd_parallel()` filtra grupos vacíos antes de lanzar pytest (`:2249–2255`).
- **Partición y paredes:** `parallel_partition()` agrupa por archivo (`:2061–2084`); la selección por archivo de nodeids elimina duplicados (`:812–827`). Las paredes se registran por proceso mediante `poll` (`:2338–2356`) y la pared total no es la suma. La observación de finalización tiene resolución de sondeo, no es el instante exacto del kernel.
- **Procesos:** se usan grupos, cadenas de PPID, subreaper y `waitpid` (`:1698–1720, 1796–1850`); la ruta de fallo parcial intenta limpiar la familia (`:2314–2332`). La garantía no queda cerrada por el hallazgo 1.
- **Canario:** la huella incorpora ruta y contenido SHA-256 (`:1564–1587`) y un delta detectado provoca descarte (`:2633–2648`). Excluir `max_mtime_ns` del veredicto (`:2418–2428`) evita rechazar cambios de metadatos de directorios temporales; para archivos legibles, el hash detecta la reescritura persistente de igual tamaño y mtime. Los hallazgos 2 y 3 limitan esa conclusión.
- **Preparación:** se obtiene de perfiles por worker y se informa separada de la pared y del solapamiento (`:2376–2389, 2554–2578`).
- **Límite de workers:** el valor predeterminado es 2 (`:1458`). En una máquina con un solo procesador, `max(1, nproc - 1)` permite un worker (`:2017–2030`), por lo que la regla literal `1..nproc-1` no se cumple; no evalué su impacto operativo suficiente para promoverlo como bloqueante adicional.
- **Separación y neutralidad:** no encontré en los dos archivos examinados nombres de modelos o clientes concretos ni ejecución de trabajo de roles. Los resultados del runner no constituyen aprobación.
- **`close`:** conserva una ejecución serial de pytest, pero su instrumentación modifica la ruta compartida; no afirmo equivalencia completa de todas sus salidas sin verificación ejecutable adicional.

## Evidencia de esta revisión

- **Intake:** Route C; `validate-packet` terminó sin diagnóstico y `render --route C` produjo la identificación recibida.
- **Revisión observada:** `git rev-parse HEAD` → `b5b0abec6137133a6a5c9502237ad691b23b360e`; `git status --short` no produjo entradas.
- **Diff:** `git diff c3c38c5d1a7f2d362bc026edf4863e1e1ca82c4d --stat -- scripts/cdad-suite.py scripts/cdad_suite_observer.py` informó cambios en ambos archivos.
- **Archivos modificados y commit de esta revisión:** ninguno.
- No ejecuté pruebas ni suite completa; la unidad asignada excluye revisar los tests. La evidencia ejecutable citada por revisiones anteriores no sustituye las comprobaciones de cierre propuestas arriba.

## Abstentions

- No verifico la equivalencia por nodeid ni el resultado de la suite completa: corresponde a otra evidencia y no se ejecutó en esta unidad.
- No afirmo seguridad de la familia de procesos fuera de Linux ni cuando falla el mecanismo de subreaper.
- No doy por verificada íntegramente la conservación de salida y comportamiento de `close`, ni la fidelidad completa de `reconcile`, `entry-check` y el observador con pruebas ejecutables en esta unidad.
