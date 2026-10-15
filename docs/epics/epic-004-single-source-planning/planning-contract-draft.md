# Contrato propuesto de planificación y revisión

Fecha: 2026-09-23; actualizado 2026-09-24. Estado: borrador para 004-003.
Aplicar [ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md):
planificar también la autonomía del ejecutor y la verificación del resultado,
sin prescribir cada herramienta.
Complementa el [plan de epic](plan.md). No es todavía una skill instalada ni
una modificación de gates aprobados. Puede usarse para preparar la propuesta C0.

## 1. Propósito y responsabilidades

Transformar un objetivo global en unidades ejecutables con contratos completos,
contexto acotado y un camino de integración comprobable. Optimizar el costo
total de planificar, construir, coordinar, revisar e integrar, incluyendo el
retrabajo. Más tareas o menos líneas por tarea no son métricas de éxito.

- Coordinador de epic: mantiene objetivo, cobertura global y dependencias.
- Architect: propone contratos y división; puede trabajar en modo planificación.
- Reviewer: examina el plan en otra sesión; contrasta también con intención
  original. No necesita ser un nuevo tipo de agente.
- Orquestador de ciclo: ejecuta el plan, detecta cambios y registra evidencia.
- Responsable autorizado: aprueba alcance y resuelve decisiones estratégicas.

El autor puede hacer autorrevisión; no reemplaza el examen independiente. Una
sesión nueva reduce el arrastre del razonamiento previo, pero no demuestra
independencia estadística entre errores de modelos.

## 2. Tres niveles existentes, con controles mejores

| Nivel | Qué debe quedar definido | Qué no se exige anticipar |
|---|---|---|
| Epic | Intención completa, límites, invariantes, features, dependencias, contratos compartidos, recorrido y aceptación global. | Detalle de implementación de todas las features. |
| Feature/ciclo | Resultado verificable, postcondiciones, tareas internas, inputs/outputs, integración y contexto de próxima tanda. | Una spec duplicada dentro del plan del epic. |
| Tarea | Cambio rechazable de manera independiente, contrato, entradas permitidas, alcance y verificación RED→GREEN. | Un ciclo completo con Memory Bank y aprobación global por cada tarea. |

La cobertura global debe ser explícita desde el principio; las soluciones y
fronteras pueden cambiar con evidencia. Una incógnita futura tiene dueño,
impacto y momento de resolución. Una tarea lista para ejecutar no contiene
`TBD` en contratos que necesita para completarse.

## 3. Procedimiento de planificación

1. Reconstruir intención y restricciones desde fuentes vigentes, sin convertir
   decisiones históricas en órdenes actuales. Enumerar resultados observables.
2. Dibujar el recorrido consumidor de principio a fin y sus fallos relevantes.
   Por cada entrada, identificar productor, consumidor, formato y verificación.
3. Identificar invariantes compartidos, autoridades y dependencias reales:
   datos, interfaces, configuración, archivos y recursos de ejecución.
4. Proponer features que entreguen capacidades verificables y tareas internas
   con RED→GREEN propio. La integración tiene dueño y evidencia explícitos.
5. Revisar la frontera de mayor riesgo: ¿necesita demasiado contexto?, ¿deja
   una pieza sin productor?, ¿el paralelo comparte state o contratos inestables?
   Comparar otra división solo si resuelve una duda real; no producir alternativas
   ceremoniales para todos los cambios.
6. Detallar la próxima tanda y sus contratos exactos. Declarar qué información
   puede recibir cada rol; no introducir implementación en entradas del test-writer.
7. Hacer autorrevisión; entregar al reviewer objetivo original, plan, fuentes
   pertinentes y dudas. Conservar informe original y resolución de hallazgos.
8. Registrar versión aprobada y ejecutar. Replanificar solo la parte afectada
   por nueva evidencia, conservando trabajos y decisiones válidos.

## 4. Ficha mínima de unidad ejecutable

Una tabla o sección en el plan existente; no crear otro archivo si duplica datos.

```text
ID estable y versión del plan
Resultado observable / postcondiciones cubiertas
Alcance incluido y excluido
Consume: contratos, interfaces, artefactos y su productor
Produce: contrato/artefacto y consumidor
Dependencias previas y condiciones para arrancar
Archivos Create/Modify/Test; owned y do-not-touch si hay paralelismo
Entradas de contexto necesarias por rol y motivo
Decisiones autónomas; capacidades necesarias y restricciones con su razón
Evidencia al re-entry y tratamiento de obstáculos/desviaciones materiales
Estimación inicial: rango, método y nivel de incertidumbre
Verificación RED→GREEN / comprobación aplicable; integración y responsable
Incertidumbres, condición para detener y criterio de replanificación
```

Las firmas exactas se fijan donde sean necesarias para que otra tarea consuma
el resultado. No diseñar cuerpos de funciones en markdown ni tests dictados
por detalles internos aún no implementados. Los permisos son independientes
de las descripciones: mencionar un path no autoriza a leerlo o editarlo.

### 4.1 Bloque canónico `plan-tasks` (declaración única)

Los hechos estructurales de la ficha viajan, en un plan borrador, dentro de un
bloque cercado `plan-tasks` con JSON. Ésta es la **única** declaración del
formato: código, tests y demás consumidores la referencian, nunca la copian
(PD-12 / invariante 6). Un bloque malformado se rechaza con diagnóstico; no se
ignora en silencio ni se trata como ausencia de bloque.

Nombres de los campos que el esquema acepta (los mismos que consumen el
validador de `prepare` y el reviewer): a nivel de plan `tasks` y
`validation_strategy`; por tarea `id`, `produce`, `consume`, `depends_on`,
`parallel`, `files`, `focal_tests`, `observable_checks`, `regressions`,
`integration_gate`, `owner` y `detail`. La estrategia común se declara una vez
en `validation_strategy` y se referencia con el literal `@validation_strategy`
en `focal_tests`, `observable_checks`, `regressions` o `integration_gate`.

El marcador por tarea `detail` admite el conjunto cerrado de valores `"next"`
(default) y `"planned"`. Qué declara una tarea según su marcador —y qué queda
exigido a cada valor— es la **regla de detalle progresivo**, enunciada una sola
vez en `skills/cdad-cycle/references/stage-2-specification.md` (sección
«Progressive detail»); este formato la **referencia** y no la re-enuncia.

```plan-tasks
{"validation_strategy": "suite completa una vez por GREEN; regresiones del area tocada",
 "tasks": [
  {"id": "T0",
   "produce": [{"artifact": "artefacto", "contract": "contrato-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["ruta/al/archivo"],
   "focal_tests": ["tests/test_ejemplo.py"],
   "regressions": ["tests/test_regresion.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T1",
   "produce": [],
   "consume": [{"artifact": "artefacto", "contract": "contrato-v1", "producer": "T0"}],
   "depends_on": ["T0"],
   "parallel": [],
   "files": [],
   "observable_checks": ["el documento publicado contiene la seccion X"],
   "regressions": [],
   "integration_gate": "revision del artefacto por el reviewer",
   "owner": "test-writer"}
]}
```

Rol **mecánico y estructural** del bloque: el validador de `prepare` lo lee y
comprueba productor/consumidor, contratos compatibles, ciclos de dependencia y
paralelismo seguro. No juzga calidad ni utilidad — eso es del reviewer (PD-2).
Por tarea se declaran las **pruebas focales** (`focal_tests`) cuando hay código,
o **comprobaciones observables** (`observable_checks`) en ciclos sin código, más
las **regresiones** afectadas (`regressions`), el **gate de integración**
(`integration_gate`) y el **responsable** (`owner`) de ejecutar cada
comprobación. La ficha de §4 sigue siendo la fuente de los campos; el bloque es
su forma legible por máquina. El ejemplo ilustra el **formato** (T0 produce y T1
consume), de modo que es estructuralmente válido si se ejecuta por el validador.

## 5. Criterios de revisión del plan

| Criterio | Pregunta y evidencia esperada |
|---|---|
| Cobertura de intención | Cada resultado del usuario tiene productor, consumidor y criterio de aceptación; lo excluido es explícito. |
| Completitud operativa | Instalación, configuración, inicio y recepción están asignados cuando el objetivo los necesita; no hay entradas mágicas. |
| Contexto suficiente | Un ejecutor puede empezar con lo declarado; no necesita adivinar restricciones globales ni cargar todo el historial. |
| Frontera útil | Una tarea tiene un resultado comprobable, sin combinar dominios independientes ni fragmentar una operación inseparable. |
| Contratos compatibles | Nombres, firmas, versiones y semántica encajan; no basta con que dos textos mencionen la misma interfaz. |
| Dependencias honestas | Grafo sin ciclos no resueltos; una supuesta tarea independiente no espera una decisión pendiente de otra. |
| Paralelismo seguro | Archivos/recursos/state no colisionan, o existe un protocolo aprobado; hay integración posterior. |
| Aislamiento de roles | Ninguna entrada/resumen filtra implementación al test-writer ni concede permisos ajenos al rol. |
| Verificación independiente | Hay oráculo observable; tests no solo comparan dos productos del mismo error de generación. |
| Viabilidad operativa | El rol puede leer/medir/calcular/ejecutar lo necesario; cada límite protege un efecto definido sin impedir su trabajo legítimo. |
| Supervisión proporcional | El orquestador dispone de evidencia suficiente al re-entry y una respuesta a desvíos; no necesita autorizar cada herramienta. |
| Costo de coordinación | Dividir evita complejidad suficiente para justificar handoffs, recargas y review adicionales. |
| Recuperación | Una interrupción permite determinar lo hecho y la próxima acción sin duplicar efectos. |

Un plan con campos completos puede seguir siendo malo. El validador comprueba
estructura/referencias/reglas formales; el reviewer evalúa semántica y utilidad.
No afirmar que un checklist o un modelo garantizan la optimalidad de la división.

## 6. Disparadores y límites de la revisión

Propuesta: revisión independiente al aprobar un epic y para planes de features
complejas con nuevas interfaces, varios dominios, límites de confianza o
paralelismo. En cambios simples, usar ficha breve y gates de CDAD proporcionados
al riesgo; no imponer un informe extenso por defecto.

Revisar de nuevo el delta si cambia el objetivo, contrato compartido, frontera
de permisos, cobertura de aceptación o dependencia que invalide otras tareas.
Reordenar tareas independientes dentro del mandato o ajustar un detalle de
implementación permitido no exige reaprobar todo el epic.

Hallazgos bloqueantes: objetivo sin cobertura, entrada necesaria sin productor,
contrato incompatible, autoridad ausente, aislamiento roto o verificación
incapaz de detectar el fallo relevante. Preferencias de organización sin
consecuencia demostrada no se vuelven bloqueantes por gusto del reviewer.

Salida de revisión: artefacto/versión revisada; hallazgos con ubicación,
consecuencia y evidencia; incertidumbres/abstenciones; cambios requeridos;
dictamen técnico. La aprobación del responsable queda registrada aparte.

## 7. Medición mínima sin benchmarks ni precisión inventada

Complemento acordado el 2026-10-05: incorporar los requisitos de
[orquestación y validación proporcionales](../../specs/004-003-planning-procedures/efficient-orchestration-requirements.md)
al procedimiento final. Define estrategia de pruebas, evidencia reutilizable,
granularidad de delegación y observación del costo de validación, sin crear
otro sistema de telemetría.

Separar estas magnitudes:

1. **Contexto inicial:** instrucciones de rol + encargo + entradas realmente
   cargadas. Referenciar un archivo no significa haber contado su contenido.
2. **Máximo contexto de llamada/sesión observado:** incluye historial activo,
   lecturas, herramientas y overhead según lo que reporte el runtime. Es la
   magnitud relevante para la ventana de 200k/100k.
3. **Consumo acumulado y tiempo:** suma de trabajo durante todas las llamadas,
   con reintentos y revisión; no es el tamaño simultáneo de contexto.

En el plan: lista de entradas con alcance/propósito, rango estimado y método
(tokenizador identificado, dato reportado o estimación cualitativa). Si solo
hay bytes, registrarlos como bytes. No aplicar una conversión universal a tokens.

En la observación: tarea/versión del plan, execution/packet, runtime/modelo,
tiempo, tokens disponibles, máximo observado, ampliaciones de contexto,
reintentos y causa de desviación. Registrar fricción del entorno y desvíos
materiales, con denominadores y límites de observabilidad. Ausencia de incidentes
reportados no activa relajaciones automáticas. Etiquetar lo no medido como desconocido.
Evitar doble contabilización de mensaje y step-finish del mismo evento.

La implementación inicial puede usar un registro pequeño por tarea al cerrar
el trabajo, sin un nuevo framework. El schema de 003-001 no contiene todavía
todo lo anterior: revisar la evolución necesaria, no inventar campos en un
registro que `additionalProperties: false` rechazará. La captura automática
más amplia sigue vinculada a 003-003/004.

Clasificar las desviaciones para mejorar: entrada omitida, dependencia oculta,
spec ambigua, tarea demasiado amplia, fragmentación excesiva, dificultad de
implementación, fallo de herramienta/permisos o medición insuficiente.

El presupuesto orienta la preparación y el checkpoint; no justifica cortar un
contrato por la mitad. No pedir que una tarea consuma un porcentaje arbitrario
de ventana ni que agote todo lo disponible. Los umbrales 120k/150k/200k de 003
son una propuesta que su spec debe validar contra el runtime real.

## 8. Uso real y decisión futura sobre planner

Aplicar el procedimiento al trabajo próximo de 004 y a la revisión del draft
003-002. Registrar qué omisiones encontró, qué fronteras cambiaron y qué
desviaciones ocurrieron al ejecutar. No rehacer desarrollos para comparar.
No atribuir causalmente ahorros entre features heterogéneas.

Considerar un agente planner propio solo si el trabajo recurrente de
descomposición/exploración exige aislamiento de contexto, especialización o
descarga del orquestador que los procedimientos actuales no resuelven bien.
No hace falta esperar un desastre, pero sí describir el problema y el resultado
esperado. Un planner también requeriría revisión: autor distinto no sustituye
evaluador independiente. Si se crea, derivarlo de las fuentes canónicas.

## 9. Ejemplos para evitar interpretaciones erróneas

- **Insuficiente:** «crear renderer; después usar paquetes». Falta quién crea
  el request, inicia ejecución, instala y entrega el resultado.
- **Mejor:** cada eslabón tiene productor/consumidor y el plan incluye un smoke
  desde proyecto consumidor; no todas esas piezas necesitan otra feature.
- **Paralelo inválido:** dos agentes cambian `install.sh` y el mismo state a la
  vez porque sus títulos dicen runtimes distintos.
- **Paralelo candidato:** adaptadores separados consumen contrato común estable,
  editan archivos disjuntos y se integran después por un único responsable.
- **Métrica engañosa:** paquete de 5k implica tarea de 5k. Las lecturas y la
  depuración posteriores pueden dominar el contexto y el costo.
- **Revisión inválida:** marcar un borrador como aprobado para poder pasarlo al
  renderer. Hay que representar explícitamente la revisión previa a aprobación.
