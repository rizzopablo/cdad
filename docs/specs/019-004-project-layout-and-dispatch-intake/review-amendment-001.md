# Revisión de la enmienda 001

**Resultado: no recomiendo sustituir todavía el texto de §4.2.** La excepción para `continuity/` y `guards/` responde al conflicto identificado en la revisión anterior, pero la redacción propuesta introduce una obligación más amplia que su lista de detección y que las consecuencias declaradas.

## Hallazgo

### La regla «todo otro registro bajo `.cdad/`» contradice la detección delimitada

**Severidad: Required · Verdict: BLOCKING · Bucket: h**

La propuesta enumera archivos bajo `.cdad/packets/` y contenido bajo `.cdad/executions/<id>/`, salvo los dos almacenes exceptuados. Sin embargo, concluye: **“Every other record under `.cdad/` remains evidence.”**

Esa última frase también abarca registros situados fuera de esas dos rutas. El árbol real contiene, por ejemplo, `.cdad/execution.json`, `.cdad/inbox/` y `.cdad/publication/`. La propuesta no aclara si cualquiera de ellos, por sí solo, debe producir ambigüedad ni cómo se detectaría respetando la regla conservada de §4.2: **“Detection uses fixed locations, not recursive discovery.”** Además, sus consecuencias mencionan registros de dispatch y receipt sin identificar sus ubicaciones ni vincularlos inequívocamente con las rutas enumeradas.

**Consecuencia:** implementaciones y pruebas pueden discrepar sobre si un proyecto con registros operativos fuera de `packets/` y `executions/<id>/` es nuevo o ambiguo. En el caso incorrecto, bootstrap podría proponer `cdad/` sin aclaración; en el contrario, podría bloquearse por archivos que no se pretendía considerar evidencia. Eso impide verificar de forma determinista PC-04.

**Cierre verificable:** sustituir la frase general por una enumeración cerrada de rutas y condiciones —incluidos los lugares concretos de dispatch y receipt si deben contar—, o definir expresamente una regla acotada para el resto de `.cdad/` compatible con detección por ubicaciones fijas. Ajustar las consecuencias y añadir fixtures positivos y negativos para cada ubicación decidida, además de los controles de `continuity/` y `guards/`.

## Alcance y evidencia

- La distinción de los dos almacenes **es coherente en intención** con permitir bookkeeping previo a la decisión del layout; su excepción no contradice por sí sola PC-04 si se incorpora expresamente al contrato.
- No doy por acreditada la afirmación de que los fixtures afectados permanecen válidos: no ejecuté las pruebas ni verifiqué exhaustivamente sus precondiciones.
- Validé el `REQUEST.json` y el `PACKET.md` nombrados mediante `cdad_packet.py validate-request` y `validate-packet`; ambos terminaron con código 0 y sin salida.
- Consulté la enmienda, la especificación, la revisión anterior, el resolver y las ubicaciones visibles bajo `.cdad/`.
- No modifiqué archivos ni creé commits. `docs/.cdad-state.json` ya aparecía modificado en `git status`.
- No ejecuté la suite completa ni pruebas focales en esta revisión.

## Abstentions

- No acredito exhaustivamente la ubicación y semántica de todos los tipos de registro de dispatch y receipt.
- No acredito la cobertura integral de Promises A–E ni PC-01–PC-16 más allá de la coherencia de esta enmienda con el texto examinado.
- No verifiqué la reconciliación completa de decisiones vigentes con `docs/adr/`.