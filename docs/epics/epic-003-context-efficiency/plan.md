---
epic_id: epic-003-context-efficiency
epic_name: MVP de eficiencia y continuidad autónoma
created_at: 2026-09-16
status: approved
approved_by: Codex (agent-delegated)
approved_at: 2026-09-17
---

# Epic 003: MVP de eficiencia y continuidad autónoma

> Nota operativa — 2026-09-23: 003-001 y la entrega añadida 003-005 están
> cerradas; 003-002/003/004 siguen pendientes. Se propone intercalar un epic
> de fuente única/bootstrap/planificación antes de 002. Ver el
> [handoff vigente](handoff.md) y el [encargo GLM](../../handoffs/2026-09-23-glm-continuation.md).
> El nuevo epic todavía no está aprobado. Las selecciones de Sol/Codex de
> este plan describen la construcción inicial; el usuario ahora asigna GLM
> al desarrollo y GPT/Claude al análisis profundo/review. El criterio de
> modelo único del recorrido de aceptación permanece hasta una enmienda
> explícita; no confundirlo con el reparto actual de construcción.

## Resultado buscado

Completar desarrollos reales pendientes con un único orquestador lógico capaz
de trabajar durante horas y tomar las decisiones delegadas, reduciendo vueltas
improductivas y manteniendo cada llamada dentro de un presupuesto compatible
con una ventana de 200k. Prioridad: tiempo, contexto y costo, conservando
contratos, aislamiento de roles, aprobaciones y evidencia.

El MVP definió originalmente cuatro entregas; 003-005 se añadió y cerró para
preparar paquetes y completar su consumo en Claude Code. La medición acompaña su uso real: no se repiten
desarrollos para comparar variantes. Menos de 100k es el siguiente objetivo;
se puede explorar sobre tareas nuevas que lo permitan, pero no condiciona el
cierre de este epic. Las cifras de ahorro no se presuponen.

Plan aprobado bajo la delegación explícita del usuario del 2026-09-17.
El mandato de este epic está en [execution.md](execution.md). Cada spec y gate
conserva su aprobación y evidencia propias. No se heredan delegaciones anteriores.

## Evidencia y decisiones de alcance

Base: [análisis documental](../../../findings/context-token-efficiency-2026-09-16.md),
[primer relevamiento](../../../findings/session-efficiency-2026-09-16.md) y
[ampliación local](../../../findings/session-efficiency-local-2026-09-16.md).
Se observaron bucles prolongados, rechazos reiterados y acumulación de contexto,
especialmente en el orquestador. La recarga habitual de skills por turno no
quedó demostrada. Los relevamientos históricos orientan prioridades; no prueban
causas ni mejoras futuras.

- Un orquestador con LLM conserva planificación y juicio estratégico. La
  mecánica se implementa con herramientas deterministas, sin administrador LLM.
- **Modelo único para el MVP — decisión del usuario (2026-09-16):** usar el
  mismo modelo en todos los roles CDAD, incluido el orquestador y el reviewer.
  Se deja de exigir diversidad de modelo/familia para este epic y sus recorridos
  de validación. Se mantienen contratos, sesiones separadas, permisos por rol,
  test-writer sin implementación y auditoría del mapeo test↔postcondición por
  otra sesión. La separación de sesiones no se presenta como independencia
  estadística de errores. No se requieren comparaciones ni rankings de modelos.
  [ADR-010](../../adr/ADR-010-modelo-unico-mvp-epic-003.md) formaliza
  la excepción en OpenCode, con vencimiento al cierre, cancelación o revocación
  del epic y sin herencia a otros trabajos. Sus controles se implementan en 001.
- **Construcción desde esta sesión:** el usuario seleccionó `gpt-5.6-sol`
  para los subagentes, disponible como selección explícita del entorno. Todos
  los roles delegados lo usarán con contexto inicial nuevo. El orquestador
  conserva el modelo de su sesión actual: esta selección no cambia el modelo
  del padre. La igualdad entre todos los roles, incluido el orquestador,
  corresponde al recorrido de validación en OpenCode; para la construcción en
  Codex se registra esta distribución y la ampliación aprobada en ADR-010.
- Núcleo portable de archivos y contratos; primera integración automática en
  OpenCode. Versión, modelo, plugins y permisos efectivos se fijan al iniciar
  el trabajo. Otros runtimes conservan sus flujos existentes; su automatización
  completa se difiere, sin afirmar garantías idénticas donde no estén probadas.
- Planificación breve por dependencias y contratos compartidos; solo se detalla
  el trabajo próximo. Se reutilizan los roles existentes.
- Se registran decisiones y razones, incertidumbres y autoridad delegada; el
  cambio de sesión no exige repetir aprobaciones ni reconstruir el objetivo.

## Entregas del MVP

| Orden | Feature | Resultado verificable | Dependencias |
|---|---|---|---|
| 1 | `003-001-role-packets` | Instrucciones por rol/subfase, templates, plan breve por dependencias y contrato mínimo de estado/medición; compatibilidad explícita del modo de modelo único. Cada ejecutor recibe restricciones y contexto aplicables. | — |
| 1b (añadida y cerrada) | `003-005-claude-code-packets` | `prepare` produce request/packet y binding de state; consumidores Claude Code aceptan paquetes. Cierre 2026-09-18, previo a 002. | 001 |
| 2 | `003-002-artifact-tools` | Operación compuesta para recibir el resultado original de un rol, persistirlo sin regeneración, comprobar alcance e identidad de evidencia y devolver un recibo breve. Reintentar la recepción no duplica el resultado. | 001 |
| 3 | `003-003-progress-guards` | Detección de repeticiones improductivas y rechazos reiterados, comprobación previa de capacidades y recuperación acotada en OpenCode; incluye agentes auxiliares del flujo. | 001, 002 |
| 4 | `003-004-context-continuity` | Memoria activa separada del historial, checkpoints y reanudación automática dentro del presupuesto 200k, conservando mandato, decisiones, trabajos pendientes y referencias. | 001, 002, 003 |
| 4b (añadida y cerrada) | `003-006-runtime-adoption` | Cableado y activación por runtime de lo construido (descubrimiento, `receive` y continuidad en el ciclo, activación por proyecto, re-adopción). Cierre 2026-10-08; límites de Claude Code y Codex declarados. | 001–004 |
| 4c (añadida) | `003-007-living-continuity` | Continuidad que tolera documentos vivos: referencias de contrato/autoridad (bloquean) vs documentos vivos (se informan); checkpoint distinto de `begin` (T4-REF/T4-CKPT de 003-006). Última tarea: reconciliar la regla de encargo atómico del orquestador con la delegación de unidades coherentes. Aprobada por el dueño 2026-10-08. | 004, 006 |

Orden secuencial para integrar y observar cada entrega. La definición detallada
de contratos, umbrales y tests pertenece a las specs de cada feature. La
instrumentación mínima empieza en 001 y se amplía con cada entrega; el análisis
histórico ya disponible no se convierte en un proyecto de benchmark separado.

## Autonomía supervisada — actualización 2026-09-24

Aplicar [ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md)
como política de diseño: capacidades suficientes, pocas barreras justificadas
y juicio del orquestador al re-entry. Los criterios de continuidad y presupuesto
se conservan. 002 recibe evidencia e incidentes sin aprobarlos; 003 detecta
fricción del entorno y desvíos, sin endurecer permisos automáticamente; 004
preserva decisiones, autoridad y política efectiva al reanudar. No agregar
un epic de seguridad ni un controlador LLM. La implementación instalada no
cambia por esta nota; las specs pendientes deben reflejar la nueva política.

## Límites del MVP

- Los roles reciben instrucciones pertinentes y conservan invariantes críticos.
  Recuperar memoria no permite al test-writer leer implementación.
- En 001, armonizar instrucciones, handoffs y validadores aplicables para que
  compartir modelo no rechace una ejecución autorizada ni invalide por sí solo
  un review. Reutilizar mecanismos existentes cuando alcancen; no desactivar
  controles de permisos, evidencia o aislamiento para habilitar este modo.
- La recepción captura el resultado original por referencia o canal acotado;
  texto regenerado por el orquestador no cumple. Devuelve hechos comprobados y
  juicio pendiente. Logs íntegros permanecen consultables fuera del contexto.
- Para runners soportados: iteración focalizada, suite completa en el gate y
  reutilización de evidencia solo con equivalencia comprobada. No se construye
  una caché universal de tests.
- El detector reconoce repeticiones y errores soportados; los casos ambiguos
  vuelven al orquestador. Reanudar una sesión no reinicia el presupuesto de
  intentos. Polling legítimo conserva condición esperada, plazo y cadencia.
- Perfil 200k inicial propuesto: entrada máxima 150k, reserva de 50k para salida
  y margen, preparar checkpoint alrededor de 120k. La spec fija el conteo
  compatible con el runtime y modelo. Abarca orquestador, roles, auxiliares y
  recuperación. Reconstruir o subdividir conservando dependencias; no truncar
  contratos silenciosamente. Continuar hasta terminar o encontrar un bloqueo
  que requiera autoridad/información no disponible.

## Contratos compartidos mínimos

- **Mandato/estado:** objetivo, alcance, autoridad delegada y aprobaciones,
  decisiones con razón, incertidumbres, tareas/dependencias, agentes y próxima
  acción. Registrar trabajo en curso antes de despacharlo y reconciliarlo al
  reanudar; el esquema detallado se define en 001.
- **Paquete:** rol/subfase, objetivo, versión del spec, restricciones,
  dependencias críticas, lecturas autorizadas, alcance de edición y resultado
  esperado. Ampliación de contexto dentro de los permisos del rol.
- **Resultado/recibo:** identidad de ejecución y artefacto original, estado,
  ubicación, verificaciones mecánicas, evidencia y juicio pendiente. Un recibo
  no sustituye el informe ni constituye por sí mismo aprobación semántica.
- **Evidencia/progreso:** revisión y cambios sin commit, comando/selección,
  entorno relevante, resultado/conteos, log, intentos y recuperación. Si no se
  demuestra equivalencia, no reutilizar el resultado como gate vigente.
- **Medición:** feature y revisiones efectivas, modelo/runtime, tiempos,
  contexto por llamada, tokens reportados, repeticiones, recuperaciones y
  retrabajo. Datos desconocidos se conservan como desconocidos; bytes no son
  tokens y contadores de tokens no son facturación.

## Validación hacia adelante y aceptación del epic

Adoptar las entregas gradualmente en desarrollos pendientes del usuario. Fijar
versiones por ejecución y registrar cuándo cambia la estrategia. No atribuir
causalmente diferencias de tiempo entre features heterogéneas; evaluar capacidad,
fallos y resultados concretos. La selección de la feature real se realiza antes
del uso completo del MVP, no requiere rehacer un desarrollo terminado.

El MVP se acepta cuando:

1. Las cuatro features cierran sus ciclos CDAD con evidencia y Memory Bank
   aprobado; se resuelven los gates de integración y closure del epic.
2. Al menos un desarrollo real pendiente completa su ciclo con el MVP,
   usando el mismo modelo en todos los roles y review en sesión separada,
   dentro del presupuesto de contexto declarado
   en todas sus llamadas gestionadas. La captura demuestra el límite y cuenta
   el overhead del runtime y herramientas; límites sin medición no cuentan.
3. En ese recorrido existe una reconstrucción automática de sesión: conserva
   decisiones y aprobaciones, reconcilia trabajo en curso y continúa sin pedir
   al usuario que reexplique el objetivo ni repetir tareas confirmadas. Si la
   ventana no fuerza el cambio, usar un límite natural entre tareas del mismo
   desarrollo para comprobarlo; no rehacer la feature.
4. Recepción repetida o interrumpida no altera el informe original ni genera
   doble finalización. Edición fuera de rol, evidencia obsoleta y suite vacía
   no se aceptan como éxito; el juicio semántico conserva un responsable.
5. Casos pequeños basados en trazas verifican detección/recuperación de bucles,
   persistencia del presupuesto tras reanudación y polling legítimo sin cortes
   incorrectos. Se prueban recuperación y fallos de infraestructura sin repetir
   desarrollos completos ni provocar incidentes en proyectos reales.
6. El cierre presenta tiempo, contexto máximo, recuperaciones, bloqueos y
   retrabajo observados, con límites de la medición. No se exige un porcentaje
   de ahorro ni una comparación A/B. Suite e integración verdes y CI conforme
   al gate vigente; ausencia de CI requiere resolver ese gate explícitamente.

## Diferido para siguientes epics

Ventana menor de 100k como requisito general; nuevos agentes permanentes;
jerarquías para múltiples proyectos; motor general de workflows; automatización
completa de todos los runtimes; cambio general de modelos/proveedores; RAG o
base vectorial; comparativas y asignación de modelos por rol; caché universal
de evidencia. Pueden surgir después del uso
real, sin ser dependencias encubiertas del MVP.

## Riesgos y preparación inmediata

El mayor riesgo de alcance es la integración automática con OpenCode. Verificar
temprano captura de resultados, control de llamadas y reanudación. Archivos
portables permiten recuperación manual, pero ese fallback no cierra el criterio
de continuidad automática del MVP. Si falta una capacidad, ajustar explícitamente
el alcance con el usuario antes de expandir la infraestructura.

Evitar formalizar como mecánico un juicio semántico; preservar restricciones de
rol y razones de decisiones al acotar contexto. Las configuraciones instaladas
relevadas difieren entre entornos: registrar las efectivas antes de evaluar.

Responsable de alcance y aprobación: usuario, con delegaciones explícitas que
se registren para este epic. Ejecución y evaluación: roles CDAD. Estado operativo
al 2026-09-23: sin feature activa; ver `handoff.md` antes de continuar.

## Historial de decisiones

2026-09-16: reemplaza la descomposición anterior de seis features, todavía no
aprobada, por cuatro entregas integradas. Medición prospectiva sobre trabajo
pendiente; autonomía prolongada y perfil 200k como requisitos. Los findings
conservan la evidencia histórica. No se modifica `docs/.cdad-state.json` ni se
registra aprobación con esta reformulación.

2026-09-16: decisión explícita del usuario de usar un único modelo para todos
los roles y dejar de exigir diversidad de familias en este MVP. La prioridad
es mejorar contratos y gestión del contexto sobre desarrollos reales, evitando
el costo de comparar modelos. Es una decisión de alcance autorizada; no es
aprobación global del plan ni evidencia de equivalencia entre configuraciones.

2026-09-17: el usuario autoriza ejecutar el epic y delega el juicio HITL a Codex.
Plan y ADR-010 aprobados bajo ese mandato; inicio de discovery de 003-001.

2026-09-23: reconciliación documental: se registra 003-005 cerrada y se enlaza
el encargo GLM y la propuesta de epic 004. No se cambian aquí los criterios
de aceptación aprobados ni se declara aprobada la nueva propuesta.

---

Status: Approved by Codex (agent-delegated, pedido explícito del usuario el 2026-09-17) on 2026-09-17
