# Propuesta de continuación — planificación y ejecución proporcional

Fecha: 2026-10-19. Estado: **propuesta diferida, sin activación ni aprobación de contratos**.
Origen: análisis de Superlite y dirección del dueño de preparar mejoras mientras
termina el desarrollo/fix vigente. No reserva números de epic o feature, no altera
el backlog activo y no concede una delegación HITL de ejecución.

Actualización 2026-10-21: por instrucción del dueño, la retrospectiva del caso
S-SYS-01 y su relación con las observaciones históricas pasan a ser **material
necesario de esta planificación**. Su incorporación no aprueba todavía los epics,
sus specs ni su ejecución.

## 1. Material de entrada

- [Hallazgo comparativo de Superlite](../../../findings/superlite-transferable-ideas-2026-10-19.md): mecanismos, evidencia y límites de transferencia.
- [Inventario de CDAD](inventory.md): qué existe, qué está en desarrollo y qué delta merece investigarse.
- [Prueba de escritorio](tabletop-active-decisions.md): aplicación ilustrativa sobre una unidad pendiente, sin sustituir su contrato.
- [Construcción incremental y validación reproducible](../proposed-cycle-incremental-construction.md): propuesta anterior relacionada, que debe reconciliarse y no duplicarse.
- [Capacidades del sistema, integración y evidencia — caso S-SYS-01](../../../findings/system-capability-planning-evidence-2026-10-21.md): retrospectiva y fuentes contrastadas; entrada necesaria para A1–A3 y para reconciliar continuidad y entorno en B.
- [Prioridades históricas de operación y aceptación](../../../findings/agent-operation-strategy-2026-10-11.md), especialmente §7: antecedente de planificación avanzada y comprobación de uso. Se consume como antecedente, no como backlog actual.

Los documentos describen una fotografía del checkout, no la versión cargada por
todos los runtimes. El desarrollo actual sigue cambiando: al iniciar se vuelve
a contrastar únicamente lo necesario con las capacidades realmente entregadas.

## 2. Intención y principios que se conservan

Reducir espera, reorientación y coordinación mecánica sin perder calidad,
autonomía prolongada, independencia de roles ni evidencia suficiente del resultado.
El contexto queda disponible para el contenido del proyecto; no se impone un
techo universal. Una tarea pequeña mantiene un recorrido pequeño.

La eficacia incluye que las partes compongan un sistema utilizable. Completar
tareas o comprobar decisiones locales no demuestra por sí solo esa capacidad.
El caso S-SYS-01 exige evaluar cómo el orden del trabajo, sus dependencias y la
transferencia de hallazgos contribuyen al resultado completo.

**Vocabulario y marco de análisis (dirección del dueño, 2026-10-21).** La
planificación parte de **contratos, garantías exigidas y evidencia**, no de TDD
ni de porcentajes de cobertura de código. El contrato declara obligaciones y
condiciones; la garantía nombra la propiedad exigida; la comprobación es el
procedimiento y la evidencia es lo observado con sus límites. Un test de código
es un instrumento posible, junto con ejecución nativa, inspección, observación
operativa y recorrido de uso. No se exige un test por frase ni se infiere una
garantía de la cantidad de tests. Esta dirección no elimina la independencia de
roles ni cambia por sí sola los contratos activos.

Se conserva test-writer separado del implementer, reviewer de solo lectura con
libertad para ampliar evidencia pertinente, autoridad de aprobación explícita y
adopción de versión entre ciclos. Modelos internos: configuración del runtime;
externos: configuración CDAD. No se evalúan ni comparan familias en la metodología.

De Superlite interesan mecanismos, no copiar sus umbrales o su reparto de roles.
No se transfieren revisión final limitada al paquete, tests e implementación por
un mismo agente, selección de modelos en skills ni ampliación automática de tests
focales a suite completa. Los ejemplos de interfaz ayudan a acordar significado;
no constituyen por sí solos un oráculo independiente ni una prueba de integración.

## 3. Orden y condiciones de entrada

1. Terminar y estabilizar el trabajo/fix vigente, respetando sus contratos.
2. En un borde seguro, comprobar la versión operativa y un recorrido legítimo de
   delegación, trabajo y recepción. No exigir deuda cero ni otra campaña de pruebas.
3. Reconciliar estas propuestas con 006-005, 006-004 y 006-006 efectivamente
   entregadas. Adoptar lo que ya exista; retirar del alcance cualquier duplicación.
4. Incorporar S-SYS-01 y los antecedentes históricos al discovery: identificar
   qué brechas siguen abiertas, cuáles se resolvieron y qué decisiones cambian
   para esta planificación. No basta con enlazar o resumir la retrospectiva.
5. Elegir un desarrollo pendiente apropiado como consumidor y acordar el primer epic.

Ahora se autoriza preparación documental y análisis. Las propuestas de abajo
todavía requieren su discovery y aprobación según el mandato vigente entonces.
Si un requisito de base sigue incompleto, resolver ese bloqueo en su trabajo
dueño; no encubrirlo dentro de una mejora de eficiencia.

## 4. Epic propuesto A — planificación ejecutable y verificación de interfaces

**Resultado:** descomponer objetivos en unidades completas, comprensibles con
entradas pertinentes y comprobables con sus consumidores. Debe aportar utilidad
aunque se continúe ejecutando en serie.

**Alcance por nivel:** `cdad-epic` organiza features, contratos compartidos,
dependencias e integración global. `cdad-cycle` organiza unidades de la feature,
entradas por rol y comprobaciones. Los principios tienen una única fuente; cada
skill consume la parte correspondiente. No hace falta otro rol planificador.

| Unidad candidata | Resultado independiente | Dependencias y evidencia |
|---|---|---|
| A1 — Mejorar el criterio de división | Descomponer en capacidades consumibles; distinguir información/interfaz de implementación, preparación operativa o evidencia previa. Relacionar el recorrido de uso y las dependencias del sistema con las tareas, con detalle progresivo y costo total. | Inventario y S-SYS-01 reconciliados. Una planificación real muestra productores, consumidores y razones de sus dependencias; distingue entrega parcial y capacidad disponible sin convertir cada detalle en requisito. |
| A2 — Verificar fronteras y transferir hallazgos | Contrastar productor y consumidor reales en las uniones relevantes; comprobar condiciones operativas cuando importen. Llevar hallazgos de exploración a los contratos, artefactos y encargos que los necesitan. | A1 y capacidades del proyecto. Instrumentación mínima para un caso real; ejemplos/fakes tienen alcance declarado y no sustituyen la integración. No construir un analizador o generador universal. |
| A3 — Recibir en trabajo pendiente | Una spec/plan y su ejecución aplican el criterio, con revisión independiente, una capacidad real de principio a fin y comprobación pertinente de uso. | A1/A2 disponibles y consumidor autorizado. Identificar responsabilidad de integración, evidencia y límites; registrar hallazgos y correcciones, incluso sin paralelismo útil. |

**Discovery de A1:** ¿qué problema deja sin resolver el procedimiento actual?
¿Qué dependencias podrían satisfacerse con un contrato y cuáles no? ¿La división
reduce complejidad o sólo agrega handoffs? ¿Qué entradas necesita cada rol?
¿Qué incertidumbres justifican detallar después? Definir el delta antes de editar.

**Consumo necesario de la evidencia histórica y de S-SYS-01:** resolver qué
garantías o dependencias del caso cambian la división, el orden, los insumos y
la aceptación de las unidades propuestas. Separar lo comprobado en documentos,
lo observado por el equipo de origen y las hipótesis causales aún abiertas.
Identificar las reglas ya presentes que no tuvieron suficiente efecto; no
resolver la brecha añadiendo la misma obligación en otra plantilla.

### Consecuencias de diseño a evaluar en A1–A3

- Un recorrido operativo temprano hace visibles actores, identidades, estado,
  configuración efectiva y consumidores donde esas relaciones importan. Se
  mantiene por relevancia, sin exigir una matriz extensa a proyectos simples.
- El grafo de tareas debe reflejar dependencias de capacidades reales y de
  preparación, no sólo firmas o disponibilidad de información. Una decisión
  implementada puede seguir necesitando medición, ejecución y observación.
- Comprobar pronto una primera capacidad reducida de principio a fin que atraviese
  fronteras reales; ampliar desde esa base. No posponer toda integración al cierre
  ni ejecutar el sistema entero para cada corrección.
- Las incertidumbres de mayor impacto justifican exploración acotada antes de
  fijar mecanismos; otras aparecen construyendo. Conservar avance y conocimiento
  según la propuesta incremental, sin una fase de predicción exhaustiva.
- Un hallazgo experimental identifica qué consumidor debe incorporarlo y qué
  evidencia mostrará su transferencia. Registrar una nota no acredita que el
  producto ya lo consuma; atender versión y vigencia de la fuente.
- Mantener continuidad de integración mediante una responsabilidad técnica
  asignada y delegada. El orquestador conserva coherencia y autoridad sin ejecutar
  ni cargar toda la depuración. Evaluar roles existentes antes de crear otro.
- Distinguir evidencia de decisiones, acciones ejecutadas, compatibilidad y uso.
  Verificar tanto las garantías defensivas como la posibilidad efectiva de
  alcanzar el resultado requerido; rechazar siempre no acredita una capacidad.
- Evaluar temprano el recorrido visible en el producto anfitrión cuando forme
  parte del objetivo. La aceptación técnica y la de uso aportan evidencia distinta.
- Consolidar el comportamiento vigente cuando la historia de correcciones impida
  comprenderlo, conservando trazabilidad y aprobaciones. No editar en silencio
  contratos activos ni exigir borrar distinciones operativas necesarias.

Estas son preguntas y resultados esperados para el discovery, no nueve nuevas
etapas, agentes, formularios o bloqueos. La spec elegirá el delta mínimo que
resuelva las brechas constatadas.

**Aceptación del epic:** la planificación cubre el objetivo global; cada unidad
entrega un resultado con consumidor y evidencia; una frontera importante se
comprueba con implementaciones reales; el caso pequeño no exige nuevos documentos
extensos. Conservar la distinción entre un fake compatible y una integración
acreditada. No exigir paralelismo si la dependencia, el riesgo o el costo lo desaconsejan.

La recepción debe distinguir tarea cerrada, mecanismo ensayado, componente
integrado y capacidad utilizable. No acreditar el resultado completo únicamente
con decisiones sobre hechos inyectados o con la implicación «si hay éxito, se
cumplen las propiedades»: también hace falta evidencia positiva del éxito exigido.

**Exclusiones:** scheduler, concurrencia automática, rediseño de recibos, selección
de modelos, código de implementación anticipado en el plan y presupuestos rígidos.
No ampliar la revisión inicial ya atendida por 006-006 sin una brecha concreta.

## 5. Epic propuesto B — ejecución supervisada con menor coordinación

**Resultado:** el orquestador concentra decisiones y supervisión; las herramientas
absorben operaciones mecánicas completas y los especialistas conservan aprendizaje
sin cargar toda la historia. Introducir concurrencia sólo sobre una base verificable.

| Unidad candidata | Resultado independiente | Dependencias y evidencia |
|---|---|---|
| B1 — Simplificar operaciones frecuentes | Reducir el ensamblaje manual de acciones ya resueltas, reutilizando entrada/dispatch/recepción/transiciones vigentes. | Trabajo real identifica fricción residual tras 006-005. Un recorrido completo requiere menos interpretación mecánica sin perder autoridad o evidencia. Puede concluir que no hace falta código nuevo. |
| B2 — Continuidad compacta de reparación | Objetivo, cambios, intentos, evidencia y próxima hipótesis recuperables mediante continuidad existente, ampliada sólo si falta algo. | Reconciliar la propuesta incremental. Una reparación pendiente puede retomarse sin repetir intentos conocidos ni perder contexto causal. Renovar sesión es una decisión, no un mandato universal. |
| B3 — Concurrencia gradual | Dos unidades independientes trabajan con propiedad de archivos, intentos, transiciones e integración inequívocos. | Contratos de A y mecánica operativa estable. Antes de código, resolver cómo representa CDAD varias unidades/paquetes sin violar su escritor único ni sus garantías vigentes. |
| B4 — Recepción de conjunto | Observar coordinación, recuperación y calidad en trabajo pendiente apropiado. | Evidencias de B1–B3. Empezar con concurrencia mínima; no usar cantidad de agentes como objetivo. |

**Aceptación del epic:** operaciones neutrales compartidas sin duplicación por
transporte; instrucciones breves con ampliación bajo demanda; dos unidades
independientes sin cambios ajenos ni confusión de resultados; interrupción
reconciliada antes de repetir efectos. Sesiones, trabajo en segundo plano y
notificaciones dependen de capacidades comprobadas, no de suposición por runtime.

**Exclusiones:** plataforma general de jobs, reemplazo del orquestador estratégico,
polling frecuente del store, barreras nuevas por comando y matrices especulativas
de runtimes. Adoptar capacidades progresivamente, declarando lo no observado.

## 6. Evaluación hacia adelante

Usar sesiones históricas como referencia descriptiva y desarrollos pendientes para
recepción. No repetir desarrollos terminados ni abrir experimentos de modelos.

Observar lo que permita el entorno: tiempo hasta primer trabajo útil; preparación
y reorientación; pruebas/reconstrucciones redundantes; bloqueos, reparaciones e
intervenciones; integración y resultado funcional. Declarar fuente y distinguir
observado, estimado y desconocido. No estimar tokens ausentes como si se midieran.

Con S-SYS-01, añadir recurrencias de problemas ya conocidos, transferencias de
hallazgos efectivamente incorporadas y avance hacia capacidades utilizables.
Son observaciones orientadas al resultado, no una puntuación obligatoria ni
otra campaña de telemetría. No atribuir todo retraso a planificación ni todos
los cambios legítimos de requisitos a un defecto del proceso.

No fijar porcentajes antes del discovery ni atribuir causalidad a tareas distintas.
Si la evidencia o eficacia empeoran, el ahorro no acredita la mejora. Para el
trabajo de cada ciclo rige la política vigente de regresión proporcional y
reutilización de evidencia; no una suite nueva por cada ajuste documental.

## 7. Handoff cuando llegue el turno

Reconciliar versiones y backlog; seleccionar el consumidor; precisar y aprobar
el plan de A; detallar sólo su próxima tanda. B conserva por ahora propósito y
fronteras. La prueba de escritorio es preparación, no spec aprobada ni prueba de
ahorro. No implementar su alternativa sobre un contrato activo.

Si la propuesta incremental puede recibirse dentro de estos resultados, proponer
su consolidación explícita. No ejecutarla dos veces ni fusionar alcances en silencio.

El handoff de planificación incluye S-SYS-01 y su matriz de evidencia como
entrada necesaria, junto con Superlite y los antecedentes históricos. La salida
explica qué consecuencias se adoptan, cuáles ya están cubiertas y cuáles se
descartan con motivo. No exige a cada especialista cargar toda la retrospectiva:
sus encargos reciben sólo los hallazgos y relaciones pertinentes a su trabajo.
