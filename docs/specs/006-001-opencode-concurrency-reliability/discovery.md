# Discovery de 006-001-opencode-concurrency-reliability: decisiones, borrador de spec y plan T1-T3

Lo esencial:
- **Afirmaciones del plan:** las tres que había que comprobar son correctas. `--server`/`--standalone`, `POLL_INTERVAL_SECONDS` y el orden `subprocess.run` → consulta durable coinciden con el código.
- **Mecanismo del fallo:** las dos sesiones fallaron porque el runtime no pudo escribir en la base compartida en 5 s. Hay al menos tres servidores de larga vida escribiendo en esa base, más uno privado por despacho. Quién tenía el bloqueo sigue sin saberse.
- **Brechas del adaptador:** encontré varias, todas con archivo:línea:
  - el timeout pierde el id de sesión;
  - no se mira si el intento anterior sigue corriendo;
  - la espera de 50 ms puede durar hasta la cota completa;
  - el modo `--server` no tiene control propio de versión.
- **Aislamiento para AC-3/T2:** se puede mover la base a un store descartable con `OPENCODE_DB` o con `XDG_DATA_HOME`. Las dos tienen un costo: mover solo la base deja escrituras en HOME, y mover el directorio de datos deja al runtime sin credenciales.

No edité ningún archivo del repo ni del consumidor. Hubo una escritura en HOME que no estaba autorizada: mis invocaciones `--help` agregaron una línea cada una al log vivo (detalle en §0).

## 0. Alcance, versiones y método

- **Repo:** HEAD `3930ec6`. Entre `29a4805` (la instalación estable del ciclo) y HEAD, `git diff` no muestra cambios en `cdad_delegate_opencode.py`, `cdad_delegate.py` ni `cli-delegation.md`.
- **Adaptador instalado igual al del repo:** el sha256 empieza por `1f3d63d6…` en el repo y en los árboles instalados de OpenCode y de Claude. La interfaz común da `b47366dd…` en el repo y en el árbol de OpenCode.
- **Runtime:** `opencode v2.0.27` (`opencode --version`).
- **Lecturas del binario:** usé `strings` en el scratchpad y ventanas de texto acotadas. El código está minificado, así que los nombres internos son evidencia, no un contrato.
- **Base de sesiones:** 5 conexiones con `sqlite3` en `file:…?mode=ro`, `timeout=2`, cierre explícito y LIMIT. La primera tardó 0,021 s. Solo leí las filas de las dos sesiones del incidente, el esquema y PRAGMAs.
- **Log del runtime (44,8 MB):** búsquedas por id y agregados en Python leyendo cada línea hasta 400–600 bytes. No imprimí ninguna línea completa.
- **Procesos:** `ps`, `/proc/<pid>/{cwd,fd}` y `ss -ltnp`, solo lectura.

**Lo que dejó mi sesión (declarado):**
- Mi sesión es Claude Code (proceso `claude`). No es OpenCode y no tiene handles sobre la base de sesiones; mis lecturas fueron de un lector ro breve.
- Ejecuté 9 invocaciones del runtime con el entorno real: `--version`, `--help`, `run --help` (estos autorizados) y además `service/serve/debug/session/api/reload --help`. Cada una agregó exactamente una línea `cli starting` al log vivo en HOME, sin otra actividad (lo verifiqué en el log). Las que no eran `--help`/`run --help` no estaban autorizadas explícitamente; no las repito.
- Ejecuté tres `opencode debug paths` con XDG aislado, con HOME aislado y con HOME aislado más `OPENCODE_DB`. Escribieron solo directorios vacíos y un log dentro del scratchpad.

**Límites de observación:**
- La vista de procesos es parcial: hay un PID namespace, `/proc/1` no es visible y el padre de dos procesos tampoco.
- No hay forma de observar transacciones, esperas de lock, progreso de checkpoints ni latencia de almacenamiento.
- Que un servidor use una sola conexión por proceso queda desconocido.

## 1. Verificación de lo que afirma el plan

| Afirmación del plan §2 | Resultado | Evidencia |
|---|---|---|
| Se usa `--server` si la config declara `server`; si no, `--standalone` | Correcta | `cdad_delegate_opencode.py:772` lee `server`; `:270-273` arma uno u otro, nunca los dos ni ninguno |
| `POLL_INTERVAL_SECONDS = 0.05` existe | Correcta | `:97`, usado en `:482` |
| Primero `subprocess.run` y después la consulta durable | Correcta | `:842` (`_invoke_destination` → `subprocess.run` en `:287`) y luego `:862` (`_await_durable_outcome`). El sondeo empieza recién cuando sale el cliente. La cifra de 10.000 consultas no tiene base |
| Las configs del consumidor omiten `server` y comparten la base | Correcta | Las dos configs tienen `sessions_db` igual al del localizador, no tienen clave `server`, tienen `auto: true` y `wait.timeout_seconds: 3600`; el binario es el instalado |
| Duraciones ~89 y ~487 s | Correctas como `time_updated − time_created` | Según la referencia cambia el número: `time_idle − time_created` da 115,1 s y 496,3 s; desde `cli starting` hasta `Failed to drain Session` en el log, 117,7 s y 500,8 s |

## 2. Las cinco decisiones de §3

### D1. Topología

**Evidencia:**
- **Un solo store compartido** en `<data>/opencode/opencode.db`. Lo que describe a la base es `journal_mode=wal`, `page_size=4096` y `page_count=1.142.175`, o sea 4.678.348.800 bytes, igual al tamaño del archivo. Además, `freelist_count=427.905` (un 37,5 % de páginas libres), un WAL de 543.028.392 bytes (el mismo tamaño que en el reporte original) y un SHM de unos 1,08 MB.
- **PRAGMAs que no describen al runtime:** `busy_timeout=2000`, `wal_autocheckpoint=1000`, `synchronous=2` y `journal_size_limit=-1` son valores de **mi** conexión (el 2000 es mi `timeout=2`).
- **Configuración del runtime según el binario:** `PRAGMA journal_mode = WAL`, `synchronous = NORMAL`, `busy_timeout = 5000`, `cache_size = -64000` y `wal_checkpoint(PASSIVE)` al abrir, dentro de un `if(Ai)` condicional. En las cadenas no aparece un `wal_autocheckpoint` propio: es el default supuesto, VERIFY.
- **Escritores visibles ahora,** con descriptores abiertos sobre `opencode.db`, `-wal` y `-shm`, todos `opencode serve`:
  1. el servicio de fondo (`serve --service`, unos 14 días);
  2. un servidor con puerto explícito, hermano del proceso de la UI web (unos 38 h); según el log aloja la sesión del orquestador del consumidor;
  3. el servidor privado (`serve --stdio`) de un cliente interactivo `opencode --standalone` (unos 3,5 días).
- **En el incidente había un cuarto escritor por despacho:** el servidor privado `serve --stdio` de cada `run --standalone`. Vive lo que vive el cliente: su última línea de log aparece unos 1,6 s después del fallo.
- **Lo que no escribe en la base:**
  - los clientes (`run` y el interactivo) no tienen descriptor sobre la base;
  - el adaptador solo lee en ro y únicamente después de que termina el cliente;
  - las sondas ro del orquestador del consumidor, que el log muestra abriendo con `mode=ro`, son **posteriores** a los dos fallos, así que no prueban nada en ningún sentido;
  - hay tres procesos huérfanos colgados de init que corren desde el tmp compartido del runtime, sin descriptor sobre la base. Su origen es desconocido.
- **Cadena del error en el runtime:** `SessionRunner.drain/runStep` (y `publishLLMEvent` en la segunda sesión) → `effect/sql/SqlError/LockTimeoutError: Failed to execute statement` → `[cause]: SQLiteError: database is locked`. Es el `LockTimeoutError` de la capa SQL, no el `EffectFlock` de archivos, que también existe en el binario.
- **Lo que queda en el store durable:** el mensaje `idle` dice `{"outcome":"failed","error":{"type":"unknown","message":"Failed to execute statement"}}`. «database is locked» solo aparece en el log. `time_idle` coincide con el fallo del log al milisegundo.
- **Tiempo entre el último mensaje del asistente y el fallo:** 25,8 s en `<ses-1>` y 9,7 s en `<ses-2>`.
- **Errores de bloqueo en todo el log** (desde 2026-10-14 13:50Z hasta ahora):
  - los dos fallos del incidente, ambos en servidores privados de workers;
  - uno el 10-14 en otro camino de código (caché del catálogo de modelos, otro proceso). La contención no es exclusiva de CDAD.
  - las otras 5 coincidencias son textos dentro de comandos del orquestador, no errores.
- **Actividad en los 60 s previos a cada fallo:**
  - antes de `<ses-1>`: 6 líneas del servidor del worker, 2 del servidor del orquestador y 2 de un proceso de larga vida;
  - antes de `<ses-2>`: solo 91 líneas del servidor del worker.

  El log no registra transacciones.

**Desconocido (no es cero):**
- quién tenía el lock;
- cuánto duraron las transacciones;
- si los checkpoints avanzan; el mtime de la base (12:33) es anterior al del WAL (12:53), lo cual es compatible con checkpoints pero no lo prueba;
- la latencia del disco;
- si hay escritores fuera del namespace visible;
- cuántas conexiones abre cada servidor.

**Recomendación:** tomar como hecho que hay N≥3 procesos escritores de larga vida más uno por despacho standalone, y que cada uno espera hasta 5 s por el lock de escritura. Declarar que el tenedor es desconocido y no prometer menos bloqueos.

### D2. Compatibilidad

**Evidencia (binario y ayuda):**
- **Proyecto:** el cliente toma `n.root ?? process.env.PWD ?? process.cwd()` y lo manda como `location[directory]` o en la cabecera `x-opencode-directory`. Si no llega, el servidor usa su propio `process.cwd()`. El adaptador fija `PWD` en `:284-285`; hay que conservarlo.
- **Agente, modelo y sesión:** se pasan como `--agent`, `--model provider/model[#variant]` y `--session` (que crea la sesión si no existe), igual en los dos modos (`opencode run --help`). El paquete viaja por stdin del cliente en ambos modos (`:287`).
- **Permisos:** los resuelve **el cliente** `run`, suscripto al stream de eventos. Con `--auto` aprueba lo que no esté denegado; sin `--auto` rechaza («This non-interactive run cannot ask the user for permission…»). En modo servidor, entonces, los permisos dependen de que el cliente siga vivo.
- **Versión con `--server`:** el cliente hace `GET /api/info` con 5 s de timeout. Si la versión difiere solo escribe «Warning: … has version …; this client is …. Continuing anyway.» en stderr: **no falla**. CDAD necesita su propio preflight.
- **Credenciales con `--server`:** la contraseña sale solo de las variables de entorno `OPENCODE_PASSWORD` u `OPENCODE_SERVER_PASSWORD`, con usuario básico `opencode`. El adaptador hereda el entorno (`:284`). No hay ninguna clave de contraseña en la config.
- **Sin ninguna de las dos flags,** el cliente hace `ensure` del servicio de fondo: lo arranca como `serve --service` si falta, e ignora diferencias de versión por defecto. Por eso «nunca invocar sin flag» tiene que ser un invariante (hoy lo garantiza `:269-273`).
- **Standalone:** lanza su propio binario como `serve --stdio --port 0` con una contraseña aleatoria y `killSignal SIGTERM`/`forceKillAfter 3 s`. La versión es la misma por construcción.
- **Identidad del rol:** `session_v2.agent == cdad-<role>` se verifica (`:228-245`, `:891`). Eso prueba el nombre, no el contenido. El store guarda hashes por sesión en `instruction_state.initial_values` (`core/instructions`, `core/environment`, …) e `instruction_blob(hash,value)`. Si incluye el prompt del agente derivado: VERIFY, va a deuda.

**Desconocido:**
- si un servidor de larga vida ve agentes `.opencode/agents/` publicados después de su primer uso de ese directorio. Existe `opencode reload` («Reload configuration»), que sugiere caché, pero recargar está reservado al dueño;
- qué hace la sesión del servidor si muere el cliente cuando hay un permiso pendiente;
- si `/api/info` expone qué store usa el servidor.

**Recomendación:**
- Preflight del modo servidor: alcanzable, credencial aceptada (nunca leer, guardar ni imprimir su valor) y `version` del servidor igual a la del cliente (`binary --version`); si la config declara `binary_version`, también igual a esa.
- Si el preflight falla, el intento termina antes del despacho.
- Identidad durable como hoy. La frescura de los agentes se mide con una sonda en T3 y se declara como límite.

### D3. Política de ejecución

**Evidencia:**
- **Standalone:** suma un proceso escritor y un arranque completo por despacho. Las cifras siguientes vienen del log de 10-15, de tres arranques privados, no del incidente: unos 96–100 watchers, 5 conexiones MCP, 7 plugins que no cargan y de 209 a 833 `spawning process`.
- **Servidor declarado:** ahorra ese proceso y el `PASSIVE` de arranque. Tiene en contra lo visto en D2: la versión solo avisa, usa la config del servidor, los agentes pueden estar en caché y el worker sigue vivo si muere el cliente.
- **Sin cola única:** un servidor compartido no crea una cola única de escrituras, porque los otros servidores siguen escribiendo.
- **Nada medido:** ningún dato muestra menos bloqueos en un modo o en el otro.

**Recomendación:**
- Agregar `mode` explícito en la config de ejecución:
  - `server` exige `server` y el preflight de D2; se documenta como preferido en operación habitual cuando el operador prepara un servidor compatible;
  - `standalone` sirve para pruebas aisladas, cuando no hay servidor o para fijar versión.
- Sin `mode`, por compatibilidad: si hay `server`, modo servidor; si no, standalone, registrado como «solicitado: sin declarar → standalone (default)». No es un fallback.
- Un `mode: server` que falla nunca cambia a standalone.
- Nunca usar el modo por defecto (servicio de fondo), nunca buscar servidores ni conectarse a otro usuario.

### D4. Recuperación

**Evidencia (brechas, con archivo:línea):**
- **El timeout pierde la correlación:** devuelve `session=None` aunque el adaptador eligió el id (`:848` y `:878-885`). El id aparece solo como texto del diagnóstico en `:882`, y en `:848` ni eso. La interfaz registra la sesión que recibe en el envelope (`cdad_delegate.py:275`), así que el ledger se queda sin id para reconciliar.
- **El timeout mata solo al hijo directo:** `subprocess.run(timeout=)` manda SIGKILL al cliente, sin grupo de procesos (`:287-299`). El limpiador del runtime (SIGTERM a su servidor privado) no llega a correr, así que el `serve --stdio` nieto puede seguir vivo (VERIFY). En `--server` el worker sigue en el servidor.
- **`failed` sin causa:** el diagnóstico de `:715-719` no lee el mensaje `idle`, que sí trae `error`.
- **Espera ciega después de salir el cliente:** si el cliente salió y la fila no está idle, el bucle sondea cada 50 ms hasta la cota (`:467-482`). Pasa con rc=0 sin idle, y con rc≠0 cuando la fila existe pero no está idle. En cada vuelta abre una conexión, corre dos `PRAGMA table_info` y uno o dos SELECT (`:426`, `:340-348`, `:360`, `:397`). Con la cota de 3600 s del consumidor eso son hasta unas 72.000 vueltas. Para el incidente no está medido.
- **Nada mira el intento anterior** antes de despachar: no existe esa comprobación.
- **Margen escaso:** la reserva de 1,0 s (`:96`) está registrada como defecto de margen. Con la cota de 2 s del fixture el adaptador espera unos 1,8 s internos y la interfaz a veces lo mata (`tests/test_005_009_t2_opencode_adapter.py:242-250`).

**Recomendación,** con el vocabulario existente:

| Situación | Terminación | Qué hace el adaptador |
|---|---|---|
| Fila idle `failed` | `blocked` | Diagnóstico con el `error` durable acotado; dice que el worker terminó y que el store no identifica la causa |
| Cliente que no arranca, o rc≠0 sin fila después de un margen de asentamiento | `transport-error` | stderr acotado, sin URL ni credenciales |
| Cliente terminado con la fila no idle, en standalone | `unknown` | Termina después del margen de asentamiento, con el id |
| Cliente terminado con la fila no idle, en servidor | `timeout` (si vence la cota) | Sigue esperando la señal durable hasta la cota |
| Vence la cota | `timeout` | Devuelve `session` con el id elegido (procedencia: «elegido; fila presente/ausente»). En standalone hace terminación ordenada del grupo propio del adaptador (SIGTERM, gracia, SIGKILL). En servidor el diagnóstico avisa que el worker puede seguir |
| Antes de despachar, un intento previo del mismo paquete con fila no idle | `blocked` | No invoca `run` |

Sin reintentos automáticos.

### D5. Frontera del arreglo

- **Le corresponde a CDAD:**
  - selección explícita de modo y preflight;
  - registro de la selección por intento;
  - correlación conservada en timeout;
  - comprobación del intento previo;
  - espera progresiva;
  - terminación ordenada de sus propios hijos;
  - diagnósticos;
  - referencia, config de ejemplo y receta de aislamiento.
- **Le corresponde al dueño u operador:**
  - quién prepara el servidor y cuántos servidores comparten el store;
  - mantenimiento (WAL de 543 MB, 37 % de páginas libres), con ventana y respaldo, nunca desde CDAD;
  - actualizaciones del runtime;
  - la exposición de red de un servidor (ver Observaciones locales).
- **Candidatos upstream:**
  - `busy_timeout = 5000` fijo; no encontré una variable que lo cambie (VERIFY);
  - `LockTimeoutError` declara `isRetryable` pero hace fallar la sesión en `publishLLMEvent`/`runStep`.
  - El reporte externo no está verificado como aplicable a 2.0.27.
- **Mitigación honesta:** un modo servidor que reduce los escritores por despacho, el rechazo de escritores duplicados del mismo paquete y una recuperación que no pierde la correlación. No elimina la contención.

## 3. Borrador de spec de 006-001 (proporcional)

**Descripción.** Selección de ejecución explícita y verificable para el adaptador OpenCode, espera proporcional y recuperación que conserva la correlación, sin gestionar servidores ni la base.

**Config de ejecución.** Claves nuevas, todas opcionales:
- `mode: "server" | "standalone"`;
- dentro de `wait`: `poll_initial_seconds` (default 1), `poll_max_seconds` (15), `settle_seconds` (30) y `terminate_grace_seconds` (5).

Los valores se fijan en la spec y no dependen del host. Las claves vigentes no cambian.

**Postcondiciones** (cada una verificable con el binario falso, un servidor HTTP de fixture en 127.0.0.1 y stores SQLite descartables):

- **PC-1 (AC-1).** El argv lleva exactamente una de `--server <url>` o `--standalone`. Nunca lleva ninguna de las dos ni ambas. Con `mode` presente, el modo efectivo es el solicitado. Sin `mode`, se aplica la regla de D3.
- **PC-2 (AC-1).** Toda terminación deja un registro I8 del worker con procedencia en texto libre en `provenance.runtime` (sin cambiar el esquema cerrado de `cdad_packet.py:2371-2375`, `:2418`). La procedencia incluye:
  - modo solicitado y modo efectivo;
  - versión del cliente observada;
  - versión del servidor observada, o «mismo binario (standalone)»;
  - store: el `sessions_db` configurado y si apareció ahí la fila correlacionada.

  Lo no observado figura como `unknown`. Hoy el registro del worker solo se escribe en `completed` (`:645`). Precedente de texto libre: `:518-521`.
- **PC-3 (AC-1, AC-6).** Con `mode: server`, si el preflight falla no se invoca `run`:
  - servidor ausente o inalcanzable → `transport-error`;
  - credencial rechazada, versión distinta o `server` sin URL → `blocked`.

  El diagnóstico nombra la causa y la acción siguiente: preparar un servidor compatible o declarar `standalone` explícitamente. Nunca cambia a standalone por su cuenta.
- **PC-4 (AC-2).** En ambos modos se cumple todo esto:
  - el sha256 de stdin es igual al de `PACKET.md`;
  - `--agent cdad-<role>`, `--session <elegido>`, `--model` si está configurado y `--auto` según la config;
  - `PWD` igual a la raíz del proyecto;
  - identidad durable verificada;
  - `completed` → `receive` con `semantic_status: pending`, sin aprobar el gate.
- **PC-5 (AC-1, AC-2).** Ninguna salida (stdout, diagnóstico, registro I8, argv) contiene la contraseña ni la URL del servidor. La URL se reemplaza por «servidor configurado».
- **PC-6 (AC-3).** Dos delegaciones concurrentes desde dos proyectos descartables, contra el mismo store descartable (y en topología servidor, el mismo servidor descartable), terminan las dos `completed`. Además:
  - el recibo de cada una lleva su propio id elegido;
  - la columna `session_v2.directory` de cada fila es su proyecto;
  - el texto final de cada una está solo en los resultados de su proyecto;
  - ninguna delegación modifica archivos del otro proyecto.

  Se registran versión, configuración y carga (dos sesiones). La prueba no se generaliza a otras cargas ni versiones.
- **PC-7 (AC-4).** Fila idle `failed` → `blocked`, con el `error.type`/`error.message` del mensaje `idle` (como máximo 200 caracteres), la mención de que el worker terminó y de que el store no identifica la causa. Sin recibo.
- **PC-8 (AC-4).** En timeout, `session` es el id elegido. En standalone no queda ningún descendiente del adaptador vivo después de la gracia. En modo servidor el diagnóstico avisa que el worker puede continuar. Sin recibo.
- **PC-9 (AC-4).** Cliente terminado con la fila no idle: en standalone, `unknown` después de `settle_seconds`; en servidor, la espera durable sigue hasta la cota. Cliente terminado sin fila después del asentamiento: rc≠0 → `transport-error`; rc=0 → `unknown`, con un diagnóstico que menciona un posible store distinto.
- **PC-10 (AC-4).** Antes de invocar `run` se lee el ledger del paquete. Si un intento previo registró una sesión cuya fila existe y no está idle → `blocked`, sin invocación nueva. No hay reintentos automáticos en ningún camino.
- **PC-11 (AC-5).**
  - Después de salir el cliente, los intervalos de sondeo empiezan en `poll_initial_seconds` y se duplican hasta `poll_max_seconds`.
  - El esquema se valida una sola vez por intento.
  - Las lecturas del store por intento quedan acotadas por la fórmula de backoff.
  - El conteo de lecturas se registra en la procedencia.
  - Un `locked`/`busy` en la lectura del adaptador se reintenta con el mismo backoff dentro de la cota y nunca escribe.
- **PC-12 (AC-5).** El adaptador responde siempre dentro de la cota de la interfaz, incluida la gracia de terminación. La reserva cubre gracia más `receive`. La interfaz nunca es la que mata al adaptador.
- **PC-13 (AC-6).** CDAD no arranca, reinicia, recarga ni detiene servidores ni el servicio de fondo. La compatibilidad se comprueba al comienzo de cada intento (PC-3). La referencia nombra al operador como responsable de preparar el servidor.
- **PC-14 (AC-8).** Quedan alineados `cli-delegation.md` (modos, claves, preflight, recuperación, límites, receta de aislamiento) y una config de ejemplo con placeholders en `skills/cdad-cycle/assets/`. No se imponen HOME, puertos, rutas, proveedor, modelo, TMPDIR ni gestor de servicios. No se duplica en los agentes ni hay allowlists. El barrido de patrones sensibles pasa.

**Invariantes:**
- store en solo lectura;
- nunca el modo por defecto ni fallback de modo;
- sin reintentos automáticos;
- la interfaz no escribe `docs/.cdad-state.json`;
- vocabulario de terminación sin cambios;
- una entrega no es un gate;
- sin secretos en las salidas;
- PD-15: un proceso separado no es un sandbox.

**Criterios:** PC-1 a PC-5 y PC-7 a PC-14 son focales con fixtures. PC-6 corre con fixture siempre, y con runtime real opt-in en un store aislado.

**Fuera de alcance:**
- identificar al tenedor del bloqueo;
- mantenimiento de la base;
- actualización del runtime y correcciones upstream;
- abortar sesiones del servidor (la ruta no está verificada);
- verificar el contenido de las instrucciones cargadas (deuda);
- límite global de agentes, sandbox, un store por proyecto;
- AC-7, que corresponde a la recepción.

## 4. Plan T1, T2 y T3

**Aislamiento de un store descartable (verificado con `opencode debug paths`, sin despachar):**

| Variable | Qué mueve | Costo |
|---|---|---|
| `OPENCODE_DB=<abs>` | Solo el archivo de la base (en el binario: `process.env.OPENCODE_DB ?? …; resolve(data, e)`). Probé `debug paths` con `db <sp>/alt/alt.db`; el archivo no se crea hasta usarse | log, snapshot, tool-output y repos siguen en el directorio de datos vivo (escrituras en HOME). La migración `import_legacy_credentials` copia `<data>/auth.json` a la base temporal: queda una copia de credenciales en tmp |
| `XDG_DATA_HOME` / `XDG_STATE_HOME` / `XDG_CACHE_HOME` | Base, log, `auth.json`, registro del servicio (`service.json` en state) y cache | Sin credenciales salvo que el operador las provea |
| `HOME` | Todo, incluida la config | Sin providers ni agentes globales |

- En ningún caso se mueve el tmp del runtime (`/tmp/opencode`).
- `test_005_010_t4_integration.py` **no** está aislado: usa la base real por variable de entorno y HOME real (`:13-51`, `:207-216`). No sirve para AC-3.
- **Recomendación:** XDG data, state y cache bajo `ROOT=$(mktemp -d)`, conservando la config.
  - Las credenciales las provee el orquestador o el dueño por un mecanismo soportado; el test no copia `auth.json`.
  - Guarda previa al despacho: `opencode debug paths` con el mismo entorno, para comprobar que `db`, `data`, `state` y `log` caen bajo ROOT y que `db` no es el store vivo.
  - Solo `--standalone`, o un `opencode serve --hostname 127.0.0.1 --port <libre>` descartable que el test lanza y detiene con `OPENCODE_SERVER_PASSWORD` aleatorio.
  - Nunca el modo por defecto.

**T1. Selección, compatibilidad y registro (PC-1 a PC-5, PC-13).**
- Fixtures: servidor HTTP `/api/info` con Basic auth y `version` configurable; el binario falso responde `--version`.
- RED y GREEN:
  ```
  python3 -m pytest tests/test_006_001_t1_selection.py -q -p no:cacheprovider
  ```
- Regresión:
  ```
  python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider
  ```
- Oráculos afectados: la matriz de argv de `test_005_010_t2_load_mode_invocation.py` (sigue vigente si se respeta la compatibilidad hacia atrás) y `OUTPUT_KEYS` (`test_005_009_t1_interface.py:100`, sin cambios).

**T2. Espera y recuperación (PC-7 a PC-12).**
- Mecánica: `Popen` con terminación ordenada; backoff; intento previo leído del ledger.
- Fixtures:
  - variantes `failed-with-idle-error`, `rc0-no-row` y `exit-row-not-idle`;
  - `hangs` existente, para comprobar que no quedan descendientes;
  - una base en modo rollback-journal con `BEGIN EXCLUSIVE`, mantenida por el test durante un tiempo acotado, para el `_StoreBusy` del lector.
- RED y GREEN:
  ```
  python3 -m pytest tests/test_006_001_t2_wait_recovery.py -q -p no:cacheprovider
  ```
- Regresión: la de T1 más `tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_009_t4_acceptance.py`.
- Oráculo afectado: `TEST_WAIT_TIMEOUT_SECONDS = 2` (`test_005_009_t2_opencode_adapter.py:417`) junto con la gracia nueva. El test-writer fija `terminate_grace_seconds` chico en los fixtures, o se acepta subir la cota.
- Opcional, opt-in en store aislado: mantener `BEGIN IMMEDIATE` más de 5 s durante una sesión real y esperar `blocked` con el error durable.

**T3. Integración, procedimiento y candidato (PC-6, PC-14).**
- El fixture concurrente necesita que el falso escriba con transacciones SQLite reales: hoy escribe con tmp más `os.replace`, lo que pisaría a un escritor concurrente.
- Fixture siempre:
  ```
  python3 -m pytest tests/test_006_001_t3_concurrency.py -q -p no:cacheprovider
  ```
- Real, opt-in:
  ```
  CDAD_OPENCODE_INTEGRATION=1 CDAD_OPENCODE_BINARY=<bin> CDAD_OPENCODE_ISOLATED_ROOT=$(mktemp -d) CDAD_OPENCODE_MODEL=<m> python3 -m pytest tests/test_006_001_t3_integration.py -q -p no:cacheprovider
  ```
  Antes, la guarda de `debug paths`.
- Sondas VERIFY dentro del mismo recorrido descartable:
  - si un servidor ya en uso toma un agente cambiado (marcador A → B);
  - si el servidor privado termina tras SIGTERM al cliente.
- Referencias:
  ```
  python3 -m pytest tests/test_005_010_t3_references.py -q -p no:cacheprovider
  make validate
  ```
- Candidato en raíz aislada:
  ```
  make staging
  HOME=$(mktemp -d) bash install.sh --force
  HOME=<mismo> bash install.sh --check
  ```
- Suite completa una sola vez al cierre de código:
  ```
  python3 -m pytest tests -q -p no:cacheprovider
  ```
- Review independiente al final.

## 5. VERIFY abiertos

- `wal_autocheckpoint` y si `busy_timeout` se puede cambiar en el runtime.
- Si `serve --stdio` termina cuando muere su cliente.
- Si un servidor de larga vida refresca los agentes del proyecto.
- Ruta de abort de sesiones en el servidor.
- Si `instruction_state` incluye el prompt del agente.
- Comportamiento de la sesión del servidor con un permiso pendiente y el cliente muerto.
- Cuántas conexiones abre cada servidor.
- Escritores fuera del namespace visible.

## Observaciones locales

Se retiraron de esta copia versionada (rutas, ids crudos, PIDs y nombres del consumidor). El orquestador las conserva en el registro local ignorado por Git. El recibo del rol conserva los bytes originales.
