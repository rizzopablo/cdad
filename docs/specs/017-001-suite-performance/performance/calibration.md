# Calibracion de operaciones — T2 (017-001-suite-performance)

- Revision medida: seis selecciones sobre `cb8f2fe677b2fe497f09501ff873881b2aab4c11`; C-P sobre `af26e0fbf2a4a0da2233ef20c81bb5d0c9d25d47`
- Fecha: 2026-11-07
- Registro aplicado: `docs/specs/017-001-suite-performance/performance/operation-scope.json`
- Comando por seleccion: `python3 scripts/cdad-suite.py close --evidence-root <dir> --nodeids <seleccion>` en proceso nuevo.
- Evidencia cruda: intentos bajo `~/<workspace>/tmp/017-001-calibration/<seleccion>/` (fuera de los origenes copiados).

## Resultado por seleccion

| Seleccion | status | pared (s) | operaciones | fases | errores de op | conteos esperados |
|---|---|---|---|---|---|---|
| C-R | complete | 2.22 | 5 | 3 | 0 | coinciden |
| C-E | complete | 3.8 | 8 | 3 | 0 | coinciden |
| C-U1 | complete | 6.26 | 7 | 6 | 0 | coinciden |
| C-U3 | complete | 2.82 | 9 | 6 | 0 | coinciden |
| C-U4 | complete | 6.14 | 10 | 6 | 0 | coinciden |
| C-D | complete | 20.27 | 15 | 9 | 0 | coinciden |
| C-P-cold | complete | 1.73 | 6 | 3 | 0 | coinciden |
| C-P-present | complete | 1.53 | 4 | 3 | 0 | coinciden |

## Contraste esperado/observado por operacion

### C-R

- `recovery.construct`: esperado 1, observado 1
- `recovery.build`: esperado 1, observado 1
- `recovery.initial-prepare`: esperado 1, observado 1
- intento: `attempt-20261107T150854549440Z-601787-ed17b76b`

### C-E

- `continuity.construct`: esperado 2, observado 2
- `continuity.build`: esperado 2, observado 2
- `continuity.initial-prepare`: esperado 2, observado 2
- intento: `attempt-20261107T150902281359Z-601948-1e576aee`

### C-U1

- `u1.lookup`: esperado 2, observado 2
- `u1.copy`: esperado 1, observado 1
- `u1.generate`: esperado 1, observado 1
- intento: `attempt-20261107T150907044957Z-602114-cb095ffe`

### C-U3

- `u3.lookup`: esperado 2, observado 2
- `u3.copy`: esperado 1, observado 1
- `u3.initial-generate`: esperado 1, observado 1
- `u3.contract-staging`: esperado 2, observado 2
- intento: `attempt-20261107T150914350095Z-602228-148d4476`

### C-U4

- `u4.lookup`: esperado 3, observado 3
- `u4.copy`: esperado 1, observado 1
- `u4.initial-generate`: esperado 1, observado 1
- `u4.contract-regenerate`: esperado 2, observado 2
- intento: `attempt-20261107T150918116789Z-602295-69adff0c`

### C-D

- `documentary.contract-regenerate`: esperado 2, observado 2
- `documentary.install-lookup`: esperado 4, observado 4
- `documentary.install`: esperado 1, observado 1
- `u3.lookup`: esperado 2, observado 2
- intento: `attempt-20261107T150925828787Z-602396-6d546867`

### C-P-cold

- `product.lookup`: esperado 2 (cold 1, cached 1), observado 2 (cold 1, cached 1)
- `product.copy`: esperado 1, observado 1 (0.226 s, hijo del lookup frio)
- `product.generate`: esperado 1, observado 1 (0.290 s, hijo del lookup frio)
- intento: `attempt-20261107T152226133446Z-631777-e79250f4`
- fuente: copia descartable real del repo **sin** `.git`, `build`, `.cdad`, `__pycache__` ni `.pytest_cache`; el checkout real no se muto (verificador compara el manifiesto antes/despues).

### C-P-present

- `product.lookup`: esperado 2 (checkout-manifest 1, cached 1), observado 2 (checkout-manifest 1, cached 1)
- `product.copy`: esperado 0, observado 0
- `product.generate`: esperado 0, observado 0
- intento: `attempt-20261107T152228799596Z-631836-765eabae`
- fuente: la misma copia descartable **con** `build/staging/manifest.json` repuesto desde el checkout real (procedencia registrada en el verificador).

## Anidamiento observado

- `recovery.construct` contiene `recovery.build` y `recovery.initial-prepare` (C-R).
- `continuity.construct` contiene `continuity.build` y `continuity.initial-prepare` (C-E, dos ocurrencias).
- `u1.copy` y `u1.generate` cuelgan del `u1.lookup` frio (C-U1).
- `u3.copy` y `u3.initial-generate` cuelgan del `u3.lookup` frio; `u3.contract-staging` son hermanas posteriores (C-U3, C-D).
- `u4.copy` y `u4.initial-generate` cuelgan del `u4.lookup` frio; `u4.contract-regenerate` son hermanas (C-U4).
- `documentary.install` cuelga de `documentary.install-lookup` frio, que contiene el `u3.lookup` anidado (C-D).
- `isolation.seed` de sesion queda como `shared` y no se adjudica al primer test; el por test queda como `test`.
- `product.copy` y `product.generate` cuelgan del `product.lookup` frio; el segundo `product.lookup` es `cached` y no repite copia ni generacion (C-P-cold).

## Incidente de captura detectado y corregido durante la calibracion

El primer intento de `C-P-cold` por `close` devolvio `complete` con **cero** operaciones `product.*`: el verificador usa `observed()` y el helper tenia un sumidero unico, de modo que `attach()` reemplazaba al observador del `close`. Se corrigio el helper a sumideros multiples (P7, commit `af26e0fb`) y se re-midio: la tabla de arriba es la corrida posterior. El incidente queda registrado porque una captura perdida que se declara `complete` es exactamente el fallo que la spec §4.4 manda diagnosticar.

## Desconocidos declarados y regla de decision

- **C-P-coste-comparable**: las dos selecciones se ejercitaron sobre una copia descartable **slim** (excluye `.cdad`, `build`, `.git`, `__pycache__` y `.pytest_cache`). Los conteos y el anidamiento son validos, pero las duraciones de `product.copy`/`product.generate` **no son comparables** con la copia real del checkout completo ni se usan para dimensionar. Regla de decision: para dimensionar `product_root` se usan las copias de **C-U1 o C-U4**, que incluyen `.cdad`; **C-U3 y C-D la excluyen** por filtro propio y no sirven para atribuir ese volumen; C-P solo prueba la rama y el anidamiento. El tiempo aislado de `.cdad` sigue **desconocido** y no se infiere del tamano: si una decision de exclusion depende de ese costo, se calibra un focal adicional sobre base recuperable (regla ya declarada en el registro).
- **Esperas deliberadas**: familia declarada desconocida en el registro; el comando envolvente no separa espera de arranque, sondeo y terminacion. No se usa para decidir.
- **Subcosto de `.cdad` dentro de las copias**: el volumen (19.141 archivos / 386 MB) es entrada observada, no tiempo; el tiempo atribuible a `.cdad` no queda aislado y no se infiere del tamano.

## Entrada a la base

Las ocho selecciones comprometidas capturan sus intervalos con identidad, contexto y anidamiento, sin errores de operacion y con conteos coincidentes. Las siete familias quedan ejercitadas y calibradas; el unico limite es el declarado arriba (duraciones C-P no comparables por fuente slim). En consecuencia, la linea base puede consumirse (T3/T4) para atribuir costo de staging.
