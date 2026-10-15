# Discovery de 005-007: planificación eficaz y aceptación de uso

Fecha: 2026-10-11. Estado: **encargo de investigación y criterios de diseño**,
no spec aprobada ni diseño interno obligatorio.
Dirección: [prioridades del dueño](../../../findings/agent-operation-strategy-2026-10-11.md).

## 1. Problema que debe resolver

El dueño considera insuficiente la mejora anterior centrada en templates.
Busca planificación avanzada con una superficie de uso simple: transformar
un objetivo amplio en unidades completas, eficientes, integrables y comprobables
sin perder el alcance global. Menos contexto debe provenir también de mejores
unidades de trabajo, no solo de compactar los prompts.

CDAD ya tiene epic/feature/tarea, dependencias, Consumes/Produces y plan-review
(004-003). Reusar esos niveles y mecanismos. No vender su renombrado como una
capacidad nueva; tampoco crear un planner separado sin demostrar su necesidad.

## 2. Preguntas que el discovery debe resolver

1. ¿Cuál es el recorrido del consumidor y la primera porción que puede usar de
   punta a punta? ¿Qué resultado intermedio reduce incertidumbre o entrega valor?
2. ¿Qué parte del problema desconocemos? ¿Una sonda pequeña cambiaría la división
   o evitaría trabajo grande sobre una premisa falsa?
3. ¿Qué contratos/datos comparten las unidades? ¿Qué decisiones tienen que estar
   tomadas para que otra unidad trabaje sin inventarlas?
4. ¿Cuánto contexto necesita cada unidad y por qué? Estimar clases/volumen de
   entradas y contrastar después con el uso; no inventar precisión de tokens.
5. ¿Qué unidades son realmente independientes? Considerar decisiones, datos,
   archivos, entorno de pruebas, recursos y forma de integrar, no solo paths.
6. ¿Quién comprobará cada resultado y cuándo? ¿Qué trabajo puede adelantarse
   mientras espera y cuál depende de una validación todavía no hecha?
7. ¿Qué aprendizaje obliga a replanificar y qué decisiones pueden postergarse?
   Conservar objetivo completo y razones; detallar solo lo ejecutable próximo.

## 3. Líneas avanzadas que vale contrastar

Investigar y seleccionar lo útil; esta lista no obliga a implementar todas.

| Enfoque | Hipótesis aplicable a CDAD | Costo o límite a contrastar |
|---|---|---|
| Unidades verticales y mapa de alcances | Construir una porción integrada utilizable antes de completar capas enteras | Infraestructura compartida puede necesitar una unidad habilitadora con consumidor explícito |
| Planificación por dependencias y camino crítico | Separar listo/bloqueado/pendiente y adelantar trabajo independiente | Más workers no reduce tiempo si comparten decisiones o generan integración costosa |
| Reducción temprana de incertidumbre | Probar la interfaz externa o hipótesis más arriesgada antes de una construcción grande | La sonda debe contestar una pregunta y tener condición de fin |
| Descomposición jerárquica progresiva | Alcance global estable, detalle local revisable; razones y supuestos recuperables | No generar un árbol exhaustivo de microtareas ni una ontología nueva |
| Partición por contexto y acoplamiento | Minimizar contexto duplicado y dependencias entre sesiones conservando unidades completas | Estimaciones imperfectas; fragmentar también consume tokens y revisiones |
| Planes alternativos pequeños | Comparar dos particiones cuando haya una decisión material de arquitectura/alcance | No exigir varias propuestas para tareas obvias ni repetir implementaciones |
| Valor de información / decisiones reversibles | Resolver pronto lo que invalida trabajo; diferir detalle de bajo riesgo | No sustituir juicio por una puntuación opaca con números inventados |

La evaluación considera costo total: ejecución, orientación, handoffs, revisión,
integración, retrabajo y atención humana. No elegir por mínimo número de tareas,
máximo paralelismo, líneas de código o un límite universal de archivos.

Como fuentes iniciales consultadas:
[Shape Up: Get One Piece Done](https://basecamp.com/shapeup/3.2-chapter-11)
propone integrar una porción antes de avanzar por capas;
[Map the Scopes](https://basecamp.com/shapeup/3.3-chapter-12) organiza el trabajo
en alcances completables. Son puntos de partida, no una metodología que se
importe entera. La investigación debe buscar también límites y alternativas.

## 4. TDD, E2E técnico y usabilidad: evidencias distintas

TDD puede incluir pruebas E2E. No demuestra automáticamente que la necesidad
esté bien formulada ni que el consumidor descubra cómo usar la solución.
Una prueba contra un doble verifica supuestos del doble; su fidelidad a una
interfaz externa necesita evidencia independiente. Caso de referencia:
005-009/005-010, sin reabrir aquí su contrato ni repetir su desarrollo.

| Pregunta | Evidencia apropiada | Qué no permite afirmar sola |
|---|---|---|
| ¿Cumple el comportamiento contratado? | Tests derivados del contrato, revisión y evidencia técnica vigente | Que ese contrato resuelve la necesidad correcta |
| ¿Se conectan las piezas reales? | Recorrido instalado con adaptador/runtime y entradas reales o representativas | Que el consumidor entiende la interfaz sin asistencia |
| ¿Se puede lograr el objetivo con esfuerzo razonable? | Tarea representativa, observación de uso, errores, recuperaciones y ayudas necesarias | Usabilidad humana validada si solo participó un agente |
| ¿La entrega sirve en su contexto? | Confirmación o evidencia del consumidor identificado y limitaciones | Generalización a todos los usuarios/entornos |

La investigación de usabilidad usa tareas y participantes representativos;
[NN/g: Usability Testing 101](https://www.nngroup.com/articles/usability-testing-101/)
es una fuente inicial. Un agente en sesión fresca sirve como consumidor de una
interfaz para agentes y como sonda de fricciones; no reemplaza automáticamente
a una persona cuando el producto está dirigido a personas.

### Receta mínima a diseñar y probar

- Definir actor, objetivo, punto de partida legítimo, entorno/versión y evidencia
  de éxito. Dar una tarea realista, no las instrucciones internas que garantizan
  que el test conozca todos los atajos.
- Ejercitar un recorrido representativo con la documentación que recibirá el
  consumidor. Registrar ayudas extraordinarias, errores y recuperación.
- Elegir pocos casos por riesgo: camino principal y bloqueo/recuperación relevante.
  Una batería grande de navegadores o escenarios no es requisito automático.
- Separar comprobación automática repetible de observación exploratoria o humana.
  Registrar limitaciones y aceptación pendiente sin convertirlas en un verde.
- Verificar la frontera externa con una sonda real pequeña antes de congelar
  dobles que podrían modelar un protocolo inventado.
- Probar el mismo artefacto/versionado que se entrega. Reutilizar evidencia
  equivalente; invalidar solo lo afectado por un cambio.

La interrupción por un defecto material se decide por su efecto sobre el
objetivo. Preferencias estéticas o variantes hipotéticas quedan en deuda
proporcional. No generar una nueva espiral de review ni exigir una prueba
humana por cada tarea interna. Si faltan acceso o participante, declarar el
límite y qué parte de la aceptación queda pendiente, con responsable.

## 5. Salidas y criterio de suficiencia de la investigación

1. Diagnóstico de los procedimientos actuales: qué criterio falta, dónde vive
   y qué consumidores deben recibirlo. No agregar otra copia de reglas.
2. Comparación breve y fundamentada de enfoques: problema que resuelve cada uno,
   evidencia/fuentes, límites y propuesta mínima elegida.
3. Aplicación a la próxima unidad real pendiente: unidades con resultado,
   dependencias, incertidumbre, insumos/contexto y aceptación. Las unidades
   habilitadoras nombran su consumidor y su comprobación de integración.
4. Plan legible por el humano: objetivo → recorrido → unidades/orden → decisiones
   y riesgos. Detalle técnico por demanda; representación visual si ayuda.
5. Plan de aceptación proporcional que distinga contrato, integración y uso;
   productor de cada insumo, actor evaluador y evidencia de cierre.
6. Medidas de seguimiento disponibles: tiempo al primer resultado útil,
   bloqueos, retrabajo de integración, contexto por rol y atención humana.
   Desconocido se conserva. Comparar con trazas históricas sin atribuir
   causalidad fuerte a tareas distintas.

La spec de 005-007 debe seleccionar una mejora implementable y su primer uso.
Si necesita un evaluador de usabilidad general, un scheduler o integración UI
compleja, proponer un ciclo posterior. La investigación de esos temas no
equivale a autorización de construcción. No cerrar 005-007 solo porque hay
una plantilla más larga o un validador que encuentra sus títulos.

## 6. Consumo y restricciones

Incluir este documento como insumo explícito del architect, junto al plan del
epic, 004-003 y la evidencia disponible de 005-002/003. El resultado de medición
enriquece la evaluación; no obliga a repetir el discovery de otra feature.

No introducir un agente planner obligatorio, perfiles de modelo nuevos,
aislamiento por repo para todos los agentes, servicios permanentes, OnlyOffice
ni una UI nueva dentro de esta feature. Conservar mandato, revisión independiente,
contexto por rol y validación proporcional. La replanificación mantiene trazabilidad
y no modifica contratos de trabajos ya despachados sin reconciliación.
