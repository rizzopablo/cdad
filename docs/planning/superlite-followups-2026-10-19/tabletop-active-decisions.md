# Prueba de escritorio: decisiones activas como dependencias

Fecha: 2026-10-19. Estado: **propuesta / prueba de escritorio; no activa ni modifica 006-004**.

Al inicio de este encargo, 006-004 figuraba `queued`. El plan ya define su alcance y aceptación; si el trabajo fue despachado desde entonces, esta nota sigue siendo evaluación externa y no altera su diseño, contratos ni autoridad. No es spec, aprobación ni encargo de implementación.

## Lente de planificación

La inspiración de Superlite se limita aquí a planificar por resultados completos y hacer visibles sus dependencias productor→consumidor. No presupone que más tareas o paralelismo sean mejores. Esto es compatible con el borrador local de planificación: cada entrada debe tener productor, consumidor y verificación, y la división debe justificar su costo de coordinación ([contrato de planificación](../../epics/epic-004-single-source-planning/planning-contract-draft.md), líneas 43–59 y 146–165). El material real de 006-004 ya concreta una fila de decisiones, su mantenimiento, distribución por rol y revisión; también incorpora el principio general-antes-que-específico ([plan del epic](../../epics/epic-006-opencode-concurrency/plan.md), líneas 273–285 y 311–326).

## Dependencias que no conviene mezclar

- **Contrato:** qué representa una decisión, cómo se declara vigente u obsoleta y qué resumen/roles necesita cada fila. Lo produce la spec aprobada bajo autoridad; lo consumen orquestador, paquetes por rol y reviewer. Una lista de archivos tocados no reemplaza este contrato.
- **Implementación:** plantilla de `systemPatterns.md`, mantenimiento al aprobar/reemplazar ADR, distribución y referencias instalables. El implementer consume contrato y RED; produce cambio revisable. Es una dependencia de código/documentos, no una autorización para decidir el contenido de un ADR.
- **Evidencia:** correspondencia de cada ADR con su fila y estado; filas entregadas al rol correcto; y consistencia entre decisión metodológica y regla instalable. La produce la validación asignada y la consume el reviewer. Que una fila exista no prueba que el rol la recibió; que el paquete la lleve no prueba que coincida con la fuente.
- **Autoridad:** el dueño aprueba ADR y alcance; el orquestador registra lo aprobado. La aprobación es entrada previa, no salida que pueda fabricar una tarea de documentación. La revisión independiente comprueba coherencia, pero no aprueba por el dueño.

Ejemplo productor-consumidor: dueño → ADR aprobado; orquestador → fila vigente y obsolescencia de la reemplazada; preparación de paquete → subconjunto de filas nombradas para el rol; rol → trabajo bajo esas decisiones; reviewer readonly → cotejo ADR↔tabla↔paquete y respeto en el cambio. Si el ADR altera metodología, su regla instalable tiene que ser otro producto explícito, con su propio productor y evidencia. Esta cadena refleja las responsabilidades de 006-004, no un defecto observado.

## Sketch ilustrativo, no descomposición aprobada

Una posible división por resultados completos sería: **A, decisión distribuible** (tabla mantenible, roles destinatarios y paquete que la consume); **B, coherencia demostrable** (cotejo de la tabla con ADR vigentes/obsoletos y comprobación de que los cambios respetan las decisiones). B consume A. Una decisión metodológica que requiera nueva regla instalable agrega un resultado enlazado, no una fila que finja completarlo. El encargo real ya agrupa estas obligaciones en 006-004; esta división solo sirve para probar el razonamiento.

El paralelismo legítimo parece escaso. A y B comparten el contrato de fila y artefactos de referencias; B necesita la forma final de A. Puede adelantarse análisis de cobertura del reviewer mientras se prepara A, pero la verificación de unión espera a la integración. Si especificar, transferir contexto y reconciliar cambios cuesta más que la independencia ganada, mantener un solo resultado es mejor. El plan real de 006-005 muestra la disciplina pertinente: declara productores/consumidores y secuencia cuando un resultado depende de otro; además serializa tareas que comparten archivo ([plan 006-005](../../specs/006-005-native-path-parity/plan.md), líneas 8–26). No se infiere una falla de 006-004 ni se atribuye ningún baseline a tokens o tiempo.

## Paquetes mínimos por rol y evidencia de unión

- **Architect:** intención, plan vigente, ADR y autoridad disponibles, plantillas/referencias consumidoras, límites y aceptación. Debe proponer contratos y dependencias; no asumir que una decisión está aprobada por estar documentada.
- **Test-writer independiente:** contrato aprobado, ejemplos de ADR vigente/reemplazado, expectativas de distribución por rol y resultado observable. Sin implementación nueva; entrega pruebas antes del cambio.
- **Implementer:** contrato, RED, archivos y permisos autorizados, decisiones vigentes aplicables y consumidores que debe actualizar. No cambia decisiones ni tests.
- **Reviewer readonly:** intención, contrato aprobado, diff, ADR pertinentes, tabla y paquetes/artefactos de salida. Comprueba uniones y reporta; no escribe ni sustituye aprobación del dueño.
- **Orquestador/dueño:** el primero necesita el ADR aprobado y el estado de los consumidores; el segundo recibe la propuesta y evidencia necesaria para resolver decisiones reservadas.

La evidencia integrada debería permitir seguir una decisión desde ADR aprobado a fila, del filtro de destinatarios al paquete, y de ahí a la revisión del cambio; incluir reemplazo/obsolescencia y la referencia instalable cuando aplique. La aprobación queda registrada aparte. CDAD conserva test-writer independiente, reviewer readonly y aprobación del dueño; el contexto se da según necesidad, sin techo universal y sin requisito de familia o modelo.

## Límites y pendientes

No se inspecciona ni cambia estado de ejecución en esta prueba. No se escriben código, tests anticipados, firmas ni schema exactos. Pendiente para una futura spec: forma mínima de fila, fuente verificable de destinatarios, tratamiento de ADR obsoleto o en disputa, y oráculo de que el paquete realmente consumió la tabla. Resolver solo lo necesario para que cada consumidor trabaje y pueda demostrarlo.

La futura aceptación debería demostrar: cada ADR relevante aparece una vez con estado y reemplazo coherentes; cada rol recibe exactamente las decisiones que le aplican; una obsolescencia se refleja en tabla y paquete; reviewer puede detectar una contradicción sin editar; un cambio metodológico apunta a regla instalable; y la aprobación no se confunde con revisión o entrega. Los criterios son propuestas, no gates vigentes.

Referencias de esta serie: [inventario](inventory.md) y [plan](plan.md).
