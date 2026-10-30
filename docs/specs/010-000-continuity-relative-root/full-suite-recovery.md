# Recuperación de evidencia de suite — 010-000

## Corrida original (no aprobada)

Comando: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q`.
Log: `.cdad/evidence/full-suite-010-000.log`.
SHA-256: `c5234d870b4ef357d3c9cb4a44de8b6a173ca7293131b4cd292c8b3241f47d0d`.
Resultado: **8 failed, 1624 passed, 5 skipped, 217 errors**, rc=1,
2661.44 s. No presentar esta corrida como verde.

Los fallos revisados contienen `Errno 28: No space left on device`; el log
contiene 419 menciones de ese diagnóstico. Tras la corrida `/tmp` conservaba
52 GB libres pero solo 70666 inodos libres (94% utilizados). Los errores de
setup incluyen imposibilidad de crear directorios numerados de pytest. Es
necesario comprobar la recuperación, no atribuir todo el fallo al entorno por
simple semejanza de mensajes.

## Hipótesis y estrategia verificable

El helper de fixtures copia el árbol fuente omitiendo algunas cachés, pero no
todo `.cdad`. Una copia limpia de los archivos trackeados evita arrastrar el
workspace de evidencia local; lotes pequeños evitan acumular todos los
directorios `tmp_path` en una sola sesión. No se cambian producto ni tests,
se omiten asserts ni se borran temporales ajenos.

- Inventario exacto: `.cdad/evidence/recovery-failed-nodeids.txt`, 225 casos
  únicos (8 failed + 217 errors) de 23 módulos.
- `git diff 8b6ed56..HEAD -- skills scripts tests install.sh Makefile` no muestra
  cambios; por tanto, los 1624 éxitos anteriores pertenecen al mismo producto y
  tests. Las diferencias posteriores son documentación/estado.
- Repetir solamente esos 225 casos en lotes acotados sobre un `git archive HEAD`
  nuevo, con staging propio. No relanzar los 1624 casos ya verdes.
- Cada lote conserva selección, comando, stdout, stderr y rc en una ruta estable
  de `.cdad/evidence`. El agregado debe acreditar los 225 sin faltantes ni
  duplicados; cualquier fallo nuevo conserva el gate abierto.
- Los cinco skips originales permanecen declarados. La composición de evidencia
  no significa una segunda corrida monolítica verde: debe explicitar que usa
  éxitos previos + recuperación verificable del resto.

## Resultado verificado de la recuperación

Evidencia: `.cdad/evidence/recovery-010-000-Q8K9jo/`.
Fuente de la copia: `ec1fd6a5d41d3dbef45846f54522227541715286`.
El orquestador comprobó `results.json`, cada resumen de lote y `COMPLETE.json`:

- 23 lotes, todos rc=0; 225 casos pasaron.
- El conjunto de nodeids es idéntico al inventario de 225 casos, sin duplicados
  ni faltantes. Cada resumen de pytest coincide con la selección de su lote.
- No hay cambios de código, tests, instalador o Makefile entre la fuente de la
  corrida original y la recuperación; solo documentación/estado.
- Los 1624 éxitos anteriores más los 225 recuperados dan **1849 passed**; se
  conservan los **5 skipped** originales. Ningún caso fallido se oculta o excluye.

La evidencia cubre la suite completa por composición de ejecuciones equivalentes.
No es una corrida monolítica verde: la original conserva rc=1 y se explica su
recuperación por lotes. No requiere cambiar tests ni producto para obtener verde.
La aprobación del cierre y del Memory Bank sigue pendiente; este documento
acredita resultados, no se atribuye autoridad estratégica.
