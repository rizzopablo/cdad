# Spec draft — 013-002-live-inventory

**Estado:** propuesta sin aprobar.  
**Autoridad:** contrato de unidad del paquete `013-002-live-inventory-architect-draft-002`, plan aprobado del epic 013 y decisiones B1, B2 y O1–O4 recogidas en el objetivo de su `REQUEST.json`.  
**Snapshot original:** `73a48058a29a2f4286afb54d9c3f5d5f3c000a28`.  
**Revisión de esta corrección:** `731a5669fb650116eb788d32f84b9d2c99c901b1`.

## 1. Descripción funcional

Quien prepara o mantiene tests puede encontrar todos los nodeids actuales mediante el inventario por capacidad y contrato, sin confundir esa clasificación con una acreditación de su protección semántica.

Quien ejecute 013-003 recibe un mapa inicial acotado y un procedimiento para actualizar inventario y genealogía cuando sustituya tests. Los controles existentes comprueban la actualización antes de aceptar el cambio.

El resultado es:

1. Inventario estructuralmente completo sobre la colección efectiva.
2. Clasificación y acreditación expresamente separadas.
3. Mapa utilizable para el lote piloto, conservando obligaciones y referencias históricas.
4. Mantenimiento integrado en gates existentes, con responsabilidades y momentos explícitos, sin corrida completa implícita.

No se promete acreditar semánticamente toda la suite ni detectar automáticamente equivalencias.

## 2. Fuentes, producto y límites

### Fuentes admitidas

El repositorio autorizado por `repository-read`, especialmente:

| Fuente | Localizador |
|---|---|
| Autoridad de esta corrección | `.cdad/packets/013-002-live-inventory-architect-draft-002/REQUEST.json`, objetivo; `UNIT-CONTRACT.md`, Unit y Shared |
| Revisión del borrador | `docs/specs/013-002-live-inventory/plan-review.md`, B1, B2 y O1–O4 |
| Plan aprobado | `docs/epics/epic-013-test-criterion/plan.md`, Alcance y Contratos entre features |
| Discovery | `docs/specs/013-test-criterion-suite-review/discovery.md`, §A.5 y §B |
| Vocabulario y sustitución | `docs/specs/013-001-criterion-coherence/spec.md`, PC-4–PC-7; ADR-041, decisión 5 |
| Contrato histórico del inventario | `docs/specs/008-002-suite-by-capability/spec.md`, §4–§6 |
| Límites históricos reconocidos | `docs/specs/008-002-suite-by-capability/closure.md:79-89` |
| Selector real | `scripts/cdad-suite.py`, `check_inventory`, `check_map`, `check_accredited_preserved`, `selection_for_changes` y `cmd_surface` |
| Datos vivos | `suite-inventory.json` y `pc-map.json` bajo `docs/specs/008-002-suite-by-capability/` |
| Candidato piloto | `tests/test_005_013_t1_unit_projection.py:1117-1223`; cierre de 005-013, §Evidencia |
| Gates existentes | `skills/cdad-cycle/references/re-entry.md`, validaciones por rol |
| Orquestación y handoffs | `sources/roles/orchestrator.md`; `skills/cdad-cycle/references/handoff-prompts.md`, handoffs de Stage 3 |
| Gate completo | `scripts/cdad-ci-gate.py`; `docs/ci-gate.md` |

Las revisiones anteriores que sirvan de referencia de conservación se identifican mediante commit y ruta. No se toman del producto mutable como si fueran un oráculo independiente.

### Producto propuesto

- Datos vivos `suite-inventory.json` y `pc-map.json` en su ubicación existente.
- Documento operativo del proyecto `docs/suite-maintenance.md`, con la sección fija `## Inventario vivo`.
- Aplicación condicional del mantenimiento en el orquestador, los gates y los handoffs existentes.
- Agentes derivados, únicamente mediante regeneración cuando cambien sus fuentes.
- Verificadores focales pertenecientes al test-writer.

Esta tabla no concede permisos: cada despacho delimita sus escrituras.

### Entradas protegidas

No se modifican para obtener aceptación:

- Esta spec una vez aprobada, el contrato de unidad y el plan aprobado.
- Las specs cerradas 008-002 y 008-006.
- Evidencias, mediciones y cierres históricos.
- Las revisiones anteriores usadas como referencia.
- Los verificadores, desde GREEN.

Los JSON vivos de 008-002 son producto mantenible; esa condición no se extiende a sus contratos ni evidencias históricas.

## 3. Contrato y postcondiciones

### Promesa A — Encontrar toda la colección actual por capacidad y contrato

**PC-1. Inventario completo.**  
En la revisión candidata a cierre:

- Todos los módulos Python del universo inspeccionado por `validate` están inventariados con su tipo correcto.
- Cada nodeid recolectado tiene al menos una asignación de capacidad y contrato.
- No quedan asignaciones explícitas a nodeids inexistentes.
- `python3 scripts/cdad-suite.py validate` termina con **rc=0**.

El universo se obtiene nuevamente al verificar. Incluye los tests incorporados por esta propia feature, si los hubiera; no se fija en 1942.

La comprobación se realiza sobre la revisión que ya contiene el último delta de inventario materializado y los cambios de tests que debe cubrir.

**PC-2. Clasificación fundada y seleccionable.**  
Las asignaciones nuevas o corregidas nombran contratos recuperables y explican su procedencia. Para los tests no basta un literal `VERIFY` ni una ruta inexistente como sustituto de contrato.

Se admite un contrato legacy real, como `spec.yaml`, sin convertirlo en una spec aprobada de feature. Se corrige la referencia errónea identificada para `test_opencode_read_map_and_steps.py`.

Las selecciones emitidas por `list --capability` coinciden con las asignaciones declaradas, ordenadas y deduplicadas. Su unión cubre la colección efectiva; no se exige que las capacidades formen una partición.

El alcance de módulo completo conserva su condición contractual: se emplea cuando el módulo pertenece íntegramente a esa asignación. Los módulos mixtos añadidos o corregidos se clasifican con el detalle necesario, sin aplicarles una capacidad por el mero prefijo de archivo.

El helper `tests/_rf2_open_pause.py` conserva como deuda explícita su contrato literal `VERIFY` y su confianza baja. No se presenta esa asignación como contrato recuperable ni como acreditación. Su resolución no forma parte de esta unidad; la deuda se registra en `docs/suite-maintenance.md` y en la evidencia de PC-3.

**PC-3. Datos comparables.**  
La entrega registra:

- Revisión y estado del árbol.
- Comando y configuración de colección.
- Cantidades efectivas de módulos, nodeids y asignaciones pendientes.
- Diferencias respecto del punto de partida.
- Deuda explícita del helper `tests/_rf2_open_pause.py`, separada de las asignaciones estructurales pendientes y de la acreditación semántica.

Los contadores auxiliares del inventario no se presentan como colección efectiva sin su método. Se actualizan o se identifica explícitamente su carácter histórico o estático.

No se reescriben mediciones históricas para aparentar actualidad.

### Promesa B — Distinguir clasificación de acreditación

**PC-4. Estados y vocabulario inequívocos.**  
La documentación operativa permite distinguir:

- Asignación a capacidad y contrato.
- Obligación y variante asociadas a un test.
- Acreditación y evidencia de esa asociación.
- Incertidumbres declaradas.

`confidence` del inventario y `validate rc=0` no acreditan protección semántica.

Las disposiciones se consumen desde 013-001/R2, sin definiciones nuevas. Los valores legacy `decision` del inventario y mapa permanecen diferenciados de la disposición única del AUDIT.

En particular, un registro legacy `eliminar` **no significa automáticamente Retirar**: puede representar la eliminación física de un origen sustituido cuya obligación continúa vigente.

Los 29 registros preexistentes del mapa no se presentan como 29 tests ni como acreditación de toda la suite.

### Promesa C — Mantener la genealogía del piloto

**PC-5. Mapa inicial acotado y verificable.**  
Se entrega un mapa inicial del candidato formado por los dos tests B1 de colisión de 005-013:

- `test_b1_collision_with_published_projection_fails_closed_and_keeps_bytes`
- `test_b1_collision_leaves_the_old_packet_valid_and_receivable`

Ambos pertenecen a `tests/test_005_013_t1_unit_projection.py`.

La elección es una **propuesta de semilla revisable**, no una declaración de redundancia ni una orden de eliminarlos. El primero observa rechazo, diagnóstico y conservación de bytes; el segundo incorpora despacho previo, correspondencia del pin y recepción posterior. Sus diferencias deben conservarse.

Para cada obligación o variante del lote se registra, usando el mapa existente:

- Contrato y localizador.
- Fuente y alcance de la acreditación, o `VERIFY` justificado.
- Nodeid original y destino actual.
- Variante y resultado observable.
- Decisión legacy compatible con el estado físico.
- Referencias a las comprobaciones y evidencias relevantes.
- Identificación del lote `013-002-live-inventory` mediante `task` o `decision_note` **en cada entrada nueva**.

Antes de una sustitución acreditada, el destino es el test actual. No se inventa un sustituto ni una acreditación para completar el mapa.

Los metadatos del piloto histórico de 008-002 conservan su alcance histórico; no se reutilizan sus cifras para describir el lote nuevo. La identificación por entrada permite recuperar el lote nuevo sin reinterpretar `pilot_modules` ni `pilot_nodeids_mapped`.

**PC-6. Actualización reproducible con cada sustitución.**  
El procedimiento entregado a 013-003 establece esta aplicación de los mecanismos existentes:

1. AUDIT identifica la revisión anterior y los registros afectados.
2. El test-writer propone el delta de tests y mapa, con la disposición de 013-001 y sus evidencias.
3. POST-AUDIT ejecuta el mantenimiento autorizado y devuelve los deltas documentales como texto; no adquiere permiso para editar documentos.
4. El orquestador materializa esos deltas al re-entry, antes de la siguiente transición.
5. La revisión independiente contrasta el mapa anterior, los tests y los destinos actuales antes de aceptar la sustitución.

Los paquetes del test-writer que necesiten consultar el mapa deben declararlo expresamente en su `read_scope`, además de identificar la revisión anterior pertinente. La spec no amplía por sí sola el alcance de lectura del rol. Esa lectura no autoriza a usar el producto futuro como oráculo.

Se conserva el origen histórico. Si un destino vuelve a sustituirse, las obligaciones anteriores siguen llegando a un destino actual recolectable y la evidencia permite recuperar los pasos intermedios.

No se identifica una obligación únicamente por su nodeid: se consideran contrato, identificador y variante. Varias obligaciones del mismo test no se colapsan por compartir origen.

Cuando sean necesarios varios destinos, los registros explicitan qué parte conserva cada uno y la revisión contrasta el conjunto. No se introduce un valor de lista incompatible en `target_nodeid`.

Los registros históricos existentes —incluidos sus `VERIFY` y placeholders declarados— no desaparecen para lograr verde. Una incertidumbre que afecte a una sustitución bloquea esa sustitución, no obliga a inventar acreditación global.

### Promesa D — Hacer visible la desactualización en el mantenimiento ordinario

**PC-7. Declaración, responsables y momentos de comprobación explícitos.**

#### Declaración del proyecto

La declaración vive en la sección fija `## Inventario vivo` de `docs/suite-maintenance.md`. Para este proyecto contiene:

- **Comando de integridad:** `python3 scripts/cdad-suite.py validate`.
- **Inventario:** `docs/specs/008-002-suite-by-capability/suite-inventory.json`.
- **Mapa:** `docs/specs/008-002-suite-by-capability/pc-map.json`.

Son instrucciones documentales consumidas por el orquestador, no un nuevo esquema de política ni una interfaz de detección automática.

El orquestador lee esa sección en los re-entries de cambios de tests y transmite la regla aplicable en los handoffs correspondientes, tanto por la ruta legacy como por paquetes.

Si falta el documento o la sección, la regla condicional no aplica y el orquestador registra explícitamente **«sin inventario vivo declarado»**, sin bloquear por esa ausencia. No presume rutas ni comandos.

Esta salida general no exime a esta unidad de entregar su declaración: `docs/suite-maintenance.md` y su contenido son producto comprometido por PC-7.

#### Altas ordinarias y materialización

En RED, properties y E2E, el test-writer entrega en su informe un delta de altas que identifica, para cada nodeid nuevo:

- Nodeid.
- Capacidad.
- Contrato.
- Procedencia de la asignación.

El delta es texto para materialización; el test-writer no escribe el inventario documental. El orquestador lo materializa al re-entry, **antes de la siguiente transición**.

Los cambios de orígenes o destinos incorporan además el delta del mapa de PC-6. POST-AUDIT devuelve los deltas documentales pertinentes bajo la misma separación de responsabilidades.

Materializar el delta no equivale a exigir `validate rc=0` en los pasos no bloqueantes. La desactualización residual queda visible y debe resolverse antes de entrar a Review.

#### Aplicación en los gates existentes

| Momento | Obligación de mantenimiento | Efecto de `validate` |
|---|---|---|
| Re-entry de RED | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea RED** ni exige rc=0 para acreditarlo |
| Re-entry de properties | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea properties** ni exige rc=0 para acreditarlo |
| Re-entry de E2E | Recibir y materializar el delta de altas antes de la siguiente transición | **No bloquea E2E** ni exige rc=0 para acreditarlo |
| Re-entry de POST-AUDIT | Materializar los deltas pertinentes y registrar la desactualización detectada | Un resultado no cero **no bloquea por inventario**; no elimina los requisitos de conservación de PC-6 |
| Re-entry de GREEN | Comprobar y registrar la desactualización respecto de la revisión recibida | Un resultado no cero **no bloquea por inventario** |
| Entrada al gate existente de Review | Exigir inventario actualizado y mapa actualizado cuando corresponda | **Bloquea** si falta evidencia pertinente o `validate` no termina con rc=0 |
| Cierre | Confirmar la integridad sobre la revisión candidata final | **Bloquea** si falta evidencia pertinente o `validate` no termina con rc=0 |

Cuando se ejecute el comando en los pasos no bloqueantes, su resultado se registra sin convertirlo en condición de verde de esa subfase. La ausencia de exigencia de rc=0 no dispensa de entregar y materializar los deltas ni de registrar la desactualización.

En la entrada a Review y en el cierre, rc=0 se mide sobre la revisión que **ya contiene los deltas materializados y los últimos cambios de tests**. Un resultado anterior a esos cambios no acredita la revisión posterior.

La aceptación exige además contraste independiente de conservación cuando haya sustitución. Las demás condiciones de los gates existentes mantienen su fuerza.

No se crea otra fase, receptor ni gate. La obligación no depende de ejecutar el gate completo de CI y se aplica aunque los datos resultantes estén bajo `docs/`.

**PC-8. Límites de los controles explícitos.**  
La entrega y sus instrucciones distinguen:

- `validate`: integridad estructural.
- Contraste del mapa anterior: conservación documental.
- Revisión independiente y evidencias de tests: protección semántica acotada.

No se afirma que `surface`, `close` o el gate de CI ya ejecuten `validate`: el código inspeccionado no lo hace.

Tampoco se atribuye al chequeo histórico de conservación una garantía que no presta: su baseline puede carecer de mapa y su comparación usa únicamente el origen. El contraste de PC-6 debe usar una revisión que sí contenga los registros anteriores.

`docs/suite-maintenance.md` advierte expresamente que un cambio en el inventario o el mapa hace que `surface` seleccione toda la colección. Para inspeccionar esa selección se usa `--collect-only`; para evidencia focal se ejecuta una selección explícita.

La colección no es una ejecución de todos los tests. Que `surface --collect-only` seleccione toda la colección tampoco autoriza ejecutarla. Sin autorización expresa de suite completa, no se ejecuta una selección completa producida por `surface`.

## 4. Invariantes verificables

1. **No pérdida:** cada obligación vigente afectada conserva un destino y evidencia pertinentes.
2. **No autoacreditación:** clasificación, presencia de campos y verde estructural no sustituyen revisión independiente.
3. **Genealogía:** el origen histórico sigue siendo recuperable aunque desaparezca físicamente el test.
4. **Autoridad:** las disposiciones pertenecen a 013-001/R2; esta feature no las redefine.
5. **Separación:** el test-writer no modifica producto documental; GREEN no modifica tests ni oráculos protegidos.
6. **Historia:** no se reescriben contratos cerrados ni evidencias anteriores.
7. **Evidencia autorizada:** no se infiere autorización de suite completa de ningún cambio o comando disponible.
8. **Revisión pertinente:** el verde estructural exigido para entrar a Review y cerrar corresponde a una revisión que contiene los últimos tests y deltas materializados.

## 5. Decisiones de diseño

- **Mantener el índice existente frente a crear otro:** el selector ya consume inventario y mapa. Se conserva una sola fuente de datos vivos.
- **Separar ejes frente a renombrar decisiones:** el vocabulario del AUDIT y los valores legacy tienen funciones distintas. Forzar una traducción uno-a-uno perdería significado.
- **Usar gates existentes frente a otro verificador universal:** `validate` ya detecta la brecha estructural. El contraste por revisión anterior cubre el mantenimiento del lote sin fingir análisis semántico automático.
- **Materialización ordinaria frente a exigir verde estructural en RED:** los roles mantienen sus permisos; el test-writer propone y el orquestador materializa. El control bloquea en la entrada a Review y en el cierre, sin invalidar RED por datos documentales que su autor no puede editar.
- **Declaración documental fija frente a detección implícita o un nuevo campo de política:** el documento de proyecto identifica comando y datos; la norma distribuida indica quién lo lee y qué registrar cuando falta. No se amplían CLI ni esquemas.
- **Semilla concreta frente a acreditar toda la suite:** el par B1 permite ejercitar una genealogía con diferencias observables conocidas. No presupone que consolidarlo sea correcto.
- **Identificación por entrada frente a reutilizar metadatos históricos:** `task` o `decision_note` permite distinguir el lote nuevo sin cambiar el esquema ni alterar las cifras del piloto anterior.
- **Deuda visible del helper frente a inventar un contrato:** se conserva el `VERIFY` de `tests/_rf2_open_pause.py` con su límite explícito; no se lo presenta como acreditado.
- **No ampliar el CLI en esta propuesta:** no se necesitan comandos, flags ni cambios de esquema para las promesas anteriores. Si la implementación demuestra una insuficiencia, debe reportarla; no relajar la aceptación ni ampliar el contrato unilateralmente.

El procedimiento general se expresa condicionalmente para proyectos con inventario declarado; las rutas y comandos particulares pertenecen a la documentación de este proyecto.

## 6. Verificación y aceptación

### Verificación estructural y focal

- Colección efectiva y `validate rc=0` sobre la revisión candidata.
- Contraste de selecciones por capacidad contra los datos declarados.
- Comprobación de recuperabilidad de las referencias nuevas y corregidas, con la deuda del helper identificada separadamente.
- Reutilización de los verificadores existentes de selección e integridad, especialmente `tests/test_008_002_suite_selection.py`.
- Verificación de la identificación del lote por entrada y conservación de los metadatos históricos.
- Verificación focal de la transmisión de PC-7 en el orquestador y los handoffs: declaración y lugar de lectura, salida explícita cuando falta, delta y materialización, pasos no bloqueantes y exigencia de rc=0 al entrar a Review y cerrar.
- Regeneración y comprobación de derivados si cambian fuentes de agentes.

El verificador focal distingue la transmisión de la regla de una garantía de obediencia del agente: no acredita ejecuciones futuras por encontrar una frase.

Los despachos del test-writer que requieran el mapa declaran expresamente su lectura y la revisión pertinente. El mapa producido no sustituye al contrato como oráculo.

AUDIT justifica cualquier verificador nuevo por la protección faltante respecto de los existentes. No se exige un test por postcondición ni repetir los controles sintéticos ya disponibles.

### Revisión semántica independiente

Contrasta:

- Asignaciones nuevas o corregidas contra contratos y tests.
- Separación entre clasificación y acreditación.
- Registros iniciales del piloto y diferencias del par B1.
- Identificación del lote nuevo sin reinterpretar los metadatos históricos.
- Conservación de los registros anteriores.
- Ausencia de instrucciones contradictorias en los consumidores modificados.
- Declaración, responsabilidades, materialización y momentos bloqueantes de PC-7.
- Uso real de la revisión anterior y límites del validador.
- Visibilidad de la deuda declarada del helper.

Registra fuentes, hallazgos, incertidumbres y alcance examinado. No acredita semánticamente toda la suite por muestreo del piloto.

### Aceptación

La feature es aceptable cuando PC-1–PC-8 tienen evidencia pertinente, no quedan bloqueos sobre esas promesas, existe revisión independiente y el dueño aprueba.

La entrada a Review y el cierre cuentan con `validate rc=0` sobre las revisiones pertinentes definidas en PC-7.

El cierre registra por separado:

- Control estructural, con revisión, comando y resultado.
- Revisión semántica acotada.
- Selección de tests realmente ejecutada.
- Deudas e incertidumbres admitidas.
- **Suite completa no realizada**, salvo autorización expresa y evidencia correspondiente.

No se modifican addons: no aplican inventario core/OCA ni instalación limpia de un addon.

## 7. VERIFY y condiciones de cierre

| Pendiente | Clasificación y resolución |
|---|---|
| Correspondencia final de las asignaciones nuevas o corregidas | Bloqueante para aceptar esas asignaciones. La cierra su contraste con contratos/tests y la revisión independiente. |
| Equivalencia o consolidabilidad del par B1 | No bloquea esta unidad: se promete mapearlo, no sustituirlo. Sí bloquea una sustitución futura sin evidencia. |
| Dos `VERIFY` históricos del mapa | Se mantienen visibles. Bloquean cualquier cambio que dependa de resolverlos; no impiden por sí mismos cerrar esta clasificación. |
| Contrato literal `VERIFY` del helper `tests/_rf2_open_pause.py` | Deuda no bloqueante de esta unidad: se promete declararla, no resolverla. Se conserva la confianza baja. Su resolución futura requiere identificar y contrastar un contrato real; no se acredita por `validate rc=0`. |
| Baseline histórica sin mapa | Límite confirmado. PC-6 exige una revisión anterior válida, no resolver retrospectivamente la medición histórica. |
| Equivalencias y protección semántica fuera del lote | No verificadas y fuera del compromiso de esta unidad. |

## 8. deferred-hardening

- **Acreditación semántica exhaustiva:** excluida por el contrato del epic.
- **Poda, controles de sensibilidad y mutación del piloto:** corresponden a 013-003; aquí no se retiran tests.
- **Clasificador automático de equivalencias:** no es necesario ni acredita conservación.
- **Rediseño del chequeo histórico de conservación:** no se promete una garantía automática nueva; la conservación comprometida se verifica contra la revisión anterior en PC-6.
- **Resolución del contrato del helper `tests/_rf2_open_pause.py`:** se mantiene como deuda explícita, sin inventar respaldo; esta unidad promete su visibilidad.
- **Resolución de deuda temporal de 008-002:** no pertenece a esta unidad; se conserva su disposición.
- **Rendimiento, fixtures y paralelismo:** corresponden a decisión posterior y, en su caso, 013-004.
- **Obediencia infalible de agentes:** no se promete. Se verifican instrucciones distribuidas y evidencia exigida por los gates existentes.

Ningún diferimiento permite posponer PC-1–PC-8.
