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

## Recorrido real contra el servicio vivo (spec §5.5) — 2026-10-16

- **Cómo se corrió:** el orquestador usó el adaptador del repo (`d0a7963`) desde un proyecto descartable, con `mode: "service"` y `service.require: true`. Encargo mínimo de token fijo; store leído solo en ro.
- **Resultado:** `blocked` en el preflight, en 1,3 s, sin despacho ni sesión. El servicio informa versión **2.0.22** y el cliente es **2.0.27**. El gate D-11 cerró sin fallback a standalone (INV-10). No se consumieron tokens del proveedor.
- **Atribución de procesos:** `service status` mostró la misma salida antes y después (comparada por digest, sin registrar la URL). Ningún servidor privado `serve --stdio` nuevo: el que había antes del despacho es el del cliente interactivo que registra el discovery.
- **Hallazgo para el dueño:** con estas versiones, un `run` sin flags del runtime se conecta igual al servicio, porque resuelve con `mismatch="ignore"`. CDAD lo bloquea; otros clientes mezclarían versiones sin aviso.
- **Estado:** la pierna c de PD-6 queda en **BLOQUEO declarado**. Llevar el servicio a la versión del cliente (actualizarlo o reiniciarlo) está reservado al dueño. La pierna b (servidor aislado) también queda bloqueada: hace falta una clave en una variable de entorno, que el orquestador no tiene ni puede extraer.

## Topología del runtime — 2026-10-17 (decisión del dueño)

- **Hallazgo:** el servicio de fondo (`serve --service`, vivo desde el 2 de octubre) ejecutaba la imagen borrada del binario anterior (2.0.22). El cliente estaba en 2.0.27. El dueño reinició OpenChamber, que levantó su propio `serve` en 2.0.27, separado del servicio.
- **Acción:** por orden del dueño («bueno matalo»), el orquestador detuvo el servicio con `opencode service stop`. Ahora `service status` responde `stopped`.
- **Quedan:** el servidor de OpenChamber (2.0.27) y un cliente interactivo `--standalone` con su servidor privado, que el dueño no pidió tocar.
- **Consecuencia para CDAD:** con el servicio detenido, `mode: "service"` cae a standalone de forma declarada (o queda `blocked` con `service.require`). Para usar el servidor único, el consumidor declara `mode: "server"` con la URL de OpenChamber y la contraseña en `OPENCODE_SERVER_PASSWORD` u `OPENCODE_PASSWORD`.

## Recorridos reales con el servicio detenido — 2026-10-17

Adaptador del repo, proyecto descartable, encargo mínimo de token fijo y store leído solo en ro.

| Caso | Terminación | Tiempo | Detalle |
|---|---|---|---|
| `mode: service`, `require: false` | `completed` | 33,9 s | Fallback declarado `service` → `standalone` (service-unavailable). Fila durable con `agent cdad-test-writer`, `idle_outcome succeeded`, `version 2.0.27` y el token. Un solo servidor privado adicional durante el despacho, que se cerró al terminar. |
| `mode: service`, `require: true` | `blocked` | 1,1 s | Sin despacho y sin servidor privado. El diagnóstico dice que CDAD nunca corre `service start`. |

**Pendiente para PD-6:** dos despachos concurrentes contra el servidor único de OpenChamber (`mode: server`). El servidor exige autenticación (401 sin contraseña) y el orquestador no tiene la contraseña en su entorno.

## Despliegue en HOME — 2026-10-17 (orden del dueño: «Despliega»)

- **Qué se instaló:** el commit `b6c2193` y siguientes (solo docs) con perfil `basic`. El respaldo previo está en el archivo del workspace (`*-cdad-pre-006-001`). El adaptador en HOME coincide con el del repo (`e90dfcb5…`) en los tres árboles.
- **`install.sh` termina en rc=1 por dos razones ajenas a 006-001:**
  1. **CONFLICT preservado:** `~/.config/opencode/agents/cdad-reviewer.md` tiene contenido del dueño (modelo propio, editado el 2026-10-15). El instalador no lo sobrescribe, que es lo correcto. Decide el dueño.
  2. **Bytecode `__pycache__`:** el staging copiaba los `.pyc` que el uso deja en el árbol de la skill, y ahora el manifest los marca *pending-removal*. Queda como deuda del instalador (**DT-8**: excluir `__pycache__` del staging).
- **Rollback:** restaurar el respaldo, o reinstalar desde `29a4805`.

## Corrección del despliegue — 2026-10-17

- **Error del orquestador:** el staging se generó con el perfil por defecto (`optimus`), porque `--basic` de `install.sh` solo deja la marca y no cambia el staging. Así se instalaron agentes con modelos fijos.
- **Corrección:** `make staging PROFILE=basic` y reinstalación. Ningún agente instalado declara `model:`. `install.sh --check` da PASS, con 391 grupos.
- **Receta correcta para desplegar:** `make staging PROFILE=basic && bash install.sh --force --basic && bash install.sh --check`.

## Hallazgo: por qué el orquestador del consumidor despacha por bash — 2026-10-17

- **Evidencia:** una sesión del orquestador del consumidor con 1.145 turnos, 6 compactaciones y ninguna sesión hija. Todos sus despachos van por `cdad_delegate.py --destination opencode`.
- **Causa:** el handoff del consumidor prescribe ese comando con una exec-config por familia de modelo, una para el implementer y otra para el reviewer. Con el perfil `basic` los agentes no fijan modelo, así que `task` no garantiza que el reviewer sea de otra familia. El adaptador sí lo garantiza.
- **Brecha en CDAD:** `cdad-cycle` §4 pone `task` primero, pero no dice qué hacer cuando el perfil no fija modelos ni cómo se elige entre `task` y el adaptador estando dentro de OpenCode.
- **Ruido de contexto:** viene sobre todo de la orientación (volcados de state, ledger y skill: más de 1,5 M de caracteres de salida) y de reparaciones hechas por el propio orquestador (scripts en `/tmp`).
- **Destino:** unidad aparte, fuera de 006-001, a decidir por el dueño.
