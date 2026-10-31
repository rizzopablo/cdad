# Clave de contraste — 010-003-documentary-pilot

**Artefacto protegido.** Esta clave no es insumo del verificador ni de T4. La compara el orquestador en el contraste posterior y no se reproduce en mensajes ni en valores de aserción del control.

**Candidato:** `tests/fixtures/010_003_documentary_pilot/challenge/negative.md` (sintético y declarado no conforme).
**Corpus examinado:** `s1` (fragmentos `s1-f01`…`s1-f05`) y `s2` (fragmentos `s2-f01`…`s2-f05`), registrados en `sources/inventory.md` como `inventory-010-003-v1`.

## Defecto 1 — Afirmación presentada como hecho sin respaldo en el corpus

- **Ubicación:** sección «Revisión del proceso»; oración: «El proceso se revisa cada año mediante una encuesta interna de satisfacción dirigida a las áreas que intervienen.»
- **Justificación:** ninguna fuente del corpus menciona revisión anual, encuestas ni satisfacción. El corpus examinado completo no contiene respaldo. La ausencia de respaldo no convierte la afirmación en universalmente falsa: el defecto es presentarla como hecho.

## Defecto 2 — Contradicción omitida

- **Ubicación:** sección «Aprobación de casos límite»; oración: «Las fuentes coinciden en un criterio único: los casos límite los aprueba la Dirección de Operaciones ([Criterio de aprobación](../sources/s2.md#s2-f03)).»
- **Justificación:** `s2-f03` sostiene que los casos límite los aprueba únicamente la Dirección de Operaciones y que no se requiere visto bueno de Cumplimiento. `s1-f02` sostiene que los aprueba el Jefe de Registro con visto bueno previo de la Unidad de Cumplimiento. Las posiciones son incompatibles; el candidato las presenta como consenso y omite `s1-f02`.

## Defecto 3 — Referencia existente que no sostiene lo afirmado

- **Ubicación:** sección «Archivo»; oración: «El archivo se organiza por número correlativo de recepción ([Plazo de respuesta](../sources/s1.md#s1-f03)).»
- **Justificación:** el enlace resuelve estructuralmente al archivo `s1` y al ancla `s1-f03`, pero `s1-f03` trata el plazo máximo de respuesta y no dice nada del archivo. La afirmación sobre el archivo se respalda en `s1-f04`, no en `s1-f03`.

## Nota de alcance

La clave enumera tres defectos, uno por clase comprometida. No agota las diferencias posibles entre el candidato y el corpus ni convierte al candidato en la única corrección admisible: el contraste posterior compara los hallazgos del informe independiente contra estas tres entradas y registra omisiones expresas.
