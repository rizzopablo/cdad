# Ejecución del epic 006

## Mandato y aprobación — 2026-10-16

El dueño respondió: «Apruebo `docs/epics/epic-006-opencode-concurrency/plan.md` y te delego la
HITL para este ciclo, con el alcance, vencimiento y límites allí definidos. Orquestalo usando CDAD
hasta completarlo.» (Pablo, 2026-10-16). La marca de aprobación quedó al final de `plan.md`.

**Delegado:** Claude (sesión de Claude Code en este repo), orquestador del epic.

**Alcance (plan §6):** activar el epic, registrar este mandato, delegar discovery, aprobar spec y
plan de `006-001-opencode-concurrency-reliability` bajo esta delegación, priorizar la review,
validar gates, aprobar el Memory Bank con evidencia y conducir el ciclo. La severidad de los
defectos no se relaja.

**Vencimiento:** al cerrar, cancelar o revocar epic-006. El plan dice «para este ciclo» sin fecha;
esta lectura es del orquestador. No hereda ni reactiva la delegación de epic-005.

**Reservado al dueño (plan §6):** despliegue o activación global, cambios en HOME, reinicio o
terminación de servicios o procesos compartidos, mantenimiento de la base viva, actualizaciones del
runtime, push y publicación.

**Un solo escritor del state:** el orquestador OpenCode no opera este repo mientras dure el epic.
El state del consumidor («el otro proyecto activo») no se modifica desde aquí.

**Instalación estable del ciclo:** `29a4805` (HOME). La candidata se construye y valida en una raíz
aislada.

**Delegación de roles:** herramienta `Agent` de Claude Code con los subagentes `cdad-*`
(`cdad-cycle` §4, `claude-code-delegation.md`), lo que no depende del runtime investigado. El
reviewer debe ser de familia distinta a la del implementer; el runtime y el modelo reales de cada
despacho se registran en su intento.

**Cierre previsto:** AC-7 necesita un despliegue autorizado por el dueño y la reanudación por el
orquestador del consumidor. Si falta, el ciclo entrega candidato, review, evidencia y receta de
despliegue y rollback, y deja AC-7 pendiente con dueño y siguiente acción (plan §7).

## Cambio de alcance aprobado por el dueño — 2026-10-16

**Propuesta del orquestador.** Usar el runtime como fue diseñado: el servicio de fondo es dueño del store y corre las sesiones concurrentes. CDAD gana un modo `service` configurado, que pasa a ser el camino normal:
- antes de despachar, comprueba con `opencode service status` que el servicio esté corriendo y que su versión sea compatible;
- si lo está, despacha sin flags y el runtime se conecta como está diseñado;
- si el servicio no corre, CDAD **no lo arranca**: despacha `--standalone` y registra el fallback (solicitado `service` → efectivo `standalone`);
- si la config lo exige de forma estricta, termina en `blocked`.

`server` (URL explícita) y `standalone` se conservan. La invariante «nunca el modo por defecto» pasa a ser «nunca arrancar ni gestionar el servicio».

**Verificación en este ciclo.** Además del recorrido aislado:
- un despacho real desde un proyecto descartable contra el servicio vivo;
- después, dos despachos concurrentes con un encargo mínimo;
- en ambos, uso normal del servicio, sin reiniciarlo ni cambiar su configuración.

Que esto elimine los bloqueos **no se demuestra**: queda como observación empírica en la recepción y después (errores de bloqueo, reintentos y tiempos frente al incidente).

**Respuestas del dueño:** «Si, de acuerdo, me parece lo mas confiable como dices: configurado.» (Pablo, 2026-10-16). El dueño evalúa por su lado que OpenChamber use el mismo servicio. Esa topología queda fuera de este ciclo y reservada al dueño.

**Hechos verificados por el orquestador (solo lectura):**
- `opencode service status` imprime la URL o `stopped` con rc=0 y no arranca nada; lo confirma una prueba con estado aislado;
- `/api/info` del servicio exige autenticación y sin ella responde 401.

**Aplicación:**
- enmienda de la spec y el plan de 006-001, con una unidad T1b encima de T1;
- el RED de T2, en curso, no cambia, porque espera y recuperación son independientes del modo.

## GREEN de T2 — 2026-10-16

- **Intento 1:** se cortó a los 90 min (rc=124) sin commit. El reconcile no encontró efectos.
- **Intento 2:** commit `ddba831`. El rol informa 3 corridas conjuntas verdes.
- **Verificación del orquestador:** 7 corridas conjuntas (focal T2 + T1 + T1b + regresiones del adaptador). 4 pasan enteras, 3 de ellas seguidas; 3 fallan con `timeout` contra la cota de 2 s de los fixtures. Los fallos coinciden con carga alta del host compartido (load ~9) y pasan aislados.
- **Disposición:** se acepta. El fallo de tiempos queda como deuda declarada (DT-7: margen de los fixtures de 2 s bajo carga del host) y va a la review. No se subió ninguna cota de test.
