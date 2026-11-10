# Decisión y contrato del lote paralelo — T6 (017-001-suite-performance)

## Decisión del dueño (2026-11-07)

Paralelizar, con **cantidad de workers configurable** y sin usar todos los
núcleos. Además, el paralelismo de tests debe convertirse en una **capacidad de
CDAD** (no una optimización exclusiva de este proyecto). Ambas cosas quedan
registradas; la segunda excede 017-001 y se propone como unidad nueva.

## Por qué se justifica (PC-9)

- Base serial medida: 4994 s de pared; costo serial reducible demostrado: 0 en
  la muestra más cara (76/76 instalaciones son acción bajo prueba; 301 CLI son
  el producto bajo prueba; el in-process es cómputo real).
- La optimización serial está bloqueada por falta de costo reducible observado
  (spec §4.4). El objetivo de reducción de pared no puede alcanzarse en serie
  sin recortar cobertura, que el dueño prohibió.
- Por lo tanto el paralelismo es la única palanca de tiempo de pared que no
  cambia lo verificado.

## Contrato del lote (a fijar antes de ejecutar)

**Superficie.** Nuevo subcomando de solo-ejecución, separado de `close` (que
queda serial e intacto):

```
python3 scripts/cdad-suite.py parallel --workers N --evidence-root <dir> [--all | --nodeids <file>] [--balance-from <profile.json>]
```

- `--workers N`: obligatorio, `1 <= N <= nproc-1`; por defecto **2**. Nunca
  todos los núcleos sin una opción explícita.
- Partición por **archivo** (nunca por test suelto): conserva el orden interno
  de cada archivo y evita separar clases/fixtures. Balanceo por costo medido si
  se pasa `--balance-from`; si no, round-robin por cantidad de nodeids.
- Cada worker es un proceso `pytest` independiente con `HOME`, `XDG_*` y `TMPDIR`
  propios (la fixture de sesión de `tests/conftest.py` ya los aísla por sesión;
  el runner garantiza que cada hijo sea una sesión distinta) y su propio
  subdirectorio de evidencia `worker-<i>/`.
- Evidencia por worker: `pytest.xml`, `phases-raw.json`, `profile.json`,
  `stdout.log`, `stderr.log`; más `parallel.json` + `parallel.md` agregados.
- El agregado **no** aplica la identidad serial: informa por worker y en total
  - pared de cada worker y pared total (reloj de pared del comando),
  - Σ fases por worker, rotulada como **trabajo medido**, nunca como pared,
  - resultado por worker y resultado consolidado,
  - solapamiento = Σ pared de workers − pared total (declarado, no "ahorro"),
  - costo de reconstrucción de cachés por worker (si se mide) y resultado neto.

## Evidencia de seguridad (PC-10)

Antes de adoptar el lote se entrega:

1. **Inventario de recursos compartidos** de la suite: HOME/XDG/TMP (fixture de
   sesión), raíces de staging (`product_staging._RUN_SCOPED_BASE`), checkout
   (`build/`, `.cdad/`), puertos, cachés de sistema.
2. **Evidencia concurrente**: dos workers con raíces distintas verificadas en el
   perfil; canary sin cambios; procesos hijos terminados (sin huérfanos);
   ningún archivo de evidencia pisado (ids únicos por worker).
3. **Equivalencia**: mismos nodeids y mismo orden interno; el conjunto de
   passed/failed/skipped por worker, consolidado, debe ser idéntico al serial
   de la misma revisión.
4. **Neto**: pared paralela vs pared serial de la misma revisión, con la carga
   del host registrada; nunca se presenta la suma de tiempos concurrentes como
   pared.

## Límites y riesgos declarados

- Tests que escriban en el checkout (`build/`, `.cdad/`) romperían el
  aislamiento: el canary y la comparación de resultados lo detectan, y el lote
  se descarta para esa selección.
- Tests con puertos fijos o recursos del sistema pueden colisionar: quedan
  fuera del lote hasta demostrar aislamiento (lista explícita).
- El costo de reconstruir cachés por worker (copias de producto/staging) puede
  comerse parte de la ganancia: se mide y se informa el neto.

## Generalización a CDAD (fuera de 017-001)

El paralelismo como capacidad del producto exige, en una unidad nueva:

- una regla de diseño de tests paralelizables (raíces propias, sin estado
  compartido, sin puertos fijos, sin escrituras al checkout) que el test-writer
  reciba en cada packet;
- una declaración de aislamiento por módulo (junto al inventario vivo) y un
  verificador que falle cuando dos workers tocan el mismo recurso;
- el runner con workers configurables como parte de la herramienta del ciclo,
  no del proyecto.

Esa unidad se abre al cerrar 017 y no se mezcla con su aceptación.

## Objetivo registrado (PC-4) para la corrida final

Fijado por el orquestador en nombre del dueño, **antes** de la corrida final y a
partir de lo medido:

- Selección: suite completa (`--all`), una sola revisión para serie y paralelo.
- Condiciones: `--workers 2`, balanceo por costo medido con el perfil serial de
  la misma revisión; host con carga registrada en ambas corridas.
- Regla de evaluación: `(pared_serial - pared_paralela) / pared_serial >= 0.15`
  **y** conjuntos de passed/failed/skipped idénticos por nodeid.
- Garantías: PC-10 completo (raíces por worker, canary, hijos terminados,
  evidencia sin colisiones) y ninguna suma de tiempos concurrentes presentada
  como pared.
- No se admite alcanzar el objetivo recortando tests ni relajando aserciones.

## Resultado preliminar del lote (runner anterior — sustituido)

> Estas cifras se midieron con el runner **antes** de las correcciones de
> `review-T6.md` (paredes tomadas del `wait()` secuencial, sin canario del
> checkout y con preparación atribuida por resta). Se conservan como historia
> del diagnóstico; **no** son la evidencia del gate. La remedición sobre la
> revisión final, con el runner corregido, se publica abajo en «Resultado sobre
> la revisión final».

## Resultado medido del lote (runner anterior)

Selección de contraste: los seis archivos más caros (57 tests), revisión
`88381176`, misma para las tres corridas. Referencia serial: `close` del 2026-11-07
(`performance/remainder-measurement.md`), pared **837.2 s**.

| Régimen | Pared total | Trabajo medido (Σ workers) | Solapamiento | Resultado |
|---|---:|---:|---:|---|
| Serial (`close`) | 837.2 s | 837.2 s | — | 57 passed |
| `parallel --workers 2` (partición por conteo) | **666.3 s** (−20.4 %) | 1110.6 s | 447.0 s | 57 passed, 0 failed |
| `parallel --workers 2 --balance-from <perfil serial>` | **552.0 s** (−34.1 %) | 1044.1 s | 550.4 s | 57 passed, 0 failed |

- Partición por conteo: workers de 447.8 s y 665.5 s (desbalance; el crítico
  manda). Balanceada por costo medido: la pared baja a 552.0 s.
- **Costo de reconstruir cachés por worker**: el trabajo medido supera la pared
  serial (1110.6 s y 1044.1 s vs 837.2 s). La diferencia (273 s y 207 s) es
  preparación duplicada por worker y **no** se presenta como ahorro; el neto es
  la pared.
- Evidencia de aislamiento: `HOME`, `XDG_*` y `TMPDIR` propios por worker
  (`worker-<i>/home`), canary sin cambios (`delta_lines: 0`), `children_terminated:
  true`, `orphans: 0`, commit y `dirty: 0` registrados.
- Equivalencia: mismos 57 nodeids, mismo orden interno por archivo, consolidado
  idéntico al serial (57 passed, 0 failed, 0 skipped).
- Intersección: `evidence/017-001-t6-parallel2` (conteo) y
  `evidence/017-001-t6-parallel2b` (balanceada).

## Inventario de recursos compartidos (PC-10)

| Recurso | Aislamiento | Verificación |
|---|---|---|
| `HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `TMPDIR` | raíz propia por worker | registradas en `parallel.json`; fixture de sesión del suite |
| Raíces de staging de producto (`product_staging._RUN_SCOPED_BASE`) | una por sesión de worker | perfil por worker; copias independientes |
| Checkout (`build/`, `.cdad/`) | solo lectura por los tests; canary | `canary.delta_lines = 0` |
| Procesos hijos | terminados y esperados | `children_terminated`, `orphans: 0` |
| Evidencia | `worker-<i>/` con ids únicos | sin colisiones en las dos corridas |
| Puertos / recursos del sistema | no usados por esta selección | queda fuera del lote cualquier archivo que los use hasta demostrarlo |

## Inventario de consumidores de puertos (selección `--all`)

Barrido sobre `tests/*.py`: **tres archivos** abren sockets, y todos usan
**puerto efímero** (bind a `0` o sonda de puerto libre), nunca un puerto fijo:

| Archivo | Sitios | Forma |
|---|---|---|
| `tests/test_006_001_t1_selection.py` | `ThreadingHTTPServer(("127.0.0.1", 0))` + `closed_port_url()` | efímero |
| `tests/test_006_001_reviewfix.py` | `ThreadingHTTPServer(("127.0.0.1", 0))` | efímero |
| `tests/test_006_001_t3_integration.py` | sonda `bind(("127.0.0.1", 0))` y `--port <libre>` | efímero |

Riesgo residual declarado: `closed_port_url()` toma un puerto libre y lo cierra
antes de usarlo como "puerto cerrado"; otro worker podría ocupar ese puerto en
la ventana entre el cierre y el uso. La probabilidad es baja (rango efímero
amplio, ventana de milisegundos) y **no se elimina**: se declara. Si aparece
como flakiness en la corrida final, esos tres archivos quedan fuera del lote con
lista explícita y la comparación se hace sobre el resto, sin recortar cobertura
silenciosamente.

## Canario del checkout

El canario actual cubre configuración y entradas de primer nivel de `HOME`; **no**
cubre `build/` ni `.cdad/` del checkout, pese a lo que afirmaba la sección
anterior. Es un defecto del runner, registrado en `review-T6.md` (hallazgo 4) y
en corrección: el canario del lote debe incluir el checkout (conteo de archivos,
tamaño y mtime máximo de `build/` y `.cdad/`) y fallar si cambian.

## Evidencia cruda dentro del repo

Para que la revisión pueda verificarla sin salir del árbol, las dos corridas del
lote están copiadas en:

- `.cdad/tmp/017-001-t6-evidence/count/` — partición por conteo (666.3 s)
- `.cdad/tmp/017-001-t6-evidence/balanced/` — balanceada por costo (552.0 s)

Cada una contiene `parallel.json`, `parallel.md`, `run.stdout`, `run.stderr`,
`canary-*.txt` y `worker-<i>/` con su `profile.json`, `attempt.json` y logs.
`evidence/017-001-t6-parallel2*` sigue siendo la ubicación estable del
workspace; la copia es de solo lectura para revisión.

## Correcciones pendientes (bloqueantes de review-T6)

1. No lanzar pytest para grupos vacíos (o rechazar la combinación).
2. Pared por worker desde el instante real de finalización de cada hijo, no
   desde el `wait()` secuencial.
3. Limpieza y espera de hijos lanzados en rutas de error; comprobación real de
   descendientes, sin `orphans: 0` fijo.
4. Canario del checkout (arriba).
5. Costo de preparación duplicada medido desde los perfiles por worker, no por
   resta contra la pared serial.

## Resultado sobre la revisión final (runner corregido)

Selección de contraste: los seis archivos más caros (57 tests). **Una sola
revisión** para ambas corridas: `3da3f4c64610d2380c8d57d3b51e749ea3adefd6`,
árbol limpio (`dirty = 0`) en los dos intentos. Evidencia cruda en
`evidence/017-001-t6-final5/{serial,parallel}` y copia de solo lectura en
`.cdad/tmp/017-001-t6-evidence-final5/`.

| Régimen | Pared | Trabajo medido | Solapamiento | Resultado |
|---|---:|---:|---:|---|
| Serial (`close --nodeids`) | **873.0 s** (`T_ext`; pytest 871.92 s) | — | — | 57 passed |
| `parallel --workers 2 --balance-from <serial>` | **546.36 s** (`total_wall_s`) | 1036.6 s | 493.8 s | 57 passed, 0 failed, 0 skipped, veredicto `accepted` |

**Reducción de pared: 37.4 %** — `(873.0 − 546.36) / 873.0`.

Paredes por worker desde sus instantes reales: worker 0 `546.4 s`
(`pgid 2843323`, 5 procesos transitorios vistos), worker 1 `493.8 s`
(`pgid 2843324`, 3 transitorios). El segundo termina antes y su pared **no**
incluye la espera del primero.

Evidencia de PC-10 en esta corrida:

- `orphans: 0` al final; `orphans_found: 8` (transitorios que murieron dentro de
  la ventana de gracia de 5 s), `cleaned: 0`, `remaining: 0`,
  `orphans_checked: true`, `subreaper: true`.
- `workers_launched: 2`, `skipped_empty_workers: 0`; `pgid` registrado por
  worker.
- Canario de configuración `unchanged: true` y canario del checkout
  `unchanged: true` sobre 20 332 archivos, con huella de contenido
  `sha256-per-file-sorted` (`b68410ce…`, coste 3.1 s por barrido) — detecta
  reescrituras de igual tamaño y mtime.
- `preparation_source: "per-worker-profiles"`; preparación medida total
  0.136 s; `duplicated_preparation_s` 0.005 s respecto del serial. El trabajo
  medido (1036.6 s) **no** se presenta como ahorro.

Mediciones previas (871.0 → 586.6 s y 855.0 → 618.25 s) con versiones
anteriores del runner se conservan como referencia de estabilidad; **no** son
la evidencia del gate.

Límites: muestra del 22.5 % del suite (los seis archivos más caros), no la
suite completa; las paredes incluyen la carga del host, registrada en
`parallel.json.host`; la garantía de familia requiere Linux (`prctl` + `/proc`)
y se declara. La acreditación final (T7) se hace con `--all` sobre una única
revisión y la regla registrada (≥ 15 % + equivalencia exacta).

## Primer intento de la corrida final (T7) — descartado y diagnosticado

Corrida sobre `1cc39d3e`, árbol limpio, `--all`, una sola revisión:

| Régimen | Pared | Resultado | Veredicto |
|---|---:|---|---|
| Serial (`close --all`) | 4354 s (`T_ext`; pytest 4340.7 s) | 2049 passed, 5 skipped, 0 failed | `rc 0`, canario de configuración limpio |
| `parallel --all --workers 2` | 2828.2 s (`total_wall_s`) | 2049 passed, 5 skipped, 0 failed | **descartado**: `rejected: canary detected changes` |

El lote paralelo **no se usa**: el runner lo descartó y la regla del contrato es
que una corrida descartada no acredita nada. Totales idénticos entre ambas
(2049 + 5), pero eso no se presenta como equivalencia demostrada porque la
corrida está rechazada.

### Causa raíz (reproducida y medida)

El veredicto `checkout_unchanged` compara `_checkout_key()`, que incluye
`max_mtime_ns` (`scripts/cdad-suite.py`, `_checkout_key`). La propia función
`checkout_canary_snapshot` documenta que el mtime máximo se conserva «como
información (no como huella)», de modo que la inclusión en la comparación
contradice su contrato declarado.

Reproducción mínima: `parallel --workers 1` sobre
`tests/test_010_004_t5_e2e.py` (2 tests, 30.5 s) → `rc 3`,
`verdict=rejected: canary detected changes`. Comparando la huella tomada antes
y después de esa corrida con la propia función:

```
files            20396   -> 20396            (igual)
total_bytes      450294782 -> 450294782      (igual)
fingerprint      3f763201… -> 3f763201…      (igual: contenido byte a byte idéntico)
max_mtime_ns     1794125396464441675 -> 1794125452695046333   (+56 s)
fingerprint_cost_s 3.0588 -> 3.0063          (no participa del veredicto)
```

`tests/test_010_004_t5_e2e.py` usa `.cdad/tmp/t5-isolated-consumer/<corrida>/`
como raíz temporal declarada y la retira al final; crear y retirar ese
subdirectorio mueve el `mtime` de los **directorios** padres (`build/`,
`.cdad/`, `.cdad/tmp`) sin cambiar un solo byte de contenido ni el conjunto de
archivos. Con `--all` el mismo churn ocurre y el lote se rechaza siempre.

### Clasificación del defecto

- **No es una aceptación laxa**: el canario falló del lado seguro (rechazó una
  corrida con contenido idéntico). No hubo riesgo de dar por válido un cambio
  real.
- **Es un defecto de veredicto**: mezcla una señal de churn legítimo
  (mtime de directorios) con la huella de contenido, y hace **imposible**
  aprobar `--all` con el runner actual.
- **Corrección**: el veredicto debe apoyarse en la huella de contenido, el
  conjunto de archivos y los bytes totales; el `max_mtime_ns` se informa pero
  no decide. Eso es estrictamente más fuerte que el mtime para detectar
  cambios persistentes (la huella por archivo ordenada ya lo cubre) y no
  relaja ninguna garantía de contenido.

Mientras la corrección no esté aprobada y el par no se repita completo sobre
una única revisión, T7 queda **no acreditada**.

### Corrección del veredicto (aplicada y probada)

`_checkout_key` compara ahora `scope`, `files`, `total_bytes`, `fingerprint` y
`fingerprint_algo`. `max_mtime_ns` sigue publicado en `parallel.json` como
información, pero no decide.

Prueba de ambos sentidos tras la corrección (18/18 del oráculo T6, focales
T1–T4 y `validate` rc 0):

| Escenario | Resultado |
|---|---|
| `parallel` sobre `test_010_004_t5_e2e.py` (el que reproducía el rechazo) | `rc 0`, `accepted`, `unchanged: true`, `max_mtime_ns` informado |
| Sonda que deja un archivo nuevo persistente bajo `.cdad/tmp` | `rejected`, `unchanged: false`, `rc 3` |

**Límite declarado de la huella**: al ser contenido, no detecta cambios de modo
(bits de permiso) ni la creación o el borrado de directorios vacíos sin
archivos. No detecta, por tanto, un cambio de permisos del checkout durante el
lote; sí detecta cualquier alta, baja o cambio de contenido de archivo. Se
declara en lugar de presentar la huella como cobertura total.

## Segundo intento de la corrida final (T7) — fallo de un meta-test bajo carga

Misma revisión `75eec556`, árbol limpio, `--all`:

| Régimen | Pared | Resultado |
|---|---:|---|
| Serial (`close --all`) | 4370 s | 2049 passed, 5 skipped, **0 failed** |
| `parallel --all --workers 2` | 2635 s | 2049 passed, **1 failed**, 5 skipped |

El fallo es
`test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change` (el test
nuevo del veredicto del canario): su `cdad-suite.py parallel` anidado agotó un
timeout de **120 s**. En aislamiento ese test tarda **7.36 s**; la familia usa
`TIMEOUT_S = 300` y este test se desvió con `timeout=120` escrito a mano. Bajo
la carga de dos workers recorriendo 450 MB de huella dos veces por corrida
anidada, el margen de 16× no alcanzó.

Clasificación: **defecto del test, no del producto**. El canario del checkout
quedó `unchanged: true` (20432 archivos) y `orphans: 0` con 20 transitorios
gestionados; ningún test de producto falló por concurrencia. La corrida, aun
así, **no se usa**: tiene un fallo y el contrato no admite excepciones.

Corrección: los timeouts de liveness de las corridas anidadas vuelven a la
convención de la familia (`TIMEOUT_S`), y la prueba de la corrección debe
ejecutarse **bajo carga concurrente**, no en aislamiento.

### Tercer hallazgo: scratch compartido entre workers dentro del checkout

Reproducido con una selección mínima (`--workers 2`: el archivo de 18
meta-tests en un worker y `tests/test_010_004_t5_e2e.py` en el otro):

```
passed=19 failed=1
FALLO: test_parallel_accepts_cdad_tmp_subdir_churn_without_content_change
rc=3  veredicto=rejected: canary detected changes
      (checkout unchanged=False)  pared_total=0.82 s
```

Mecanismo: `tests/test_010_004_t5_e2e.py` copia el producto completo —19 mil
archivos, ~450 MB— dentro de `.cdad/tmp/t5-isolated-consumer/<corrida>/` **en el
checkout real**, y lo retira al terminar. Si otro worker (o un meta-test que
lanza el runner anidado) toma una huella del checkout durante esa ventana, ve
un conjunto de archivos que aparece y desaparece: el canario lo rechaza con
razón, porque efectivamente algo cambió el árbol durante la corrida.

Ese único mecanismo explica los dos síntomas del segundo intento: el rechazo a
0.82 s y la corrida anidada que superó 120 s escaneando un árbol que se estaba
copiando (450 MB en crecimiento).

**No es un falso positivo del canario**: es scratch de test dentro del árbol
vigilado, compartido por dos workers. La corrección correcta es sacar ese
scratch del checkout (como ya hace `tests/product_staging.py`, que trabaja
sobre una copia temporal propia), no debilitar el canario ni subir timeouts a
ciegas. Medición de apoyo: un barrido completo del canario cuesta 3.3 s en
caliente y 3.5 s bajo dos lectores pesados, así que el costo del escaneo no es
el problema; el problema es escanear mientras otro proceso escribe ahí.

### Corrección del scratch de test (aplicada y probada bajo carga)

`tests/test_010_004_t5_e2e.py` ya no escribe la raíz aislada dentro del
checkout: usa `run_scoped_mkdtemp` de `tests/product_staging.py`, fuera del
árbol, con limpieza de clase. Promesas y aserciones del test intactas; solo
cambió la ubicación de la raíz y los docstrings que afirmaban —falsamente— que
`.cdad/tmp` era una raíz temporal declarada por la política (hoy
`temporary_roots` está vacío en `docs/cdad-policy.json`).

Prueba bajo carga concurrente (el escenario que fallaba), `--workers 2`:

| Selección | Resultado |
|---|---|
| 18 meta-tests + los 2 de `t5_e2e` (20 nodeids) | **20 passed**, 0 failed, `verdict: accepted` |
| Canario del checkout | `unchanged: true` (20 458 archivos) |
| Huérfanos | `0` (transitorios gestionados) |
| Residuos | `.cdad/tmp` sin `t5-isolated-consumer` |

El archivo solo: 2 passed en 23.89 s. Con esto ningún test escribe scratch
dentro del checkout durante el lote, que era la causa real de los rechazos.

## Corrida final anterior — `83674246` (histórica, superada)

> **No es la evidencia vigente.** Esta corrida se hizo con un runner anterior a
> las correcciones *fail-closed* del veredicto. Se conserva como historia del
> diagnóstico; sus cifras **no** acreditan nada. La evidencia vigente es la de
> `bf0e7483`, más abajo, y su copia de solo lectura está en
> `.cdad/tmp/017-001-final-evidence/`. Los crudos de este par histórico viven
> en `evidence/017-001-final3/{serial,parallel}`.

`--all`, una sola revisión para ambas corridas, árbol limpio (`dirty = 0`) antes
de empezar y al terminar.

| Régimen | Pared | Resultado | Veredicto |
|---|---:|---|---|
| Serial (`close --all`) | **4235 s** (`T_exterior`; pytest 4232.96 s) | 2050 passed, 5 skipped, 0 failed | `rc 0`, canario de configuración limpio |
| `parallel --all --workers 2 --balance-from <serial>` | **2925.34 s** (`total_wall_s`) | 2050 passed, 5 skipped, 0 failed | `accepted` |

**Reducción de pared observada: 30.92 %** (histórica). La equivalencia fue
exacta: 2055 nodeids en cada régimen, 0 diferencias de resultado por nodeid.
Ninguna de estas dos cifras se usa como acreditación.

### Atribución de la corrida serial (T3 `reconcile`)

| Concepto | Valor |
|---|---:|
| `T_pytest` | 4232.96 s |
| Preparación (medida, compartida) | **445.64 s** (10.5 %) |
| Resto no desglosado | **3779.79 s** (89.5 %) — desconocido |
| `R_pytest` | 7.54 s |
| `R_exterior` | 2.04 s |
| Cota de redondeo (2055 tests) | 1.03 s |

`status: complete`. Diagnóstico declarado: `operation-without-register-entry`
(3 operaciones sin entrada en el registro de alcance; viene de la base y no
cambia la atribución). El resto sigue publicado como **desconocido**: no se
clasifica por descarte.

### Condiciones de la corrida

- Workers `2704.4 s` (1171 passed + 3 skipped, `pgid 2586641`) y `2925.3 s`
  (879 passed + 2 skipped, `pgid 2586642`); ambos arrancan juntos, el segundo
  termina antes y su pared no incluye la espera del primero.
- `orphans: 0` con `orphans_found: 20` (transitorios que murieron dentro de la
  gracia de 5 s), `orphans_cleaned: 0`, `subreaper: true`.
- Canario de configuración `unchanged: true` y canario del checkout
  `unchanged: true` sobre 20 469 archivos, huella por contenido `60f0d866…`
  (coste 3.32 s por barrido).
- Preparación: `preparation_source: per-worker-profiles`, total medida
  182.07 s; duplicada en el lote **23.28 s**, informada aparte y **no**
  presentada como ahorro. El trabajo medido (5619.7 s) es la suma de ambos
  workers y supera la pared por concurrencia; tampoco es ahorro.

### Qué queda declarado como no probado

- La pared depende de la carga del host (registrada en `parallel.json.host`);
  no se controla carga externa.
- La garantía de familia de procesos requiere Linux (`prctl` + `/proc`).
- Los tres intentos previos, con sus causas, quedan documentados arriba: dos
  rechazos por el canario y un fallo de liveness de un meta-test. **No aportan
  evidencia** y no se usan para acreditar nada.

## Corrida final definitiva (T7) — `bf0e7483`

El par de `83674246` quedó **superado**: entre una y otra corrida el runner
recibió las correcciones *fail-closed* del veredicto (familia no acreditable,
canario posterior a la limpieza, barrido incompleto registrado y evidencia
exclusiva por invocación, `review-final-product-002.md`). La evidencia válida
es la de esta revisión, con el runner que se entrega.

`--all`, misma revisión, árbol limpio antes de empezar y al terminar:

| Régimen | Pared | Resultado | Veredicto |
|---|---:|---|---|
| Serial (`close --all`) | **4459 s** (`T_exterior`; pytest 4458.5 s) | 2054 passed, 5 skipped, 0 failed | `rc 0`, canario de configuración limpio |
| `parallel --all --workers 2 --balance-from <serial>` | **2593.15 s** (`total_wall_s`) | 2054 passed, 5 skipped, 0 failed | `accepted`, `family_verifiable: true` |

**Reducción de pared: 41.84 %** (objetivo registrado ≥ 15 %) y **equivalencia
exacta**: 2059 nodeids en cada régimen, 0 sólo en serial, 0 sólo en paralelo,
0 diferencias de resultado por nodeid.

### Atribución serial (`reconcile`)

| Concepto | Valor |
|---|---:|
| `T_pytest` | 4458.5 s |
| Preparación medida | **448.90 s** (10.1 %) |
| Resto no desglosado | **4002.51 s** (89.9 %) — desconocido |
| `R_pytest` | 7.12 s |
| `R_exterior` | 0.47 s |
| Cota de redondeo (2059 tests) | ~1.03 s |

### Evidencia de integridad

- Workers `2514.3 s` (1042 passed + 4 skipped, `pgid 4052896`) y `2593.1 s`
  (1012 passed + 1 skipped, `pgid 4052897`).
- `orphans: 0` con `orphans_found: 20`, `cleaned: 0`, `remaining: 0`,
  `subreaper: true`, `family_verifiable: true`.
- Canario de configuración `unchanged: true`; canario del checkout
  `unchanged: true` sobre 20 607 archivos con `incomplete: []`.
- Preparación `per-worker-profiles`: 170.07 s total medida por worker;
  duplicada en el lote **16.34 s**, informada aparte.
