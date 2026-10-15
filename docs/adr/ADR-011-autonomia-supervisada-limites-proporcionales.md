# ADR-011 — Autonomía supervisada y límites proporcionales

Fecha: 2026-09-24.
Estado: **Decisión metodológica aceptada por instrucción del usuario** de
revisar CDAD y ajustar los epics para priorizar instrucciones comprensibles,
confianza en el criterio del agente y supervisión del orquestador.
Implementación: pendiente en 004-001/002/003 y 003-002/003/004; este ADR no
cambia permisos instalados, no activa epics ni aprueba specs aún inexistentes.

Relación: sustituye como política objetivo la obligatoriedad universal del
catch-all deny y las allowlists por nombre de comando de ADR-009/cdad-010.
Conserva sus observaciones técnicas históricas y garantías útiles. No altera
ADR-010 ni concede autoridad de publicación o delegaciones HITL adicionales.

## Problema y evidencia

La configuración acumuló controles que impiden operaciones necesarias para
cumplir los contratos y que no equivalen a aislamiento de recursos. El caso
C0 documenta rechazos de medición, alternativas incompletas y una agregación
incorrecta pese a disponer de los valores individuales correctos. Ver
[finding](../../findings/permission-friction-c0-2026-09-24.md).

La política de cdad-010 ya pedía expectativas explicadas y consecuencias ante
incumplimientos injustificados. Sin embargo, algunos textos metodológicos
prometen corrección forzada por barreras, y los adaptadores/validadores fijan
medios específicos como si fueran principios. Fuente única no debe perpetuar
esa complejidad. Tampoco corresponde concluir que todo control es inútil o
extrapolar tasas globales de error a partir de un caso.

## Decisión

CDAD asume agentes cooperativos, capaces de elegir cómo trabajar dentro de un
encargo autorizado. El orquestador responde por la coherencia global y verifica
resultados con evidencia, apoyándose en revisión independiente. La protección
frente a un ejecutor hostil no es una garantía de una allowlist CDAD ni el
objetivo de estos epics. Si un despliegue la necesita, la proporciona un entorno
de aislamiento apropiado y la verifica por separado.

### Principios que se conservan

1. Objetivo y contrato verificables antes de implementar; alcance y autoridad
   explícitos, sin convertir cada decisión técnica en una consulta al usuario.
2. Sesiones y contexto separados entre autor de tests, implementer y reviewer.
   Test-writer deriva del contrato sin consumir implementación; implementer
   conserva tests aprobados; reviewer juzga con independencia del autor.
3. RED/GREEN, auditoría del vínculo test↔postcondición, revisión y evidencia
   vigente. Una suite verde por sí sola no demuestra el objetivo completo.
4. Memoria durable, decisiones con razones y continuidad de trabajos/presupuestos.
5. El cumplimiento del encargo incluye los principios relevantes, no solo la
   existencia del artefacto. El agente informa obstáculos y desviaciones.

### Libertad operativa y control

El encargo indica resultado, alcance, entradas, invariantes con su motivo,
decisiones delegadas, evidencia de salida y condiciones de escalamiento.
El agente elige herramientas, estrategia, cálculos y verificaciones locales
dentro de ese marco; no se prescribe una única forma textual de comando.

El principio es **permitir trabajo legítimo dentro del alcance y supervisar
su resultado**. Las restricciones duras se justifican por un efecto concreto,
la dificultad de revertirlo/observarlo y su costo de fricción. No por la
posibilidad abstracta de que un comando sea potente. Cada restricción retenida
declara su objetivo, mecanismo, límite conocido y cómo verificar que no impide
el trabajo necesario. Esto integra el contrato del rol, no otra aprobación
por llamada ni un catálogo creciente de prohibiciones.

| Situación | Control apropiado |
|---|---|
| Decisiones locales reversibles dentro del encargo | Autonomía y comprobación al entregar; no permiso por cada herramienta. |
| Acción externa, destructiva relevante o fuera del alcance | Comprobar autoridad vigente antes del efecto. Si ya fue autorizada, actuar dentro de ella; si no, escalar. |
| Contaminación del contexto del test-writer | Sesión nueva, selección de entradas y controles de acceso pertinentes cuando estén disponibles. Declarar qué está realmente protegido. |
| Cambio de archivos fuera del rol | Ámbito claro y diff/snapshot de contenido al re-entry; un guard sencillo puede prevenir el accidente sin bloquear las capacidades legítimas. |
| Denegación inesperada o herramienta incompatible | Informar evidencia breve al orquestador; resolver herramienta/política/encargo, sin reintentos equivalentes ni evasión encubierta. |

Una sesión separada evita heredar contexto; no impide nuevas lecturas. Un
worktree separa cambios, no es un sandbox. Un paquete sin source no impide que
otras herramientas lo lean. Un guard de Edit/Write no media automáticamente
Bash. Logs pueden mostrar lecturas, pero ausencia de logs no demuestra ausencia
de acceso; tampoco una lectura observada se deshace reiniciando la misma memoria.

No se exige construir un sandbox general para continuar. Elegir el mecanismo
mínimo disponible y declarar su garantía: instrucciones + inputs seleccionados,
controles mediados por herramientas o aislamiento de recursos comprobado.
Si se expuso implementación al test-writer, registrar la contaminación y
rehacer la parte afectada en otra sesión con entradas apropiadas; no pedirle
que "olvide" lo leído ni seguir llamando independiente a ese trabajo.

### Capacidades mínimas por rol

| Rol | Autonomía y evidencia esperadas |
|---|---|
| Architect / planificación | Explorar fuentes permitidas, medir, calcular y contrastar opciones; devolver contratos y dudas fundamentadas. No modifica el producto ni aprueba su propuesta. |
| Test-writer | Elegir estrategia de falsificación, editar tests autorizados y ejecutarlos por el runner acordado. No inspecciona implementación mediante archivos, salidas o proxies. |
| Implementer / refactorer | Resolver y depurar dentro del alcance de implementación, ejecutar tests y conservar los tests aprobados. Devuelve diff y evidencia del estado realmente probado. |
| Reviewer / scribe | Leer entradas necesarias, calcular y verificar afirmaciones; entregar informe/borrador fiel, sin modificar ni aprobar el producto. |
| Orquestador | Preparar encargos, materializar, verificar, resolver desviaciones y replanificar dentro del mandato; escalar solo decisiones que lo excedan. |

Read-only se refiere al producto/repositorio: no obliga a prohibir temporales,
logs o cálculos en un espacio de trabajo declarado. Especificar ese espacio y
su limpieza sin ampliar permisos a archivos ajenos. La materialización oficial
de architect/reviewer/scribe sigue bajo ADR-003; no se cambia por esta aclaración.
Que un runner ejecute código no autoriza al test-writer a inspeccionar source.

## Verificación del orquestador y decisiones ante desvíos

Verificar en límites de tarea/subfase y ante señales relevantes, no inspeccionar
manualmente cada comando. Reutilizar estado, diff, resultados y logs existentes.
El mínimo es resultado contra contrato, ámbito de cambios, evidencia de tests
y revisión efectiva, más incidentes/limitaciones declarados.

`git diff --stat` sirve para orientar la inspección, no para probar cumplimiento.
Comparar contenido y archivos nuevos/no trackeados respecto de una base conocida,
sin atribuir al agente cambios previos o concurrentes ajenos. Para evidencia
de tests importa el snapshot al ejecutarlos, no solo el diff final; una escritura
transitoria revertida no queda demostrada por el estado final. Declarar los
límites de observabilidad en vez de convertirlos en vigilancia exhaustiva.

| Hallazgo | Respuesta |
|---|---|
| Decisión razonable dentro del contrato | Aceptar; no abrir incidente por una preferencia de herramientas. |
| Obstáculo del entorno o regla defectuosa | Registrar fricción y corregir la causa; no atribuir al agente una violación por recibir un deny. |
| Desviación explicada sin violar invariantes | Resolver dentro del mandato, documentando razón y evidencia. Un cambio real de alcance requiere su autoridad. |
| Incumplimiento material / evidencia inválida | No cerrar el gate afectado; corregir o repetir solo lo invalidado, conservando trabajo válido. |
| Efecto grave, repetido o fuera de autoridad | Detener la parte afectada, informar y escalar; revisar encargo/capacidades antes de añadir un control específico. |

No hay repetición automática de la tarea completa por cualquier desvío. No se
acepta evidencia inventada ni se justifica retroactivamente una acción externa
no autorizada. Aprobación, recepción mecánica y cumplimiento semántico siguen
siendo cosas distintas.

Registro mínimo de incidente material, usando el handoff/resultado existente:
tarea/ejecución, expectativa, hecho y evidencia, impacto, causa conocida o
incierta, resolución, responsable y trabajo que sigue válido/pendiente. No
crear un servicio de incidentes ni un archivo por cada comando rechazado.

## Medición y evolución

Observar ambas caras: fricción (denegaciones, reintentos, tiempo, ausencia de
capacidades) y riesgo (desviaciones materiales, evidencia invalidada, retrabajo).
Contar también tareas/llamadas y disponibilidad de observación para interpretar
los totales. Desconocidos no son cero; una sesión sin incidentes reportados no
prueba cumplimiento ni obliga a quitar otro control automáticamente.

Aplicar en desarrollos reales pendientes. Mantener las métricas como feedback
para decisiones del orquestador, no un scoring que cambie permisos por sí solo.
El grado de restricción se decide por evidencia y consecuencias; puede aumentar
o disminuir para una frontera concreta, sin endurecer todo CDAD.

## Aplicación, transición y vencimiento de reglas antiguas

- **004-001:** política por capacidades/efectos primero; simplificación acotada
  de adaptadores OpenCode/Claude Code y controles pertinentes, después generación.
  Actualizar assertions que fijan el mecanismo antiguo con su reemplazo útil.
- **004-002:** política de proyecto, ámbito efectivo y espacio de trabajo
  coherentes; ejecución/autoridad estable, capacidades antes de despachar.
- **004-003:** encargos breves con razones, decisiones delegadas y re-entry con
  tratamiento proporcional de desviaciones. Revisión independiente sin microgestión.
- **003-002:** preservar resultados/incidentes originales y evidencia asociada
  al snapshot; el receipt no decide si una desviación es aceptable.
- **003-003:** detectar fricción del entorno y falta de progreso, además de
  fallos del agente; el guard escala, no concede autoridad ni endurece políticas.
- **003-004:** conservar política/garantía efectiva, decisiones sobre incidentes
  y budgets al reanudar, sin reintroducir silenciosamente defaults antiguos.

El diseño objetivo de este ADR rige los próximos contratos. La política
instalada anterior sigue operando hasta su migración comprobada; no es permiso
para que un ejecutor burle una denegación. No hace falta otro epic, un nuevo
agente, un framework de permisos ni abrir todo Bash globalmente. La primera
entrega debe mostrar que el trabajo legítimo es realizable y que las pocas
fronteras retenidas cumplen su propósito en el runtime probado.
