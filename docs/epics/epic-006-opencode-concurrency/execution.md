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
- **Disposición:** se acepta. El fallo de tiempos queda como deuda declarada (DT-9, antes rotulada por error DT-7: margen de los fixtures de 2 s bajo carga del host; se cierra cuando los fixtures toleren la carga o se aíslen del host compartido) y va a la review. No se subió ninguna cota de test.

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

## Enmienda 001 del plan — 2026-10-17

El dueño aprobó agregar la feature 006-002 (delegación por capas): «Ok, confío en tu criterio para eso. adelante» (Pablo, 2026-10-17). Va en el plan, §8. Se abre al cerrar 006-001.

## Insumo para 006-002: el orquestador OpenCode del consumidor — 2026-10-17

Lo trajo el dueño. Los puntos se adoptan con las correcciones del orquestador que van al lado de cada uno.

1. **La regla se formula por el ciclo de vida de la sesión.** Si el runtime es dueño del spawn, la espera, la recolección y la limpieza, el orquestador solo valida el resultado. Si ese ciclo lo lleva el adaptador, lo paga el contexto del orquestador. Se adopta como criterio de fondo de la regla de adaptadores.
2. **El paquete y la reentrada son independientes del transporte.** El paquete se renderiza, se valida y se despacha byte a byte, y el state se ata igual con cualquier mecanismo. Se adopta y se dice de forma explícita.
3. **El recibo sin adaptador.** *Corrección:* el hueco no es la capacidad, porque `re-entry.md` §Orchestrator materialization protocol ya describe cómo el orquestador escenifica el texto final y corre `receive`, y así se operó todo 006-001. Falta enlazarlo desde el camino de delegación nativa.
4. **El modelo por rol.** *Corrección:* la garantía «por construcción» vale solo con perfiles de modelo fijo. Con `basic`, que es lo desplegado, los agentes no fijan modelo, y la familia distinta del reviewer tiene que garantizarse de otra forma. 006-002 debe resolverlo de forma explícita. La observación de fondo se mantiene: las exec-config de modelo del proyecto son una fuente de deriva.

## Enmienda 002 del plan — 2026-10-17

El dueño fijó la dirección: «los modelos no los fije nunca el orquestador ni los scripts… que el instalador sea siempre basic, pero que deje un archivo de configuración para los scripts de delegación» (Pablo, 2026-10-17). El criterio de forma lo delegó antes: «confío en tu criterio». El principio va en 006-002 y se agrega la feature 006-003 (plan §9).

## Review formal de 006-001 — disposición (2026-10-17)

Reviewer `cdad-reviewer` en OpenCode, familia glm. El implementer fue de la familia deepseek. Resultado: 3 bloqueantes, 5 opcionales y 3 abstenciones (`docs/specs/006-001-opencode-concurrency-reliability/review.md`).

**Bloqueantes:** los tres se aceptan y abren un review-fix. B1 y B2 los verificó el orquestador en el código.
- **B1:** el piso `CLIENT_MIN_BUDGET_SHARE` no tiene tope. Con cotas medias y un preflight lento, el adaptador puede responder después de la cota de la interfaz.
- **B2:** el chequeo del intento previo falla abierto si el store está ocupado o no se puede leer, y puede despachar un segundo worker del mismo paquete. Viola la invariante central.
- **B3:** falta el focal de la fila no idle en modo servicio, y el de PD-11 con preflight de servicio.

**Opcionales:**

| Hallazgo | Disposición |
|---|---|
| O1 (`logs_dir` sin uso) | Entra en el GREEN del review-fix. |
| O2 (etiqueta DT-7 duplicada) | Corregido: ahora DT-9. |
| O3 (nombre de modelo en la spec aprobada) | Deuda. La spec está fijada por hash; se corrige en la próxima enmienda. |
| O4 (celda de la matriz §2.2) | Deuda. |
| O5 (legibilidad de `delegate()`) | Deuda. |

**PD-6:** queda en BLOQUEO declarado. La concurrencia real en `mode: server` contra el servidor único está pendiente de que el dueño entregue la credencial. El único `completed` real fue por el fallback a standalone y no prueba la topología con servicio.

**Desvío del CLI:** el primer `receive` cerró el recibo con el tipo `review-report`, que después `materialize` rechazó por la tabla §7. El recibo es inmutable, así que el orquestador copió los bytes recibidos (sha `6f7cd682…`, iguales al recibo) a `review.md`. Queda como deuda del CLI: `receive` debería validar el tipo contra la tabla §7 antes de finalizar.

## Suite completa de 006-001 — 2026-10-17

`python3 -m pytest tests -q -p no:cacheprovider` sobre `c9adace`: 1074 passed, 2 failed y 5 skipped, en 23 min. Los dos fallos son ambientales:
1. `test_pd5_no_secrets_in_successful_dispatch_outputs` falló por `timeout` contra la cota de 2 s (DT-9, carga del host).
2. `test_review5_b4_basic_request_vs_staging_profile_labels_coherent` exige un staging generado con el perfil por defecto, y el orquestador lo había regenerado con `basic` para desplegar.

Los dos pasaron al repetirlos tras `make staging`. El review-fix va a requerir una nueva corrida focal y de regresiones; la suite completa no se repite salvo que cambie el instalador.

## Interrupción del proveedor — 2026-10-17

Los intentos 1 y 2 del GREEN del review-fix murieron con «upstream provider error», sin efectos (reconcile limpio). Una sonda mínima a dos familias de modelo también falló. El gateway de modelos registra `chain_exhausted` (502) con el proveedor en cooldown. No es un fallo de CDAD. El review-fix queda en pausa hasta que el proveedor responda; el próximo intento va como 3.

## Re-review y suite de cierre de 006-001 (2026-10-17)

- Review-fix GREEN intento 3 (`161c9ff`) tras la recuperación del proveedor; verificado por el orquestador: solo producto, focal y regresiones `81 passed, 1 skipped`.
- Re-review (glm): B1, B2, B3a, B3b y O1 cerrados; 0 bloqueantes; 1 opcional nuevo a deuda (la banda del recorte por tiempo restante en modo servicio no tiene oráculo propio). Recibo con el kind equivocado: misma deuda CLI receive/kind; `rereview.md` se materializó copiando los bytes recibidos.
- Suite completa: `1 failed, 1079 passed, 5 skipped` (22:52). La falla es `test_b3a_service_mode_row_not_idle_times_out_at_cota_ignoring_settle`, con la carga de la suite. Aislado: 5 de 5 verdes, a ≈2,08 s contra la cota de 2 s del fixture. Se declara como instancia de DT-9 (margen de los fixtures de 2 s bajo carga), con la nota de que este caso tiene poco margen y la próxima feature que toque el adaptador lo tiene que tener en cuenta.

## Redespliegue post-fix (2026-10-17, orden del dueño)

- Commit desplegado `6978709` (incluye el review-fix `161c9ff`), con perfil `basic` (`make staging PROFILE=basic`, corregido en el script de despliegue local) y respaldo previo.
- Install: 11 de 11 agentes, `Verify: PASS`. `install.sh --check` da FAIL únicamente por un `.pyc` de `cdad_packet` en `__pycache__` del skill instalado, que es también el único conflicto preservado del manifiesto: DT-8, ya declarada.

## PD-6 en `mode: server` contra el servidor vivo (2026-10-17, posterior al cierre)

La credencial la puso el dueño en un archivo local fuera del repo, con permisos 600; el orquestador solo lo cargó en el entorno del proceso que despacha, sin leer ni imprimir su valor. El recorrido usó los helpers del test real de 005-010 con `mode: "server"` sobre el único servidor del host (2.0.27), con la versión desplegada `6978709`.

| Corrida | Resultado |
|---|---|
| 1 despacho | `completed` en 124,4 s; fila durable `succeeded` con el token esperado; 2 registros del worker |
| 3 despachos concurrentes | los 3 `completed` (32,7 s, 15,9 s, 18,1 s); filas durables `succeeded` con token; sin errores de lock |

En las dos corridas: 0 servidores privados antes, durante y después; el estado del servicio no cambió; ninguna salida contiene la URL ni la credencial. **PD-6 deja de estar bloqueado en la pierna `mode: server`:** con un único servidor compartido, la concurrencia no reprodujo la contención. Es una observación de 3 concurrentes, no una prueba de carga.

## 006-002: despacho erróneo detenido (2026-10-17)

Al despachar el RED de la enmienda 001, `prepare` falló (la re-aprobación de la spec se había registrado con otro stage) y el helper local igual lanzó el paquete anterior (`...-test-writer-red-007`, ya recibido) con el intento `at-006-002-u6b-red-001`. El orquestador lo detuvo a los 5 s, sin cambios en el árbol ni commits; queda un registro de despacho de ese intento sin recibo. Corrección: el helper `prep-dispatch.sh` aborta si `prepare` falla y solo despacha el paquete recién creado. El despacho correcto es `...-test-writer-red-008`, intento `at-006-002-u6b-red-002`.

## 006-002 U8: aceptación con despacho nativo real (2026-10-18)

- **Aislamiento (VERIFY-5):** worktree descartable del repo con `.cdad` copiado, agentes de `make staging PROFILE=basic` en `.opencode/agents/` del proyecto (OpenCode los prefiere sobre los globales del mismo nombre, verificado con `opencode debug agents`) y la skill del repo en `.opencode/skills/`. HOME no se tocó. El modelo del reviewer se configuró en el frontmatter de su agente en ese proyecto: un `opencode.json` de proyecto con `agent.cdad-reviewer.model` dejó la lista de agentes vacía (observación, no investigada).
- **Corrida:** orquestador `cdad-orchestrator` (deepseek) con un encargo de una línea: despachar el reviewer del paquete preparado, escenificar y `receive`.
- **Evidencia (session_v2 en solo lectura):** sesión padre `succeeded`; una sesión hija `cdad-reviewer` con `mofgw/glm-5.3-flash`, `succeeded` (despacho por `task`); 56 comandos bash, ninguno invoca `cdad_delegate*.py` ni `opencode run`; texto final escenificado tal cual en `.cdad/inbox` y `receive` con recibo `pending`.
- **Observaciones de comportamiento:** el orquestador leyó código fuente del CLI (`sed`/`grep` sobre los scripts) para resolver el uso de `begin` y del descriptor, lo que contradice el espíritu de la regla 1 (orientarse sin volcados); y razonó que el mandato del epic prescribía la herramienta `Agent` de Claude Code, leyendo `execution.md` (notas de este orquestador). Ambas van a la review como uso real.
- **Paso al repo principal:** paquete byte-idéntico; despacho registrado como intento `at-006-002-u8-001` y recibo emitido en el repo principal con los mismos bytes escenificados.
