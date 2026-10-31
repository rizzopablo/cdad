# Inventario del corpus — inventory-010-003-v1

**Identificador del inventario:** `inventory-010-003-v1`.
**Ruta de este inventario:** `tests/fixtures/010_003_documentary_pilot/sources/inventory.md`.
**Raíz del corpus:** `tests/fixtures/010_003_documentary_pilot/`. Las rutas de la tabla son relativas a esa raíz.
**Origen:** corpus sintético. Los documentos `s1` y `s2` son ficticios, escritos para el piloto documental 010-003; describen un proceso inventado de recepción y aprobación de solicitudes y no incorporan fuentes externas, sistemas reales ni datos de clientes.

## Fuentes autorizadas

| Identificador | Ruta relativa al corpus | SHA-256 |
|---|---|---|
| s1 | sources/s1.md | 9f8c3cb3c7da6de8e654ee83b492f11136125e2615eaae76e4d6518356b6daff |
| s2 | sources/s2.md | 2d7133724cae17218ab718784d53b3282cf6b3501ac838262a317fad44d70117 |

## Correspondencia entre identificadores y archivos

`s1` corresponde a `sources/s1.md` y `s2` corresponde a `sources/s2.md`. No hay otras fuentes autorizadas: un identificador que no figure en la tabla no es una fuente del corpus, y un archivo bajo `sources/` que no figure en la tabla no está inventariado.

## Convención de anclas

- Cada fragmento citable lleva un ancla HTML explícita y única dentro de su fuente.
- Forma exacta del ancla: `<a id="s1-f01"></a>`, con el identificador de la fuente (`s1` o `s2`) y el número de fragmento en dos dígitos.
- El ancla ocupa sola su línea e inmediatamente precede al fragmento que identifica.
- No se usan anclas derivadas automáticamente del texto de un encabezado.

## Convención de enlaces relativos

- Una cita es un enlace Markdown `[texto](ruta-relativa#ancla)`.
- La ruta se resuelve contra el directorio del documento examinado y debe normalizar a una de las rutas de la tabla, resueltas contra la raíz del corpus.
- El fragmento debe ser un ancla registrada de esa fuente.
- El documento examinado identifica este inventario por su ruta y su identificador; esa identificación no cuenta como cita ni como respaldo factual.
- Una referencia que no resuelva a una fuente de la tabla y a un ancla registrada se rechaza.

## Versión de las fuentes

La versión de cada fuente se hereda de este inventario: los bytes registrados son los de la tabla y su SHA-256 permite verificarlos. Este inventario es un registro, no una tercera fuente de hechos.
