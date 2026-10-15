# Continuidad de las features 003-002, 003-003 y 003-004

Estado: briefs técnicos; no sustituyen discovery, spec ni aprobación CDAD.
Actualizado: 2026-09-24. Sin push automático.

Aplicar [ADR-011](../../adr/ADR-011-autonomia-supervisada-limites-proporcionales.md):
libertad operativa dentro del encargo, supervisión con evidencia y respuesta
proporcional. El control no se mide por cuántas operaciones bloquea.

## Regla vigente para continuar

Punto de entrada: [handoff GLM](../../handoffs/2026-09-23-glm-continuation.md).
001 y 005 están **cerradas**. Antes de construir 002 se propone el
[epic 004 de fuente única y planificación](../epic-004-single-source-planning/plan.md),
aún borrador. GLM desarrolla; GPT/Claude hacen análisis profundo y review.
No usar automáticamente Sol ni heredar el mandato HITL de otra sesión.

Después del trabajo estructural aprobado, abrir cada feature pendiente con
`cdad-cycle`: discovery, spec, test audit, RED/GREEN, POST-AUDIT, review y
Memory Bank. Actualizar el handoff durable antes de cada delegación/transición.
No repetir desarrollos terminados ni hacer A/B; usar trabajo real pendiente y
fixtures pequeños para fallos provocados.

Los contratos entregados de 001/005 son la base, junto con las enmiendas que
realmente cierre 004. No reescribirlos sin consumidor/migración explícitos.
Mantener ADR-010 limitado a su alcance. Estos briefs no aprueban nuevos schemas,
umbrales ni tecnologías: el architect debe resolverlos contra el código vigente.

### Dependencias que cruzan las tres features

| Contrato | Productor responsable | Consumidor / decisión pendiente |
|---|---|---|
| Identidad estable, política y paquete | 001/005 + bootstrap propuesto en 004 | 002/003/004; no regenerar execution_id al reanudar. |
| Resultado original del agente | Canal de salida del runtime elegido | 002 recibe; documentar quién deposita bytes y cómo detecta truncamiento/fallo. |
| Receipt/evidencia durable | 002 | Re-entry, guards y reconciliación; no equivale a aprobación. |
| Eventos y presupuestos persistidos | 003 | Prevención de bucles y continuidad; no reiniciar al rotar sesión. |
| Active record/checkpoint | 004 de epic 003 | Reconstrucción/reconciliación automática; distinto del epic 004 propuesto. |

**Atención a los IDs:** `003-004-context-continuity` es la cuarta feature del
MVP original; `epic-004-single-source-planning` es otro epic intercalado.

Antes de cerrar cada spec, comprobar la capacidad crítica del runtime con el
menor probe útil. Si no se puede capturar un resultado, interceptar una llamada
antes de exceder su ventana o reconciliar sesiones, declararlo temprano. No
construir toda la solución sobre APIs supuestas ni confundir mocks con soporte
real. El probe histórico no certificó aislamiento completo.

## 003-002 — Artifact tools

### Material disponible

- `docs/specs/003-002-artifact-tools/discovery-draft.md`
- `docs/specs/003-002-artifact-tools/spec-draft.md`
- `docs/specs/003-002-artifact-tools/plan-draft.md`

Son drafts recuperados de `/tmp`; **no están aprobados**. Un architect nuevo
debe auditarlos contra 001/005 y los cambios efectivamente cerrados de epic 004. No
regenerarlos desde cero si siguen siendo válidos.

### Resultado y límites

Recibir los bytes originales de un rol, persistirlos atómica e idempotentemente
y devolver un recibo mecánico pequeño. Recepción, materialización y aprobación
semántica son operaciones distintas. El orquestador materializa desde el
original durable con autorización explícita; ningún helper resume, regenera o
aprueba contenido.

El draft propone `cdad_result.py`, store project-local `.cdad/runtime`, payload
UTF-8 de hasta 1 MiB, staged files, receipts inmutables, concurrencia local,
journal de materialización y evidencia acotada de Python unittest. No incluye
fetch SDK, blob store, workflow engine, cache universal, loops ni checkpoints.

### Decisiones que el architect debe confirmar

1. Si `.cdad/runtime` y `.cdad/inbox` son las raíces finales, su gitignore,
   permisos, cleanup y protección ante symlinks/solapamiento con source.
2. Semántica observable de dos receives concurrentes y de temporales huérfanos.
3. Reconciliación con `active_packet`: receive no modifica state; definir la
   transición única que aplica el orquestador y cómo se recupera tras crash.
4. Política cerrada `artifact_kind -> target`, CAS y journal de materialización.
5. Si el runner Python unittest pertenece al MVP de 002 o debe reducirse para
   evitar que artifact tools crezca hacia un sistema general de evidencia.
6. Adaptar campos y estados al schema realmente cerrado de 001; añadir
   migración/compatibilidad sólo si existe un consumidor real.
7. Identificar el productor de `RESULT.json` y de los staged files a partir de
   la salida original del runtime. Excluir fetch SDK del helper no elimina esta
   dependencia: definir un puente mínimo o una captura manual fiel explícita,
   con integridad/truncamiento verificables. Un fixture solo prueba el receptor.
   La captura automática necesaria para el recorrido final debe tener dueño
   y entrega asignados antes de cerrar el plan, no quedar implícita.

### Ajuste por autonomía supervisada

Conservar en el resultado original incidentes/obstáculos y referencias a la
política efectiva. El receipt valida hechos mecánicos; el orquestador decide
aceptación, corrección o escalamiento dentro del mandato. No convertir cada
deny en tarea fallida ni decidir cumplimiento por la existencia de un diff.
La evidencia debe identificar el estado probado, incluyendo archivos nuevos;
el estado final solo no demuestra ausencia de cambios transitorios. Actualizar
los schemas mínimos que se necesiten, sin un servicio separado de incidentes.

### Gates mínimos

- Bytes, digest e identidad exactos; UTF-8 vacío/inválido y exceso de tamaño
  fallan sin resultado durable.
- Retry y concurrencia idénticos convergen al mismo receipt byte a byte;
  contenido divergente conflictúa sin overwrite.
- Interrupción antes/después de publicación se reconcilia sin doble efecto.
- Receipt siempre conserva `semantic_status=pending` y no cambia state.
- Materialización sólo a target permitido, create-only/CAS, traversal y
  symlink seguros, retry parcial por journal.
- Evidencia de test no puede declarar verde una suite vacía, sólo skipped,
  stale, mutada o de alcance desconocido.
- Smoke desde instalación aislada, sin tocar la instalación real.

### Primer paso exacto

Actualizar `handoff.md`; delegar a GLM en modo architect con la base de código
vigente tras el trabajo estructural aprobado, los contratos de 001/005 y las
fuentes de 004 pertinentes. Pedir delta sobre los tres drafts, no reescritura;
resolver las siete decisiones anteriores y preparar una revisión GPT/Claude
antes de construir. El architect respeta su contrato read-only: devuelve los
borradores para materialización por el coordinador, salvo permiso vigente
explícito que establezca otro mecanismo.

## 003-003 — Progress guards

### Resultado

Detectar churn sin progreso, rechazos repetidos e intentos imposibles antes de
que consuman horas/contexto. Aplicar recuperación acotada y persistente sin
convertir el guard en orquestador estratégico. Debe vigilar también auxiliares
y sesiones reanudadas.

### Ajuste por autonomía supervisada

El guard observa tanto fricción del entorno como fallos del agente: una
operación legítima denegada, un wrapper incompatible o evidencia incompleta
pueden explicar el estancamiento. Clasificar con objetivo, rol, scope y efecto,
no solo el nombre del comando. Escalar una síntesis accionable al orquestador;
no conceder permisos ni endurecerlos automáticamente por un contador.
Registrar tareas/llamadas observables para interpretar tasas; desconocido no
es cero. Pruebas cubren trabajo legítimo que progresa, error de política y
violación material, además de los bucles. Sin benchmark ni feature adicional.

### Contratos de entrada

- Paquete, execution/state y métricas de 001.
- Receipt, resultado original, evidencia y journal de 002.
- Fricción medida en 004-001 (criterio 6): [friction-intake-004-001.md](friction-intake-004-001.md).
- Eventos observables de OpenCode documentados en `runtime-discovery.md`:
  tool calls/results, mensajes, status, children, errores y tokens reportados.
- Desconocidos permanecen `null`; bytes, tokens, costo y contexto simultáneo no
  se mezclan.

### Discovery obligatorio

1. Definir una huella canónica de intento: herramienta + argumentos
   canonicalizados + clase/tupla estable del resultado, excluyendo ruido.
2. Separar repetición improductiva de polling legítimo, relectura justificada,
   flaky tests e investigación que produce evidencia nueva.
3. Definir pre-flight determinista de capacidad/permisos/paths antes de llamar
   al agente, usando datos reales del runtime y sin afirmar sandbox inexistente.
4. Definir presupuesto persistido por unidad de trabajo: intentos, tiempo,
   rechazos y recuperación; reanudar no reinicia contadores.
5. Tabla cerrada de acciones: retry con cambio, backoff/poll, repackage,
   nueva sesión desde checkpoint, escalar al orquestador o bloquear. El guard
   nunca cambia spec, autoridad ni prioridad estratégica.
6. Aislamiento OpenCode: resolver primero la lectura de configuración heredada
   que invalidó el smoke; no enviar prompts/proveedores hasta demostrarlo.

### Postcondiciones sugeridas

- P1: detecta N repeticiones equivalentes sin progreso usando una regla
  explícita y deja evidencia de por qué son equivalentes.
- P2: polling con condición, deadline y cadencia válidos no se corta antes de
  tiempo; al vencer escala una sola vez.
- P3: rechazos de permisos/capacidad se prevalidan o se acotan; nunca hay loop
  ilimitado de la misma llamada denegada.
- P4: cada recuperación consume presupuesto durable y produce receipt/evento;
  restart o nueva sesión no lo reinicia.
- P5: ambigüedad o necesidad de decisión semántica vuelve al orquestador con un
  paquete breve, sin decisión autónoma encubierta.
- P6: fixtures de trazas cubren bucle, progreso real, polling, flaky y crash;
  no se repite un desarrollo completo para probarlos.

### Riesgos que no deben quedar implícitos

- Umbrales fijos pueden cortar trabajo válido; comenzar con reglas conservadoras
  y evidencia observable, no scoring opaco.
- Hash de salida completa es frágil; canonicalizar sólo campos estables y
  conservar la evidencia original por referencia.
- Abort puede llegar después de iniciar una llamada cara; el presupuesto 200k
  requiere prevención y margen, no sólo watchdog posterior.

### Primer paso exacto

Después de cerrar 002, delegar discovery a GLM en modo architect con las trazas
y hallazgos ya versionados y depurados de datos privados. Exigir una taxonomía de progreso y una tabla
evento→acción antes de escribir spec.

## 003-004 — Context continuity

### Resultado

Mantener una memoria activa pequeña y reconstruir automáticamente una sesión
del orquestador durante trabajo prolongado, conservando mandato, autoridad,
decisiones, tareas, agentes en curso, presupuestos y referencias a evidencia.
El historial completo queda fuera del prompt activo y sigue consultable.

### Ajuste por autonomía supervisada

Checkpoint/active record conservan versión de política, capacidades/limitaciones
reales, decisiones sobre desvíos y trabajo aún válido. Rotar sesión no reinicia
presupuestos ni obliga al usuario a repetir autorizaciones. No reintroducir
allowlists históricas por defecto ni cargar el historial entero de incidentes:
resumen activo y referencias íntegras recuperables según el rol.

### Dependencias

- 001 aporta identidad, paquete, estado y métricas.
- 002 aporta resultados/receipts originales e idempotencia de efectos.
- 003 aporta presupuestos, eventos, acciones de recuperación y detección de
  trabajo en curso. No diseñar continuidad ignorando esos schemas.
- `runtime-discovery.md` confirma create/list/messages/children/fork/status,
  pero el smoke no prueba aislamiento completo ni límite duro de contexto.

### Discovery obligatorio

1. Separar tres capas: active record pequeño, checkpoint inmutable y log/historia
   referenciable. Definir autoridad y checksum de cada una.
2. Contenido mínimo del active record: objetivo, scope, autoridad/expiración,
   decisiones con razón, incertidumbres, grafo de tareas, gates, agentes/sesiones
   activos, receipts/evidencia, presupuesto consumido y siguiente acción.
3. Protocolo write-ahead antes de dispatch y reconciliación posterior mediante
   session status + receipts. Una sesión desaparecida no equivale a fracaso ni
   autoriza repetir efectos.
4. Trigger preventivo: perfil inicial 200k con entrada máxima 150k, reserva 50k
   y preparación alrededor de 120k, pero sólo usando contadores compatibles del
   runtime. Si el límite real es desconocido, registrar `null` y usar margen
   conservador; no convertir bytes en tokens.
5. Reconstrucción selectiva: nuevo orquestador recibe active record, contratos
   vigentes y referencias necesarias, no transcript completo. Debe pedir
   expansión sólo dentro del permiso del rol.
6. Resolución de split-brain: dos sesiones reanudadas, checkpoint stale,
   autoridad vencida, state/receipt divergentes y tareas ya finalizadas.

### Postcondiciones sugeridas

- P1: checkpoint conserva todos los campos obligatorios y detecta tampering o
  references inexistentes.
- P2: reanudación reconstruye próxima acción sin pedir al usuario repetir
  objetivo/aprobaciones y sin heredar delegaciones expiradas.
- P3: trabajo dispatched se reconcilia antes de retry; efectos ya recibidos o
  materializados no se duplican.
- P4: presupuesto e intentos sobreviven al cambio de sesión; ninguna llamada
  gestionada excede el perfil declarado según la métrica disponible.
- P5: restricciones por rol sobreviven a checkpoint/repackage; el test-writer
  nunca recibe implementación por continuidad.
- P6: recorrido real pendiente incluye al menos una reconstrucción en un límite
  natural, más fixtures de crash/split-brain/stale sin rehacer trabajo cerrado.

### Aceptación del recorrido real

Identificar una feature pendiente antes de la integración final y usarla cuando
la continuidad esté disponible. No terminarla antes para luego repetirla. Registrar versiones,
modelo/runtime, máximo de contexto reportado, tiempos, recuperaciones, bloqueos
y retrabajo. No atribuir ahorro causal entre features heterogéneas ni exigir un
porcentaje. Si ninguna ventana fuerza rotación, hacerla entre tareas naturales
del mismo desarrollo, sin repetir la tarea.

### Primer paso exacto

Después de cerrar 003, delegar discovery a GLM en modo architect. Antes de spec debe
entregar schema del active record, algoritmo de reconciliación, triggers con
unknowns y matriz de crash/restart/split-brain.

## Política de modelos del recorrido final

El plan aprobado exige modelo único para el desarrollo real de aceptación.
La decisión reciente asigna desarrollo a GLM y análisis/review a GPT/Claude.
Documentar antes del recorrido si se conserva el criterio de modelo único en
esa validación o se aprueba una enmienda; no tratar el reparto de construcción
como evidencia del criterio original ni repetir la feature para comparar.

## Cierre del epic

No cerrar por tener las suites de las entregas individuales verdes. Además se requiere: desarrollo
real pendiente con modelo único, llamadas dentro del perfil declarado,
reconstrucción automática demostrada, recepción idempotente, guards sobre
trazas, integración/CI resuelta explícitamente y Memory Bank aprobado. Registrar
limitaciones y abstenciones sin convertirlas en garantías.
