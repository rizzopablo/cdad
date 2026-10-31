# Relevamiento del proceso de recepción y aprobación de solicitudes (documento sintético)

**Documento sintético.** Relevamiento ficticio del piloto documental 010-003. El corpus es sintético y este producto también lo es: no describe personas, sistemas ni organizaciones reales, y no incorpora fuentes externas ni datos de clientes.

**Corrección del candidato negativo.** Este documento corrige el candidato `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`, declarado no conforme: conserva su estructura por secciones y sus afirmaciones respaldadas, elimina la afirmación presentada como hecho sin respaldo en el corpus, registra la contradicción entre fuentes que el candidato omitía y corrige la referencia que existía pero no sostenía lo afirmado.

**Inventario.** Las citas resuelven contra el inventario `inventory-010-003-v1` (`tests/fixtures/010_003_documentary_pilot/sources/inventory.md`). La versión de cada fuente se hereda de ese inventario; su identificación no cuenta como respaldo factual.

## Recepción y registro

Toda solicitud se registra el día de su recepción en el libro de entradas, con un número correlativo que se conserva en el expediente. El registro consigna la fecha, el nombre declarado por la persona solicitante y la vía por la que llegó la solicitud ([Registro de la solicitud](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f01)).

La vía de recepción, presencial o electrónica, no altera la numeración correlativa ni el orden de registro de las solicitudes ([Vía de recepción](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f02)).

Cuando la solicitud llega incompleta se observa y se pide completarla ([Recepción incompleta](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f05)).

## Aprobación de casos límite

Las fuentes no coinciden en un criterio único; se conservan ambas posiciones porque no hay decisión acreditada que resuelva el conflicto:

- Posición de la fuente `s1`: los casos límite son las solicitudes cuyo monto declarado es exactamente igual al umbral fijado en el anexo de montos, y los aprueba el Jefe de Registro con el visto bueno previo de la Unidad de Cumplimiento ([Casos límite según Registro](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f02)).
- Posición de la fuente `s2`: los casos límite los aprueba únicamente la Dirección de Operaciones, y no se requiere visto bueno de la Unidad de Cumplimiento para resolverlos ([Casos límite según Operaciones](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f03)).

## Plazo de respuesta

La fuente `s1` fija un plazo máximo de quince días hábiles para responder una solicitud completa, contados desde el registro de la solicitud ([Plazo de respuesta](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f03)); ese registro se realiza el día de la recepción ([Registro de la solicitud](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f01)). La fuente `s2` fija un plazo máximo de quince días hábiles contados desde la recepción completa de la solicitud ([Plazo según Operaciones](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f04)). La fuente `s1` indica además que, cuando la solicitud llega incompleta, el plazo de respuesta corre desde la recepción completa y no desde la primera presentación ([Recepción incompleta](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f05)). Los inicios difieren: `s1-f03` cuenta desde el registro —que `s1-f01` sitúa el día de la recepción—, mientras que `s1-f05` y `s2-f04` cuentan desde la recepción completa. El corpus no aclara si una solicitud completada después se registra de nuevo, por lo que el inicio exacto del plazo en ese caso queda sin dirimir; este relevamiento no elige una regla ni propone conciliación (ver el pendiente P-02 de la sección Pendientes).

## Archivo

Las solicitudes resueltas se archivan en el legajo anual durante cinco años, y el legajo se organiza por número correlativo de recepción ([Archivo anual](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f04)). La fuente `s2` indica que el legajo anual se archiva por número correlativo y fecha de resolución, y se conserva durante cinco años ([Archivo según Operaciones](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f05)). La diferencia de organización del legajo entre ambas fuentes —número correlativo de recepción frente a número correlativo y fecha de resolución— queda sin dirimir.

## Divergencia registrada

Existe una contradicción entre las dos fuentes autorizadas sobre quién aprueba los casos límite y si se requiere el visto bueno de la Unidad de Cumplimiento: la fuente `s1` atribuye la aprobación al Jefe de Registro con visto bueno previo de la Unidad de Cumplimiento ([Casos límite según Registro](../../../../tests/fixtures/010_003_documentary_pilot/sources/s1.md#s1-f02)), mientras que la fuente `s2` la atribuye únicamente a la Dirección de Operaciones sin ese visto bueno ([Casos límite según Operaciones](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f03)). Este relevamiento no inventa consenso ni elige una posición por conveniencia: conserva ambas con sus localizadores.

## Pendientes

- **P-01 (no bloqueante).** Falta la decisión acreditada que resuelva quién aprueba los casos límite y si se requiere el visto bueno de la Unidad de Cumplimiento (divergencia de la sección Divergencia registrada, relativa a la sección Aprobación de casos límite). Información faltante: acto o criterio que dirima entre la posición de la fuente `s1` y la de la fuente `s2`. Contexto: la fuente `s2` indica que su procedimiento se aplica junto con el del Área de Registro y no lo reemplaza ([Nota de procedimiento](../../../../tests/fixtures/010_003_documentary_pilot/sources/s2.md#s2-f01)), sin que ello fije prelación alguna entre ambas posiciones. Condición de cierre: incorporar la decisión acreditada con su localizador y reformular la sección Aprobación de casos límite en consecuencia. Responsable: designación pendiente. Clasificación: no bloqueante, porque el contrato del piloto promete documentar la divergencia en lugar de resolverla.

- **P-02 (no bloqueante).** Falta la información que permita fijar el inicio exacto del plazo de respuesta cuando la solicitud llega incompleta y se completa después (sección Plazo de respuesta). Información faltante: si una solicitud completada después se registra de nuevo, dado que `s1-f03` cuenta desde el registro —que `s1-f01` sitúa el día de la recepción— mientras que `s1-f05` y `s2-f04` cuentan desde la recepción completa, sin que ninguna fuente aclare ese registro posterior. Condición de cierre: incorporar la regla o decisión acreditada sobre el registro de las solicitudes completadas, con su localizador, y precisar en consecuencia el inicio aplicable en la sección Plazo de respuesta. Responsable: designación pendiente. Clasificación: no bloqueante, porque el contrato del piloto promete documentar las divergencias existentes en lugar de resolverlas.
