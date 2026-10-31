# 010-003 — Piloto documental con evidencia independiente

**Versión:** 5.  
**Estado:** pendiente de revisión y aprobación.  
**Épica:** `epic-010-documentary-specialization`.  
**Dependencias:** 010-001 y 010-002.  
**Base de decisiones:** D-1–D-6 de `discovery-decisions-2026-10-31.md`, resoluciones de `plan-review-resolutions-2026-10-31.md`, resoluciones de `plan-review-2-resolutions-2026-10-31.md`, resoluciones de `plan-review-3-resolutions-2026-10-31.md` y resoluciones de `plan-review-4-resolutions-2026-10-31.md`.

## 1. Descripción funcional

### Recorrido del usuario

- **Actor:** autoridad que acepta el piloto, asistida por el orquestador.
- **Objetivo:** obtener un relevamiento documental trazable y distinguir qué acredita un control automático, qué encontró una revisión independiente y qué se acepta funcionalmente.
- **Punto de partida legítimo:** contratos documentales y procedimiento de encargo existentes; todavía no hay evidencia del piloto.
- **Primer resultado útil:** un documento corregido sobre un proceso ficticio, acompañado por evidencia recuperable de detección estructural y semántica.

El piloto documenta la recepción y aprobación de solicitudes de un proceso exclusivamente ficticio. Su promesa es presentar lo respaldado y las divergencias existentes, **no resolverlas ni definir un proceso operativo inequívoco**.

Se prepara un desafío con defectos conocidos, separado del producto corregido. Una sesión independiente revisa ese desafío sin recibir la clave de contraste ni el producto corregido. La aceptación requiere tanto los resultados comprometidos de ese ensayo como la revisión del documento final.

El producto es una corrección del candidato negativo: este es un insumo obligatorio de GREEN. La preparación precede a GREEN; el ensayo del desafío sucede después de GREEN y antes de revisar el producto, manteniendo la corrección fuera del alcance del primer reviewer.

## 2. Alcance y decisiones

### 2.1. Aplicación de las normas existentes

Se aplican, sin reproducir ni modificar su definición:

- `skills/cdad-cycle/references/documentary-contracts.md`.
- Procedimiento documental de `skills/cdad-cycle/references/handoff-prompts.md`, sección «Documentary engagement — operating procedure».

010-003 ejecuta el piloto; no vuelve a implementar los contratos de 010-001 ni la integración de 010-002.

El encargo del ensayo incluye `skills/cdad-cycle/references/documentary-contracts.md` como lectura e insumo porque el paquete manda leer esa norma. Las lecturas normativas de método que no revelan respuestas se registran sin invalidar, según la promesa C y la resolución O-10 de la tercera vuelta. Citar aquí el procedimiento no autoriza al reviewer del desafío a abrirlo ni a recorrer otras referencias.

### 2.2. Alternativas relevantes

| Decisión | Alternativa descartada | Criterio |
|---|---|---|
| Control estructural específico para las citas del piloto | Validador documental universal | Basta comprobar localización y versión sin interpretar formatos arbitrarios ni decidir respaldo semántico. |
| Desafío sembrado y declarado | Esperar errores espontáneos o presentar una entrega defectuosa como conforme | Permite evaluar detección sobre defectos conocidos sin falsear el origen de los errores. |
| Clave fijada antes del ensayo y contraste posterior | Reconstruir el resultado esperado desde el informe | Evita una acreditación circular. |
| Localizadores por identificadores internos estables | Números de línea o ventanas de texto | Permite recuperar fragmentos sin depender del rewrap. |
| Revisión del desafío y del producto en encargos separados | Mostrar ambos antes del primer informe | Conserva el valor del ensayo independiente. |
| Documentar ambas posiciones incompatibles | Elegir una sin decisión acreditada | Corresponde a la promesa aprobada de D-2. |
| Mantener preparación → GREEN → ensayo → revisión del producto | Adelantar el ensayo a GREEN | La resolución B-2 registra que el ciclo exige GREEN antes de un encargo de review. Se conserva el orden y se excluyen contractualmente y por alcance el producto y los informes reveladores. |
| Hitos T1–T8 con encargos separados dentro de ellos | Convertir cada hito en un único despacho o añadir campos y mecanismos | La resolución O-1 acepta esta organización; cada encargo conserva un rol y una subfase. |
| Declarar específicamente el objeto de T5 en `objective` e `invariants` | Interpretar «el diff completo» como autorización de lectura o modificar los bloques de instrucciones | La autoridad resolvió BN-1: la declaración específica del objeto prevalece sobre la frase genérica del rol, conserva el alcance y no crea mecanismos ni modifica bloques. |
| Commit de preparación antes de GREEN y registro versionado antes del ensayo | Fijar la preparación cuando el producto ya existe o conservar solo una declaración no versionada | La resolución NB-1 hace recuperables los bytes previos y la inspección sin reconstruirlos desde el resultado. |
| Ejecutar el verificador sin leerlo en T4 | Ampliar la lectura a `tests/`, mover el verificador o cambiar la política | BN-2 adopta la vía 1: la ruta exacta no es declarable sin `test_files` y la raíz `tests/` incluye la clave. Ejecutarlo conserva rutas y política sin abrir ese alcance. |
| Acotar la salida focal con `--tb=no` e inspeccionar el verificador antes de GREEN | Permitir tracebacks con su cuerpo o confiar solo en excluir el archivo como lectura | BN-3 conserva el fundamento de BN-2: se muestran nombres de casos, mensajes y valores de aserción, no el cuerpo; T3 comprueba que el verificador no lea ni reproduzca la clave. `pytest` no es un sandbox. |
| Distinguir lecturas reveladoras de referencias de método | Invalidar por cualquier lectura normativa no listada inicialmente | O-10 adopta un criterio único: invalida lo que revela respuestas, no lo que enseña a revisar; toda lectura observada se registra y las no clasificadas se fundan individualmente. |

### 2.3. Organización propuesta de archivos

Las siguientes rutas son **artefactos por crear**, no interfaces existentes:

| Función | Ruta |
|---|---|
| Fuentes ficticias | `tests/fixtures/010_003_documentary_pilot/sources/` |
| Inventario cerrado | `tests/fixtures/010_003_documentary_pilot/sources/inventory.md` |
| Candidato negativo semántico | `tests/fixtures/010_003_documentary_pilot/challenge/negative.md` |
| Muestras del control estructural | `tests/fixtures/010_003_documentary_pilot/structural/` |
| Clave de contraste protegida | `tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md` |
| Verificador y pruebas del piloto | `tests/test_010_003_documentary_pilot.py` |
| Producto documental editable | `docs/specs/010-003-documentary-pilot/product/relevamiento.md` |
| Registro de preparación | `docs/specs/010-003-documentary-pilot/preparation-record.md` |
| Copias durables de evidencia | `docs/specs/010-003-documentary-pilot/evidence/` |
| Informes y registros materializados por el orquestador | `docs/specs/010-003-documentary-pilot/` |

El test-writer prepara fuentes, desafío, muestras y clave desde el contrato aprobado, antes de leer cualquier producto del implementer. No reutiliza como respuestas los ejemplos ilustrativos de `discovery.md`. El implementer escribe únicamente en `product/`.

La clave es un insumo de aceptación protegido, no una fuente del relevamiento. Su exclusión del ensayo es contractual y de alcance; no se presenta como aislamiento técnico infalible.

**Antes de T4** debe existir un commit identificado de preparación que contenga corpus, inventario, candidato negativo, muestras estructurales, clave y **verificador**, incluido `tests/test_010_003_documentary_pilot.py`. El orquestador inspecciona antes de GREEN la construcción de los tres defectos y fija los bytes preparados. El request de T4 cita ese commit y el commit del producto desciende de él.

El orquestador materializa `preparation-record.md` con:

- Identificador del commit de preparación.
- Ruta y SHA-256 de cada artefacto preparado y del verificador fijado.
- Resultado de la inspección de cada una de las tres clases de defecto, sin reproducir las respuestas concretas, y comprobación previa a GREEN de que el verificador no lee `oracle/` y sus mensajes y valores de aserción no reproducen contenido de la clave. Una comparación contra la clave pertenece al contraste del orquestador, no al verificador.
- Ubicación de los snapshots recuperables y de las copias durables previstas.

El registro cita el commit de los artefactos; no exige incluir en ese mismo commit un registro que contenga su propio identificador. `preparation-record.md` se versiona mediante un commit bajo el directorio de la feature **antes del despacho de T5**. El request de T5 cita tanto el commit de preparación como el commit del registro.

`challenge-review.md` y `challenge-contrast.md` se versionan después de su producción en un commit descendiente del de preparación. Las fechas de git no prueban el orden por sí solas: la fijación comprobable descansa en los hashes de los artefactos, la inspección previa y los registros y relaciones de commits conservados.

`.cdad/` está ignorado por git y no se conserva por la vía versionada. Lo que deba perdurar se copia bajo la feature: requests y paquetes validados, evidencia recuperable del despacho y sesión, transcripción usada en la auditoría de lecturas, informes originales y snapshots declarados por hash. El registro de preparación y el índice de cierre identifican sus rutas y hashes. Las copias reveladoras tampoco forman parte del alcance del reviewer del desafío.

### 2.4. Corpus y localizadores

El corpus contendrá dos documentos Markdown ficticios, con posiciones incompatibles sobre una decisión del proceso y fragmentos suficientes para construir el desafío. No incorpora fuentes externas, sistemas reales ni datos de clientes. El inventario es un registro adicional, no una tercera fuente de hechos.

Antes del ensayo se fija `tests/fixtures/010_003_documentary_pilot/sources/inventory.md`, identificado como `inventory-010-003-v1`, con:

- Identidad y ruta de cada fuente autorizada.
- Versión o snapshot recuperable y SHA-256 de sus bytes.
- Correspondencia entre identificadores usados y archivos examinados.
- Convención de anclas y correspondencia de los fragmentos citables.

La convención propuesta para este piloto es:

- Identificadores de fuente `s1` y `s2`.
- Anclas HTML explícitas y únicas dentro de cada fuente, con forma `<a id="s1-f01"></a>`, cambiando el identificador de fuente y el número de fragmento según corresponda.
- Enlaces Markdown relativos desde el documento examinado hasta el archivo inventariado, con el identificador explícito como fragmento.
- Identificación del inventario por ruta e identificador en el documento; la versión de las fuentes se hereda de ese inventario.

No se usan anclas derivadas automáticamente del texto de un encabezado. T3 entrega a T4 el inventario y esta convención como interfaz de citación ya fijada.

El control comprueba que las referencias examinadas resuelven a esas fuentes y fragmentos. Rechaza un producto con **cero referencias a fuentes**, así como toda referencia a una fuente no inventariada. Identificar el inventario no cuenta como respaldo factual.

**No determina automáticamente qué frases son factuales ni si el fragmento citado sostiene una afirmación.** Esa suficiencia corresponde a revisión semántica.

No se introduce un esquema de transporte, tipo de artefacto ni formato de resultado nuevo.

## 3. Contrato

### Promesa A — El ensayo tiene una base recuperable y un resultado esperado no reconstruido

- **PC-01.** El inventario identifica todas las fuentes autorizadas y permite recuperar exactamente las versiones utilizadas. El corpus y los candidatos están declarados como sintéticos.
- **PC-02.** Existe un candidato negativo, explícitamente no conforme, con los tres defectos comprometidos: afirmación sin respaldo en el corpus, contradicción omitida y referencia existente que no sostiene lo afirmado.
- **PC-03.** Antes del ensayo queda fijada una clave que identifica, para cada defecto, su ubicación en el candidato y la justificación contra el corpus. La clave y los snapshots no se reescriben para hacerlos coincidir con el informe recibido.

**Verificación:** inspección independiente del desafío y la clave por el orquestador antes del despacho; hashes y snapshots recuperables. La mera presencia de tres etiquetas no demuestra que los defectos estén bien construidos.

La anterioridad se acredita según §2.3: commit de preparación con el verificador antes de T4, citado por su request y antecesor del commit del producto; inspección previa, registro versionado antes del despacho de T5 y request de T5 que identifica ambos commits de preparación y registro. Las fechas de git no bastan como prueba del orden.

### Promesa B — El control detecta el defecto estructural y muestra expresamente su límite

- **PC-04.** Al comprobar una muestra con un fragmento citado inexistente, el control rechaza esa muestra y ofrece un diagnóstico que identifica documento examinado, referencia problemática y causa.
- **PC-05.** Al corregir ese localizador, manteniendo lo demás equivalente, el control acepta la muestra estructural corregida.
- **PC-06.** El mismo control acepta una tercera muestra: el candidato negativo semántico, cuyas referencias son estructuralmente resolubles aunque conserva los tres defectos de PC-02.

**Verificación:** ejecución efectiva del control sobre las tres muestras. El test afirma sus resultados y diagnósticos; no busca la palabra `FAIL` en un informe.

La muestra estructural corregida no es el producto funcional corregido ni una clave semántica alternativa. La comprobación del producto incluye los rechazos por cero referencias y fuente no inventariada de §2.4; no se acepta un verde vacío.

### Promesa C — La detección semántica se acredita mediante una sesión real independiente

- **PC-07.** Una sesión de reviewer independiente del productor recibe el contrato, el candidato negativo y el corpus inventariado. No recibe la clave, el producto corregido ni informes que revelen las respuestas antes de cerrar su primer informe.
- **PC-08.** Ese primer informe identifica y fundamenta los tres defectos:
  - Para la afirmación sin respaldo: localiza la afirmación y delimita el corpus examinado; no convierte ausencia de respaldo en falsedad universal.
  - Para la contradicción omitida: localiza ambas posiciones incompatibles y dónde el candidato omite la divergencia.
  - Para la referencia insuficiente: localiza afirmación, referencia resoluble y fragmento, y explica la insuficiencia.
- **PC-09.** Se conserva el informe original cerrado, con alcance y abstenciones, antes de revelar la corrección. También se conservan request y paquete validados, identificación recuperable de sesión y despacho, snapshots y contraste posterior del orquestador con la clave.

**Verificación:** evidencia de la sesión real y examen del informe original. No acredita esta promesa una simulación, un informe escrito por el productor ni un test que reconozca frases esperadas.

El encargo incluye también, como lectura normativa no reveladora, `skills/cdad-cycle/references/documentary-contracts.md`. Las referencias normativas de método `design-principles.md`, `stage-4-review.md` y `verdict-tuple.md`, bajo `skills/cdad-cycle/references/`, se declaran como tales: sus lecturas se registran y no invalidan porque no revelan respuestas. No son fuentes del relevamiento ni autorizan explorar otras referencias. `discovery.md` no es un insumo del ensayo.

**Objeto y precedencia de T5 — decisión de la autoridad sobre BN-1.** El request de T5 declara en `objective` e `invariants` que el objeto revisado es **solo** `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`, frente al contrato, el inventario y las fuentes declaradas. El diff de la unidad y cualquier operación git que muestre contenido —incluidos `git show`, `git log -p` y `git diff`— quedan fuera del objeto y del alcance. La declaración específica del encargo prevalece sobre la frase genérica del bloque de reviewer «the complete diff against the approved contract». Esta precedencia fue decidida por la autoridad en `plan-review-2-resolutions-2026-10-31.md`, BN-1; no modifica los bloques de `packets/{roles,substages}` ni concede lecturas adicionales.

El orden es T3 → T4 → T5 → T6 por la resolución B-2. Aunque el producto ya exista durante T5, quedan fuera del alcance del reviewer `product/`, `oracle/`, `structural/`, `discovery.md`, cualquier informe GREEN o de contraste y sus copias reveladoras. El paquete no autoriza una exploración general del repositorio ni seguir referencias a otros documentos.

Antes de acreditar independencia, el orquestador recupera la transcripción del store de sesiones del runtime en modo lectura, usando la sesión identificada en el despacho, y audita las lecturas declaradas hasta el cierre del primer informe contra esas exclusiones. Si no puede recuperarla, la independencia **no se acredita**; la ausencia de evidencia no se presume como ausencia de lecturas.

La resolución O-10 de la tercera vuelta fija esta regla de auditoría:

| Lectura declarada antes del cierre del primer informe | Efecto |
|---|---|
| `product/`, `oracle/`, `structural/`, `discovery.md`, informes GREEN o de contraste y sus copias | **Invalida** el ensayo como independiente; se registra. |
| El diff de la unidad y operaciones git que muestren contenido (`git show`, `git log -p`, `git diff`) | **Invalida**; se registra. |
| Referencias normativas de método que no revelan respuestas (`design-principles.md`, `stage-4-review.md`, `verdict-tuple.md`) | Se **registra**; no invalida. |
| Cualquier otro documento no listado como insumo | Se **registra**; el auditor decide y funda si revela respuestas. Si las revela, invalida; si no, no invalida por contaminación. |

El criterio es uno solo: **invalida lo que revela respuestas, no lo que enseña a revisar**. Registrar una lectura no concede autorización para efectuarla ni amplía el alcance del encargo. No se ocultan ni reclasifican lecturas invalidantes. Esta comprobación examina la evidencia disponible, no demuestra ausencia de accesos no registrados ni constituye aislamiento técnico.

Si falta cualquiera de los tres hallazgos, esa detección **no queda acreditada** y el piloto no cumple esta promesa. Una revisión posterior informada no repara retrospectivamente el ensayo.

Una falla técnica sin FINAL TEXT —por ejemplo, fallo de transporte o paquete inválido— no consume el ensayo y admite un re-despacho declarado, conservando el incidente. Un informe entregado al que le falta un hallazgo no se reintenta para «encontrarlo». Esta excepción técnica no permite borrar una contaminación observada ni renovar silenciosamente el corpus o el resultado esperado.

### Promesa D — El documento corregido es trazable y conserva la incertidumbre comprometida

- **PC-10.** Existe un relevamiento Markdown en el directorio de producto, separado del contrato, las fuentes, la clave y los verificadores. Cada afirmación factual conservada identifica respaldo localizable en el inventario.
- **PC-11.** La corrección elimina la presentación como hecho de lo no respaldado y corrige la atribución sustentada en una referencia insuficiente. Cuando no hay decisión acreditada que resuelva la contradicción, conserva ambas posiciones y sus localizadores.
- **PC-12.** Las propuestas, si existen, se reconocen como tales. Cada pendiente queda localizado y clasificado, con la información o decisión faltante, condición de cierre y responsable conocido o designación pendiente. La divergencia puede quedar abierta porque el contrato promete documentarla; no se usa esa admisión para dejar sin cumplir otra postcondición.
- **PC-13.** Un encargo independiente revisa el producto corregido contra contrato y fuentes, declara qué examinó y registra hallazgos y abstenciones. Los bloqueantes encontrados se corrigen y se re-verifican antes de solicitar aceptación.

**Verificación:** control estructural sobre el producto y revisión semántica independiente de todas sus afirmaciones factuales y del tratamiento de los tres defectos conocidos. El verde estructural no sustituye esa revisión.

T4 recibe obligatoriamente el candidato negativo, además del contrato, inventario y fuentes. Su request declara el contrato por ruta exacta, clase `contract`; inventario y las dos fuentes mediante la raíz `tests/fixtures/010_003_documentary_pilot/sources/`, y candidato mediante la raíz `tests/fixtures/010_003_documentary_pilot/challenge/`, ambas de clase `tests` y restringidas contractualmente a esos insumos. La ruta exacta de clase `tests` se rechaza. El producto autorizado usa su raíz `product/`; `oracle/` y `structural/` quedan fuera. El verificador `tests/test_010_003_documentary_pilot.py` no es insumo ni lectura de T4: se ejecuta como `focal_test` sin leer el archivo. Las normas usan la raíz `skills/cdad-cycle/references`, clase `implementation`, con autorización contractual restringida a `documentary-contracts.md` y `stage-3-tdd.md`; el selector mecánico más amplio no autoriza otras referencias. El recorte es necesario porque el default `repository-read` del implementer incluiría la clave: una corrección escrita leyendo la clave convierte la corrección en copia.

Antes de T4 se comprueba que el paquete sea construible: `validate-request` y `validate-packet` deben dar rc=0 sobre su request y paquete efectivos. No basta que el recorte esté escrito. Una lectura obligatoria incompatible se detiene y escala, sin restaurar `repository-read`. El request cita el commit de preparación y el commit del producto desciende de él.

T4 y el implementer de T7 ejecutan el mismo comando focal: `python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py`. El implementer ve nombres de casos, mensajes de aserción y sus valores, que informan la corrección; no ve el cuerpo del verificador ni recibe la clave o las muestras estructurales como insumo. La medición registrada en la cuarta resolución muestra que `--tb=no` suprime el cuerpo, pero la línea `FAILED` conserva mensajes y valores. Por ello, antes de GREEN se comprueba que el verificador no lea `oracle/` ni reproduzca contenido de la clave en esos mensajes o valores; las comparaciones contra la clave pertenecen al contraste del orquestador. La autorización de ejecución no concede lectura del archivo ni de los insumos protegidos. `pytest` es una herramienta, no un sandbox; no se promete aislamiento técnico.

T6 sucede después del cierre del primer informe de T5 y en una sesión distinta. Recibe producto, contrato, inventario, fuentes, candidato negativo, clave y `challenge-contrast.md` para verificar la corrección comprometida. La re-verificación de T7 cubre todo el diff del producto, incluidas afirmaciones nuevas, cambios de respaldo y efectos sobre divergencias y pendientes, no solo los hallazgos inicialmente afectados.

El encargo `implementer/review-fix` de T7 repite el recorte corregido de T4 y añade el informe de T6: contrato por ruta exacta, clase `contract`; inventario, fuentes y candidato por las raíces `sources/` y `challenge/`, clase `tests`, restringidas a esos insumos; normas por la raíz `skills/cdad-cycle/references`, clase `implementation`, restringidas a `documentary-contracts.md` y `stage-3-tdd.md`; e informe `product-review.md` como lectura de clase `contract`. T7 añade expresamente `docs/specs/010-003-documentary-pilot/product/` como raíz de lectura de clase `contract`, para incluir el producto declarado como insumo. La ruta exacta de clase `tests` se rechaza. No incluye `oracle/`, `structural/` ni el veredicto del reviewer sobre el desafío. El verificador sigue siendo ejecución focalizada, no insumo ni lectura; un selector mecánico más amplio no autoriza otras referencias.

### Promesa E — El cierre distingue comprobación, revisión y aceptación

- **PC-14.** El cierre mantiene tres registros separados y enlazados:
  1. Evidencia estructural: revisión medida, comandos, resultados, alcance y límites.
  2. Evidencia semántica: informe original del desafío, contraste posterior y revisión del producto corregido.
  3. Aceptación funcional recuperable de la autoridad habilitada, identificando la versión aceptada y los pendientes admisibles.
- **PC-15.** El cierre declara que la muestra es sembrada y sintética; que el contrato del ensayo declara que hay tres defectos y sus clases, de modo que se acredita detección sobre un desafío declarado, no detección a ciegas; que la detección se acredita sobre esa muestra; y que no se demuestran detección infalible, conducta general de modelos, errores espontáneos del productor ni fidelidad de un documento de cliente.

**Verificación:** revisión de los registros y decisión explícita de aceptación. Un recibo de transporte no satisface ninguna aceptación semántica o funcional.

## 4. Invariantes verificables

| Invariante | Evidencia |
|---|---|
| **INV-01.** El productor no modifica fuentes, contrato, muestras, clave ni verificadores. | Scopes publicados, comparación de bytes protegidos antes/después y diff auditado. |
| **INV-02.** El test-writer deriva el oráculo del contrato y los insumos autorizados, no del producto producido. | Paquetes, procedencia declarada y secuencia de preparación anterior a GREEN. |
| **INV-03.** El primer informe del desafío no se sustituye después de revelar información adicional. | Artefacto original recuperable y cronología del ensayo y de la revelación. |
| **INV-04.** Estructura, fidelidad y aceptación permanecen como resultados distintos. | PC-06 y registros separados de PC-14. |
| **INV-05.** No se introducen datos de clientes, binarios, roles, agentes, selectores, campos del estado ni formatos de transporte nuevos. | Inventario y diff completo de la unidad. |
| **INV-06.** El piloto no modifica la toolchain ni `packets/{roles,substages}` y no depende de líneas o rewrap para sus controles. | Diff y revisión del verificador. |
| **INV-07.** Cada encargo conserva un rol y una subfase; architect y reviewer no escriben producto. | Requests, resultados y auditoría de alcances. |

Las comparaciones de bytes demuestran conservación en los estados observados, no ausencia de escrituras transitorias. Los invariantes procedimentales no se convierten artificialmente en propiedades aleatorias.

El request de T5 incorpora en sus `invariants` la delimitación y precedencia de su objeto establecidas en la promesa C, sin cambiar estas siete invariantes de la feature.

## 5. Aceptación medible y evidencia

Se acepta el piloto únicamente cuando:

1. PC-01–PC-15 tienen evidencia por su vía declarada.
2. Las tres muestras producen los resultados de PC-04–PC-06.
3. El primer informe independiente contiene los tres hallazgos fundamentados.
4. El documento corregido pasa el control comprometido y su revisión semántica.
5. No quedan pendientes que impidan acreditar el contrato.
6. Los insumos protegidos conservan sus bytes en las comparaciones registradas.
7. Pasan las pruebas focalizadas y regresiones pertinentes; quien cierre ejecuta la suite completa conforme a la política vigente.
8. La autoridad habilitada acepta explícitamente la versión identificada.

| Evidencia | Contenido mínimo |
|---|---|
| Preparación | Commit identificado anterior a T4 con corpus, inventario, candidato, muestras, clave y `tests/test_010_003_documentary_pilot.py`; request de T4 que cita ese commit y commit del producto descendiente de él; `preparation-record.md` con SHA-256 por artefacto, procedencia e inspección de los tres defectos sin respuestas; commit del registro anterior al despacho de T5; ambos commits de preparación y registro citados por el request de T5. |
| AUDIT/RED/GREEN | Selección de pruebas, comandos, salidas, códigos de retorno, revisión medida y causa del RED; request y paquete efectivos de T4 con `validate-request` y `validate-packet` rc=0. |
| Ensayo independiente | Paquete validado, sesión y despacho recuperables, snapshots, transcripción recuperada del store del runtime y auditada según la tabla de la promesa C, e informe original cerrado; incidencias técnicas y re-despachos declarados, si existen. Sin transcripción recuperable no se acredita independencia. |
| Contraste posterior | Correspondencia fundamentada entre clave y hallazgos; omisiones expresas; `challenge-review.md` y `challenge-contrast.md` versionados en un commit descendiente del de preparación. |
| Producto y correcciones | Versión, diff, control estructural, revisión y re-verificación de todo el diff; recorte de lectura declarado para `implementer/review-fix` de T7. |
| Cierre | Tres registros de PC-14, límites y aceptación; índice de rutas y hashes de las copias durables de evidencia. |

Los tests se agrupan por promesa observable. No se exige una prueba por postcondición ni variantes equivalentes sin consecuencia distinta.

El reparto de D-4 se conserva: los controles de repositorio acreditan resultados estructurales, localizadores, estados observados de bytes y declaraciones transportadas; los hallazgos semánticos, el contraste efectivo, la producción y la revisión requieren ejecución real de los roles. La aceptación corresponde a la autoridad habilitada.

## 6. Riesgos operativos

- **I-8:** una denegación de lectura necesaria al test-writer se informa y escala; no se rodea con otra herramienta.
- **I-9/I-10:** se usa el CLI del proyecto; esta unidad no modifica sus fuentes de instrucciones.
- **I-11/I-12:** los controles nuevos no emplean ventanas de líneas ni asociaciones sensibles al rewrap.
- **I-13:** se verifica la compatibilidad rol/subfase/tipo antes de recibir un resultado. Para reviewer/review corresponde `review`; no se inventan tipos.
- **Instalación global:** no se atribuyen al agente instalado obligaciones que solo están acreditadas en el repositorio y el paquete.
- **Contaminación del ensayo:** cualquier lectura declarada de `product/`, `oracle/`, `structural/`, `discovery.md`, un informe GREEN o de contraste o sus copias reveladoras antes del cierre del primer informe invalida su acreditación como ensayo independiente. El diff de la unidad está excluido; una operación git que muestre contenido, incluidos `git show`, `git log -p` y `git diff`, cuenta como lectura del objeto excluido y también invalida. Las referencias normativas no reveladoras se registran sin invalidar; los demás documentos no listados se registran y el auditor funda si revelan respuestas, conforme a la tabla de la promesa C. Se audita la transcripción disponible; la exclusión y la precedencia de BN-1 son contractuales y de alcance, no aislamiento técnico.
- **Transcripción no recuperable:** no se acredita independencia; no se presume por ausencia de evidencia.
- **Fijación temporal:** las fechas de git no prueban el orden por sí solas. Deben conservarse los hashes, la inspección previa y los commits requeridos, incluido el verificador antes de T4, la cita de ese commit por su request y la descendencia del commit del producto.
- **Lectura del verificador:** T4 y el implementer de T7 ejecutan el comando focal con `--tb=no`, sin leer el archivo. Ven nombres de casos y mensajes y valores de aserción, no el cuerpo; no reciben clave ni muestras estructurales como insumo. T3 comprueba que el verificador no lea `oracle/` ni reproduzca la clave. Esa salida no acredita fidelidad semántica; `pytest` no es un sandbox.
- **Durabilidad:** `.cdad/` no se conserva versionado; sus evidencias necesarias se copian a la feature con rutas y hashes recuperables.

## 7. `deferred-hardening`

| No comprometido | Motivo |
|---|---|
| Parser documental universal, formatos binarios y corpus de clientes | El piloto usa Markdown sintético y una convención acotada. |
| Detección semántica automática | No sustituye el contraste independiente comprometido. |
| Generalización estadística o comparación de modelos | Una muestra sembrada y una sesión no acreditan esas conclusiones. |
| Sandbox, vigilancia de accesos o prueba de ausencia de escrituras transitorias | No son capacidades del mecanismo existente. |
| Reparar I-8–I-13 o actualizar la instalación global | Requiere sus contratos y autorizaciones; aquí se respetan sus límites. |
| Rendimiento, cobertura exhaustiva y combinatoria sin consecuencia contractual | No protegen otra promesa observable del piloto. |

Ninguna exclusión permite omitir los tres hallazgos, la revisión del producto o la aceptación.

## 8. Referencias verificadas

- Discovery: `docs/specs/010-003-documentary-pilot/discovery.md`, §§2–7.
- Decisiones: `docs/specs/010-003-documentary-pilot/discovery-decisions-2026-10-31.md:10-87`.
- Resoluciones del primer dictamen: `docs/specs/010-003-documentary-pilot/plan-review-resolutions-2026-10-31.md:9-83`.
- Dictamen sobre spec v1 y plan v2: `docs/specs/010-003-documentary-pilot/plan-review.md:9-50`.
- Segundo dictamen, sobre spec v2 y plan v3: `docs/specs/010-003-documentary-pilot/plan-review-002.md:31-67`.
- Resoluciones de la segunda vuelta: `docs/specs/010-003-documentary-pilot/plan-review-2-resolutions-2026-10-31.md:10-136`.
- Tercer dictamen, sobre spec v3 y plan v4: `docs/specs/010-003-documentary-pilot/plan-review-003.md:9-62`.
- Resoluciones de la tercera vuelta: `docs/specs/010-003-documentary-pilot/plan-review-3-resolutions-2026-10-31.md:9-101`.
- Cuarto dictamen, sobre spec v4 y plan v5: `docs/specs/010-003-documentary-pilot/plan-review-004.md:9-74`.
- Resoluciones de la cuarta vuelta: `docs/specs/010-003-documentary-pilot/plan-review-4-resolutions-2026-10-31.md:10-79`.
- Resultado del piloto y aceptación del epic: `docs/epics/epic-010-documentary-specialization/plan.md:47-88`.
- Norma documental: `skills/cdad-cycle/references/documentary-contracts.md:38-176`.
- Procedimiento: `skills/cdad-cycle/references/handoff-prompts.md:112-165`.
- Límite de 010-002: `docs/specs/010-002-documentary-role-integration/closure.md:155-170`.
- Independencia del test-writer: `sources/roles/test-writer.md:18-35`.
- Scopes admitidos: `skills/cdad-cycle/scripts/cdad_packet.py:1419-1499`.
- Lecturas normativas del implementer: `skills/cdad-cycle/packets/roles/implementer.md:1-3`, `skills/cdad-cycle/packets/substages/implementer-green.md:1` y `skills/cdad-cycle/packets/substages/implementer-review-fix.md:1`.
- Referencias de método del reviewer: `skills/cdad-cycle/packets/roles/reviewer.md:1-4`; su tratamiento en el ensayo se decide en la resolución O-10 de la tercera vuelta.
- Tipos existentes: `skills/cdad-cycle/scripts/cdad_result.py:826-859`.
- Defectos abiertos: `docs/epics/epic-010-documentary-specialization/backlog.md:9-18`.

Las referencias heredadas de la v1 conservan su función de antecedentes. Las resoluciones de las cuatro vueltas de 2026-10-31 precisan el orden, los insumos, la precedencia del objeto de T5, los registros del piloto, el recorte construible de T4 y T7, la auditoría de lecturas no reveladoras, la salida focal acotada y el mapa de selectores admitidos. No constituyen evidencia de una ejecución del piloto todavía no realizada.

**Status: Pending approval.**

---
