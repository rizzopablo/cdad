# Informe de revisión T5: candidato negativo `challenge/negative.md`

**Conclusión: NO CONFORME.** Las tres clases de defecto de PC-02 están presentes: F-1, F-2 y F-3. No se modificó ningún archivo.

- **Ruta C:** `render --request` coincide byte a byte con `PACKET.md` (`cmp` sin diferencias). El SHA-256 del contrato coincide con `f2dce9e0…`. El contexto de ejecución es v2.
- **Inventario:** los hashes de `s1` y `s2` coinciden con `inventory-010-003-v1`.
- **Enlaces:** los cinco enlaces resuelven a fuentes inventariadas y a anclas existentes. Eso no prueba respaldo.

## Contraste de cada afirmación

| # | Ubicación | Afirmación | Resultado |
|---|---|---|---|
| A1 | Título y líneas 3 y 5 | Documento sintético, NO CONFORME | Metadato, no es un hecho del proceso. Coherente con PC-01 y PC-02 |
| A2 | «Recepción y registro», línea 9 | Registro el día de recepción, en el libro de entradas, con correlativo conservado en el expediente | **Respaldada** por `s1#s1-f01`, casi literal |
| A3 | «Aprobación de casos límite», línea 13, primera parte | «Las fuentes coinciden en un criterio único» | **No respaldada y contradicha** por el corpus (F-2) |
| A4 | Línea 13, segunda parte | Los casos límite los aprueba la Dirección de Operaciones | **Respaldada solo como posición de `s2`** (`s2#s2-f03`). No es un hecho común del corpus |
| A5 | «Plazo de respuesta», línea 17 | Plazo máximo de quince días hábiles | **Respaldada** por `s1#s1-f03`. Ver O-2 |
| A6 | «Archivo», línea 21 | El archivo se organiza por número correlativo de recepción | **La referencia citada no sostiene lo afirmado** (F-3) |
| A7 | «Revisión del proceso», línea 25 | Revisión anual mediante encuesta interna de satisfacción a las áreas | **No respaldada** en el corpus examinado (F-1) |

## Hallazgos

### F-1: afirmación presentada como hecho sin respaldo (clase PC-02/1)
- **Ubicación:** sección «Revisión del proceso», única oración (línea 25). No tiene ninguna referencia.
- **Fundamento:** leí completos `s1` (f01–f05) y `s2` (f01–f05). Ningún fragmento trata de una revisión periódica del proceso, una encuesta o la satisfacción. Lo único «anual» del corpus es el legajo (`s1-f04`, `s2-f05`), que no guarda relación con esto.
- **Límite:** esto delimita el corpus inventariado y no prueba que la afirmación sea falsa. Solo digo que estas dos fuentes no la acreditan. Tampoco está marcada como propuesta ni como pendiente (`documentary-contracts.md` §1).
- **Veredicto:** `BLOCKING`, severidad Required, bucket `m`.
- **Consecuencia:** el lector toma por hecho observado una práctica sin fuente.
- **Condición de cierre verificable:** ninguna afirmación de ese contenido queda presentada como hecho sin un fragmento inventariado que la sostenga.

### F-2: contradicción omitida (clase PC-02/2)
- **Ubicación:** sección «Aprobación de casos límite», oración única (línea 13). La omisión está en «Las fuentes coinciden en un criterio único» y en citar solo `s2-f03`.
- **Posición 1, `s1#s1-f02`:** «Los casos límite los aprueba el Jefe de Registro con el visto bueno previo de la Unidad de Cumplimiento.»
- **Posición 2, `s2#s2-f03`:** «Los casos límite los aprueba únicamente la Dirección de Operaciones. No se requiere visto bueno de la Unidad de Cumplimiento para resolverlos.»
- **Incompatibilidad:** difieren en dos puntos, quién aprueba y si hace falta el visto bueno. «Únicamente» excluye al Jefe de Registro.
- **Por qué no se concilia:** el corpus no contiene ninguna decisión acreditada ni regla de precedencia. `s2-f01` dice que la nota se aplica junto con el procedimiento del Área de Registro «y no lo reemplaza», lo que no resuelve el conflicto a favor de `s2`.
- **Agravante:** el candidato no solo calla la divergencia, sino que inventa un consenso, y `s2-f03` tampoco sostiene «coinciden».
- **Veredicto:** `BLOCKING`, severidad Required, bucket `m`.
- **Consecuencia:** se elimina una posición sin decisión (`documentary-contracts.md` §1, Contradiction) y se presenta como unívoco un punto que la promesa del piloto deja abierto.
- **Condición de cierre verificable:** ambas posiciones quedan visibles con su propio localizador y sin afirmación de consenso.

### F-3: referencia que resuelve pero no sostiene lo afirmado (clase PC-02/3)
- **Ubicación:** sección «Archivo», oración única (línea 21), enlace `../sources/s1.md#s1-f03`, rotulado «Plazo de respuesta».
- **Fragmento citado:** `s1-f03` dice «El plazo máximo para responder una solicitud completa es de quince días hábiles contados desde el registro de la solicitud.»
- **Por qué no alcanza:** habla solo del plazo. No menciona el archivo, el legajo ni su organización. El enlace pasa un control estructural y aun así no da respaldo. El propio rótulo delata el desajuste con la afirmación.
- **Límite:** esto no significa que el contenido carezca de apoyo en todo el corpus. `s1-f04` trata ese tema, pero el candidato no lo cita. El defecto es la atribución (`documentary-contracts.md` §1, Evidence, y §2). Ver O-1 sobre `s2-f05`.
- **Veredicto:** `BLOCKING`, severidad Required, bucket `m`.
- **Consecuencia:** quien siga la cita no encuentra lo afirmado, de modo que la trazabilidad es solo aparente.
- **Condición de cierre verificable:** el localizador de la afirmación apunta a un fragmento que la sostiene.

### Otras observaciones

- **O-1, `OPTIONAL`, bucket `m` (línea 21):** `s1-f04` organiza el legajo «por número correlativo de recepción», y `s2-f05` «por número correlativo y fecha de resolución». Es una diferencia no mencionada en el candidato. Ver abstención AB-1.
- **O-2, `OPTIONAL`, bucket `m` (línea 17):** el candidato omite desde cuándo corre el plazo.
  - `s1-f03` dice «desde el registro» de una solicitud completa.
  - `s1-f05` y `s2-f04` dicen «desde la recepción completa».
  - No lo trato como contradicción: `s1-f01` fija el registro el día de recepción, y `s1-f05` cubre la solicitud incompleta. Para una solicitud completa ambos puntos coinciden.
  - Lo afirmado es cierto, pero incompleto.
- **O-3, `BLOCKING` frente a la convención, bucket `m` (documento completo):** el candidato no identifica el inventario por ruta e identificador, como exigen `inventory.md` (línea 31) y spec §2.4. De ahí heredan las citas su versión. No pertenece a las tres clases de PC-02.

## Alcance examinado

**Leído completo, en orden:**
- `REQUEST.json`, `PACKET.md` y `execution.json`
- `spec.md`
- `documentary-contracts.md`
- `verdict-tuple.md`
- `inventory.md`, `s1.md`, `s2.md` y `negative.md`

**Leído parcialmente:** de `stage-4-review.md` solo los encabezados y las menciones a la calibración, mediante `grep`. La calibración aplicada viene de mi rol y de `verdict-tuple.md`.

**No leído:** `design-principles.md`, `product/`, `oracle/`, `structural/`, `discovery.md`, el plan, los registros de preparación, los informes GREEN o de contraste, y el verificador. No ejecuté ninguna operación git.

**Para la auditoría de lecturas:**
- Ejecuté `skills/cdad-cycle/scripts/cdad_packet.py render --help` y `render --request …`, además de un intento fallido con la ruta posicional. Es la validación que exige la ruta C. El script no se leyó, pero está fuera de `read_scope`.
- `find . -name cdad_packet.py` listó diez rutas de copias bajo `.cdad/evidence/`, truncado por `head`. Solo vi nombres, sin contenido.
- El contexto automático de la sesión mostró los asuntos de los últimos commits y el nombre `tdd-t4-green.md`, sin contenido.

**Comandos adicionales:** `cat`, `ls`, `sha256sum` y `cmp`. Modified files: ninguno. Commit: ninguno.

## Abstenciones

- **AB-1, `ABSTAIN` sobre O-1:** el corpus no permite decidir si `s1-f04` y `s2-f05` son incompatibles o complementarios, porque ambos usan el correlativo.
- **AB-2, `ABSTAIN` sobre la verdad externa:** no juzgo si alguna posición es correcta ni cuál debe prevalecer en F-2, ni si la encuesta de F-1 existe fuera del corpus.
- **AB-3, `ABSTAIN` sobre la familia de modelo del productor:** no está declarada. El bucket `m` suma cita exacta y contrato en contexto, y no suma el punto de diff porque está excluido.
- **AB-4, `ABSTAIN` sobre la completitud:** el candidato pudo omitir contenido del corpus (`s1-f05`, `s2-f02`, conservación por cinco años). El contrato no fija una lista de cobertura para él, así que no lo evalúo como defecto.

## Avisos al orquestador sobre la acreditación

Quedan fuera del objeto revisado, pero afectan a la acreditación, y no los resolví:

1. **Faltan los commits en el request.** `REQUEST.json` no cita los commits de preparación y de registro que exigen spec §2.3 (línea 85) y la tabla de evidencia de §5. `contract.commit` es `null`. Para el gate de integración, esa fijación no está acreditada por este request.
2. **Estado del contrato inconsistente.** El paquete declara `approved-feature-spec`, pero `spec.md` dice «pendiente de revisión y aprobación» (línea 4) y «Status: Pending approval» (línea 295). No detuve la revisión porque el objeto y los hashes son inequívocos, pero la aprobación no consta en el propio archivo.
