# Plan — 010-003-documentary-pilot

**Versión:** 6.  
**Estado:** pendiente de revisión y aprobación junto con la spec.  
**Spec:** `docs/specs/010-003-documentary-pilot/spec.md`, versión 5.  
**Resoluciones:** `plan-review-resolutions-2026-10-31.md`, B-1–B-4 y O-1–O-8; `plan-review-2-resolutions-2026-10-31.md`, BN-1 y NB-1–NB-6; `plan-review-3-resolutions-2026-10-31.md`, BN-2 y O-9–O-12; `plan-review-4-resolutions-2026-10-31.md`, BN-3 y O-13–O-14.

## Steps

- [ ] T1 — Revisar y aprobar contrato, plan y fronteras.
- [ ] T2 — AUDIT y POST-AUDIT independientes.
- [ ] T3 — Preparar corpus, clave, verificador y RED.
- [ ] T4 — GREEN documental con producto separado.
- [ ] T5 — Ejecutar y cerrar el ensayo semántico independiente.
- [ ] T6 — Revisar el producto corregido.
- [ ] T7 — Corregir y re-verificar hallazgos.
- [ ] T8 — Cerrar con evidencia, aceptación y Memory Bank.

## Estrategia y lectura de los hitos

T1–T8 son hitos, no despachos. Cada encargo dentro de un hito conserva un solo rol y una sola subfase, con paquete y sesión propios. El orquestador coordina y materializa; no se convierte en rol despachable. Esta organización está aceptada por la autoridad en la resolución O-1.

La ejecución es secuencial, sin paralelismo comprometido. Se mantiene T3 → T4 → T5 → T6 por la razón registrada en B-2: el ciclo exige GREEN antes de un encargo de review. T5 recibe los insumos preparados en T3, pero su reviewer no recibe el producto de T4 ni información reveladora. T6 comienza después del cierre del primer informe de T5.

Se conserva la descomposición existente en lugar de crear tareas y campos adicionales: la separación operativa se declara en las comprobaciones observables de cada hito. Los hitos llevan `detail: "next"` porque esta revisión explicita sus verificaciones ya definidas; eso no autoriza despacharlos anticipadamente ni omitir sus dependencias.

Se aplican la norma de `skills/cdad-cycle/references/documentary-contracts.md` y el procedimiento documental de `skills/cdad-cycle/references/handoff-prompts.md`, sin reproducirlos ni modificarlos.

El bloque estructurado no concede permisos. Cada paquete delimita sus fuentes, producto, insumos protegidos, verificaciones y límites. Los archivos nuevos indicados a continuación son artefactos por crear, no interfaces existentes.

La exclusión de información del ensayo es contractual y de alcance, no aislamiento técnico. El producto, `oracle/`, `structural/`, `discovery.md` y los informes GREEN o de contraste quedan fuera del alcance de T5, incluidas sus copias reveladoras. También quedan excluidos el diff de la unidad y las operaciones git que muestren contenido.

La autoridad resolvió BN-1: `objective` e `invariants` de T5 fijan específicamente su objeto y prevalecen sobre la frase genérica del bloque de reviewer relativa al diff completo. Esa decisión no modifica los bloques de instrucciones, no amplía lecturas y no elimina la comprobación de otras incompatibilidades del paquete.

La tercera vuelta adopta BN-2, vía 1: T4 ejecuta el verificador sin recibirlo como insumo ni leer su código. No se amplía la raíz a `tests/`, no se mueve el archivo ni se cambia la política. O-10 distingue las lecturas reveladoras de las referencias de método: se registra lo observado y se invalida por revelación de respuestas, no por aprender a revisar.

La cuarta vuelta adopta BN-3: el comando focal usa `--tb=no` y T3 inspecciona que el verificador no lea `oracle/` ni reproduzca la clave en mensajes o valores de aserción. El implementer ve nombres de casos, mensajes y valores, no el cuerpo; no recibe clave ni muestras estructurales como insumo. `pytest` es una herramienta, no un sandbox. O-13 explicita las raíces admitidas y su restricción contractual; O-14 añade `product/` como raíz de lectura de clase `contract` en T7.

## T1 — Contrato y fronteras

**Responsable:** orquestador; revisión por el rol correspondiente y aprobación por la autoridad habilitada.

**Archivos:** `spec.md` v5, `plan.md` v6 y registro recuperable de aprobación bajo el directorio de la feature, materializados por el orquestador.

Antes de despachar:

- Resolver contradicciones de contrato y contrastar las correcciones con B-1–B-4, O-1–O-8, BN-1, NB-1–NB-6, BN-2, O-9–O-12, BN-3 y O-13–O-14.
- Confirmar separación entre fuentes, desafío, clave, muestras, producto y evidencias reveladoras.
- Mantener la clave exacta fuera del contrato que recibirá el reviewer del desafío. El contrato puede nombrar las clases de defecto; no debe revelar las respuestas concretas.
- Confirmar que PC-15 declara que el contrato anticipa los tres defectos y sus clases: el ensayo no acredita detección a ciegas.
- Comprobar que los tipos de resultado previstos existen para cada rol/subfase.

El encargo de revisión del borrador corresponde a `reviewer/plan-review`, separado de su autor. Su dictamen no aprueba la propuesta. Los bloqueantes se resuelven o se descartan con fundamento por la autoridad competente antes de aprobar.

**Verificador:** revisión de suficiencia y aprobación explícita.  
**Dependencias:** ninguna.

## T2 — AUDIT y POST-AUDIT

**Responsable:** test-writer para AUDIT; sesión distinta para auditar el mapeo.

**Encargos separados:** primero `test-writer/audit`; después `test-writer/post-audit`, en otra sesión.

**Salida:** `test-audit.md` y evidencia de POST-AUDIT, materializados por el orquestador.

**Superficies iniciales de pruebas:**

- Nuevo `tests/test_010_003_documentary_pilot.py`.
- Nuevos fixtures bajo `tests/fixtures/010_003_documentary_pilot/`.
- Regresiones existentes:
  - `tests/test_010_001_documentary_contracts.py`.
  - `tests/test_010_002_documentary_role_integration.py`.

El AUDIT confirma las selecciones pertinentes y enumera expresamente los tests existentes que permanecen intactos. No autoriza cambios de toolchain ni lecturas del producto para construir el oráculo.

El mapeo distingue:

| Acreditación automática | Acreditación mediante ejecución real |
|---|---|
| Integridad observable del corpus y resultados estructurales | Los tres hallazgos independientes del desafío |
| Referencias resolubles del producto | Suficiencia de cada respaldo factual |
| Conservación de bytes en snapshots comparados | Alcance y abstenciones reales del reviewer |
| Forma y alcances de los paquetes | Producción, revisión y aceptación del documento |

Incluye los rechazos por producto sin referencias y referencia a fuente no inventariada, sin confundirlos con detección semántica.

**Verificador:** auditoría independiente del mapeo y resolución de sus bloqueantes.  
**Dependencia:** T1.

## T3 — Corpus, clave, control y RED

**Responsable:** test-writer, subfase `red`; escritura únicamente en los tests autorizados. El orquestador inspecciona la preparación, identifica el commit y materializa su registro fuera del encargo de escritura del test-writer.

**Archivos por crear:**

- `tests/fixtures/010_003_documentary_pilot/sources/`.
- `tests/fixtures/010_003_documentary_pilot/sources/inventory.md`.
- `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`.
- `tests/fixtures/010_003_documentary_pilot/structural/`.
- `tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md`.
- `tests/test_010_003_documentary_pilot.py`.

**Materialización por el orquestador:**

- `docs/specs/010-003-documentary-pilot/preparation-record.md`.
- Copias durables necesarias bajo `docs/specs/010-003-documentary-pilot/evidence/`.

### Trabajo

1. Construir las dos fuentes ficticias y `sources/inventory.md` desde el contrato, sin derivarlos del producto ni reutilizar como respuestas los ejemplos ilustrativos de `discovery.md`.
2. Preparar el candidato negativo y fijar la clave.
3. Preparar las muestras estructural rota y corregida.
4. Construir el control acotado y probar las tres muestras de la spec.
5. Añadir la comprobación estructural del producto esperado sin leerlo para derivar reglas; debe rechazar cero referencias y toda referencia a fuente no inventariada.

### Interfaz T3 → T4

T3 entrega `tests/fixtures/010_003_documentary_pilot/sources/inventory.md`, identificado como `inventory-010-003-v1`, con las rutas, identidades, versiones o snapshots recuperables y SHA-256 de las dos fuentes.

La convención queda fijada por la spec §2.4: fuentes `s1` y `s2`, anclas explícitas de forma `<a id="s1-f01"></a>` y enlaces Markdown relativos con ese fragmento. No se usan slugs automáticos ni números de línea. El producto identifica el inventario por ruta e identificador; esa identificación no cuenta como una cita factual.

El candidato negativo es también un insumo obligatorio de T4. La clave y las muestras estructurales permanecen protegidas, fuera de su escritura y de su lectura; la clave no es insumo de producción. El verificador queda fijado para su ejecución focalizada, sin incorporarlo como insumo ni lectura de T4.

### Fijación antes de GREEN y del ensayo

El orquestador inspecciona que el desafío y la clave fundamentan realmente las tres clases de defecto; no basta contar etiquetas. Antes de GREEN comprueba también que el verificador **no lee `oracle/`** y que sus **mensajes y valores de aserción no reproducen contenido de la clave**. Si una aserción necesitara comparar contra la clave, esa comparación no pertenece al verificador sino al contraste del orquestador. El resultado de esta comprobación se conserva en `preparation-record.md`, sin reproducir respuestas.

**Antes de T4** debe existir un commit identificado de preparación que contenga:

- Corpus y las dos fuentes.
- `sources/inventory.md`.
- Candidato negativo.
- Muestras estructurales.
- Clave de contraste.
- Verificador y pruebas: `tests/test_010_003_documentary_pilot.py`.

La inspección de los defectos y la fijación de esos bytes preceden a GREEN. El request de T4 cita el commit de preparación; el commit del producto debe descender de él. Se conservan ambas identidades y la relación de descendencia para que un tercero pueda comprobar el ancla de «anterior a T4».

El orquestador materializa `preparation-record.md` con el identificador del commit de preparación, ruta y SHA-256 de cada artefacto preparado y del verificador fijado, resultado de inspección de los tres defectos sin reproducir sus respuestas, y snapshots recuperables y rutas de copias durables.

El registro se materializa después de identificar el commit de preparación; no se exige que contenga el hash de su propio commit. **Antes del despacho de T5**, `preparation-record.md` debe estar versionado mediante un commit bajo el directorio de la feature. El request de T5 cita el commit de preparación y el commit del registro.

Después de producirse, `challenge-review.md` y `challenge-contrast.md` se versionan en un commit descendiente del de preparación.

Las fechas de git no prueban el orden por sí solas. La fijación comprobable se apoya en los hashes de los artefactos, la inspección previa y los registros y relaciones de commits conservados; no en la fecha de autor como prueba suficiente.

`.cdad/` no se conserva versionado. El orquestador copia a `evidence/` de la feature lo que deba perdurar de paquetes, requests, despachos, sesiones, transcripción auditada y snapshots, con rutas y hashes recuperables. Los informes originales y el contraste se materializan en la feature. Las copias reveladoras se excluyen de T5 igual que sus originales.

### RED esperado

- Las demostraciones estructurales pueden estar verdes desde su creación: el rechazo de una muestra negativa es el **resultado esperado de una prueba que pasa**.
- La obligación aún ausente es el documento funcional: su prueba falla mediante una aserción explícita por producto inexistente, no por errores de importación.
- La revisión semántica queda pendiente de ejecución real; no se fabrica un RED semántico mediante un informe simulado.

**Comando previsto desde la raíz del repositorio, todavía no ejecutado para este piloto:**

```bash
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
```

El runner está disponible; el archivo lo crea este hito antes de ejecutar el comando.

**Verificador:** resultados observados frente a los esperados, causa del RED, inspección del oráculo y commit recuperable de todos los artefactos y del verificador antes de T4; cita por el request de T4 y descendencia exigida para el commit del producto; registro versionado y ambos commits de preparación y registro identificados antes del despacho de T5.  
**Dependencia:** T2.

## T4 — GREEN documental

**Responsable:** implementer, subfase `green`.

**Único directorio editable:**  
`docs/specs/010-003-documentary-pilot/product/`.

**Archivo por crear:**  
`docs/specs/010-003-documentary-pilot/product/relevamiento.md`.

**Insumos:** contrato aprobado, `sources/inventory.md`, fuentes autorizadas y, obligatoriamente, `challenge/negative.md`. El producto corrige los tres defectos conocidos del candidato; no es un documento nuevo sin referente de corrección. El verificador fijado se ejecuta sin modificarlo ni leerlo: no es un insumo del encargo. La clave no es necesaria para producir el relevamiento y permanece fuera de sus insumos.

**`read_scope` del request:** contrato por ruta exacta, clase `contract`; inventario y las dos fuentes mediante la raíz `tests/fixtures/010_003_documentary_pilot/sources/`, y candidato mediante la raíz `tests/fixtures/010_003_documentary_pilot/challenge/`, ambas de clase `tests` y con autorización contractual restringida a esos insumos. La ruta exacta de clase `tests` se rechaza. El producto autorizado usa su raíz `docs/specs/010-003-documentary-pilot/product/`. Las normas usan la raíz `skills/cdad-cycle/references`, clase `implementation`, con autorización contractual restringida a `documentary-contracts.md` y `stage-3-tdd.md`; esa raíz mecánica no autoriza leer otras referencias. `oracle/`, `structural/` y `tests/test_010_003_documentary_pilot.py` quedan fuera.

El default del implementer es `repository-read` y sin este recorte incluiría la clave: una corrección escrita leyendo la clave convierte la corrección en copia.

La vía 1 de BN-2 conserva rutas y política: la ruta exacta del verificador, de clase `tests`, no es declarable porque `test_files` no está en la política; la raíz que lo contiene es `tests/` e incluye la clave. No se ensancha esa raíz para obtener lectura del archivo.

Antes de despachar, el orquestador:

1. Comprueba el commit de preparación anterior a T4, incluido el verificador, y su cita en el request de T4.
2. Comprueba que el verificador no figure como insumo ni lectura y que el recorte excluya `oracle/` y `structural/`; confirma la inspección de T3: el verificador no lee `oracle/` y sus mensajes y valores de aserción no reproducen contenido de la clave.
3. Valida el request y el paquete efectivos con `validate-request` y `validate-packet`, ambos con rc=0. La comprobación exige un paquete construible, no solo una intención escrita.
4. Comprueba la compatibilidad de las lecturas normativas declaradas con el paquete. Una lectura obligatoria incompatible se detiene y escala; no se restaura `repository-read` para eludir el límite.

### Trabajo

- Crear `product/relevamiento.md` como corrección del candidato negativo.
- Aplicar la trazabilidad y el tratamiento de divergencias de PC-10–PC-12 mediante la convención fijada en T3.
- Ejecutar el verificador ya fijado como `focal_test`, sin modificarlo ni leer su archivo, y trabajar con su salida.
- Informar versión producida, archivos cambiados, comandos y resultados; conservar el commit del producto, descendiente del commit de preparación citado por el request.

Con `--tb=no`, el implementer ve nombres de casos y mensajes y valores de aserción, que informan la corrección; no ve el cuerpo del verificador ni recibe la clave o las muestras estructurales como insumo. La medición de la cuarta resolución muestra que la línea `FAILED` conserva mensajes y valores aunque desaparezca el cuerpo; por eso T3 comprueba que no reproduzcan contenido de la clave. La autorización de ejecución no concede lectura del archivo ni de los insumos protegidos. `pytest` es una herramienta, no un sandbox; no hay aislamiento técnico prometido.

El producto puede existir antes del ensayo del desafío, pero **no se muestra ni se incorpora al alcance del reviewer de T5**. Tampoco se incorporan sus informes GREEN o de contraste ni copias reveladoras.

**Comprobación focalizada:**

```bash
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
```

**Regresiones:**

```bash
python3 -B -m pytest -q \
  tests/test_010_001_documentary_contracts.py \
  tests/test_010_002_documentary_role_integration.py
```

**Verificador:** request y paquete efectivos validados con rc=0, pruebas focalizadas y auditoría del diff; comparación de bytes protegidos antes/después; request que cita la preparación y commit del producto descendiente de ella. El verde de esta tarea es estructural, no aceptación semántica.  
**Dependencia:** T3.

## T5 — Ensayo semántico independiente del desafío

**Responsable:** reviewer, subfase `review`, en sesión independiente del productor y del autor de la clave.

**Salida:** `challenge-review.md`, materializado desde el informe original; artefacto de reviewer/review: `review`.

### Preparación del encargo

Los insumos autorizados son:

- Contrato exacto aprobado, sin respuestas concretas.
- `tests/fixtures/010_003_documentary_pilot/sources/inventory.md` y las dos fuentes inventariadas.
- `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`.
- `skills/cdad-cycle/references/documentary-contracts.md`, como lectura normativa: el paquete manda leerla y no revela respuestas.
- Las referencias normativas de método `skills/cdad-cycle/references/design-principles.md`, `skills/cdad-cycle/references/stage-4-review.md` y `skills/cdad-cycle/references/verdict-tuple.md`, declaradas como tales y no como fuentes del relevamiento. Sus lecturas no reveladoras se registran sin invalidar, según O-10.

Quedan excluidos:

- `oracle/`, `structural/` y `product/`.
- Cualquier informe GREEN, de contraste o previo que revele respuestas, incluidas sus copias.
- `discovery.md`; sus ejemplos no se reutilizan como respuestas.
- El plan, los registros de preparación y los demás documentos no incluidos expresamente como insumos del ensayo. Su lectura observada se clasifica según la tabla de auditoría; registrarla no la autoriza.
- El diff de la unidad y las operaciones git que muestren contenido, incluidos `git show`, `git log -p` y `git diff`.

Los scopes se delimitan mediante clases existentes:

- La lectura exacta del contrato utiliza su clase `contract`, sin ampliar al directorio completo de la feature.
- Las fuentes y el desafío usan raíces disjuntas bajo `tests`.
- Las normas se declaran como insumos identificados por sus rutas. Para su selector de lectura se usa la raíz admitida `skills/cdad-cycle/references`, clase `implementation`, con autorización contractual restringida a las lecturas normativas declaradas. Esa raíz mecánica no autoriza leer otras referencias.
- No se usa `repository-read` ni una raíz amplia que incluya producto, clave, muestras o informes reveladores.

### Objeto declarado y precedencia de BN-1

El request fija en `objective` e `invariants`:

- El único objeto revisado es `tests/fixtures/010_003_documentary_pilot/challenge/negative.md`, frente al contrato, el inventario y las fuentes declaradas.
- El diff de la unidad queda fuera del objeto y del alcance.
- No se ejecutan operaciones git que muestren contenido, incluidos `git show`, `git log -p` y `git diff`.
- La declaración específica del objeto prevalece sobre la frase genérica del bloque de reviewer «the complete diff against the approved contract», por decisión de la autoridad registrada en `plan-review-2-resolutions-2026-10-31.md`, BN-1.

No se modifican los bloques de `packets/{roles,substages}`. La precisión del objeto no añade una forma de transporte ni un selector nuevo.

El request cita el commit de preparación y el commit de `preparation-record.md`; esas identidades no autorizan al reviewer a abrir el registro, sus artefactos excluidos ni su contenido mediante git.

### Comprobación previa al despacho

El orquestador:

1. Valida paquete y destinatario, y comprueba que `objective`, `invariants` y scopes fijan el objeto y las exclusiones anteriores.
2. Comprueba que el commit de preparación contiene corpus, inventario, candidato, muestras, clave y verificador, que el request de T4 lo cita y que el commit del producto desciende de él.
3. Comprueba la inspección previa, hashes y snapshots, el registro versionado antes del despacho y la cita de ambos commits de preparación y registro en el request de T5.
4. Registra la sesión y el despacho de forma recuperable.
5. Comprueba que el paquete no imponga otra lectura fuera de los insumos y lecturas normativas declarados.

La última comprobación **reconoce la precedencia decidida en BN-1**: la frase genérica sobre el diff completo no cuenta como imposición de leerlo porque el objeto está declarado específicamente en el request. Las lecturas normativas de método no reveladoras se tratan según O-10. Cualquier otra lectura que el paquete sí imponga fuera de lo autorizado se detiene y se escala; no se rodea ni se interpreta como permiso implícito.

### Ejecución y cierre del primer informe

1. El reviewer contrasta el desafío con las fuentes y devuelve hallazgos, localizadores, alcance y abstenciones.
2. El informe original queda recibido y conservado sin alteraciones como `challenge-review.md`, antes de revelar información adicional.
3. El orquestador recupera en modo lectura la transcripción del **store de sesiones del runtime**, usando la sesión identificada en el despacho, y conserva la copia recuperable utilizada en la auditoría.
4. Audita las lecturas declaradas hasta el cierre del primer informe mediante la tabla siguiente. Incluye las lecturas por operaciones git que muestren contenido.
5. Solo después del primer informe cerrado contrasta con la clave y materializa `challenge-contrast.md`.
6. Versiona `challenge-review.md` y `challenge-contrast.md` en un commit descendiente del de preparación y conserva sus identidades en el índice de evidencia.

La auditoría de lecturas es parte de la acreditación de independencia y aplica la decisión O-10:

| Lectura declarada antes del cierre del primer informe | Efecto |
|---|---|
| `product/`, `oracle/`, `structural/`, `discovery.md`, informes GREEN o de contraste y sus copias | **Invalida** el ensayo como independiente; se registra. |
| El diff de la unidad y operaciones git que muestren contenido (`git show`, `git log -p`, `git diff`) | **Invalida**; se registra. |
| Referencias normativas de método que no revelan respuestas (`design-principles.md`, `stage-4-review.md`, `verdict-tuple.md`) | Se **registra**; no invalida. |
| Cualquier otro documento no listado como insumo | Se **registra**; el auditor decide y funda si revela respuestas. Si las revela, invalida; si no, no invalida por contaminación. |

El criterio es uno solo: **invalida lo que revela respuestas, no lo que enseña a revisar**. La clasificación no concede permiso para leer documentos fuera del alcance ni permite ocultar o reclasificar una lectura invalidante.

Si no se puede recuperar la transcripción, la independencia **no se acredita**: no se presume por ausencia de evidencia.

La exclusión y la precedencia son contractuales y de alcance, no aislamiento técnico ni prueba de ausencia de accesos no registrados. Las fechas de git no prueban por sí solas el orden; deben conservarse los hashes y la inspección previa establecidos en T3.

**Verificador:** correspondencia fundamentada de los tres hallazgos, no coincidencia literal de frases, y auditoría recuperable del alcance observado.

### Salidas de fallo

- **Falla técnica sin FINAL TEXT:** no consume el ensayo; se conserva el incidente y se permite un re-despacho declarado sobre los insumos fijados. Esto no borra una contaminación observada.
- **Informe entregado sin uno de los tres hallazgos:** no acredita esa detección; no se reintenta para «encontrarlo».
- **Ensayo contaminado:** no acredita independencia; se registra el bloqueo.
- **Transcripción no recuperable:** no acredita independencia; se registra la falta de evidencia.

No se sustituye el original ni se usa una revisión informada como reparación retrospectiva. Cambiar corpus o resultado esperado exige una decisión explícita; no constituye un reintento técnico autorizado por este plan.

**Dependencias:** T3 y T4. T3 produce los insumos; T4 precede al review por el orden de gates registrado en B-2, sin revelar su producto al reviewer.

## T6 — Revisión del producto corregido

**Responsable:** reviewer, subfase `review`, mediante otro encargo delimitado y en una sesión distinta de T5, independiente del productor.

**Archivos examinados:**

- Producto corregido.
- Contrato aprobado.
- Inventario y fuentes autorizadas.
- Candidato negativo.
- Clave de contraste fijada.
- `challenge-contrast.md`.

**Salida:** `product-review.md`, materializado desde un resultado `review`.

### Trabajo

- Confirmar que el diff real corresponde al producto documental autorizado.
- Contrastar todas las afirmaciones factuales del relevamiento.
- Revisar la corrección de los tres defectos conocidos mediante candidato, clave y contraste posterior.
- Verificar conservación de ambas posiciones y clasificación de pendientes.
- Ejecutar el control estructural y declarar sus límites.
- Emitir hallazgos, alcance y abstenciones.

**Comprobación focalizada:**

```bash
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
```

**Verificador:** revisión independiente contra PC-10–PC-13, separada del contraste del desafío.  
**Dependencias:** T4 y T5; el primer informe de T5 debe estar cerrado antes de revelar el producto y los demás insumos reveladores.

## T7 — Corrección y re-verificación

**Responsables:** implementer para corregir; reviewer para re-verificar.

**Encargos separados:** `implementer/review-fix`, seguido de `reviewer/review`. No se combinan en un despacho.

**Escritura del implementer:** únicamente `docs/specs/010-003-documentary-pilot/product/`.

**`read_scope` del encargo `implementer/review-fix`:** contrato aprobado por ruta exacta, clase `contract`; inventario y las dos fuentes mediante la raíz `tests/fixtures/010_003_documentary_pilot/sources/`, y candidato mediante la raíz `tests/fixtures/010_003_documentary_pilot/challenge/`, ambas de clase `tests` y restringidas contractualmente a esos insumos. La ruta exacta de clase `tests` se rechaza. Las normas usan la raíz `skills/cdad-cycle/references`, clase `implementation`, con autorización contractual restringida a `documentary-contracts.md` y `stage-3-tdd.md`; esa raíz mecánica no autoriza otras referencias. Se añade el informe de T6 `docs/specs/010-003-documentary-pilot/product-review.md`, clase `contract`, y expresamente la raíz de lectura `docs/specs/010-003-documentary-pilot/product/`, clase `contract`, para incluir el producto declarado como insumo.

El recorte repite el de T4 corregido por BN-2 y añade el informe de T6; no se usa el default `repository-read`, que incluiría la clave. Quedan fuera `oracle/`, `structural/` y el veredicto del reviewer sobre el desafío, `challenge-review.md`. El verificador no es insumo ni lectura: el implementer lo ejecuta como `focal_test` sin leerlo y usa su salida, con el mismo límite declarado en T4.

- Corregir hallazgos reales.
- Repetir el control estructural.
- Re-verificar **todo el diff del producto**, no solo los hallazgos inicialmente afectados: incluye afirmaciones nuevas, cambios de respaldo y efectos sobre divergencias y pendientes.
- Conservar informes previos y registrar la versión revisada.

Si no hay correcciones necesarias, se registra esa conclusión sin fabricar cambios.

Si se necesita modificar fuentes, clave o verificador, detener esa parte y devolverla al rol competente. Un cambio que altere el contrato exige su aprobación y una decisión explícita sobre la vigencia de la evidencia anterior.

**Comprobación focalizada:**

```bash
python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py
```

**Regresiones sobre la versión corregida:**

```bash
python3 -B -m pytest -q \
  tests/test_010_001_documentary_contracts.py \
  tests/test_010_002_documentary_role_integration.py
```

**Verificador:** ausencia de bloqueantes, cobertura de todo el diff y trazabilidad de cada corrección a su re-verificación; request del implementer con el recorte de lectura declarado.  
**Dependencia:** T6.

## T8 — Cierre, aceptación y Memory Bank

**Responsable:** orquestador para gates y materialización; autoridad habilitada para aceptación; scribe para borradores de Memory Bank.

**Registros separados:**

- `structural-evidence.md`.
- Informes semánticos originales, contraste, auditoría de lecturas y re-verificaciones.
- `functional-acceptance.md`.
- `closure.md`, como índice de evidencia y límites.

Todos se materializan bajo `docs/specs/010-003-documentary-pilot/`.

### Secuencia

1. El orquestador completa el mapeo PC→evidencia y confirma snapshots protegidos, commit de preparación anterior a T4 con verificador, request de T4 que lo cita y commit del producto descendiente de él, validaciones efectivas de T4 con rc=0, registro versionado antes de T5, ambos commits de preparación y registro citados por el request de T5 e informes del desafío versionados en un descendiente del de preparación. Confirma también la auditoría según O-10 y el recorte de lectura del implementer en T7.
2. Quien cierre crea previamente `.cdad/evidence/010-003-closure/`, comprueba las pruebas focalizadas y regresiones pertinentes y ejecuta la suite completa una vez conforme a la política vigente; conserva cualquier intento fallido y su resolución.
3. El orquestador copia a la feature las evidencias de `.cdad/` que deban perdurar y completa su índice de rutas y hashes; no depende de versionar `.cdad/`.
4. El orquestador solicita aceptación únicamente sin bloqueantes.
5. La autoridad habilitada acepta la versión identificada y sus pendientes admisibles; el orquestador conserva el registro.
6. Se despacha exclusivamente `scribe/memory` para los borradores de Memory Bank desde la evidencia.
7. La autoridad habilitada aprueba esos borradores y el orquestador los materializa mediante el procedimiento existente.

La coordinación, aceptación y materialización no se presentan como subfases de un rol despachable.

**Comandos previstos de cierre, únicamente por quien cierre:**

```bash
mkdir -p .cdad/evidence/010-003-closure/
python3 scripts/cdad-suite.py close --all \
  --evidence-root .cdad/evidence/010-003-closure
```

**Regresiones que T8 debe acreditar sobre la versión de cierre:**

- `tests/test_010_001_documentary_contracts.py`.
- `tests/test_010_002_documentary_role_integration.py`.

No es necesario repetirlas separadamente si la selección completa registrada ya las acredita sobre la misma versión. Esta obligación coincide con la entrada T8 de `plan-tasks`.

El cierre declara el límite de PC-15: el contrato anuncia los tres defectos y sus clases; lo acreditado es detección sobre un desafío declarado, no detección a ciegas.

La comprobación de tipos ocurre **antes de recibir** cada resultado, en atención a I-13. El scribe no produce el relevamiento ni lo aprueba.

No se hace push, publicación ni actualización de la instalación global.

**Verificador:** PC-14–PC-15, aceptación recuperable y cierre conforme.  
**Dependencia:** T7 y acreditación de todas las promesas.

## Asignación de evidencia

| Promesa | Hitos | Evidencia decisiva |
|---|---|---|
| A — Base recuperable y clave previa | T2, T3 | Inventario, fuentes sintéticas, commit de preparación con verificador antes de T4, cita por su request, commit del producto descendiente, inspección previa, hashes y registro versionado antes de T5. |
| B — Detección estructural y límite | T3, T4 | Resultados efectivos de las tres muestras, rechazos por referencias ausentes o fuentes no inventariadas y control del producto. |
| C — Detección semántica independiente | T5 | Request con ambos commits y objeto delimitado, paquete y sesión reales, transcripción recuperada y auditada según O-10, primer informe cerrado y contraste posterior versionados en un descendiente del de preparación. |
| D — Producto trazable e incertidumbre | T4, T6, T7 | Corrección del candidato sin lectura de la clave ni del código del verificador, paquete construible de T4 validado con rc=0, revisión factual con clave y contraste, recorte de lectura del implementer en T7, correcciones y re-verificación de todo el diff. |
| E — Cierre diferenciado | T8 | Registros separados, copias durables identificadas, límites —incluido el desafío declarado— y aceptación recuperable. |

Cobertura de postcondiciones: PC-01–PC-03 → T2/T3; PC-04–PC-06 → T3; PC-07–PC-09 → T5; PC-10–PC-12 → T4/T6/T7; PC-13 → T6/T7; PC-14–PC-15 → T8.

Las regresiones existentes de 010-001 y 010-002 se ejecutan en T4 y sobre las correcciones de T7; T8 conserva su acreditación final mediante la suite completa. T2 confirma la selección sin modificar sus verificadores.

Se conserva el reparto de D-4: los tests acreditan estructura, localizadores, bytes observados y declaraciones transportadas; no acreditan que un rol haya encontrado los defectos, contrastado efectivamente las afirmaciones, producido o revisado el documento. Esas obligaciones requieren sesiones reales y evidencia recuperable.

Se conserva el `deferred-hardening` de la spec. Este plan no amplía el piloto a un parser universal, detección semántica automática, corpus de clientes, reparación de la toolchain ni garantías de aislamiento técnico.

## Referencias de la tercera y cuarta vueltas

- Dictamen sobre spec v3 y plan v4: `docs/specs/010-003-documentary-pilot/plan-review-003.md:9-62`.
- Decisiones BN-2 y O-9–O-12: `docs/specs/010-003-documentary-pilot/plan-review-3-resolutions-2026-10-31.md:9-101`.
- Cuarto dictamen, sobre spec v4 y plan v5: `docs/specs/010-003-documentary-pilot/plan-review-004.md:9-74`.
- Decisiones BN-3 y O-13–O-14: `docs/specs/010-003-documentary-pilot/plan-review-4-resolutions-2026-10-31.md:10-79`.
- Bases anteriores y referencias del contrato: spec v5, §§2 y 8.

## Proyección estructurada

Los campos `files` enumeran las superficies editables previstas de los encargos de producción o pruebas. Los hitos de coordinación y revisión usan `files: []`; sus documentos examinados y resultados materializados quedan declarados en la prosa y en `observable_checks`.

```plan-tasks
{
  "validation_strategy": "Recorrido secuencial de ocho hitos, organizacion aceptada en O-1; cada encargo conserva un solo rol y una sola subfase, con paquete y sesion propios. T1 coordina revision y aprobacion. T2 separa audit y post-audit. T3 fija corpus, inventario, candidato, muestras, clave y verificador mediante commit anterior a T4, inspeccion previa y preparation-record.md versionado antes de T5; comprueba antes de GREEN que el verificador no lee oracle/ ni reproduce la clave en mensajes o valores de asercion; las comparaciones contra la clave pertenecen al contraste del orquestador. Registra RED por producto ausente. T4 corrige obligatoriamente el candidato solo en el producto autorizado, con read_scope recortado que excluye oracle, structural y el codigo del verificador; este no es input ni lectura, se ejecuta como focal_test con --tb=no y su salida informa la correccion. Se ven nombres de casos, mensajes y valores de asercion, no el cuerpo; no se reciben clave ni muestras estructurales como insumo. Pytest es una herramienta, no un sandbox. Declara documentary-contracts.md y stage-3-tdd.md como lecturas normativas, sin autorizar otras referencias por el selector mecanico mas amplio. Antes de despachar T4, validate-request y validate-packet sobre request y paquete efectivos dan rc=0. Su request cita el commit de preparacion y el commit del producto desciende de el. Se mantiene T3 -> T4 -> T5 -> T6 porque el ciclo exige GREEN antes de review, segun B-2. El request de T5 cita los commits de preparacion y registro. Su objective e invariants fijan solo challenge/negative.md como objeto frente a contrato, inventario y fuentes; la autoridad resolvio en BN-1 que esa declaracion prevalece sobre la frase generica del reviewer relativa al diff completo. El diff de la unidad y las operaciones git que muestren contenido quedan excluidos; cualquier otra lectura obligatoria incompatible se detiene y escala. T5 recibe solo los insumos autorizados y las lecturas normativas declaradas; excluye producto, oracle, structural, discovery e informes reveladores. Recupera la transcripcion del store de sesiones del runtime en modo lectura, con sesion identificada en el despacho; sin transcripcion no acredita independencia. Audita las lecturas declaradas segun O-10: las rutas e informes reveladores y sus copias invalidan, incluido discovery; el diff de la unidad y git show, git log -p o git diff con contenido invalidan; las referencias normativas de metodo no reveladoras se registran sin invalidar; cualquier otro documento no listado se registra y el auditor funda si revela respuestas. Invalida lo que revela respuestas, no lo que ensena a revisar; registrar no autoriza lecturas. Conserva el primer informe antes del contraste y versiona ambos informes en un commit descendiente del de preparacion. La exclusion es contractual y de alcance, no aislamiento tecnico; las fechas de git no prueban orden por si solas. Una falla tecnica sin FINAL TEXT admite re-despacho declarado; un informe sin un hallazgo no se reintenta para encontrarlo. T6 revisa el producto en sesion distinta de T5 con candidato, clave y contraste. T7 separa correccion y re-verificacion de todo el diff; el implementer repite el recorte corregido de T4 y anade el informe de T6, sin oracle, structural ni veredicto del desafio. O-13 declara contrato por ruta exacta de clase contract, sources/ y challenge/ por raices de clase tests restringidas a inventario, fuentes y candidato, y normas por raiz skills/cdad-cycle/references de clase implementation restringida a documentary-contracts.md y stage-3-tdd.md; la ruta exacta de clase tests se rechaza. O-14 anade en T7 la raiz de lectura product/ de clase contract para el producto declarado como insumo. T8 crea el directorio de evidencia antes de la suite, acredita las regresiones 010-001 y 010-002, distingue cierre, aceptacion y scribe/memory y conserva en la feature lo durable de .cdad/, que no se versiona. PC-15 declara deteccion sobre un desafio anunciado, no a ciegas. Los controles automaticos no acreditan fidelidad semantica. Las regresiones existentes permanecen protegidas. Quien cierra ejecuta la suite completa conforme a la politica vigente en T8. El bloque no autoriza escrituras ni anticipa despachos.",
  "tasks": [
    {
      "id": "T1",
      "detail": "next",
      "depends_on": [],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "El orquestador confirma contrato, fuentes, desafio, clave, muestras, producto y tipos de resultado separados; no revela respuestas concretas al reviewer del desafio y comprueba B-1..B-4, O-1..O-8, BN-1, NB-1..NB-6, BN-2, O-9..O-12, BN-3 y O-13..O-14.",
        "Encargo reviewer/plan-review independiente del autor sobre spec v5 y plan v6; dictamen recuperable y bloqueantes resueltos o descartados con fundamento por la autoridad competente.",
        "La autoridad habilitada aprueba explicitamente spec y plan; el orquestador materializa fielmente y conserva la aprobacion. Coordinacion y aprobacion no son un despacho de rol."
      ],
      "regressions": [],
      "integration_gate": "Spec y plan revisados y aprobados, fronteras y tipos compatibles; la entrega del borrador no constituye aprobacion.",
      "owner": "orquestador"
    },
    {
      "id": "T2",
      "detail": "next",
      "depends_on": ["T1"],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "Primer encargo test-writer/audit: mapa PC-01..PC-15 a controles automaticos, ejecucion real de roles y aceptacion; seleccion pertinente de pruebas y lista explicita de tests existentes intactos.",
        "Segundo encargo test-writer/post-audit en sesion distinta: auditar suficiencia e independencia del mapeo y resolver sus bloqueantes antes de RED.",
        "El orquestador materializa test-audit.md y evidencia de POST-AUDIT; ningun encargo deriva el oraculo del producto ni autoriza cambios de toolchain."
      ],
      "regressions": [],
      "integration_gate": "Mapeo auditado y suficiente, seleccion de regresiones confirmada y bloqueantes resueltos antes de construir los verificadores.",
      "owner": "test-writer"
    },
    {
      "id": "T3",
      "detail": "next",
      "depends_on": ["T2"],
      "parallel": [],
      "files": [
        "tests/fixtures/010_003_documentary_pilot/sources/",
        "tests/fixtures/010_003_documentary_pilot/sources/inventory.md",
        "tests/fixtures/010_003_documentary_pilot/challenge/negative.md",
        "tests/fixtures/010_003_documentary_pilot/structural/",
        "tests/fixtures/010_003_documentary_pilot/oracle/contrast-key.md",
        "tests/test_010_003_documentary_pilot.py"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py"
      ],
      "observable_checks": [
        "Encargo test-writer/red: crear corpus, sources/inventory.md, candidato, muestras y clave desde el contrato, sin derivarlos del producto ni reutilizar respuestas ilustrativas de discovery.md; entregar a T4 la convencion de anclas de la spec 2.4.",
        "El orquestador inspecciona los tres defectos antes de GREEN y comprueba que el verificador no lee oracle/ y que sus mensajes y valores de asercion no reproducen contenido de la clave; una comparacion contra la clave pertenece al contraste del orquestador, no al verificador; antes de T4 identifica el commit que contiene corpus, inventario, candidato, muestras, clave y tests/test_010_003_documentary_pilot.py. El request de T4 cita ese commit y el commit del producto debe descender de el. Materializa preparation-record.md con ese commit, SHA256 por artefacto y verificador, inspeccion sin respuestas y snapshots recuperables; versiona el registro antes del despacho de T5. Las fechas de git no bastan: se conservan hashes e inspeccion previa.",
        "El control rechaza fragmento inexistente con diagnostico, producto con cero referencias y toda referencia a fuente no inventariada; acepta muestra corregida y candidato semanticamente defectuoso.",
        "Registrar RED por asercion explicita de producto inexistente, no por imports o entorno; conservar comandos, salidas, rc y esperado frente a observado sin simular revision semantica."
      ],
      "regressions": [],
      "integration_gate": "Corpus, inventario, candidato, muestras, clave y verificador fijados en commit anterior a T4, inspeccion previa y RED legitimo; request de T4 que cita la preparacion y descendencia exigida para el commit del producto; registro versionado antes del despacho de T5.",
      "owner": "test-writer"
    },
    {
      "id": "T4",
      "detail": "next",
      "depends_on": ["T3"],
      "parallel": [],
      "files": [
        "docs/specs/010-003-documentary-pilot/product/relevamiento.md"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py"
      ],
      "observable_checks": [
        "Encargo implementer/green: corregir obligatoriamente el candidato negativo en product/relevamiento.md desde contrato, inventario y fuentes. El request declara contrato por ruta exacta de clase contract; inventario y fuentes por raiz tests/fixtures/010_003_documentary_pilot/sources/ y candidato por raiz tests/fixtures/010_003_documentary_pilot/challenge/, clase tests y restringidas a esos insumos; la ruta exacta de clase tests se rechaza. El producto usa su raiz autorizada. Las normas usan raiz skills/cdad-cycle/references, clase implementation, restringida contractualmente a documentary-contracts.md y stage-3-tdd.md; el selector mecanico mas amplio no autoriza otras referencias. Excluye oracle, structural y tests/test_010_003_documentary_pilot.py; el verificador no es input ni lectura, se ejecuta como focal_test sin leerlo. El default repository-read incluiria la clave y una correccion escrita leyendola seria copia.",
        "Aplicar PC-10..PC-12 sin inventar consenso ni presentar propuestas o ausencias de respaldo como hechos. Con --tb=no el implementer ve nombres de casos, mensajes y valores de asercion, no el cuerpo del verificador; no recibe clave ni muestras estructurales como insumo. La linea FAILED conserva mensajes y valores, por lo que T3 comprueba que no reproduzcan contenido de la clave. La salida informa la correccion; pytest es una herramienta, no un sandbox y no se promete aislamiento tecnico.",
        "Antes de despachar, comprobar commit de preparacion con el verificador citado por el request de T4 y validar request y paquete efectivos mediante validate-request y validate-packet, ambos rc=0: el paquete debe ser construible, no solo declarar la intencion. Una lectura obligatoria incompatible se detiene y escala sin restaurar repository-read. Conservar commit del producto descendiente del de preparacion, verificador fijado y regresiones verdes; registrar version y diff y comparar bytes protegidos antes y despues.",
        "Producto, oracle, structural e informes GREEN o de contraste quedan fuera del alcance de T5; el verde estructural no acredita aceptacion semantica."
      ],
      "regressions": [
        "tests/test_010_001_documentary_contracts.py",
        "tests/test_010_002_documentary_role_integration.py"
      ],
      "integration_gate": "Producto separado y estructuralmente conforme; request y paquete efectivos de T4 validados con rc=0; read_scope recortado sin clave, muestras ni codigo del verificador; request que cita la preparacion y commit del producto descendiente; regresiones pertinentes verdes y diff limitado al producto autorizado; insumos protegidos conservados.",
      "owner": "implementer"
    },
    {
      "id": "T5",
      "detail": "next",
      "depends_on": ["T3", "T4"],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "Encargo reviewer/review en sesion independiente del productor y del autor de la clave: recibe solo contrato exacto, inventario, fuentes, candidato y lecturas normativas declaradas: documentary-contracts.md, design-principles.md, stage-4-review.md y verdict-tuple.md. Objective e invariants fijan solo challenge/negative.md como objeto y excluyen el diff de la unidad y operaciones git con contenido. La declaracion especifica prevalece sobre la frase generica del rol por decision BN-1; esa frase no impone otra lectura y cualquier otra imposicion incompatible se detiene y escala.",
        "Validar paquete, destinatario y fijacion de T3: commit de preparacion con verificador citado por el request de T4 y antecesor del commit del producto; commit del registro anterior al despacho de T5 y ambos commits de preparacion y registro citados por su request; conservar sesion, despacho y snapshots. Recuperar en modo lectura la transcripcion del store de sesiones del runtime mediante la sesion identificada en el despacho; si no se recupera, no acreditar independencia.",
        "Auditar las lecturas declaradas hasta el cierre segun O-10: product, oracle, structural, discovery.md, informes GREEN o de contraste y sus copias invalidan; el diff de la unidad y git show, git log -p o git diff con contenido invalidan; referencias normativas de metodo no reveladoras, incluidas design-principles.md, stage-4-review.md y verdict-tuple.md, se registran sin invalidar; cualquier otro documento no listado como insumo se registra y el auditor decide y funda si revela respuestas. Si revela, invalida; si no, no invalida por contaminacion. Invalida lo que revela respuestas, no lo que ensena a revisar; registrar no autoriza lecturas fuera de alcance.",
        "El primer informe fundamenta los tres defectos con localizadores, alcance y abstenciones; se conserva original cerrado en challenge-review.md antes del contraste posterior con la clave en challenge-contrast.md. Versionar ambos informes en un commit descendiente del de preparacion; las fechas de git no prueban orden por si solas.",
        "Sin FINAL TEXT por falla tecnica, registrar incidente y re-despacho declarado; un informe entregado sin un hallazgo no acredita deteccion y no se reintenta para encontrarlo, ni se sustituye por revision informada. Una contaminacion observada no se borra con un re-despacho."
      ],
      "regressions": [],
      "integration_gate": "PC-07..PC-09 acreditadas por una sesion real y los tres hallazgos fundamentados, transcripcion recuperable auditada segun O-10 sin lecturas invalidantes, informe original cerrado antes de revelar la correccion e informes versionados conforme a la fijacion requerida.",
      "owner": "reviewer"
    },
    {
      "id": "T6",
      "detail": "next",
      "depends_on": ["T4", "T5"],
      "parallel": [],
      "files": [],
      "focal_tests": [
        "python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py"
      ],
      "observable_checks": [
        "Otro encargo reviewer/review, en sesion distinta de T5 y posterior a su primer informe cerrado: examina producto, contrato, inventario, fuentes, candidato, clave y challenge-contrast.md; no edita producto.",
        "Contrastar todas las afirmaciones factuales, la correccion de los tres defectos conocidos, ambas posiciones incompatibles y la clasificacion de pendientes contra PC-10..PC-13.",
        "Ejecutar el control estructural y declarar sus limites; comprobar el diff autorizado.",
        "El orquestador materializa product-review.md desde un resultado review, conservando hallazgos, alcance y abstenciones para T7."
      ],
      "regressions": [],
      "integration_gate": "Revision independiente del producto recuperable y completa respecto del alcance comprometido; hallazgos identificados para correccion y re-verificacion.",
      "owner": "reviewer"
    },
    {
      "id": "T7",
      "detail": "next",
      "depends_on": ["T6"],
      "parallel": [],
      "files": [
        "docs/specs/010-003-documentary-pilot/product/relevamiento.md"
      ],
      "focal_tests": [
        "python3 -B -m pytest -q --tb=no tests/test_010_003_documentary_pilot.py"
      ],
      "observable_checks": [
        "Primer encargo implementer/review-fix: corregir hallazgos reales solo en product, repetir control estructural y regresiones y registrar version y diff. Su read_scope repite el de T4 corregido: contrato por ruta exacta de clase contract; inventario y fuentes por raiz tests/fixtures/010_003_documentary_pilot/sources/ y candidato por raiz tests/fixtures/010_003_documentary_pilot/challenge/, clase tests, restringidas a esos insumos; la ruta exacta de clase tests se rechaza. Normas por raiz skills/cdad-cycle/references, clase implementation, restringida a documentary-contracts.md y stage-3-tdd.md. Anade el informe de T6 product-review.md como lectura de clase contract y la raiz de lectura docs/specs/010-003-documentary-pilot/product/, clase contract, para incluir el producto declarado como insumo. No usa repository-read; excluye oracle, structural y el veredicto del reviewer sobre el desafio, challenge-review.md. El verificador no es input ni lectura: se ejecuta con --tb=no como focal_test sin leerlo; el implementer ve nombres de casos, mensajes y valores de asercion, no el cuerpo, y no recibe clave ni muestras estructurales como insumo. Su salida informa la correccion; pytest no es un sandbox, sin aislamiento tecnico. Un selector mecanico mas amplio no autoriza otras referencias.",
        "Segundo encargo reviewer/review independiente: cubrir todo el diff del producto, incluidas afirmaciones nuevas y respaldos cambiados, y vincular cada correccion con su evidencia; conservar informes previos.",
        "Si no hay correcciones necesarias, registrar esa conclusion sin fabricar cambios.",
        "Una necesidad de cambiar fuentes, clave o verificador se detiene y vuelve al rol competente; si cambia el contrato requiere aprobacion y decision sobre evidencia anterior."
      ],
      "regressions": [
        "tests/test_010_001_documentary_contracts.py",
        "tests/test_010_002_documentary_role_integration.py"
      ],
      "integration_gate": "Sin bloqueantes, pruebas y regresiones pertinentes verdes y correcciones re-verificadas; request del implementer con read_scope recortado conforme a O-12, O-13 y O-14; fuentes, clave y verificadores protegidos.",
      "owner": "implementer y reviewer, en encargos separados"
    },
    {
      "id": "T8",
      "detail": "next",
      "depends_on": ["T7"],
      "parallel": [],
      "files": [],
      "focal_tests": [
        "python3 scripts/cdad-suite.py close --all --evidence-root .cdad/evidence/010-003-closure"
      ],
      "observable_checks": [
        "Coordinacion del orquestador, sin despacho de rol: completar PC-01..PC-15 a evidencia, snapshots protegidos, diff conforme y compatibilidad de tipos antes de recibir cada resultado; confirmar commits de preparacion, registro e informes y sus condiciones de anterioridad y descendencia. Confirmar request de T4 que cita la preparacion, commit del producto descendiente, validate-request y validate-packet efectivos de T4 con rc=0, auditoria segun O-10 y recorte de lectura del implementer en T7.",
        "Quien cierre crea previamente .cdad/evidence/010-003-closure/, ejecuta la suite completa conforme a la politica vigente y acredita tests/test_010_001_documentary_contracts.py y tests/test_010_002_documentary_role_integration.py sobre la misma version; conserva comandos, revision medida, salidas, rc, seleccion y limites, incluidos intentos fallidos y su resolucion.",
        "Aceptacion por la autoridad habilitada, sin subfase de rol: solo sin bloqueantes, con version identificada y pendientes admisibles; el orquestador conserva functional-acceptance.md.",
        "Encargo separado scribe/memory: devolver borradores de Memory Bank desde la evidencia; la autoridad habilitada los aprueba y el orquestador materializa mediante el procedimiento existente.",
        "Materializar structural-evidence.md y closure.md y enlazar informes originales, contraste, transcripcion auditada y re-verificaciones; copiar a la feature lo que deba perdurar de .cdad/, con rutas y hashes, sin versionar .cdad/. Declarar muestra sembrada y sintetica, contrato que anuncia tres defectos y sus clases, deteccion sobre desafio declarado y no a ciegas, y limites de generalizacion."
      ],
      "regressions": [
        "tests/test_010_001_documentary_contracts.py",
        "tests/test_010_002_documentary_role_integration.py"
      ],
      "integration_gate": "Todas las promesas acreditadas, suite completa de cierre conforme con regresiones identificadas, tres registros separados y aceptacion recuperable; Memory Bank materializado solo tras aprobacion.",
      "owner": "orquestador"
    }
  ]
}
```

**Status: Pending approval.**

---
