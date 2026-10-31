# Registro de preparación — 010-003-documentary-pilot

Registro de la preparación de T3, anterior a T4 (GREEN) y a T5 (ensayo). Fija los
bytes, el commit y el resultado de la inspección, **sin reproducir las respuestas
de la clave**.

## Commit de preparación

| Campo | Valor |
|---|---|
| Commit | `cd2d57b32e43e138cd831a3a40b5dd8fa075a67a` |
| Autor | `cdad-test-writer` (rol de escritura de T3) |
| Mensaje | `test(010-003): corpus, clave, muestras y verificador del piloto (RED)` |
| Alcance | 10 archivos, 767 inserciones, **solo** bajo `tests/` |
| Fecha | 2026-10-31 |

El commit contiene corpus, inventario, candidato, muestras estructurales, clave y
verificador. El commit del producto de T4 deberá descender de él.

## Artefactos fijados

| Artefacto | Ruta | SHA-256 |
|---|---|---|
| Fuente `s1` | `tests/fixtures/010_003_documentary_pilot/sources/s1.md` | `9f8c3cb3c7da6de8e654ee83b492f11136125e2615eaae76e4d6518356b6daff` |
| Fuente `s2` | `tests/fixtures/010_003_documentary_pilot/sources/s2.md` | `2d7133724cae17218ab718784d53b3282cf6b3501ac838262a317fad44d70117` |
| Inventario | `tests/fixtures/010_003_documentary_pilot/sources/inventory.md` | `86ffe51cb8cb825502b97a2d87faefc713f9a4cab97d9b99292697abe6ab2fdf` |
| Candidato negativo | `tests/fixtures/010_003_documentary_pilot/challenge/negative.md` | `ff45d9e3613c74145f5a85e23cae5d8ffb5008362642dbc9124fc59b1c249e1e` |
| Muestra rota | `tests/fixtures/010_003_documentary_pilot/structural/broken.md` | `12b2697ca6f0188c6c77e3ad53593658721e9478757ad7aec0cdd962d5912e4c` |
| Muestra corregida | `tests/fixtures/010_003_documentary_pilot/structural/corrected.md` | `4ef7d8edaca7a8a5c78993457b869cbce859704ab0c44226bf61d325c82e7393` |
| Muestra sin referencias | `tests/fixtures/010_003_documentary_pilot/structural/no-references.md` | `89e325185e26ca3e190a75044da15785b6aa26c9e4d58860806baa48f2e196b7` |
| Muestra con fuente no inventariada | `tests/fixtures/010_003_documentary_pilot/structural/uninventoried.md` | `9b1ca18f9d410b23bd41fcf29c3294b55a66a58b89385fdf4721717b299a5538` |
| Clave de contraste | `tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md` | `91c277c1d7167db8a3df756a66c0e93166ac620ec95f9166e001a6a8921f7423` |
| Verificador | `tests/test_010_003_documentary_pilot.py` | `8e2a1878538838306543e2767d54993480cb4147f8f7b205415d9f7f48e35737` |

El inventario se identifica como `inventory-010-003-v1` y registra los SHA-256 de
`s1` y `s2`, que coinciden byte a byte con los archivos.

## Inspección de los tres defectos (sin reproducir las respuestas)

El orquestador inspeccionó el desafío y la clave antes de GREEN. El resultado se
declara por clase; la ubicación y la justificación concretas viven sólo en la
clave y en el contraste posterior.

| Clase de defecto comprometida | Resultado | Cómo se comprobó |
|---|---|---|
| Afirmación presentada como hecho sin respaldo en el corpus | **Presente y bien construida.** La afirmación existe en el candidato; el corpus examen completo no la respalda. | Lectura del candidato y búsqueda de los términos de la afirmación en `s1` y `s2`: sin coincidencias. La ausencia de respaldo no se presentó como falsedad universal. |
| Contradicción omitida | **Presente y bien construida.** Dos fragmentos de fuentes distintas sostienen posiciones incompatibles sobre el mismo punto; el candidato presenta una como consenso y omite la otra. | Lectura de ambos fragmentos: uno exige un visto bueno que el otro excluye expresamente. |
| Referencia existente que no sostiene lo afirmado | **Presente y bien construida.** El enlace resuelve estructuralmente a un ancla registrada, y ese fragmento trata otra materia. | Resolución del enlace contra el inventario y lectura del fragmento: el respaldo real está en otro fragmento de la misma fuente. |

Las tres clases son distinguibles entre sí: la primera no tiene referencia, la
tercera resuelve y no sostiene, y la segunda es una omisión de una posición
incompatible. Ninguna se construyó a partir del producto (que no existía) ni de
los ejemplos del Discovery.

## Inspección del verificador

| Comprobación | Resultado |
|---|---|
| El verificador no lee la clave | **Cumple.** No nombra `oracle/` ni `contrast-key` en ninguna línea; sus lecturas son inventario, fuentes, muestras estructurales, candidato y producto. |
| Los mensajes y valores de aserción no reproducen la clave | **Cumple.** Ningún mensaje, docstring o valor comparado contiene términos del contenido de la clave. |
| Comparación contra la clave | No existe en el verificador: pertenece al contraste del orquestador. |
| Dependencia de líneas o rewrap | **No.** El control resuelve identificadores y anclas; T8 compara el mismo veredicto bajo rewrap. |
| Muestras exigidas | Las cinco: rota, corregida, sin referencias, fuente no inventariada y candidato semántico estructuralmente aceptado. |
| Salida acotada | El comando focal declarado usa `--tb=no`; la corrida del RED muestra nombres y mensajes, no el cuerpo del test. |

## RED registrado

```
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
.....F..
1 failed, 7 passed
rc=1
```

El único fallo es la prueba del producto: `AssertionError` de la aserción de
existencia, no `FileNotFoundError` ni `ImportError`. Los otros siete pasan
porque su resultado esperado es aceptar o rechazar muestras ya construidas, tal
como declara el plan.

## Snapshots y copias durables

- **Snapshots de los bytes preparados:** el commit `cd2d57b3` es el snapshot; sus
  objetos de git son recuperables por hash sin depender de `.cdad/`.
- **Copias durables previstas:** `docs/specs/010-003-documentary-pilot/evidence/`
  recibirá los request y paquete validados de T5, la transcripción auditada, el
  informe original (`challenge-review.md`), el contraste
  (`challenge-contrast.md`) y los snapshots declarados por hash.
- **Lo que no se versiona:** `.cdad/` está ignorado por git; su contenido no se
  usa como evidencia durable.

## Estado

Preparación fijada antes de T4. El registro se versiona **antes del despacho de
T5**, junto con el commit de preparación que cita.
