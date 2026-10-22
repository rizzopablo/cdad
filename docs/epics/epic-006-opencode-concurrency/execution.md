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

## 006-002: re-review y suite de cierre (2026-10-18)

- Review-fix B-1: RED `5c85d68` → GREEN `a25fc20`. Re-review (glm): B-1 cerrado, 0 bloqueantes; NF-1 y `sub-agent-strategies.md:49-50` (frontmatter de permisos y hooks de Claude Code en la skill) a deuda de capas.
- Suite completa: `1119 passed, 5 skipped` (21:47), sin fallas.

## Despliegue y push tras 006-002 (2026-10-18, orden del dueño)

- **Despliegue en HOME** de `e4d17e3` con perfil `basic` y respaldo previo. El primer `install.sh --check` mostró que las dos referencias retiradas por 006-002 (`opencode-delegation.md`, `claude-code-delegation.md`) seguían instaladas como `pending_removal`: el instalador no borra lo que dejó de desplegar, y solo `--uninstall` lo retira. Se corrió `--uninstall` (borra solo lo registrado en el manifiesto) y se reinstaló con `basic`. Queda solo DT-8 (`.pyc`).
- **Hallazgo para 006-003:** un despliegue normal deja en HOME archivos retirados que un orquestador puede seguir leyendo. 006-003 toca el instalador y es el lugar para resolverlo.
- **Push:** `main` a `origin` (`81ee8d3..41fc8b6`, fast-forward), tras barrer la anonimización sobre todo lo publicado; se saneó un id de sesión de fixture en `rf-red.md` de 006-001. No se publicaron ramas privadas ni los archivos sin trackear de otro agente.

## 006-003: paquete despachado sin entrega (evidencia para 006-005)

El 2026-10-18 el dueño retiró la verificación de familia (enmienda A-5 de la spec de 006-003) mientras el GREEN `-005` corría. Lo detuve a los ~3 min, sin cambios. `register-transition --transition disposition --resolution abandoned` registró la decisión, pero el paquete activo quedó en `dispatched`. Así, `prepare` rechaza todo paquete nuevo (PD-4), `--replace-packet` solo acepta paquetes nunca despachados y `reconcile` es de solo lectura. Ningún comando lleva un paquete despachado a `failed`. Lo cambié a mano (`active_packet.status: failed`, un solo campo, con la disposición como autoridad) y `validate-state` dio VALID. Es el caso «intento interrumpido sin entrega» de la enmienda 004: 006-005 tiene que darle un camino mecánico.

## 006-003: suite completa antes de la review

`pytest tests/` sobre `f072cf3`: **1166 passed, 1 failed, 5 skipped** (30 min). El fallo es `test_006_001_t1_selection.py::TestPd2ServerPreflight::test_pd2_connection_refused_is_transport_error` (`'timeout' != 'transport-error'`), que en aislamiento pasa 3/3 (1,6 s). Es la misma carrera conocida de los fixtures del adaptador bajo la carga de la suite, no una regresión de 006-003. `make validate` en este checkout da 168/1: el único FAIL es F011 por la deriva de la instalación del dueño, que es anterior al despliegue. Contra la instalación de aceptación de U8 da 169/0.

## 006-003: suite de cierre

`pytest tests/` sobre `8638d06` (tras la re-review focal 2): **1177 passed, 5 skipped, 0 failed** (30 min). PD-8c cumplida.

## Despliegue tras 006-003 (orden del dueño, 2026-10-18)

`.cdad/local/deploy-006-003.sh`: respaldo previo en `<workspace>/archive/` (árboles instalados + manifiesto), `make staging` sin perfil, `install.sh --force`, `install.sh --check`. Instalado `4bd9e0c`.
- **Obsoleto propio retirado en la instalación:** el marcador `.cdad-models-profile` (PD-6a en uso real). 11/11 agentes por runtime; ningún agente instalado tiene `model:`.
- **Config del usuario:** se creó `delegation.json` como plantilla vacía (`models.opencode` sin roles) y `opencode-server.env.example`; el `opencode-server.env` existente quedó intacto (solo se miraron metadatos: modo 600).
- **Reviewer instalado:** el respaldo ya era la versión generada anterior. La personalización del dueño (`model:` propio) se perdió entre los respaldos del 2026-10-17 a las 02:21 (todavía la tiene) y a las 19:35 (ya no), o sea en un despliegue de 006-001. Hoy solo cambió el texto del producto (A-5). Queda recuperable desde ese respaldo, a decisión del dueño.
- **`--check`:** FAIL solo por DT-8 (dos `.pyc` de `__pycache__` registrados como conflicto).
- **Efecto en el consumidor:** sus exec-configs con `model` ya no fijan el modelo (D3). Hasta que se completen `models.opencode.<rol>` en `delegation.json`, la delegación externa usa el modelo por defecto del destino.

## Uso real del adaptador por el orquestador (desde 2026-10-18, pedido del dueño)

El orquestador despacha ahora por el adaptador instalado (`cdad_delegate.py --destination opencode`, `mode: server` contra el servidor del dueño), sin `-m`: el modelo sale de `delegation.json`. Los defectos que aparezcan se registran acá.

- **D-ADP-1 (006-003 U6, real):** en `mode: server`, el adaptador carga la credencial de `opencode-server.env` para su propio preflight, pero no se la pasa al cliente `opencode run` que lanza. El cliente hereda `env = dict(os.environ)` (`cdad_delegate_opencode.py:426`) y falla con «Server … requires a password; set OPENCODE_PASSWORD» (`termination: transport-error`). Los tests de U6 no lo detectaron porque su binario falso no autentica. Lo que sí funcionó: `model_configured` salió de `delegation.json` con su procedencia. **Rodeo documentado:** exportar la variable en el entorno del proceso que despacha (`set -a; . ~/.config/cdad/opencode-server.env; set +a`), que es la precedencia de §2.3. **Fix propuesto:** inyectar la credencial resuelta solo en el entorno del cliente (nunca en argv ni en logs), con un test cuyo binario falso exija la variable. **Aprobado por el owner (2026-10-18) para 006-005; ya no como U0 aparte, sino dentro del módulo de runtime OpenCode (ver «Decisiones del owner» abajo)**, con este criterio: la credencial la resuelve e inyecta el adaptador sin que ningún agente intervenga. Ni el orquestador ni la sesión de rol la cargan, la ven ni la pasan. El cliente la recibe en `OPENCODE_PASSWORD` solo en `mode: server`. Al cerrar U0 se retira el rodeo del helper local de despacho.
- **D-ADP-2 (diagnosticado, 006-005 draft):** un despacho deja **dos** registros de intento para el mismo paquete. El del adaptador OpenCode (`opencode-<id>`) trae `model_reported` correcto, leído de `session_v2.model`, y coincide con `model_configured`. El de la interfaz común (`delegate-opencode-<id>`, `cdad_delegate.py` `_observation`) lo fija en `null` con la procedencia «destination adapter reported no model», porque el sobre del adaptador no lleva el modelo y `_normalize_envelope` solo conserva sesión, terminación, entrega y diagnóstico. **Fix propuesto (006-005):** un solo registro por despacho, escrito por una sola capa, con la observación que el módulo de runtime ya produce.
- **D-ADP-3 (límite de diseño, no defecto):** el adaptador entrega siempre una sola parte `role-report` con el texto final (`cdad_delegate_opencode.py` `FINAL_TEXT_ARTIFACT_KIND`). `cdad_result.py` `_allowed_kinds` lo admite a propósito para el architect en `discovery`/`draft`. El costo: `spec.md` y `plan.md` no salen como partes propias con hash del rol, sino del informe materializado (`docs/specs/006-005-native-path-parity/architect-draft-001.md`, delivery registrada). **Propuesta para 006-005:** que las partes esperadas las declare el paquete y que el núcleo las separe por marcadores, en las dos vías. El architect decide si entra o va a deuda.
- **D-ADP-4 (confirmado en código, no observado en vivo):** el adaptador arma el agente como `cdad-<rol>` (`cdad_delegate_opencode.py` `_entry_agent_name`) y nunca lanza la variante por stack (`cdad-<rol>-odoo`), aunque `prepare` publica las derivadas `-odoo` (`cdad_packet.py`, sufijo `-odoo` → rol base). `REQUEST.json` no tiene campo de agente ni de stack. Un proyecto con `stack: odoo` recibiría el agente genérico sin aviso. En este proyecto no se manifiesta (sin stack).

### Decisiones del owner sobre el despacho (2026-10-18, entran a 006-005)

1. **Una entrada para el orquestador:** `cdad_dispatch.py --packet <id> [--runtime X]`. El runtime sale del flag (contexto de la conversación) o, si no viene, de la configuración del proyecto; si no hay ninguno, error claro. El orquestador no pasa exec-config, modelo, credencial ni modo, ni carga entornos.
2. **Un módulo por runtime que sabe lanzar, esperar y recoger.** Resuelve desde la config de usuario de CDAD (junto a `delegation.json`, una sección por runtime) binario y versión verificada, modo y URL, modelo por rol y credencial si la usa. La credencial de OpenCode `mode: server` (D-ADP-1) es parte de ese módulo, no un contrato genérico de entorno. Se retiran el exec-config local y el helper de despacho con su rodeo.
3. **El agente viaja en el paquete:** `prepare` lo resuelve con rol más `stack` y lo escribe en `REQUEST.json` (`agent`). El módulo de runtime lo traduce a su invocación; si el agente no está publicado, falla cerrado antes de despachar (D-ADP-4).
4. **En la vía nativa el orquestador decide `subagent_type` al despachar.** La divergencia no se puede prevenir; se **detecta**: `record` verifica que el agente de la sesión sea el del paquete (llave «agente» de la correlación), en las dos vías.
5. **Mismo runtime que el orquestador → subagente nativo; otro runtime → adaptador.** Sin override de agente en `prepare` mientras no haya un caso real.
6. Pendiente de verificar en el ciclo: `opencode run --agent cdad-<rol>-odoo` de punta a punta.
- **D-ADP-3 escalado a defecto real (2026-10-18, plan-review de 006-005):** el dictamen del reviewer llegó por el adaptador como `role-report`, y `materialize` lo rechaza: `artifact_kind 'role-report' is not permitted for role 'reviewer'/substage 'plan-review'` (`cdad_result.py` `_allowed_kinds`). Re-recibir los mismos bytes con el kind `plan-review` choca con el recibo durable («the incoming part set differs from the durable receipt»). Por la misma tabla, la vía del adaptador deja sin materializar la entrega de **todo rol salvo el architect**: el reviewer admite solo `review`/`plan-review`, el test-writer `test-audit` o `test-writer-role-report`, el implementer `implementer-role-report` y el scribe `scribe-*`. **Rodeo:** el orquestador copió el dictamen byte a byte a `docs/specs/006-005-native-path-parity/plan-review.md` (`cmp` idéntico a la parte del recibo) y registró la entrega con el sha del recibo y del artefacto. **Consecuencia:** D-15 del draft-002 (D-ADP-3 a deuda) queda sin sustento: hay un caso real. **Propuesta mínima para 006-005:** el kind de la parte lo fija el núcleo desde rol y subfase del paquete (el único kind admisible cuando hay uno; `role-report` para el architect), en las dos vías.

### Decisiones del owner sobre los gates de 006-005 (2026-10-18)

Tras el análisis de un revisor externo (Codex) y la recomendación del orquestador, el owner confirmó:
1. **PD-19 aprobada** (enmienda de la consecuencia INV-9 de 005-012): la disposición deja `failed` el paquete activo sin recibo durable. Condiciones: afecta solo al paquete identificado; repetirla es seguro; conserva el tratamiento de entregas tardías; marcar `failed` no detiene un worker ni un proceso remoto, así que antes de repetir el encargo se reconcilian sus efectos posibles (`reconcile`).
2. **Runtime explícito:** `--runtime` en cada despacho; no hay «runtime del proyecto» (el mismo proyecto se trabaja desde varios entornos; lo que importa es el destino del despacho). Un valor por defecto puede sumarse después si aporta utilidad. V-9 queda resuelta.
3. **Modelo y credencial fuera de `runtimes.json`:** el modelo sigue en `delegation.json` y la ruta de la credencial donde la fijó ADR-033. Corrige el fraseo «credencial si la usa» de la decisión 2 de despacho.

Puntos del revisor externo que entran al draft-004:
- **Correlación por transporte:** la regla general es demostrar la asociación entre intento, paquete y ejecución con la evidencia de cada transporte; las llaves concretas son del módulo y de la vía (en la externa el módulo crea la sesión y la conoce por id; no hay padre que comparar). La igualdad rígida `directory == raíz` no prueba el proyecto y rechaza el recorrido legítimo desde otra carpeta. Tres resultados distintos: identidad verificada; no verificable (garantía menor declarada con entrega nativa confiable); verificada e incorrecta (rechazo, nunca `unknown`).
- **Escritura efectiva del temporal:** autorizar `.cdad/tmp` en el paquete no basta si el agente derivado no puede escribirlo (hoy el test-writer derivado edita solo tests, `_derived_maps`). U3 incluye el permiso del agente derivado; la aceptación exige una escritura real con la herramienta del rol (`scope_validation: passed` no lo prueba: lo ignorado queda fuera del manifiesto).
- **Transición del consumidor:** paso de migración explícito y acotado (qué se traslada, cómo se verifica, en qué borde se adopta), sin dos fuentes vigentes a la vez.

### Evidencia para 006-006: qué revisa el reviewer (2026-10-18)

La review completa del draft-002 y la re-review focal del draft-003 verificaron la coherencia interna, las citas de código y la letra de las decisiones del owner, y no detectaron los dos defectos de recorrido que vio el revisor externo (correlación igual en ambas vías; temporal autorizado pero no escribible). El procedimiento instalado ya pide juzgar si el plan alcanza la intención (`reviewer-plan-review.md`: «a well-formed plan that does not is a blocking finding»). La falla fue de operación: la intención no viajó como escenarios comprobables en el encargo (el del orquestador enumeró decisiones y puntos de letra) y el alcance focal de la re-review excluyó volver a trazarla. Criterio del owner: el reviewer revisa **cumplimiento del contrato** (lo principal) y calidad (secundaria). Propuesta para 006-006: el encargo de review lleva la intención como escenarios de recorrido; el reviewer traza cada escenario por las PD («si todas pasan, ¿el especialista puede hacer su trabajo?»); y una re-review focal vuelve a trazarlos cuando la corrección cambió el diseño.

## 006-005: spec y plan aprobados (2026-10-18)

Recorrido de enmienda 006 aplicado: architect draft-002 → review (2 B, 8 O) → draft-003 → re-review focal (sin B) → revisor externo + decisiones del owner → draft-004 con escenarios E1..E5 → review por escenarios (1 B: el recorrido de U6 recibía dos veces el mismo paquete) → draft-005 → re-review por escenarios (sin B; O-6, O-7 erratas de letra declaradas en la marca). Aprobación del orquestador por HITL delegada; PD-19 y las decisiones de runtime, modelo y credencial, del owner. Evidencia para 006-006: con los escenarios como vara, la review encontró defectos de recorrido que las reviews centradas en la letra no vieron (B-1 de U6, O-2 copia del agente, O-3 umbral de discriminación). Todas las entregas del reviewer se copiaron a mano por D-ADP-3 (lo corrige U7/PD-23 de esta feature).


## Delegación HITL amplia (2026-10-19)

El owner delega el HITL completo al orquestador para avanzar sin consultarle, «con criterio amplio de acuerdo a la necesidad del usuario real del sistema». Sigue vigente: sin push hasta que el owner lo autorice; despliegues en HOME y operaciones de servicio solo por orden del owner.

## 006-005: sonda V-7 antes del RED de U2 (2026-10-19)

Lectura de solo esquema (`PRAGMA table_info(session_v2)`, `mode=ro`) del store de la versión instalada (OpenCode v2.0.27): la tabla **sí** expone `parent_id`, `directory`, `time_created` y `agent`, además de `id`, `model`, `time_idle` e `idle_outcome`. La premisa de la spec («hoy sólo `agent` es evaluable») venía de `SESSION_V2_COLUMNS` (el subconjunto que el módulo **exige**), no del esquema real. Consecuencia para U2: `capabilities.session_correlation` declara las columnas observadas y, con `parent_id`/`time_created`/`directory` presentes, el umbral de §2.3 se alcanza en esta versión; la vía nativa (E1) puede acreditar «verificada» en lugar de quedar en garantía menor. El umbral y el `unknown` siguen vigentes para versiones que no las expongan. No cambia el contrato: la spec ya hacía depender la acreditación de lo que la versión exponga. **Ampliación (2026-10-19, U6-4):** tipos y unidades, leídos también solo del esquema: `time_created` es `INTEGER NOT NULL` en milisegundos epoch, `parent_id`/`agent` `TEXT`, `directory` `TEXT NOT NULL`. La sonda original registró solo nombres y por eso los fixtures inventaron segundos `REAL`. Una sonda de store debe registrar tipo y unidad.

## 006-005 U6: recorrido real (en curso, 2026-10-19)

- **E5, migración real del orquestador (el consumidor real de esta vía):** `cdad_dispatch.py migrate --runtime opencode --legacy-exec-config .cdad/local/exec-oc-server.json` en `--dry-run` imprimió la sección clave por clave e informó dónde viven modelo y credencial; la corrida real escribió la sección en `~/.config/cdad/runtimes.json` (archivo nuevo, solo lo lee el código nuevo; reversible); repetirla dio rc≠0 sin pisar. Decisión del orquestador bajo la delegación amplia: usar la config real del usuario, porque redirigir `XDG_CONFIG_HOME` también cambiaría el entorno del cliente `opencode` y confundiría el recorrido.
- **Hallazgo U6-1 (defecto real):** la verificación de E5, `cdad_dispatch.py capabilities --runtime opencode`, responde `version: unknown` y «the execution configuration declares no durable session store (`sessions_db`) … no destination binary (`binary`)» aunque la sección los tiene. Causa (código): `module_capabilities` invoca `--capabilities` del módulo sin pasarle la configuración derivada de la sección, que `dispatch` sí entrega. Los tests de U1b/U2 no lo vieron porque el fixture le pasa la configuración al módulo directamente. Efecto en el uso previsto: el paso «migrar → capabilities → despachar» no puede verificar nada. Fix propuesto: `capabilities` deriva la sección y la entrega al módulo por el mismo canal que `dispatch`, con un RED que lo observe por la entrada.
- **Hallazgo U6-1 corregido** (RED `ed64092`, GREEN `caaab97`): `capabilities` real ahora responde `version: opencode v2.0.27`, `session_correlation: true`, `native_observation: true` y nombra las columnas observadas.
- **Proyecto descartable:** worktree del repo en HEAD `52ff3ad` dentro de otro repo git (layout anidado), con `.cdad` copiado; coordinador ejecutado desde la carpeta de afuera con `--project-root`. Política del proyecto aceptada con `temporary_roots: [".cdad/tmp"]` por `prepare --reconcile-policy` con decisión citada (revisión 2 de la ejecución).
- **E3+E2, vía externa (test-writer):** `cdad_dispatch.py dispatch --packet … --runtime opencode` sin credencial en el entorno del coordinador ⇒ `termination: completed` (D-ADP-1 corregido en uso real); **un** registro de intento, el del módulo, con `model_reported` = `model_configured` (D-ADP-2); la parte llega como `test-writer-role-report` y `materialize` rc=0 con bytes idénticos (D-ADP-3); el agente derivado lleva `.cdad/tmp` como `allow` y el rol **escribió el auxiliar con su herramienta sin bloqueo** (E2 por la vía externa) y commiteó solo `tests/` con su test pasando; transición `delivery` ⇒ `completed`.
- **Hallazgo U6-2 (preexistente, transversal):** el recibo del despacho externo sale con `scope_validation: unknown`. Ninguna pieza del producto produce `observed_changes` (el manifiesto de cambios observados): `cdad_result.py` solo lo consume, y lo construyen los fixtures de test (también el de PD-17). En uso real, el control mecánico de que un rol con escritura tocó solo su alcance nunca corre, en ninguna vía; quedan como barreras los mapas de permiso del agente y la revisión del diff por el orquestador. No lo introduce 006-005 y no impide E2 (el rol trabaja), pero la evidencia de alcance de PD-17 solo existe en fixtures. Propuesta: deuda con disparador para una feature propia (producir el manifiesto con la línea base al `begin` y al final de la corrida, en las dos vías).
- **E3, scribe por la vía externa:** la parte única llega como `role-report` y `materialize` rc=0 dentro de `docs/specs/<feature>/`; el mismo informe hacia `docs/activeContext.md` ⇒ rc=2 nombrando la raíz permitida (el Memory Bank sigue fuera). E3 cumple sin excepción.
- **E1+E2, vía nativa con el coordinador en la carpeta de afuera:** orquestador OpenCode (agente global `cdad-orchestrator`, modelo pasado por el orquestador Claude) iniciado en la carpeta contenedora, con id de sesión padre elegido; en v2.0.27 la herramienta se llama `subagent` (no `task`). El hijo `cdad-test-writer` trabajó con `pwd` = la carpeta de afuera y rutas absolutas del proyecto. **E2 nativo BLOQUEADO, atribuido a la copia global (O-2):** la escritura del auxiliar y la del test fueron rechazadas por `permission.rejected` («This non-interactive run cannot ask the user for permission…»), también para `tests/`; el proyecto de la sesión es la carpeta de afuera, así que el runtime no carga los derivados del proyecto y aplica la copia global, cuyos mapas son relativos a esa carpeta. No invalida U3 (la vía externa escribió el auxiliar). El hijo creó el test por redirección de shell y lo declaró: la barrera de `edit` no cubre bash (límite conocido de permisos por ruta).
- **Hallazgo U6-3 (defecto de contrato, E1):** `record` del intento nativo rechaza la entrega: «the `project` key does not match … The session directory must belong to the authorized project root». La sesión hija corrió en la carpeta **contenedora** del proyecto, lo que la regla de pertenencia trata como contradicción. Pero E1 exige que la vía nativa funcione con el coordinador iniciado desde otra carpeta: §2.3 contradice a E1 en este layout. **Decisión del orquestador (HITL delegada, criterio del revisor externo: la igualdad o pertenencia rígida no debe descartar un recorrido legítimo):** la llave «proyecto» pasa a tres valores — directorio dentro de la raíz ⇒ coincide; directorio **ancestro** de la raíz ⇒ no evaluable (no prueba ni contradice: el contenedor puede alojar otros proyectos); directorio ajeno a la raíz ⇒ contradicción (rechazo). La acreditación positiva sigue exigiendo una llave discriminante (padre o momento la dan aquí). Se corrige con RED/GREEN y se re-registra el intento nativo.

- **U6-3 corregido** (fix `e7c39a5`): re-registrado el intento nativo, ya no hay rechazo. Sale `session: null` con «not evaluable: `moment`; not evaluable: `project` (ancestro)». La entrega byte-exacta se recibió como PD-6, garantía menor declarada: `receive` rc=0, parte `test-writer-role-report`, `semantic_status: pending`. Se conserva como evidencia del comportamiento previo al fix siguiente. No se re-registra el mismo despacho (PD-1).
- **Hallazgo U6-4 (defecto real de la vía nativa, dos partes):**
  1. **El momento nunca es evaluable contra el store real.** En v2.0.27, `session_v2.time_created` es `INTEGER NOT NULL` en **milisegundos epoch**; `parent_id` y `agent` son `TEXT` y `directory` es `TEXT NOT NULL`. La entrada solo interpreta instantes ISO, así que la llave queda `unknown`. Además, la degradación sale con las mismas palabras que el caso ancestro («not evaluable»), sin nombrar que el valor del store no se pudo leer como instante (O-6/INV-4). Causa de fondo: la sonda V-7 registró nombres de columnas, no tipos ni unidades, y el fixture de U2 inventó segundos `REAL`. Ningún test vio la forma real.
  2. **La selección del candidato bajo el padre es arbitraria.** `--observe` toma la primera fila con ese `parent_id`, sin filtrar por agente ni momento. E1 tenía un solo hijo y no se vio. Una sesión de orquestación real despacha muchos hijos a lo largo de su vida:
     - un hijo anterior de otro rol ⇒ contradicción de `agent`, es decir, el **rechazo de una entrega legítima**;
     - dos hijos del mismo rol posteriores a `--since` ⇒ elección arbitraria con todas las llaves coincidiendo, es decir, una **acreditación falsa** (viola INV-2). El test O-3 de U1b no lo detecta porque un módulo falso reemplaza la selección.
  - **Decisión del orquestador (HITL delegada):**
    - **Candidatos:** las filas bajo el padre declarado cuyo agente es el del paquete y cuyo momento es posterior a `--since`. Con exactamente uno ⇒ se evalúa. Con ninguno ⇒ no hay fila. Con más de uno ⇒ no se acredita, se nombra la ambigüedad y **nunca** se rechaza.
    - **Unidades:** el instante del store es un hecho del runtime, así que la entrada recibe un instante interpretable sin adivinar unidades.
    - **Diagnóstico:** un valor no interpretable se nombra como tal. La nota no verificada nombra también las llaves que sí coincidieron.
  - Se corrige con RED/GREEN, sobre un store descartable con la forma real, a través del módulo real. Después del fix, un despacho nativo nuevo desde la carpeta de afuera debe salir **verificado**: padre y momento coinciden, proyecto no evaluable.
- **E4, intento que no vuelve, por la vía externa.** Paquete nuevo, `dispatch` lanzado desde la carpeta de afuera. Con el rol en curso (auxiliar ya escrito con su herramienta) se simuló la caída del coordinador: SIGKILL al grupo de `dispatch` y del módulo, y el cliente del runtime quedó vivo, como en una caída real o en el timeout de la herramienta de shell de un coordinador agente.
- **Hallazgo U6-5 (defecto real, bloquea E4):** el registro I8 de la vía externa se escribe **al terminar** («every termination posterior to loading REQUEST.json»). Una muerte del proceso lo salta. Evidencia observada:
  1. Sin registro de intento, el paquete queda `prepared` con una sesión del runtime trabajando en el proyecto.
  2. `reconcile` ⇒ `classification: not-started`, `repeat_effect: false` («no dispatch and no receipt»): declara seguro repetir.
  3. `register-transition --transition disposition` ⇒ rechazo, «has no dispatch record … only a dispatched packet can be dispositioned»: no hay comando que lleve el paquete a `failed`.
  4. El cliente huérfano terminó y **commiteó** su test (`test: u6 probe e4`) sin que el estado lo registre; `reconcile` repetido sigue en `not-started`.
  5. El chequeo de intento previo (INV-10, doble escritor) solo mira registros con sesión, así que un re-despacho abriría un segundo escritor y repetiría el efecto.
  - El defecto es preexistente: el registro al final viene de 006-001. Pero E4 de 006-005 nombra exactamente este caso («un intento que no vuelve … sin repetir efectos») y la condición (d) de PD-19 del owner presupone que `reconcile` ve el despacho. Es un callejón sin salida para el uso previsto: solo saldría editando el estado a mano, cosa que el método prohíbe.
- **Enmienda U6-5 (decisión del orquestador bajo la delegación HITL amplia; review con 3 B ⇒ revisión 2 ⇒ re-review focal con E4 re-trazado: apta para RED).** Documentos: `docs/specs/006-005-native-path-parity/u6-5-decision.md` y sus dos reviews.
  - **Write-ahead:** el módulo externo escribe su registro I8 **provisional** (marca `write-ahead:`) antes de lanzar el cliente, y lo completa **una vez** en toda terminación con la misma observación que hoy escribe la terminación.
  - **Falla del write-ahead:** cierra antes de lanzar (`blocked`).
  - **Contratos enmendados:**
    - 006-001: D-5 (momento del registro y su falla), PD-8 (cláusula pre-despacho, solo para el registro provisional) y §2.6 (marca delante del primer literal);
    - la regla write-once del ledger admite una compleción única sobre la marca;
    - 006-005: la fila E4 de §3.1 se acota a la vía externa y el límite nativo D-U65-4 entra a §9 (salida procedimental: el siguiente coordinador ejecuta `record`).
  - **Deuda:** recuperar como entrega tardía la salida del huérfano que queda en el store (D-U65-5).
  - El texto de la spec aprobada está fijado por sha en la ejecución: la enmienda se aplica a `spec.md` en el cierre de la feature, con re-pin declarado, igual que los demás hallazgos de U6.
- **U6-4** (RED `8fe0d8c`, GREEN `b06bd2f`) y **U6-5** (RED `a0d96b5`, testfix `569682d` por contradicción del oráculo 3 con el 8 que detectó el implementer, GREEN `471db74`) quedan cerrados. Focales de 006-005: 116/116.
- **Re-recorrido en un proyecto descartable nuevo** (worktree en `83a897f`, con los dos fixes, coordinador en la carpeta de afuera):
  - **E1 nativo ⇒ verificado** «(parent, moment)», proyecto no evaluable (ancestro). La sesión del registro es la del hijo real y `model_reported` sale del store; `receive` rc=0 y la entrega queda `completed`. E2 nativo desde la carpeta de afuera sigue bloqueado por la copia global (O-2, límite declarado), y esta vez el rol se detuvo sin rodeo.
  - **E4 ⇒ cumple.** Con el rol en curso, el registro provisional `write-ahead:` ya tenía la sesión elegida. Tras el SIGKILL del grupo de `dispatch` con el cliente vivo:
    1. `reconcile` ⇒ `dispatched-unknown` (no autoriza repetir);
    2. el re-despacho ⇒ `blocked` («prior attempt … still LIVE»), sin lanzar un segundo cliente;
    3. `disposition` ⇒ `failed`, con `validate-state` VALID;
    4. el siguiente `prepare` procede.
    - El huérfano terminó y commiteó su test (efecto tardío visible en git). El estado sigue VALID y `reconcile` sigue sin autorizar la repetición. Su salida en el store es la deuda D-U65-5.
- **V-11 ⇒ cumple.** En otro proyecto descartable, el fixture `stack: odoo` (campo de bootstrap, declarado) da `REQUEST.json.agent` = `cdad-test-writer-odoo`. El despacho externo real (OpenCode v2.0.27) muestra `session_v2.agent` = `cdad-test-writer-odoo` e `idle_outcome` `succeeded`, con un único registro I8 final (sin marca) y la entrega recibida.
- **Hallazgo U6-6 (paridad, menor):** `model_reported` difiere entre vías. La externa lo normaliza a `<provider>/<model>`; la nativa (`record`) guarda el JSON crudo de `session_v2.model`. La atribución es correcta en las dos, pero la forma no es paritaria, y esta feature es la paridad de la vía nativa. Decisión: se corrige con un RED/GREEN corto, normalizando en el módulo, que conoce su store, igual que el momento de U6-4.
- **E1b, vía nativa con el coordinador en la raíz del proyecto** (otro proyecto descartable, agentes derivados del proyecto vigentes): la correlación sale **verificada** por las tres llaves (parent, moment, project). Pero el rol **no pudo escribir nada**: `permission.rejected` («cannot ask the user for permission») incluso en `tests/**`, que el mapa derivado permite. Así que el bloqueo de E2 nativo no se explica solo por la copia global (O-2).
- **Hallazgo U6-7 (defecto real, transversal y grave: las barreras por ruta no rigen en OpenCode v2.0.27).** Los agentes generados llevan la palanca `write: ask` (cdad-010 P1) **después** del mapa `edit`, en **todos** los roles, y v2.0.27 la evalúa para la herramienta de escritura. Se cumplió la regla de vigilancia que el propio comentario declara («if a future OpenCode version evaluates `write` at runtime…»). Con la última regla que coincide, todo pasa a *ask*:
  - **vía externa** (`--auto` aprueba los *ask*): **el rol escribe fuera de su alcance**;
  - **vía nativa no interactiva:** se rechaza **todo**.
  - **Sondas en el proyecto descartable, con agente derivado y despachos reales:**
    - **P1**, externa, test-writer intentando `docs/…`, fuera de su mapa ⇒ **escrito**;
    - **P2**, externa, sin la línea `write: ask` ⇒ `docs/…` «Permission denied: edit» y `tests/…` escrito;
    - **P3**, nativa desde la raíz, sin la línea ⇒ el subagente se invoca igual, el rol escribe el auxiliar en `.cdad/tmp` (V-14) y su test con su herramienta, el test pasa y commitea `tests/`, y la correlación sale verificada.
  - Atribución: la palanca. Por el mismo mecanismo (inferido, a verificar en la aceptación del fix), los roles de solo lectura (architect, reviewer, scribe) pueden escribir por la vía externa.
  - **Alcance en el uso real:** la copia instalada en HOME tiene la misma palanca, así que cada despacho externo actual corre sin barrera de escritura efectiva. La auditoría de los commits de rol de esta sesión no muestra escrituras fuera de alcance: los commits `test:` tocaron solo `tests/`.
  - **Decisión del orquestador (HITL delegada):** se corrige ya en el repo dentro de 006-005 (E2 es su escenario), quitando la palanca del generador para todos los roles, con RED/GREEN y una aceptación real que repite P1/P3 y una sonda de rol de solo lectura.
  - El **despliegue en HOME queda para la orden del owner**; hasta entonces, el orquestador audita el diff de cada rol contra su alcance.

## Despliegue del fix U6-7 (orden del owner, 2026-10-19)

`.cdad/local/deploy-006-005-u6-7.sh` (mismo procedimiento que 006-003: respaldo en `<workspace>/archive/`, `make staging`, `install.sh --force`, `--check`). Verify PASS, 11 agentes. Los agentes instalados de OpenCode ya no llevan la clave `write`. Los derivados de cada proyecto se rehacen desde la copia instalada en su próximo `prepare`. El owner también cambió los modelos en `delegation.json` por la crisis de proveedores, y autorizó abrir una feature para la review de borradores de spec (contrato `draft-spec`).
- **Hallazgo U6-8 (operación; criterio del owner: «ligarlo a una versión minor en la config puede ser excesivo»).** OpenCode pasó de v2.0.27 a v2.0.32 con el mismo esquema de `session_v2` (sonda de solo esquema: columnas y tipos iguales). Igual, el despacho quedó `blocked` porque el `binary_version` configurado (2.0.27) no coincidía con el servidor. El orquestador actualizó el valor en `runtimes.json` y en la config local para seguir. **Decisión:**
  - el control compara versiones **observadas**, cliente contra servidor, nunca contra un número escrito en la config;
  - la compatibilidad del store se verifica por **capacidad**: faltan las columnas que la correlación evalúa ⇒ fail-closed nombrándolas;
  - `binary_version` pasa a opcional e informativo: una diferencia se declara en el diagnóstico y no bloquea, y `migrate` deja de escribirlo.
  - Se corrige con RED/GREEN después de U6-7b.
- **Redespliegue con U6-7b y U6-8 (misma orden del owner, 2026-10-20)** en `b69bbac`: Verify PASS, y los scripts instalados coinciden con el repo.
  - `--check` FAIL solo por DT-8 (`.pyc` en `__pycache__`) y por «missing staged» de `cdad-orchestrator.md`/`cdad-reviewer.md` de OpenCode: son las copias que el owner personalizó (el reviewer con `model:` propio) y quedaron preservadas.
  - Ninguna de las dos lleva la clave `write`.

## Orden: 006-006 antes que 006-004 (owner, 2026-10-20)

En otro proyecto activo no se pudo pedir la review de un borrador de spec. El reviewer rechazó dos paquetes con razón: el contrato por defecto es la spec aprobada, el plan de la épica no se acepta para el reviewer y `draft-plan` exige `plan-tasks`. El owner aprobó atenderlo ya. Es el punto 1 de la enmienda 006 (006-006, aprobada el 2026-10-18), así que no se abre feature nueva ni se agrega un tipo de contrato: se adelanta **006-006 a 006-004**, tras cerrar 006-005. El orden queda 006-005 → 006-006 → 006-004.

## 006-005: review de etapa 4 (2026-10-20)

`docs/specs/006-005-native-path-parity/review.md`: 3 B y 2 O. Decisiones del orquestador (HITL delegada):
- **B-1:** gana la barrera del rol. El implementer nunca edita tests, ni convencionales ni co-ubicados, aunque estén dentro de una raíz de implementación; el derivado aplica la barrera del agente generado restringida por la política, nunca ampliada. Se reemplaza por A-1 el oráculo B3 previo (`test_004_002_t5_reviewfix.py`, que exigía permitir `src/tests/x.py`).
- **B-2:** la observación se normaliza en una frontera común (momento y modelo), cualquiera sea la forma de seleccionar la fila.
- **B-3:** las instrucciones distinguen la vía externa (consumir el recibo de `delivery_ref`) de la nativa (`record` escenifica y luego `receive`).
- **O-1:** se aplica al cierre.
- **O-2:** deuda.

## Push tras 006-005 (2026-10-20, orden del owner)

`main` a `origin` (`41fc8b6..5328712`, fast-forward, 327 commits). Antes se barrió la anonimización sobre los 216 archivos publicados: rutas del host, ids de sesión, IPs y puertos (el único hallazgo fue el puerto por defecto de OpenCode en un fixture) y nombres de otros proyectos (`sanitize.py`: 0 cambios). No se publicaron ramas privadas ni los archivos sin trackear de otro agente.

## 006-006: discovery y decisiones (2026-10-20)

`docs/specs/006-006-spec-plan-review/discovery.md`. Hallazgo central: el CLI no exige tareas, exige el token `plan-tasks` («el objeto está modelado como un plan»). Decisiones del orquestador (HITL delegada; el owner la mantuvo el 2026-10-20), todas según la recomendación del architect:
- **Diseño O2:** `contract.object_kind` (`spec`|`plan`) como extensión aditiva del contrato, el mismo patrón que `plan_version`. Sin kind, subfase, agente, etapa ni artefacto nuevos; los checks de plan solo se aplican si la forma es `plan`.
- **Q4, identidad doble:** cuando la revisión cubre spec y plan, el contrato fija los dos documentos por digest.
- **Q3:** se permite revisar el borrador de otra feature; el dictamen vive en la carpeta de la feature activa y nombra el objeto y su digest. La tabla de destinos no se amplía.
- **Q2, gate 2→3:** artefacto `plan-review.md` presente, con cada bloqueante resuelto o descartado con razón escrita. Obligación supervisada, sin bloqueo duro en el CLI.
- **Q5:** la revisión es siempre obligatoria, con profundidad proporcional.
- **Q1:** la exención solo la da el owner, explícita y registrada en `stage_history` (`exempted_by`, `delegated`, `requested_by`, `reason`).
- La deuda de nombre (`plan-review`/`draft-plan`) queda declarada.

## 006-006 construcción, recorrido y cierre (2026-10-20)

- U2, U3 y U4: RED→GREEN, sin A-1. U5 se cerró con el testfix del fixture (faltaba `delivery`).
- Owner, 2026-10-20: «estoy esperando este desarrollo para continuar otros proyectos, así que cuando necesites hacer despliegue hazlo». Despliegues en HOME en `a276531` (antes del recorrido) y en `86cb942` (cierre), con respaldo en `archive/`.
- U6, recorrido real (`u6-acceptance.md`): E1–E7 cumplen. Hallazgo **W-1**: un paquete de borrador preparado no se podía reemplazar. Decisión del orquestador: arreglarlo dentro de la feature (afecta la re-review de E4, que es uso previsto). RED `4f755ac`, GREEN `de629b8`, verificado con el CLI desplegado. **W-2** (rc=0 del adaptador en `blocked`) queda como observación.
- Review de etapa 4: apta para cierre, 0 B / 2 O. O-2 se aplicó; O-1 pasa a deuda.
- Suite de cierre: 1404 passed, 5 skipped.
- Siguiente: 006-004-active-decisions-table. El push queda a la espera de la orden del owner.

## 006-004 discovery y decisiones (2026-10-20, orquestador bajo HITL delegada)

El owner abrió la feature («Adelante con la siguiente feature»). Discovery: `docs/specs/006-004-active-decisions-table/discovery.md`. Decisiones del orquestador; Q1–Q6 siguen la recomendación del architect:

- **Diseño O1:** campo opcional del request con las filas vigentes, más una sección aditiva del render que solo aparece con filas (sin filas, el render es byte-idéntico). El CLI valida la forma de cada fila y que nombre al rol del paquete. Se descartan:
  - O2 (el CLI parsea la tabla del proyecto): acopla el producto a un formato de documento;
  - O3 (texto libre): no es verificable;
  - O4 (`--input`): no llega al test-writer.
  La completitud (que el orquestador declare todas las filas del rol) queda como procedimiento, deuda D-1.
- **Q1:** filas para las decisiones en vigor (Accepted/Verified) y para las reemplazadas, marcadas obsoletas con su reemplazo. Los Proposed no son filas.
- **Q2:** los roles los declara quien aprueba el ADR, al aprobarlo. El reviewer verifica que los roles existan; no juzga si la asignación es correcta.
- **Q3:** la feature siembra la tabla de este repo con ADR-034 primero y las decisiones en vigor que puedan justificarse con evidencia, y declara cuáles quedan fuera y por qué.
- **Q4:** «sin cambios en `status`» abarca el campo Status de los ADR y la máquina de estados. No se normaliza el vocabulario.
- **Q5:** la plantilla usa `## Current decisions` y este repo `## Decisiones vigentes`, como primer H2. El título no es dependencia del producto.
- **Q6:** el orquestador mantiene la tabla cuando se aprueba un ADR. No cambia el exit gate de stage 5.
- **Tope de filas por paquete:** declarado y fail-closed (D-6), con el valor que proponga la spec.
- **ADR-034:** la fuente única es una referencia del skill. La obligación de cada rol va en la fuente del rol y en su bloque estático, con un puntero (D-2). La aprobación del ADR-034 la hace el orquestador bajo la HITL delegada; el owner puede vetarla.

## 006-004 U5: siembra (2026-10-20)

El orquestador aprueba el **ADR-034** bajo la HITL delegada; el dueño puede vetarlo. Se materializó con `Accepted` y se sembró la tabla «Decisiones vigentes» de este repo: 26 filas y 8 `Proposed` excluidos. Evidencia: `docs/specs/006-004-active-decisions-table/u5-seeding.md`.

## 006-004 review de etapa 4: resolución de B-2 (orquestador)

- **Hallazgo:** el GREEN de U7 (`8f41160`) cambió `docs/systemPatterns.md:17` aunque su paquete (`…-implementer-green-005`) solo autorizaba implementación. La entrega quedó con `scope_validation: unknown`.
- **Auditoría del diff:** una sola línea. En el resumen de la fila de ADR-007, `(economical | optimus | premium)` pasa a `(economical, optimus, premium)`: las barras de la celda partían la fila de la tabla en columnas espurias. No hay ningún otro cambio en `docs/`.
- **Disposición:** esa parte de la entrega queda **inválida como entrega del rol**. El orquestador **adopta la corrección bajo su propia autoridad**: el upkeep de la tabla es suyo (ADR-003; plan U4/U5, «el orquestador escribe sus propias filas directamente en `docs/`»). Los bytes resultantes son idénticos a los del commit, así que no se reescribe la historia ni se cambia ningún oráculo.
- **Verificación:** el comprobador de la tabla de `tests/validate-consistency.sh` pasa sobre esos bytes (corrida de cierre).
- **Deuda:** el adaptador no produce `observed_changes`, por eso `scope_validation` queda `unknown` (U6-2 de 006-005, ya declarada). Este caso es una instancia más de esa deuda.
