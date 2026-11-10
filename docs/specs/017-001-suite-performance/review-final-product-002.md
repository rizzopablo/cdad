# review-final-product-002.md

## Dictamen

**Producto apto para aceptación en el alcance focal de esta unidad:** los cuatro bloqueantes de `review-final-product.md` quedan **cerrados** con las sondas ejecutadas y el contraste del código. Este dictamen no constituye aprobación ni acredita por sí solo el cierre completo de la feature.

## Veredicto por bloqueante

### 1. Familia no acreditable — cerrado

Con una selección liviana verde:

- `CDAD_SUITE_FAULT=no-subreaper`: **rc 3**, veredicto `discarded: process family guarantee not verifiable`, `family_verifiable: false`.
- `CDAD_SUITE_FAULT=no-sweep`: **rc 3**, mismo tipo de descarte, `family_verifiable: false`, `orphans: null`.

Ambos mensajes nombraron la falla. El control sin la variable terminó con **rc 0**, `accepted`, `family_verifiable: true` y `orphans: 0`.

La costura no permite aceptar esas dos fallas: `family_unverifiable` participa directamente en el descarte (`scripts/cdad-suite.py:2649, 2745–2764, 2778–2786`).

### 2. Canario tardío — cerrado

La sonda lanzó un hijo que esperó dos segundos y escribió un archivo único bajo `build/`. El worker duró 0,90 s; el runner observó un descendiente (`orphans_found: 1`) y terminó con `orphans: 0` dentro de la gracia declarada de 5 s.

Resultado: **rc 3**, `rejected`, `checkout_canary.unchanged: false`. El archivo existía al terminar la corrida y se verificó su eliminación posterior.

El código toma la fotografía final después de resolver la familia (`scripts/cdad-suite.py:2549–2629`).

### 3. Barrido incompleto — cerrado

Con un subdirectorio modo `000` y un archivo dentro de `.cdad/tmp`:

- **rc 3**, veredicto `rejected`.
- `checkout_canary.incomplete` incluyó `.cdad/tmp/.review-022-63f993078f`.
- Se restauraron los permisos y se verificó la eliminación del directorio.

Los errores de recorrido y lectura se registran como incompletitud (`scripts/cdad-suite.py:1580–1624`), y esta impide aceptar la corrida (`:2770–2782`).

### 4. Evidencia reutilizada — cerrado

La primera invocación terminó **rc 0**, `accepted`. La segunda, sobre la misma raíz, terminó **rc 2**, sin stdout y con diagnóstico de destino ocupado y evidencia previa en stderr. No reportó resultados de tests en su salida.

El `parallel.json` que permanecía en el directorio seguía mostrando `accepted` y un test pasado: **pertenecía al primer intento**, no fue producido ni presentado como resultado de la segunda invocación.

El producto rechaza los artefactos existentes y crea `worker-<i>` con `exist_ok=False` (`scripts/cdad-suite.py:2287–2306, 2352–2356`).

## Comandos y evidencia

Las sondas se ejecutaron mediante un programa Python temporal en memoria, que creó sus entradas y raíces bajo `<tmp>/review-022-v601pord`, con `PYTHONDONTWRITEBYTECODE=1`. Usó la misma selección liviana para las sondas ordinarias. Los comandos efectivos fueron:

```sh
CDAD_SUITE_FAULT=no-subreaper /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/no-subreaper --nodeids <tmp>/review-022-v601pord/no-subreaper.nodeids
CDAD_SUITE_FAULT=no-sweep /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/no-sweep --nodeids <tmp>/review-022-v601pord/no-sweep.nodeids
env -u CDAD_SUITE_FAULT /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/clean --nodeids <tmp>/review-022-v601pord/clean.nodeids
env -u CDAD_SUITE_FAULT /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/late --nodeids <tmp>/review-022-v601pord/late.nodeids
env -u CDAD_SUITE_FAULT /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/unreadable --nodeids <tmp>/review-022-v601pord/unreadable.nodeids
env -u CDAD_SUITE_FAULT /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/reuse-first --nodeids <tmp>/review-022-v601pord/reuse-first.nodeids
env -u CDAD_SUITE_FAULT /usr/bin/python3 scripts/cdad-suite.py parallel --workers 1 --evidence-root <tmp>/review-022-v601pord/reuse-first --nodeids <tmp>/review-022-v601pord/reuse-second.nodeids
```

Las rutas temporales fueron eliminadas en `finally`; no quedan para inspección posterior. La salida registró `finally_clean: True True True` y `git status --short` no mostró cambios.

- Focal completa: `python3 -m pytest tests/test_017_001_suite_parallel.py -p no:cacheprovider -q` → **22 passed in 233.05s**.
- `python3 scripts/cdad-suite.py validate` → **`status: ok`**, 2059 nodeids recolectados, 246 módulos inventariados y 31 entradas de mapa. La salida recuperada no muestra explícitamente el código de salida.
- El diff de las correcciones no modifica la lógica de partición, cálculo de paredes, preparación ni la ventana de gracia; mueve la fotografía posterior a la resolución de familia. `close` no fue modificado por estas correcciones.
- Revisión observada: `213e834614cfd9393651ade91a30467d79c84b73`. No edité archivos ni creé commits.

## Abstentions

- No afirmo equivalencia ejecutable completa de todas las salidas de `close` ni acredito la suite completa de la feature: no se ejecutaron como parte de esta re-revisión focal.
- La sonda tardía acredita el caso observado; no promete confinamiento universal ni detección de escrituras transitorias que desaparezcan antes de la fotografía final.
