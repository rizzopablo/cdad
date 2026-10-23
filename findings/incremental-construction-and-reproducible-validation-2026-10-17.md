# Construcción incremental, delegación y validación reproducible

Fecha: 2026-10-17.
Estado: **hallazgo documentado; incorporación metodológica por evaluar**.
Caso anonimizado: S-ITER-01, integración de un proyecto consumidor.

El dueño solicita documentar la situación y planificar un ciclo posterior.
Esto autoriza esta documentación y planificación, no la aprobación de una spec,
la ejecución del ciclo ni cambios en los contratos actualmente despachados.

Propuesta de ciclo: [evaluación e incorporación](../docs/planning/proposed-cycle-incremental-construction.md).

## 1. Fuentes y alcance de la comprobación

Se leyó el tramo final de la conversación del consumidor, el encargo original
reproducido por el dueño, su corrección, el ADR-0005 sobre laboratorio persistente,
el ADR-0006 sobre construcción incremental y el encargo operativo actualizado.
Se contrastaron con las referencias actuales de CDAD indicadas en §7.

El ADR-0006 figura como **propuesto**, no como decisión metodológica aprobada.
Su incorporación al consumidor está registrada en el commit `784a42c` de ese
repositorio. Los localizadores privados de la sesión y los archivos de origen
se conservan fuera del material publicable, en `.cdad/local/`.

Se verificó el contenido de esos documentos y mensajes. **No se ejecutó el
laboratorio, no se inspeccionó el host remoto y no se acreditó su aceptación.**
Los tiempos, transferencias y resultados remotos mencionados por el orquestador
son evidencia relatada en la sesión, no mediciones independientes de esta revisión.
No se usan para prometer un ahorro cuantitativo.

## 2. Secuencia del problema

1. El consumidor realizaba ventanas de integración costosas. Al retirar los
   usuarios y recursos de cada prueba se retiraban también almacenes y preparación
   reutilizables; la siguiente ventana volvía a descargar o construir insumos.
2. El dueño distinguió infraestructura preparada de recursos de una ejecución.
   ADR-0005 registra esa decisión local: conservar base, plantillas y cachés;
   limpiar recursos propios de la prueba; distinguir preparación y uso.
3. Se delegó construir la herramienta del laboratorio y ejecutar dos ventanas.
   El encargo incluyó la suite de integración del producto, prohibió corregir
   producto/arnés y pidió no interrumpir las ventanas. La preparación del entorno
   y la aceptación del producto quedaron acopladas en un recorrido costoso.
4. Aparecieron problemas de entorno/herramienta. Según el relato, las corridas
   continuaron aun cuando ya se conocían fallos relevantes, y las correcciones
   dieron lugar a más recorridos completos.
5. El orquestador propuso enumerar previamente todas las incógnitas y sondearlas.
   El dueño señaló que parte de los obstáculos sólo aparece al resolver los
   anteriores: construir, observar, anotar, corregir y continuar conserva avance.
6. La discusión produjo una distinción más amplia: explorar y validar tienen
   propósitos diferentes; el alcance de la intervención se decide por la
   información necesaria, el costo y la confianza en el estado existente.
7. Al revisar el despacho se identificaron restricciones explícitas que explicaban
   la conducta del delegado. No hay base para atribuirla a desobediencia del agente.
8. El dueño entregó ADR-0006, se incorporó como propuesta y se corrigió el encargo.
   El orquestador retomó la sesión delegada con estado y pendientes explícitos.
   Esa reanudación no demuestra todavía el cierre del trabajo remoto.

## 3. Tres niveles distintos

| Nivel | Decisión | Qué puede generalizarse |
|---|---|---|
| Laboratorio del consumidor | Base preparada persistente y limpieza por ejecución; ADR-0005. | Separar recursos reutilizables y recursos temporales cuando corresponda. No imponer contenedores, usuarios ni un laboratorio persistente a todos. |
| Encargo concreto | Alcance, permisos de corrección, secuencia, pruebas y entrega del operador. | El encargo debe ser coherente con el propósito y permitir trabajo legítimo dentro del alcance. |
| Metodología | Construcción incremental y validación reproducible; ADR-0006 propuesto. | Conservar avance y aprendizaje; elegir comprobaciones por su propósito; distinguir resultado observado de reproducción demostrada. |

La infraestructura que habilita desarrollar es un entregable posible, pero no
se transforma automáticamente en una feature del producto ni exige otra épica.
Cambiar el mecanismo del producto requiere su propio contrato y autoridad.

## 4. Esencia del ADR-0006 que se propone evaluar

El desarrollo acumula capacidad y conocimiento: conserva lo que funciona,
investiga los problemas e incorpora las correcciones en procedimientos y
artefactos reutilizables. No todo puede conocerse antes de empezar; tampoco
corresponde renunciar a investigar por adelantado lo que sí puede verificarse.

La extensión de la intervención y de la comprobación responde a la pregunta que
debe resolverse. Puede ser apropiado continuar, aislar, reconstruir una parte o
repetir el recorrido completo, atendiendo al costo y a la confianza en el estado.

Exploración y validación reproducible pueden alternarse. La primera comprende
y completa la solución; la segunda comprueba que el resultado se obtiene mediante
el procedimiento registrado, sin depender de intervenciones olvidadas.

La delegación expresa ese propósito y concede margen coherente. Las restricciones
y los criterios de aceptación se justifican por el resultado, no por ritual.
El cierre exige evidencia adecuada del propósito; no fija una secuencia universal
de corrección, limpieza y repetición.

## 5. Errores de interpretación que deben evitarse

- **Siempre reiniciar / nunca reiniciar.** Ambas reglas sustituyen el juicio que
  el ADR busca habilitar. Un estado incierto o un cambio que invalida prerrequisitos
  puede exigir reconstrucción; un fallo local puede permitir seguir trabajando.
- **Siempre terminar una validación.** Si un prerrequisito invalida lo posterior,
  detener puede ser correcto. Si los controles siguen siendo independientes y
  útiles, continuar puede aportar evidencia. La limpieza segura se resuelve aparte.
- **Toda intervención invalida toda evidencia.** Una corrida intervenida puede
  probar comportamientos concretos; no acredita automáticamente la reproducción
  completa con el procedimiento final. Delimitar qué resultados siguen aplicando.
- **Validación reproducible significa ausencia de personas.** Puede incluir pasos
  manuales explícitos y reproducibles. La ejecución desatendida es otro requisito,
  cuando el contrato lo pida; el problema son las reparaciones no incorporadas.
- **Una corrida sin errores nuevos basta.** Puede no ejercitar el objetivo, ocultar
  fallos conocidos o pasar en vacío. Siguen rigiendo contrato, cobertura pertinente
  y evidencia suficiente. No se exige un número fijo de corridas exitosas.
- **Siempre conservar la sesión.** Lo durable es el conocimiento y el estado
  relevante. Retomar una sesión o renovarla depende de su utilidad, contaminación
  y presión de contexto; no se sacrifica independencia de roles.
- **Exploración permite cambiar cualquier cosa.** Se conserva el alcance: arreglar
  una herramienta autorizada no habilita alterar tests aprobados, producto, servicios
  o contratos ajenos. Si falta autoridad se reconcilia el encargo, sin evasión.
- **Cada herramienta debe tener un sistema de checkpoints.** Poder ejecutar pasos
  o retomar puede ser muy valioso en recorridos costosos, pero no es requisito
  universal ni razón para construir otra plataforma.

La corrección del despacho mejoró su propósito, pero volvió a usar expresiones
como «no reinicies una corrida» y «la validación sí llega al final». Son ejemplos
de cómo se puede perder el principio incluso al intentar aplicarlo.

## 6. Diagnóstico e hipótesis

**Confirmado en el material leído:** el encargo prescribía recorridos completos
y prohibía interrumpirlos; mezclaba resultados de entorno y de producto; el ADR
propuesto evita esa prescripción universal. El delegado tenía motivos explícitos
para ejecutar así. El problema no se resuelve culpando al worker ni agregando denies.

**Hipótesis por evaluar:** CDAD puede reducir retrabajo si sus procedimientos y
encargos distinguen mejor la pregunta de aprendizaje de la de aceptación, conservan
avance confiable y hacen explícita la autoridad para corregir. Este caso no demuestra
una tasa global de fallos, ahorro de tokens ni el tamaño óptimo de cada tarea.

Un mal despacho no refuta el principio metodológico: revela una responsabilidad
de la metodología al preparar encargos. Tampoco un único caso justifica rehacer
CDAD entero. Primero corresponde identificar qué reglas existen y dónde divergen.

## 7. Relación con CDAD existente

| Fuente actual | Lo que ya cubre | Delta a evaluar |
|---|---|---|
| [ADR-011](../docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md) | Autonomía explicada, alcance y supervisión; trabajo legítimo posible. | Coherencia del encargo con construcción exploratoria y correcciones autorizadas. |
| [Stage 3, Test evidence policy](../skills/cdad-cycle/references/stage-3-tdd.md) | Regresión proporcional; suite de cierre; proyecto declara comandos. | No usar el recorrido de aceptación como instrumento obligatorio de cada diagnóstico. |
| [Re-entry](../skills/cdad-cycle/references/re-entry.md) | Equivalencia, evidencia reutilizable, reintentos con información y replanteo. | Diferenciar estado de trabajo reutilizado y evidencia reutilizada; intervenciones e invalidación pertinente. |
| [Stage 2](../skills/cdad-cycle/references/stage-2-specification.md) | Especificación y planificación de unidades. | Propósito y unidad de iteración que no obliguen a reconstruir lo ya aprendido. |
| [Epic 006](../docs/epics/epic-006-opencode-concurrency/plan.md) | Trabajo vigente sobre delegación, configuración y decisiones aplicables. | Coordinar después con lo que realmente aterrice; no cambiar ahora sus contratos. |

El aporte es transversal: planificación, discovery, implementación, depuración,
integración e infraestructura. No es una nueva etapa obligatoria ni autorización
para omitir RED/GREEN, separar menos los roles o acreditar producto por relato.

## 8. Próximo paso autorizado y límites

Queda preparada una **propuesta de un ciclo posterior**, no activado. No se edita
el plan del epic actual, la spec activa, el state, las delegaciones, los paquetes
ni las instalaciones. El futuro orquestador debe reconciliar el diseño con la
versión existente al iniciar, porque hay otros desarrollos en marcha.

La aceptación se observará hacia adelante sobre trabajo real pendiente. No se
repetirá un desarrollo completo para comparar, no se impondrá un presupuesto de
contexto y no se evaluarán modelos. Eficacia, seguridad y calidad de evidencia
prevalecen sobre ahorro de tokens o cantidad de llamadas.
