# Metodologías relacionadas con CDAD: comparación y oportunidades

Fecha: 2026-10-09. Investigación acotada, previa a una propuesta de desarrollo.
Referencia local inspeccionada: `7f66619`; los archivos de trabajo pueden seguir
cambiando. Este documento no aprueba cambios, no modifica ciclos activos y no
demuestra todavía ahorros de tiempo o tokens.

## 1. Pregunta y criterio

¿Qué prácticas externas pueden mejorar la utilidad, el feedback, la división
del trabajo y la continuidad de CDAD, preservando contratos e independencia
de roles sin aumentar innecesariamente la coordinación?

Se consultaron autores originales, documentación oficial y procedimientos
públicos. Se distingue entre lo que prescribe una fuente, lo que observamos
localmente y las propuestas de adaptación. Las experiencias de proveedores y
las instrucciones de repositorios no son benchmarks comparativos.

## 2. TDD: feedback incremental, no especificación exhaustiva anticipada

Kent Beck describe una lista de escenarios y la ejecución incremental de un
test, implementación y refactor opcional. Advierte contra escribir todos los
tests de antemano y contra fabricar expectativas a partir del resultado actual.
Fuente: [Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd).

**Aplicación propuesta:** CDAD agrega al TDD una separación entre quien define
el oráculo y quien implementa. Esa separación no pertenece al canon clásico
ni prueba ausencia de errores correlacionados. Mantenerla, pero trabajar con
grupos pequeños y coherentes de comportamientos para no pagar una nueva sesión
por cada assertion ni anticipar una batería enorme para todo el epic.

El loop debe conservar evidencia RED genuina y confianza en la regresión;
la frecuencia y selección de las corridas son decisiones de ingeniería.
Refactorizar con evidencia vigente evita convertir cada refactor en otro ciclo
completo de discovery, aprobación y documentación.

## 3. BDD y Example Mapping: comprobar la intención antes de construir

BDD organiza discovery, formulación y automatización alrededor de ejemplos
concretos compartidos. Example Mapping distingue historia, reglas, ejemplos
y preguntas pendientes; puede revelar que una historia necesita dividirse.
Fuentes: [BDD](https://cucumber.io/docs/bdd/),
[Example Mapping](https://cucumber.io/docs/bdd/example-mapping/).

**Aplicación propuesta:** antes de cerrar una spec, describir el recorrido
normal, fallos relevantes y recuperación desde el consumidor real. Luego
derivar postcondiciones. Así se verifica también que el contrato interpreta
bien la intención, algo que una suite verde contra una spec equivocada no hace.

Ejemplo para CDAD: «Proyecto existente, identificadores propios, ninguna spec
aprobada: una solicitud breve permite analizar, registra decisiones en su
fuente correspondiente y no habilita construcción anticipada». Los detalles
del entorno se descubren; no se exige que el usuario los incluya en un prompt
extenso. No hace falta introducir Cucumber, Gherkin ni un agente nuevo.

## 4. Design by Contract: obligaciones de ambas partes

Meyer distingue precondiciones a cargo del cliente y garantías a cargo del
proveedor, además de invariantes. No consiste simplemente en añadir prohibiciones.
Fuente: [entrevista a Bertrand Meyer](https://www.artima.com/articles/design-by-contract).

**Aplicación propuesta:** el contrato de un encargo debe incluir qué entrega el
agente y qué le proporciona el sistema: entradas, autoridad, herramientas,
alcance y una salida legítima frente a un bloqueo. Pedir discovery mientras
el arnés exige una spec ya aprobada es una contradicción del proveedor.

Los contratos documentales de CDAD, hashes y gates no equivalen a verificación
formal del programa. Un hash identifica una revisión del artefacto; no acredita
que sus requisitos sean correctos, completos o útiles.

## 5. XP/INVEST y Shape Up: dividir por valor y riesgo

Bill Wake propone historias independientes, negociables, valiosas, estimables,
pequeñas y verificables, y describe cortes verticales que atraviesan las capas
del sistema. La independencia es una preferencia, no una posibilidad universal.
Fuente: [INVEST y SMART](https://xp123.com/invest-in-good-stories-and-smart-tasks/).

Shape Up aborda riesgos y supuestos que pueden desbordar un trabajo acotado,
antes de comprometerse con la construcción.
Fuente: [Risks and Rabbit Holes](https://basecamp.com/shapeup/1.4-chapter-05).

**Aplicación propuesta:** una feature debe cerrar una capacidad o riesgo
significativo; una tarea interna puede entregar una pieza técnica con consumidor
identificado. No exigir valor de usuario autónomo a cada helper, ni dividir
siempre por capas, archivos o comandos. El costo de coordinación también cuenta.

Definir cobertura global y dependencias temprano, detallar la próxima tanda,
y reservar investigaciones acotadas para incógnitas que impidan comprometer
un contrato. En tareas listas para construir no deben quedar decisiones
indispensables sin resolver. No trasladar literalmente plazos humanos o
topes universales de iteraciones al trabajo de agentes.

## 6. Estrategia de tests: velocidad y calidad del oráculo

La pirámide de tests propone un portafolio económico de comprobaciones,
evitando depender excesivamente de tests amplios y costosos; Fowler también
explicita que la recomendación depende del costo real de cada nivel.
Fuente: [Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html).

Los tests de propiedades generan entradas para comprobar una propiedad. La
mutación altera el programa para comprobar si los tests detectan el cambio;
hay mutantes equivalentes que no indican un defecto de la suite.
Fuentes: [Hypothesis](https://hypothesis.readthedocs.io/en/latest/quickstart.html),
[PIT](https://pitest.org/quickstart/basic_concepts/).

**Aplicación propuesta:** tests focales rápidos y regresión del área afectada,
con pocas pruebas del recorrido real instalado donde importan las fronteras.
No fijar un porcentaje universal de cobertura ni una cantidad de casos por
postcondición. Usar propiedades o mutación selectivamente cuando verifican
una invariante o una duda material sobre el oráculo, no como nuevos gates
obligatorios para todos los cambios.

Proporcionalidad no significa excluir límites relevantes porque la spec no
enumeró cada ejemplo. Si el caso revela una ambigüedad contractual importante,
devolverla a la autoridad correspondiente y precisar el contrato; si deriva
claramente de una obligación existente, justificar su test contra ella.

## 7. Entrega continua y recorrido temprano

Continuous Delivery mantiene el producto en condiciones de ser entregado;
no obliga a desplegar automáticamente cada cambio.
Fuente: [Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html).

Cockburn describe un Walking Skeleton como una implementación pequeña que
recorre las piezas principales de extremo a extremo y permite evolucionarlas.
Se pudo consultar una publicación del autor que remite a su texto original;
el archivo original no fue accesible mediante la herramienta.
Fuente: [publicación de Alistair Cockburn](https://www.linkedin.com/posts/alistaircockburn_what-is-a-walking-skeleton-and-why-do-i-need-activity-7419086703577071616-D8Cs).

**Aplicación propuesta:** comprobar temprano un recorrido mínimo desde una
solicitud del usuario hasta una delegación útil desde el producto instalado.
Ampliarlo al agregar capacidades, en lugar de descubrir la instalación o
el bootstrap al final del epic. Preparar una versión entregable al cerrar;
cambiar la versión operativa entre ciclos según la política de despliegue.

## 8. Sistemas de agentes: continuidad y revisión proporcional

Anthropic describe sesiones incrementales con progreso persistido y estado
verificado; señala que la compacción por sí sola no resolvió sus problemas.
Su artículo de contexto propone recuperación bajo demanda, notas estructuradas
y compacción, reconociendo sus costos y pérdidas posibles.
Fuentes: [agentes de larga duración](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents),
[ingeniería de contexto](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

**Aplicación propuesta:** continuidad de la misión y la autoridad a través de
sesiones renovadas. El orquestador necesita objetivo, frontera de trabajo,
decisiones, pendientes y referencias a evidencia; no todo el historial.
El paquete debe ser suficiente para empezar y permitir búsquedas pertinentes:
poner todo detrás de referencias también puede generar exploración costosa.

Superpowers prescribe briefs, reportes y diffs por archivo; re-reviews acotadas
al arreglo; reutilización de tests ejecutados sobre el mismo código; y estados
explícitos para necesidad de contexto o bloqueo.
Fuente: [subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md).

**Aplicación propuesta:** tomar esos patrones donde falten, sin importar sus
topes literales de rondas, restricciones generales de paralelismo o una review
formal por cada paso. Su plan también puede incluir assertions escritas como
código; CDAD debe preservar la responsabilidad independiente del test-writer.
Fuente: [writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md).

Spec Kit separa requisitos, plan y tareas, y ofrece análisis de consistencia
entre artefactos. No demuestra por ello mejor productividad que CDAD.
Fuente: [flujo de Agentic SDD](https://github.github.com/spec-kit/reference/agentic-sdd.html).

**Aplicación propuesta:** reutilizar la estructura ya existente en CDAD y
revisar contradicciones entre intención, spec, plan, paquete y capacidades.
Agregar documentos equivalentes sería contraproducente.

## 9. Contraste con el repositorio inspeccionado

| Observación local | Consecuencia / propuesta pendiente |
|---|---|
| `skills/cdad-cycle/references/stage-2-specification.md` ya define tareas con contrato, Consumes/Produces y plan de validación. | Mejorar criterios y ejemplos; no inventar otro nivel obligatorio de planificación. |
| `skills/cdad-cycle/references/stage-3-tdd.md` y el paquete `implementer-green.md` ya definen regresión proporcional y cierre con suite completa. | La contradicción anterior fue corregida en estas fuentes; no reportarla otra vez como vigente. |
| `skills/cdad-cycle/assets/spec-template/spec.md` todavía propone cobertura de líneas y un número de entradas aleatorias como criterios. | Revisar el default para alinearlo con evidencia basada en comportamiento y riesgo. |
| El ejemplo JSON de `planning-contract-draft.md`, hoy referenciado como dueño del formato, todavía dice suite completa por GREEN. | Reconciliar ejemplos con la política canónica; los agentes también aprenden de los ejemplos. |
| El Run budget genérico impone STOP tras dos corridas sin convergencia. | Evaluar si debe ser una señal de diagnóstico/replanificación según costo y evidencia, en vez de un corte universal. |
| La regla de relevancia dice que una postcondición no dispara más tests que los que pide. | Aclarar cobertura semántica: una obligación puede necesitar varios ejemplos sin ampliar el alcance del producto. |

Estas observaciones son de lectura, no una auditoría integral de producto
instalado ni un dictamen de cierre del ciclo en curso.

## 10. Prioridad sugerida y validación hacia adelante

1. **Intención y bootstrap:** solicitud breve, discovery guiado y registro de
   hechos en sus dueños. Ejemplos observables del arranque y la recuperación.
2. **Coherencia metodológica:** reconciliar templates, ejemplos y criterios
   con las políticas vigentes. Ningún paquete debe exigir lo que el arnés impide.
3. **División y continuidad:** unidades con contratos completos, próxima tanda
   detallada y renovación del contexto conservando misión, autoridad y evidencia.
4. **Validación proporcional:** suites/reviews sin duplicación, hallazgos
   materiales atendidos y deuda explícita; propiedades/mutación cuando aporten.

No cambiar el alcance de 005-005 mientras está en construcción. Seleccionar
el siguiente ciclo de corrección al reconciliar su entrega final, porque puede
resolver parte de estas observaciones. No crear de antemano un ciclo por idea.

Medir en desarrollos reales: tiempo hasta el primer despacho útil, tiempo y
contexto de recuperación, corridas repetidas sin cambio pertinente, rondas de
review con defectos materiales, bloqueos legítimos y regresiones que escapan.
Registrar contexto máximo por llamada aparte del total acumulado; declarar
desconocidos los tokens que el entorno no exponga. La cantidad de tareas,
tests, archivos y commits no demuestra utilidad ni eficiencia por sí sola.

## 11. Registro de investigación y límites

- Búsquedas: canon TDD; BDD/Example Mapping; contratos de Meyer; pirámide,
  propiedades y mutación; INVEST; Shape Up; Walking Skeleton; entrega continua;
  Superpowers/Spec Kit; contexto y arneses de larga duración.
- Selección: fuentes originales/oficiales con procedimientos inspeccionables;
  no se usaron rankings comerciales ni comparativas de modelos como evidencia.
- Se consultaron también [principios ágiles](https://agilemanifesto.org/iso/es/principles.html),
  [ADRs de Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
  y [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents).
  Refuerzan simplificación, decisiones persistidas y complejidad justificada;
  no implican sumar una herramienta o documento obligatorio.
- Se localizó una [revisión reciente sobre tests y LLMs](https://arxiv.org/abs/2609.12012),
  pero solo se inspeccionó su ficha/resumen; no sustenta recomendaciones de
  rendimiento ni una afirmación de consenso experimental.
- No se ejecutaron comparaciones, suites ni instalaciones. No se probaron
  todos los runtimes. Las instrucciones de Superpowers y Spec Kit son fuentes
  mutables: describen lo consultado hoy, no toda su historia.
- No se demuestra aún que CDAD complete el mismo alcance con menos de 100k
  o 200k de contexto. Las prácticas proponen un camino para comprobarlo con
  trabajo real, sin repetir desarrollos ni imponer un proveedor.

El artículo de design docs que motivó la investigación sigue siendo útil como
criterio de comunicación y detalle proporcional; la decisión de qué construir,
cómo dividirlo y cómo verificarlo necesita el conjunto de prácticas anterior.
Referencia: [Write an effective design doc](https://refactoringenglish.com/excerpts/write-an-effective-design-doc/).
