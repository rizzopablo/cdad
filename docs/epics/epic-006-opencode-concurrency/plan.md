# Epic 006 — Delegación OpenCode fiable con concurrencia

Fecha: 2026-10-16.

**Estado: propuesta para aprobación del dueño.** Preparada por su solicitud de
planificación; no activa el epic, no aprueba una spec y no concede autoridad por
sí misma. Epic-005 permanece cerrado. Los identificadores son propuestos: antes
de activarlos, comprobar que no fueron asignados por otra sesión.

## 1. Resultado y prioridad

Permitir que CDAD delegue trabajo a OpenCode mientras otras sesiones legítimas
siguen trabajando, con una selección de runtime explícita, entrega verificable
y recuperación útil ante fallos del almacenamiento compartido.

Es una corrección prioritaria porque dos despachos reales del implementer
terminaron por contención en la base de sesiones. No exige separar los proyectos,
restringir el contexto global de los agentes ni serializar todo el desarrollo.

| Orden | Feature propuesta | Resultado | Dependencias |
|---|---|---|---|
| 1 | `006-001-opencode-concurrency-reliability` | Diagnóstico acotado, política de ejecución y corrección del adaptador/procedimiento; aceptación aislada y recepción en trabajo real. | Producto de epic-005 disponible; autoridad nueva para este ciclo. |

Este epic contiene una sola feature para utilizar el arranque normal del
architect: el CLI vigente necesita un epic activo para su contrato. No reabrir
epic-005 ni completar el nuevo plan con mejoras ajenas al incidente.

## 2. Evidencia inicial y sus límites

Comprobaciones realizadas en el incidente de un proyecto consumidor:

- OpenCode declara versión `2.0.27`; dos sesiones del implementer terminaron
  `failed`, aproximadamente a los 89 y 487 segundos.
- Ambos errores de runtime incluyen `LockTimeoutError` y `database is locked`.
  En el segundo aparece `SessionRunner.publishLLMEvent`: falló la persistencia
  de un evento del LLM. Esto acredita el mecanismo, no identifica al tenedor
  del bloqueo.
- La base usa WAL. Se observaron aproximadamente 4,6 GB de base y 543 MB de WAL
  (unidades decimales). El tamaño del WAL **no prueba** checkpoint starvation:
  SQLite puede conservarlo y reutilizarlo sin truncarlo.
- El adaptador del repo y el instalado coincidían byte a byte al revisarlos.
  `cdad_delegate_opencode.py` elige `--server` cuando la configuración declara
  `server`; en otro caso usa `--standalone`. Las configuraciones examinadas del
  consumidor omitían `server` y compartían la misma base.
- `POLL_INTERVAL_SECONDS = 0.05` existe, pero el adaptador primero espera al
  cliente mediante `subprocess.run` y **después** consulta el resultado durable.
  No hay evidencia de 10.000 consultas de ese bucle durante los 487 segundos.
  No usar ese cálculo como línea base ni como explicación del fallo.
- Se reportaron varios servidores/runtimes usando el store. El inventario de
  procesos y el responsable del bloqueo necesitan verificación nueva.

Fuentes para interpretar la evidencia:
[concurrencia y WAL de SQLite](https://sqlite.org/wal.html),
[reporte similar de OpenCode en otra versión](https://github.com/anomalyco/opencode/issues/47566).
El reporte externo no demuestra que exista una corrección aplicable al runtime
instalado. Disco libre no descarta latencia de almacenamiento; éxito de otras
sesiones no identifica al tenedor del bloqueo.

Rutas de código para discovery, relativas al repo:
`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`,
`skills/cdad-cycle/scripts/cdad_delegate.py` y
`skills/cdad-cycle/references/cli-delegation.md`.
Comprobar sus versiones; los números de línea pueden cambiar.

## 3. Discovery breve: decisiones que debe resolver

El architect recibe este plan y un registro local del incidente. Entrega evidencia,
decisiones recomendadas y una spec/plan proporcionales; no reproduce desarrollos
ni necesita investigar exhaustivamente toda la infraestructura.

1. **Topología real:** distinguir clientes de servidores, procesos necesarios de
   posibles huérfanos, stores compartidos y ejecuciones activas. Inventariar sin
   interrumpir ni terminar procesos. Determinar qué se puede observar y qué queda
   desconocido sobre transacciones, espera de locks y progreso de checkpoints.
2. **Compatibilidad:** verificar cómo el servidor recibe proyecto, rol, permisos,
   modelo y paquete; cómo resuelve agentes de proyecto y qué versión carga.
   Un servidor compartido no garantiza una cola única de escrituras ni agentes
   actualizados. Un marcador de archivos no demuestra instrucciones cargadas.
3. **Política de ejecución:** comparar reutilizar servidor declarado con usar
   standalone. La preferencia inicial es reutilizar un servidor compatible en
   operación habitual; la decisión final requiere evidencia. Standalone sigue
   disponible para usos justificados. No buscar servidores arbitrarios, conectar
   a otro usuario ni cambiar silenciosamente de modo o de store.
4. **Recuperación:** diferenciar sesión fallida, cliente desconectado, timeout y
   resultado todavía desconocido. Un timeout del cliente no prueba que terminó
   el worker. Reconciliar antes de repetir o permitir otro escritor.
5. **Frontera del arreglo:** precisar qué corrige CDAD y qué requiere mantenimiento
   o una corrección upstream de OpenCode. Si el bloqueo no puede eliminarse aquí,
   implementar una mitigación soportada y declarar su límite; no prometer capacidad
   concurrente ilimitada ni convertir CDAD en administrador de bases.

Usar consultas pequeñas, de solo lectura, con duración acotada y cierre explícito.
No escanear todas las conversaciones ni ejecutar carga sobre el store vivo.
Los identificadores, endpoints, credenciales, rutas personales y procesos concretos
pertenecen a un registro local ignorado por Git. La documentación versionada usa
alias y rutas relativas, con las limitaciones de observación declaradas.

## 4. Criterios para la spec y la aceptación

El architect los convierte en postcondiciones verificables; esta lista no sustituye
la aprobación de la spec.

**AC-1 — Selección comprensible.** Cada intento permite conocer modo solicitado y
efectivo, identidad/procedencia del runtime y store, o qué no pudo verificarse.
Secretos y datos locales no aparecen en salidas públicas. Una configuración
incompatible da diagnóstico y acción siguiente; no hace fallback silencioso.

**AC-2 — Mismo encargo y autoridad.** En los modos soportados se conservan proyecto,
paquete byte-idéntico, rol, capacidades y modelo configurado cuando corresponda.
Se verifica la identidad de sesión y la entrega durable con el mecanismo existente.
Una entrega no aprueba el gate. No ampliar alcances para resolver infraestructura.

**AC-3 — Concurrencia útil.** Una prueba controlada demuestra dos sesiones
independientes concurrentes en la topología elegida, correlación correcta de sus
entregas y ausencia de interferencia en sus encargos. No requiere dos paquetes
activos en un mismo ciclo CDAD: usar ejecuciones/proyectos descartables separados.
Declarar versión, configuración, carga y alcance de la prueba; no generalizarla a
todas las cargas o versiones.

**AC-4 — Fallo recuperable.** Contención, servidor no disponible y ausencia de
resultado producen una terminación/diagnóstico coherentes, sin éxito ni receipt
fabricados. Reutilizar el vocabulario existente cuando alcance. Antes del nuevo
intento se comprueba si el anterior sigue ejecutándose y qué efectos dejó.
No reintentar automáticamente escrituras o comandos del proyecto completos.

**AC-5 — Espera proporcional.** El adaptador no consulta cada 50 ms de forma
indefinida. Preferir señal de finalización soportada o polling con intervalo
razonable/espera progresiva, presupuesto total y consultas acotadas. Elegir valores
en la spec, configurables donde aporte utilidad; no vincularlos a este VPS.
Mantener la validación durable, incluso si se usan notificaciones.

**AC-6 — Versión estable.** Definir quién prepara/gestiona el servidor y cómo se
comprueba compatibilidad al comenzar. No recargar un servidor compartido ni cambiar
la instalación de un ciclo activo para resolver el despacho. Una incompatibilidad
debe ofrecer una salida legítima: servidor preparado o modo explícito compatible.

**AC-7 — Recepción real.** Tras el despliegue autorizado, retomar una unidad pendiente
del consumidor desde su estado reconciliado. Observar su convivencia con actividad
normal, sin inducir bloqueos en producción ni repetir el desarrollo ya realizado.
Registrar entrega, re-entry, errores, reintentos y tiempos observados. Un único éxito
es evidencia de ese recorrido, no prueba de eliminación de toda contención.

**AC-8 — Producto portable.** Alinear adaptador, configuración de ejemplo y referencia
canónica con las decisiones. No imponer HOME, puertos, paths, proveedor, modelo,
TMPDIR ni un gestor de servicios específico. No duplicar el procedimiento en todos
los agentes ni introducir allowlists por comando.

## 5. Construcción propuesta: tres unidades y una recepción

| Unidad | Resultado | Validación proporcional |
|---|---|---|
| T1 | Política explícita de selección, compatibilidad y diagnóstico; implementación mínima donde discovery confirme la brecha. | RED/GREEN focales sobre invocación y comportamiento observable; regresiones del adaptador afectado. |
| T2 | Espera eficiente y recuperación ante infraestructura, preservando correlación, límites y efectos previos. | Contención/fallo controlados en stores y procesos descartables; recuperación sin falsa entrega ni ejecución duplicada. |
| T3 | Integración de los modos soportados, procedimiento canónico y candidato instalable. | Recorrido concurrente aislado; revisión independiente; suite completa una vez al cierre de código. |
| Recepción | Despliegue autorizado entre ciclos y AC-7 sobre trabajo real. | Evidencia instalada y del consumidor; sin otra suite completa si no cambió código ni condiciones que la invaliden. |

T1 precede a T2; T3 integra ambas. No multiplicar sesiones por cada diagnóstico o
variante. El test-writer define los tests sin ver implementación nueva; el
implementer no edita tests; el reviewer es independiente del implementer y conserva
la política de modelos vigente para la ejecución. La recuperación del rol no debe
depender exclusivamente del runtime OpenCode que se está investigando: Claude
puede usar delegación nativa autorizada y declarar sus capacidades reales.

El plan de feature incluye comandos concretos y alcance de validación por unidad.
Regresión focal durante RED/GREEN; suite completa una vez al cierre de código,
repetida solo si cambios o evidencia invalidada lo justifican. Una review formal al
final, seguida de re-review de bloqueantes; variantes sin impacto material van a
deuda. Priorizar resultado y evidencia frente a cantidad de tests o trámites.

No fijar una reducción porcentual inventada de locks, tokens o tiempo. Medir lo
observado: modos/procesos utilizados, espera, consultas del adaptador cuando sea
medible, finalizaciones, errores, reintentos e intervenciones. Desconocido no es cero.
No exigir un presupuesto de contexto universal: mantener pequeña la coordinación
y dar a cada rol el contenido técnico que necesite para trabajar bien.

## 6. Autoridad, arranque y límites operativos

- El mandato de epic-005 venció. Su referencia en `status` es histórica; no heredar
  ni reactivar aquella delegación. La nueva autoridad procede del encargo que el
  dueño efectivamente entregue a Claude y queda registrada con ese alcance.
- Este plan permanece propuesto hasta recibir esa aprobación. Con el encargo de
  inicio que lo apruebe, Claude puede activar el epic, registrar el nuevo mandato,
  delegar discovery, aprobar spec/plan bajo esa delegación y conducir el ciclo.
  No registrar ahora aprobación de una spec inexistente.
- Un solo escritor del state de CDAD. No modificar el state del consumidor desde
  este epic: su orquestador reconcilia y retoma su unidad con su propia autoridad.
- Operar el ciclo con una instalación estable identificada al comenzar; construir
  y validar la candidata en una raíz aislada. No cambiar la propia instalación en
  mitad de su construcción ni la de otros proyectos activos.
- Quedan reservados al dueño: despliegue/activación global, cambios en HOME,
  reinicios o terminación de servicios/procesos compartidos, mantenimiento de la
  base viva, actualizaciones del runtime, push y publicación. Preparar primero la
  acción concreta y su impacto; pedir autorización solo cuando se necesite.
- No borrar WAL/SHM, ejecutar VACUUM/checkpoints agresivos ni copiar únicamente
  el archivo principal de una base viva como supuesto respaldo consistente.
  Si hace falta mantenimiento, proponer ventana, método de respaldo y verificación.
- No imponer un límite global de agentes, un sandbox por proyecto, una migración
  de base o un fork de OpenCode como atajo sin justificar un cambio de alcance.

## 7. Handoff y cierre honesto

En cada cambio de sesión dejar un handoff breve con versión, unidad, paquete e
intento vigentes, cambios, evidencia reusable, incertidumbres y próxima acción.
IDs crudos y detalles operativos se conservan localmente; el resumen versionado
está anonimizado. No releer todo el historial para reanudar.

Si hace falta autorización operativa para la recepción, entregar candidato,
review, evidencia y receta de despliegue/rollback, dejando AC-7 pendiente con dueño
y siguiente acción explícitos. No acreditar aceptación real por pruebas aisladas
ni cerrar el epic como totalmente aceptado mientras falte esa comprobación.

La investigación puede concluir que parte de la solución es upstream. El resultado
útil sigue siendo una mitigación comprobada, selección de ejecución comprensible
y recuperación que no pierda trabajo; el cierre declara el riesgo residual.

## 8. Enmienda 001 — feature 006-002 (2026-10-17)

**Por qué es de este epic.** El incidente vino de un orquestador dentro de OpenCode que delegaba a OpenCode lanzando `run --standalone` por bash. Su arnés nativo (`task`) no lo hacía. 006-001 vuelve seguro el adaptador. 006-002 corrige la regla que llevó a usarlo.

**Principio de capas (del dueño):**
- **skills:** la metodología, general y única;
- **agentes:** el comportamiento por runtime (OpenCode, Claude Code y los que se sumen);
- **scripts:** independientes del runtime y dependientes del SO (bash y Python en GNU/Linux).

**Regla de adaptadores:** sirven para orquestar agentes de **otro** runtime o para un runtime **sin delegación propia**. En cualquier otro caso se delega con el mecanismo nativo.

**Feature `006-002-delegation-by-layer`** (depende de 006-001):
1. `cdad-cycle` §4 queda sin reglas de runtime: el principio, la regla de adaptadores y las invariantes de rol (reviewer de otra familia, aislamiento).
2. Cada agente orquestador (OpenCode y Claude Code) declara cómo delega en su runtime y cómo garantiza la familia distinta del reviewer en cada perfil, incluido `basic`.
3. Las referencias de delegación propias de cada runtime pasan de la skill a la capa del runtime.
4. Disciplina de contexto del orquestador:
   - orientarse con `status`, sin volcados;
   - rotar la sesión en los bordes de tarea;
   - no reparar por su cuenta (delegarlo a un rol);
   - no usar `/tmp`.

**Aceptación:**
- ninguna skill nombra herramientas de un runtime para delegar;
- cada agente orquestador tiene su regla;
- los tests de referencias y `make validate` pasan;
- un orquestador OpenCode con perfil `basic` puede resolver el despacho del reviewer sin ambigüedad.

**Fuera de alcance:** el handoff y la config del consumidor, que actualiza su dueño; runtimes nuevos.


## 9. Enmienda 002 — modelos por configuración; feature 006-003 (2026-10-17)

**Principio (del dueño):** los modelos nunca los fija el orquestador ni los scripts. Dentro del runtime se usa el que esté configurado en el entorno. En los despachos a otro entorno, el modelo sale de un archivo de configuración. Elegir modelo no es una decisión de orquestación.

**006-002 suma:**
- el principio anterior;
- la regla de despacho por dueño del ciclo de vida de la sesión;
- el paquete y la reentrada independientes del transporte;
- el recibo en la delegación nativa, enlazado a `re-entry.md`.

**Feature `006-003-installer-single-profile-delegation-config`** (depende de 006-002):
1. El instalador queda siempre `basic`: sin perfiles y sin mapa de modelos. ADR-007 queda reemplazado.
2. El instalador deja una plantilla de configuración de delegación (modelo por rol y destino). La completa el usuario o la configura el agente una sola vez a pedido.
3. Los scripts de delegación toman los modelos solo de ese archivo.
4. El invariante del reviewer de otra familia pasa a ser una **verificación de configuración**. Un script compara los modelos efectivos del reviewer y del implementer, avisa si son de la misma familia, y el gate de review registra «invariante no garantizado» en vez de esconderlo.

5. **Credencial del servidor OpenCode (agregado 2026-10-17).** El instalador crea `~/.config/cdad/` (respetando `$XDG_CONFIG_HOME`) con la config de delegación y un `opencode-server.env.example` sin valor que explica de dónde sale la contraseña (la del `opencode serve` que se use; con OpenChamber, su configuración) y que debe estar en el entorno del proceso que despacha. El usuario lo copia a `opencode-server.env` con permisos 600. El script lo carga si existe, sin leer ni imprimir el valor, y lo rechaza con un diagnóstico claro si los permisos son más abiertos que 600. Un campo `credential_env_file` de la config de delegación apunta a otra ruta. El diagnóstico de 401/403 nombra las variables, la ruta y de dónde sale el valor.

**Aceptación:**
- con un fixture de servidor que exige credencial, el diagnóstico basta para resolverlo sin otra documentación; el `.env` con permisos abiertos se rechaza;
- sin perfiles en `install.sh` ni en `make staging`;
- el agente orquestador y los scripts no nombran modelos;
- la verificación de familias está probada con fixtures;
- `install.sh --check`, `make validate` y la suite pasan.

**Fuera de alcance:** la config de agentes del runtime del dueño (OpenChamber) y la del consumidor.

## 10. Enmienda 003 — decisiones vigentes; feature 006-004 (2026-10-17)

**Problema:** un ADR registrado no gobierna el trabajo siguiente si ningún rol lo recibe. El índice de un proyecto puede incluso afirmar que no hay decisiones.

**Feature `006-004-active-decisions-table`** (después de 006-002), chica a propósito:
1. `systemPatterns.md` (plantilla del Memory Bank) suma la sección «Decisiones vigentes»: una fila por ADR con archivo, estado (vigente u obsoleto, y cuál lo reemplaza), resumen en una línea y roles que deben consumirlo.
2. El orquestador la mantiene: agrega la fila al aprobarse un ADR y marca el reemplazado como obsoleto. El paquete de cada rol lleva las filas vigentes que lo nombran.
3. El reviewer revisa que la tabla coincida con los ADR del repo y que el cambio respete las decisiones vigentes de su rol.
4. Una decisión que cambia la metodología de CDAD no está terminada hasta que su regla está en el skill o el agente instalable; la fila guarda la referencia.

**Aceptación:** plantilla y referencias actualizadas (`stage-5`, re-entry, reviewer); un test de texto que fija la sección y las dos responsabilidades; `make validate` y la suite pasan.

**Fuera de alcance:** índices generados, gates de cita obligatoria y cambios en `status`.

Status: Approved by Pablo on 2026-10-16; enmienda 001 (006-002) approved by Pablo on 2026-10-17; enmienda 002 (006-003) approved by Pablo on 2026-10-17; enmienda 003 (006-004) approved by Pablo on 2026-10-17; agregado de credencial a 006-003 approved by Pablo on 2026-10-17
