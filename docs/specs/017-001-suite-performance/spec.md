---
feature_id: 017-001-suite-performance
status: draft
approved_by: null
approved_at: null
---

# Spec: Rendimiento de la suite

Borrador v3. No aprobado.

## 1. Descripción funcional

El responsable de la suite podrá conocer dónde se consume el tiempo y reducir la preparación repetida sin perder comprobaciones, transiciones contractuales ni aislamiento.

La entrega incluye:

- Instrumentación de `close`, con XML, resultados y duraciones por test y fase.
- Observación calibrada de operaciones comprometidas de preparación, incluidas operaciones ejecutadas dentro de `call`.
- Una línea base completa y recuperable, con sus límites de atribución explícitos.
- Atribución por test, archivo y actividad, conciliada con el tiempo exterior mediante residual explícito.
- Optimización serial de preparación, con comparación antes/después sobre selección idéntica.
- Decisión fundada sobre paralelismo: no se aplica sin justificación de costo y evidencia de seguridad.
- Corrida completa final verde atribuible.

No se promete todavía una reducción numérica. El dueño la fijará después de examinar la línea base, conforme a su decisión del 2026-11-07.

## 2. Autoridad, fuentes y límites

### Contrato

Rigen el plan aprobado del epic 017, su proyección de unidad y las cuatro decisiones registradas en `discovery-decisions-2026-11-07.md`.

El dueño autorizó la corrida base, la final instrumentada y las focales necesarias. Esa autorización no convierte una corrida fallida en evidencia suficiente ni habilita repeticiones completas rutinarias.

### Fuentes examinadas

Antecedente v1: snapshot `2a1b143a34c28cb58dba00200941d6195b008d5d`.

Corrección v2: revisión examinada `69b228869eab5efdc279007dca1d6ce423170f15`; cambio preexistente en `docs/.cdad-state.json`.

Entradas de la corrección v2:

- Spec v1: SHA256 `1cff418c36c6392645c5d66b524104681198a021f8d57caab5445b61ad9de273`.
- Plan v1: SHA256 `fe082bcd6ec7e01cd9b48bc5da77118fbe1cc6bc9201e8026c1b4b091e41416a`.
- `plan-review.md`, hallazgos 1–2: SHA256 `ae7ff32d9383d30a44eb7938902e482db1e536dd87cf7e5b6796580ac4506c76`.
- Proyección de unidad del paquete `017-001-suite-performance-architect-draft-002`: SHA256 `5524dfdde86a5314884690a5d3b13202be5034c0eadad1669d6f92ae2262d9b6`.

Corrección v3: revisión examinada `a4cab04fb214e8709ea2b5e0c01d6abe9268deac`; cambio preexistente en `docs/.cdad-state.json`.

Entradas de la corrección v3:

- Spec v2: SHA256 `581f96b2a84f1bc383171ced289bf741621c1ceea68a8c387b7f8579cfb1273b`.
- Plan v2: SHA256 `93ca1cb3280bb4a0f8abc713f9f51e04d989985e8fdee3b03d0e9d7c1ff11e47`.
- `plan-review-002.md`, hallazgo y cierre verificable: SHA256 `4af8dd35dfac8434b527adfc4ef2512f6f1d3b88a84d7e94405968b1fd9afc23`.
- Proyección de unidad del paquete `017-001-suite-performance-architect-draft-003`: SHA256 `5524dfdde86a5314884690a5d3b13202be5034c0eadad1669d6f92ae2262d9b6`.

La corrección v3 contrasta la precedencia serial y la aceptación final con el plan del epic, la decisión 3 del dueño y la re-revisión. Conserva el mapeo técnico heredado de v2 sin presentarlo como una nueva auditoría de implementación. No aporta mediciones de rendimiento ni demuestra seguridad paralela.

Fuentes de las decisiones y del mapeo:

- `docs/epics/epic-017-suite-performance/plan.md`, §§Alcance y Criterios de aceptación.
- `docs/specs/017-001-suite-performance/discovery.md`, §§2–6.
- `docs/specs/017-001-suite-performance/discovery-decisions-2026-11-07.md`, decisiones 1–4 y límites; SHA256 `3db97f7e3d071fb86f23cb32d9ff9917a2466d00279bbc191e975503c32a182a`.
- `docs/specs/013-003-redundancy-pilot/closure.md:9-16`.
- `docs/suite-maintenance.md`, §§Inventario vivo, Momentos de comprobación, Quién registra validate y Límites de los controles.
- `docs/ci-gate.md`, §§Qué corre, Cuándo el verde es atribuible y Costo y autorización.
- `docs/epics/epic-016-traceability-and-suite-review/integration.md:7-20,45-49`.
- `scripts/cdad-suite.py:777-948,954-999`.
- `scripts/cdad-ci-gate.py`, invocación y atribución del intento de `close`.
- `tests/conftest.py:28-126` y `tests/product_staging.py:30-92`.
- Los helpers y tests concretos citados en §3 y §4.2.

Las cifras históricas del discovery no constituyen una línea base actual. No acreditan ahorro ni seguridad paralela.

### Alcance de modificación propuesto

Los paquetes posteriores delimitarán rutas exactas y temporales:

- Implementación: `scripts/cdad-suite.py` y un observador pequeño bajo `scripts/` si resulta necesario.
- Tests y preparación de tests: únicamente archivos identificados por AUDIT, bajo `tests/`, mediante el test-writer.
- Producto documental: `docs/specs/017-001-suite-performance/performance/`.
- Evidencia cruda: directorios de intento nuevos en el workspace declarado por cada paquete.

La implementación no editará tests ni helpers bajo `tests/`. El test-writer no leerá implementación para construir su oráculo. El orquestador materializará los deltas documentales correspondientes.

Los contratos, decisiones aprobadas, registros históricos y evidencia cruda capturada son entradas protegidas: no se corrigen para obtener aceptación del informe.

### Exclusiones

No se eliminan, sustituyen ni consolidan tests. No se cambian contratos cerrados, expectativas, omisiones, deadlines contractuales ni transiciones comprobadas para ganar velocidad.

No hay publicación, instalación global, despliegue, acreditación semántica universal ni campaña universal de mutación.

## 3. Decisiones de diseño

### Instrumentación general de `close`, no un runner paralelo

Se propone instrumentar de forma fija y aditiva las invocaciones de `close`, incluidas las que realiza el gate existente.

La alternativa específica sería ejecutar pytest con opciones de medición mediante un wrapper separado. Se descarta porque permitiría medir una ruta distinta de la usada para acreditar el cierre y duplicaría responsabilidades.

La instrumentación general se limita a observación: no admite argumentos arbitrarios de pytest, no redefine selección ni crea otro veredicto.

Actualmente `close` fija el argv, elimina `PYTEST_ADDOPTS` y anula `addopts` (`scripts/cdad-suite.py:859-880`). Exportar opciones no satisface esta spec.

### Preparación reutilizable, estado mutable independiente

Se permite reutilizar una plantilla de bytes o resultado de preparación cuando sus entradas estén identificadas y ningún consumidor pueda modificar el recurso reutilizado.

Los proyectos, HOME, entornos e instalaciones mutables no se comparten como si fueran plantillas inmutables. Cuando un test necesite escribir, recibirá una copia propia.

No se fusionan todas las cachés por conveniencia. Una caché local ya puede ser la solución correcta si sus entradas o sus efectos difieren.

### Copias de producto, no exclusión indiscriminada de `.cdad`

Se medirá qué partes de `.cdad` entran realmente en las copias y cuánto cuestan. Solo se excluyen rutas demostradas ajenas a la preparación y a la promesa comprobada.

La regla será relativa a la raíz concreta de origen. No se aplicará un filtro global que borre también `.cdad` de fixtures o proyectos sintéticos.

Ejemplos que justifican revisar las copias:

- `tests/product_staging.py:57-81`.
- `tests/test_006_002_u1_delegation_section.py:169-205`.
- `tests/test_006_005_u4_single_entry.py:860-880`.

Otros helpers ya excluyen `.cdad`; no se les atribuirá ese costo sin medirlo.

### Regeneración contractual como excepción explícita

No se cachea la acción que el test debe observar.

Por ejemplo, `TestPd20DeterministicStaging` ejecuta dos generaciones y compara sus resultados (`tests/test_006_005_u4_single_entry.py:884-934`). Ambas generaciones seguirán siendo reales.

Tampoco se sustituirán procesos CLI por llamadas internas solo para reducir tiempo.

### Observación común con fronteras concretas, no profiler universal

Los intervalos usan un contrato común de identidad, contexto y anidamiento. Las fronteras concretas se fijan sobre los recorridos candidatos antes de la base.

La alternativa de medir únicamente fases es insuficiente: mezcla preparación y acción contractual dentro de `call`. La alternativa de observar indiscriminadamente todas las funciones y procesos excede la atribución acotada y puede añadir un costo innecesario.

Se comprometen intervalos relevantes y calibrables; lo demás permanece desconocido o residual, con la regla de decisión de §4.4.

### Serie primero; paralelismo condicionado

El aislamiento actual modifica entorno global del proceso (`tests/conftest.py`). No demuestra ejecución segura mediante hilos.

La alternativa paralela solo se evaluará después de ejecutar y medir la optimización serial. Esa precedencia ordena el trabajo: no exige alcanzar en serie el objetivo final antes de evaluar la alternativa.

Se descarta exigir éxito serial como condición de entrada a esa evaluación porque impediría considerar una mejora paralela útil y segura precisamente cuando el resultado serial fuese insuficiente, en contra de la decisión 3 del dueño.

Si se justifica, el paralelismo deberá usar separación de procesos y acreditar los recursos efectivamente compartidos. No se instala ni habilita un mecanismo concreto por suposición. Mantener obligatoriamente toda la solución en serie requiere una decisión expresa del dueño; no se infiere de la dependencia entre tareas.

## 4. Contrato de medición

### 4.1 Identidad y comparabilidad

Cada corrida registra:

- Revisión y estado del árbol.
- Comando exterior y argv efectivo de pytest.
- Lista ordenada de nodeids y su hash.
- Configuración efectiva, variables relevantes sin secretos, versiones de Python, pytest y plugins activos.
- Plataforma, recursos disponibles y carga observada.
- Estado inicial del staging: ausente o presente, con procedencia y hash del manifiesto; presencia no equivale a frescura.
- Política de cachés: proceso nuevo, entradas disponibles y reutilizaciones.
- Volumen auxiliar de `.cdad` relevante para las copias: rutas, cantidad de archivos, bytes y método de conteo.
- Alcance de operaciones observado y referencia a su calibración.
- Resultados, fallos, skips y sus motivos.
- Ubicación y hashes de los artefactos crudos.

La evidencia viva y los temporales de medición no deben convertirse recursivamente en entradas de una copia de producto.

Cada corrida completa tiene una revisión fijada. Base y candidata pueden ser revisiones distintas, pero su diferencia debe ser recuperable y limitada a los cambios declarados.

Toda comparación de rendimiento exige selección y orden idénticos, instrumentación equivalente y condiciones iniciales descritas. Si cambian, se declara qué comparación deja de ser válida.

No se recorta la colección final para aparentar comparabilidad. Si aparecen verificadores nuevos tras la base:

- La corrida final sigue ejecutando toda la colección vigente.
- Se conservan comparaciones focales antes/después sobre la misma selección.
- No se presenta el cociente de los totales completos como comparación de selección idéntica.
- Si el objetivo aprobado exige esa comparación completa, se resuelve la incompatibilidad con el dueño antes de consumir la corrida final; una nueva base no queda autorizada automáticamente.

### 4.2 Artefactos de `close` y alcance calibrado

Propuesta de interfaz nueva, no descripción de una API existente.

Cada intento conserva los artefactos actuales y agrega:

- `pytest.xml`: resultados y duración total por caso.
- `profile.json`: mediciones y diagnóstico de su integridad.

`profile.json` tendrá al menos:

- `schema_version`.
- `status`: `complete` o `incomplete`.
- `diagnosis`: motivo cuando la medición no sea completa.
- `pytest_argv`: argv efectivo.
- `pytest_wall_s`: tiempo monotónico alrededor del proceso hijo.
- `phases`: registros con `nodeid`, `when` (`setup`, `call`, `teardown`), `duration_s` y `outcome`.
- `operations`: intervalos observados de preparación o espera deliberada, identificados por operación, contexto, comienzo, fin y relación de anidamiento cuando corresponda.
- Referencia inequívoca al alcance de operaciones aplicado y su versión o hash.

Se conservan las fases realmente emitidas. Una fase no ejecutada se distingue de una fase ejecutada con duración cero. La preparación fuera de un test se identifica como compartida, no se adjudica arbitrariamente.

El log incluye duraciones sin limitarse a los casos más lentos. El XML no sustituye el registro de fases ni se usa para reconstruir nodeids ambiguos: su correspondencia con la selección se comprueba durante la calibración.

#### Registro previo de operaciones

Antes de consumir la base se conserva `performance/operation-scope.json`. Es un registro de alcance, no una afirmación de cobertura universal.

Cada entrada identifica:

- Operación y familia candidata.
- Fuente y frontera de comienzo/fin; contexto de test, fase o preparación compartida.
- Clasificación: preparación, acción contractual, espera deliberada o desconocida.
- Mecanismo de observación propuesto, productor responsable y límites.
- Estado: comprometida para medir o desconocida expresamente.
- Selección focal y recorrido que permite calibrarla, con ocurrencias y relaciones esperadas cuando sean conocidas.
- Regla de decisión si permanece desconocida.

El registro debe resolver, sin omitir silenciosamente, estas familias identificadas:

1. Construcción y preparación inicial de proyectos dentro de `call`, incluidos los recorridos de `_RecoveryProject` y `_Project` (`tests/test_007_002_dispatch_recovery.py:409-426,506-518`; `tests/test_007_003_continuity_at_edges.py:490-537`).
2. Copias, generación de staging y reutilización de los helpers candidatos de §3.
3. Regeneraciones que son acciones contractuales y no preparación eliminable.
4. Esperas deliberadas relevantes para la atribución; si no se observan, su costo permanece desconocido.

Se compromete como mínimo la observación de preparación real dentro de `call` en recorridos candidatos conocidos. No es admisible declarar todas las operaciones desconocidas ni cumplir este mínimo con un ejemplo sintético ajeno a esos recorridos.

Una familia puede quedar parcialmente desconocida si se identifica qué parte falta, por qué no puede observarse sin alterar la transición y cómo se decidirá sin atribuirle un costo ficticio.

#### Calibración anterior a la base

La calibración conserva selección ordenada, revisión, condiciones, artefactos y un contraste esperado/observado.

Comprueba:

- Correspondencia entre selección, nodeids, XML, resultados y fases emitidas.
- Presencia de los intervalos comprometidos en recorridos que realmente los ejercitan.
- Identidad, contexto, comienzo/fin y anidamiento correctos.
- Distinción entre preparación, acciones contractuales y operaciones compartidas.
- Ausencia de doble conteo y conservación de los efectos y transiciones observados.
- Registro de rutas no ejercitadas y operaciones desconocidas, sin convertir su ausencia en duración cero.

Para los recorridos comprometidos de preparación dentro de `call`, una selección conocida debe emitir intervalos no vacíos, correctamente atribuidos. Un perfil solo de fases o una lista vacía de operaciones no satisface esa calibración.

La calibración valida fidelidad y contabilidad, no una duración exacta ni un ahorro. No usa umbrales temporales estrechos como oráculo.

La API concreta del observador y las opciones compatibles con la versión instalada de pytest son VERIFY de implementación. Deben resolverse y demostrarse en focal antes de la base.

### 4.3 Semántica conservada

Se mantienen:

- Selección por capacidad, archivo de nodeids o colección completa.
- Reserva exclusiva de un intento por invocación.
- Campos y significado actuales de `attempt.json`.
- Salidas parciales, resultados, motivos de skip y canarios.
- Neutralización de opciones heredadas que oculten las líneas necesarias para el resumen.
- Propagación del resultado de pytest y tratamiento vigente de errores de uso e interrupciones.
- Atribución del gate existente, sin segundo pytest.

Los nuevos campos y referencias son aditivos. No se renombran ni reinterpretan campos existentes.

Un perfil ausente, parcial o inconsistente impide acreditar la medición, aunque el resultado contractual de pytest sea verde. No se sustituye su rc por un supuesto éxito del perfil ni se oculta un fallo de instrumentación.

Una entrega intermedia de XML y fases puede ser útil, pero no acredita por sí sola una base ni completa PC-1.

### 4.4 Atribución, conciliación y entrada a la base

La ejecución serial permite sumar las duraciones observadas de las fases sin confundirlas con el tiempo exterior.

Se distinguen:

1. Preparación interna medida, incluso dentro de `call`.
2. Esperas deliberadas medidas.
3. Resto de las fases: ejecución no desglosada y sobrecosto interior pendiente de atribución.
4. Sobrecosto fuera de las fases: colección, arranque, finalización, controlador y evidencia, donde estén medidos.
5. Residual no atribuido, con alcance y signo explícitos.

Los deadlines configurados y los `sleep` escritos en el código no se contabilizan como tiempo observado. Solo se atribuye espera efectivamente medida.

Los intervalos anidados o solapados no se suman dos veces. El tiempo de un proceso hijo ya incluido en una operación padre se informa como desglose, no como costo adicional.

Para cada test:

- `S_test` es la suma de sus fases observadas.
- La preparación y espera identificadas son subconjuntos disjuntos de ese tiempo.
- Su resto se conserva explícitamente.

Para cada archivo:

- `S_file` es la suma de `S_test` de sus nodeids.
- Las operaciones compartidas externas a esos tests permanecen separadas.

Para la corrida:

- Se mide `T_pytest` alrededor del proceso hijo.
- `R_pytest = T_pytest - suma(S_test)`.
- Se mide `T_exterior` alrededor del comando completo.
- `R_exterior = T_exterior - T_pytest`.

Los intervalos identificados dentro de esos residuos se desglosan sin volver a sumarlos. Lo no identificado permanece como residual.

El informe declara fronteras de cada reloj, resolución, redondeo y límites de observación. Una discrepancia superior a la precisión declarada se diagnostica; no se fuerza a cero ni se presenta una identidad aritmética como explicación causal.

La atribución ordena archivos y tests por costo, identifica la preparación medida y localiza las principales incertidumbres. No extrapola una muestra focal a toda la suite.

#### Condición de entrada a la base

El orquestador no inicia la corrida base hasta disponer de:

- Registro de operaciones fijado, con compromiso mínimo de preparación dentro de `call`.
- Calibración focal satisfactoria de todos los intervalos comprometidos sobre recorridos conocidos que los ejerciten.
- Método de agregación reproducible y comprobado sobre esa evidencia focal.
- Desconocidos identificados, responsables y reglas de decisión documentados.
- Revisión, selección, condiciones y ubicación de evidencia fijadas.

La ausencia de un intervalo esperado bloquea la base hasta corregir y recalibrar. No se declara desconocido retrospectivamente para aceptar una calibración fallida.

En la corrida base se contrasta nuevamente el alcance declarado con lo realmente observado. Un recorrido no ejercitado se distingue de un fallo de captura; si falta un intervalo que debía emitirse, la medición queda incompleta.

#### Decidir cuando algo permanece desconocido

Una operación desconocida permanece dentro del resto o residual correspondiente; no se etiqueta como preparación medida ni como ejecución contractual por descarte.

Puede elegirse una optimización solo por el costo observado que la respalda. Si la elección o el objetivo dependen de una operación desconocida, se detiene esa decisión y se propone una focal adicional sobre revisión base recuperable, antes de modificarla.

Esa focal exige selección y condiciones explícitas, calibración del nuevo intervalo y contraste antes/después equivalente. No añade retroactivamente intervalos a la corrida completa base ni autoriza otra corrida completa.

Si no existe costo reducible suficientemente observado para elegir una optimización, se informa el bloqueo. No se decide por tamaño de archivos, cantidad de nodeids o intuición.

## 5. Postcondiciones por promesa observable

### A. El responsable obtiene mediciones sin cambiar el cierre

<!-- cdad:pc PC-1 promise=A -->
**PC-1.** Una selección focal conocida ejecutada mediante `close` produce XML y perfil recuperables, con correspondencia verificable entre nodeids, resultados y fases emitidas. Además, los recorridos candidatos comprometidos de preparación dentro de `call` producen los intervalos esperados, correctamente identificados, contextualizados y contabilizados según §4.2. La ausencia de intervalos esperados o una medición incompleta impiden acreditar la calibración y la base.

<!-- cdad:pc PC-2 promise=A -->
**PC-2.** La instrumentación conserva la semántica de §4.3: selección, rc, skips, interrupciones, reserva independiente, logs y canarios. Su integración no agrega otra ejecución de pytest al gate.

### B. El responsable dispone de una línea base reproducible

<!-- cdad:pc PC-3 promise=B -->
**PC-3.** Solo después de satisfacer la condición de entrada de §4.4 se conserva una corrida completa terminada sobre revisión fijada, con colección efectiva, resultados y todos los metadatos de §4.1. La evidencia vincula el registro de operaciones y su calibración con los intervalos realmente capturados. Otro responsable puede reconstruir el comando y las condiciones declaradas sin depender de temporales desaparecidos.

<!-- cdad:pc PC-4 promise=B -->
**PC-4.** Después de examinar la base y antes de aceptar una optimización, el dueño registra el objetivo de reducción, la magnitud medida, selección de comparación, condiciones y regla de evaluación. La decisión identifica los límites de atribución que puedan afectarla. Hasta entonces no se afirma que una reducción determinada sea suficiente.

### C. El responsable puede localizar el costo sin cifras ficticias

<!-- cdad:pc PC-5 promise=C -->
**PC-5.** El informe incluye todos los nodeids de la base con sus fases observadas, agregación por archivo y clasificación de las operaciones medidas en preparación, espera deliberada y resto. Contrasta captura y alcance comprometido; identifica operaciones no ejercitadas y desconocidas con sus límites. Preparación dentro de `call` no se clasifica automáticamente como verificación contractual, y una ausencia de captura no se presenta como costo cero.

<!-- cdad:pc PC-6 promise=C -->
**PC-6.** La conciliación de §4.4 se reproduce desde la evidencia cruda mediante un comando y método versionados, previamente comprobados sobre la calibración focal. No hay doble conteo y toda diferencia conserva residual y diagnóstico. Las operaciones no medidas no se presentan como costos explicados ni como fundamento de una optimización sin resolver la decisión correspondiente.

### D. La preparación tarda menos sin perder comprobaciones

<!-- cdad:pc PC-7 promise=D -->
**PC-7.** Cada optimización aplicada identifica el costo medido que pretende reducir, las entradas y alcance de la caché o copia, sus consumidores y las transiciones que deben permanecer reales. El contraste focal antes/después usa idénticos nodeids y orden, instrumentación equivalente, y registra valores absolutos, diferencia, condiciones y límites. Si necesita una operación antes desconocida, se aplica la regla de §4.4 antes de modificar la preparación.

<!-- cdad:pc PC-8 promise=D -->
**PC-8.** Primero se ejecuta y mide la optimización de preparación serial, con resultados contractuales conservados. Su balance registra el resultado frente al objetivo de PC-4, el costo residual observado y, cuando corresponda, la reducción aún pendiente. Ese resultado medido permite evaluar PC-9 aunque todavía no alcance el objetivo final; no acredita por sí solo la aceptación de §7. La evidencia incluye el costo y volumen de `.cdad` en las copias afectadas; una exclusión no elimina fixtures o estado necesarios ni comparte recursos mutables entre tests.

### E. El paralelismo es una decisión fundada, no una suposición

<!-- cdad:pc PC-9 promise=E -->
**PC-9.** Tras ejecutar y medir la optimización serial se registra una decisión sobre paralelismo, basada en costo residual y objetivo pendiente, incluso si el resultado serial aún no alcanza ese objetivo. Si no se justifica, no se demuestra seguro o no puede evaluarse dentro del mandato, se declara y no se aplica. Una restricción de mantener obligatoriamente toda la solución en serie debe constar como decisión expresa del dueño, no como condición implícita del plan. Ninguna decisión de no aplicar paralelismo dispensa del objetivo final ni de las garantías.

<!-- cdad:pc PC-10 promise=E -->
**PC-10.** Si se aplica paralelismo, la entrega incluye inventario de recursos compartidos y evidencia concurrente sobre los consumidores afectados: HOME/XDG/TMP separados, copias mutables independientes, cachés sin escrituras compartidas, procesos finalizados y evidencia por intento sin colisiones. Se mide también el costo de reconstruir cachés por worker y el resultado neto; sumar tiempos concurrentes no se presenta como tiempo de pared.

### F. El resultado sigue protegiendo los mismos contratos

<!-- cdad:pc PC-11 promise=F -->
**PC-11.** El diff y la revisión independiente confirman ausencia de poda, debilitamiento de aserciones, omisiones nuevas para ganar tiempo, reducción de esperas contractuales o sustitución de acciones verificadas por cachés. Los contratos cerrados permanecen intactos.

<!-- cdad:pc PC-12 promise=F -->
**PC-12.** La revisión candidata final conserva una corrida completa instrumentada verde atribuible, con skips declarados y canario examinado, más la integridad del inventario vivo sobre esa revisión. El cierre distingue control estructural, ejecución real y revisión semántica acotada; no atribuye a uno las garantías del otro.

## 6. Invariantes verificables

- **INV-1 — Identidad:** toda cifra remite a intento, revisión, selección y método recuperables.
- **INV-2 — Conservación:** optimizar preparación no altera obligaciones, aserciones, efectos ni transiciones comprobadas.
- **INV-3 — Aislamiento:** no se reutiliza estado mutable entre tests; no se escribe preparación en el checkout ni en el HOME del operador.
- **INV-4 — Caché válida:** la reutilización tiene entradas y vida útil identificadas; una preparación cuya ejecución sea parte de la promesa no se sustituye por caché.
- **INV-5 — Contabilidad:** un intervalo contribuye una sola vez al total; los desgloses no se suman nuevamente.
- **INV-6 — Honestidad:** ausencia de medición no equivale a cero, perfil incompleto no equivale a base válida y omisión no equivale a pase.
- **INV-7 — Separación:** quien implementa no modifica su verificador; quien produce el informe no modifica sus fuentes de aceptación.
- **INV-8 — Calibración previa:** ningún intervalo se presenta como comprometido y válido para la base sin evidencia focal previa sobre un recorrido conocido que lo ejercite.

## 7. Verificación y aceptación

AUDIT identificará primero los verificadores reutilizables. Por ejemplo, `tests/test_008_002_suite_evidence.py` ya comprueba preservación de intentos, concurrencia de reservas, selección, skips e interrupciones; eso no demuestra todavía la instrumentación nueva.

Los tests se seleccionan por promesa observable, sin exigir uno por PC ni variantes equivalentes. Los verificadores nuevos se derivan de esta spec y declaran su contribución respecto de los existentes.

La verificación combina:

- Calibración focal con resultados, fases e intervalos comprometidos conocidos.
- Contraste entre alcance declarado y operaciones efectivamente capturadas.
- Evidencia completa base y final.
- Comparaciones focales antes/después.
- Recálculo determinista de la atribución.
- Revisión independiente de los helpers y transiciones afectados.
- `python3 scripts/cdad-suite.py validate` en los momentos y responsables de `docs/suite-maintenance.md`.

No se usan umbrales temporales estrechos como oráculo de corrección. El rendimiento se evalúa mediante el objetivo y método aprobados después de la base.

La aceptación requiere PC-1–PC-12, los invariantes y que la solución final satisfaga el objetivo registrado en PC-4 sobre su selección, condiciones y regla de evaluación aprobadas. La solución final puede ser serial o combinar la optimización serial con paralelismo justificado y seguro conforme a PC-9–PC-10.

Cumplir PC-8 acredita la ejecución y medición previas de la optimización serial, no necesariamente el objetivo final. Un resultado serial insuficiente permite pasar a la evaluación de PC-9, pero no aceptar la feature. La decisión «sin paralelismo» puede satisfacer PC-9–PC-10, pero no dispensa de alcanzar el objetivo final. Si el dueño exige mantener toda la solución en serie, esa restricción debe quedar registrada expresamente.

Los desconocidos admitidos son límites de atribución declarados, no dispensas de una promesa comprometida. Si impiden elegir o verificar la optimización, bloquean esa decisión hasta aplicar §4.4.

Si el objetivo no puede alcanzarse sin perder garantías, se informa el bloqueo y se solicita decisión del dueño; no se rebaja unilateralmente.

## 8. VERIFY y decisiones pendientes

- **API de observación y opciones de pytest:** implementer, con verificación focal independiente. Bloquea la base hasta demostrar compatibilidad y fidelidad.
- **Fronteras y selección de operaciones:** arquitecto para mapeo técnico; test-writer para oráculo independiente. Se resuelve antes de la base mediante registro de alcance y calibración satisfactoria.
- **Operaciones expresamente desconocidas:** responsable identificado por entrada. No bloquean documentar su desconocimiento; sí bloquean decisiones o aceptación que dependan de atribuirles un costo.
- **Objetivo de reducción:** dueño, después de la base. Bloquea aceptación del rendimiento; no bloquea instrumentación ni medición.
- **Preparación realmente dominante:** medición base. Bloquea elegir una optimización por intuición.
- **Comparabilidad efectiva:** responsable de las corridas. Bloquea cualquier cociente antes/después cuyo alcance no coincida.
- **Seguridad paralela:** solo bloquea aplicar paralelismo; la alternativa serial permanece disponible.

Estos pendientes no se convierten en resultados por aprobar este borrador.

## 9. deferred-hardening

- **Campaña estadística de corridas completas repetidas y múltiples hosts:** fuera del mínimo autorizado. Se informan condiciones y límites de las observaciones; no se promete significancia estadística.
- **Profiler universal de todos los procesos y operaciones:** no es necesario para la atribución acotada. No difiere el registro y calibración previos de las operaciones comprometidas; las restantes conservan desconocimiento o residual explícito.
- **Optimización de toda caché existente:** no se migra masivamente sin evidencia de costo y conservación.
- **Reducción de presupuestos de propiedades:** no se aplica por cantidad de nodeids ni por intuición. Si la base demuestra que domina el costo, se presenta una propuesta concreta con conservación verificable y aprobación antes de cambiar presupuestos.
- **Garantía universal de confinamiento o ausencia de escrituras transitorias:** el canario y los controles actuales no la ofrecen. Se revisan recursos y efectos concretos, sin describirlos como sandbox.
- **Poda, reescritura de contratos y publicación:** excluidas por el contrato del epic, no pendientes de esta unidad.

Ningún diferimiento posterga una promesa comprometida.
