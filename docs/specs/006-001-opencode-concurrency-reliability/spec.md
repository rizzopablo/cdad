> Spec **DRAFT (etapa 2, subetapa `draft`), SIN APROBAR.** La redacta el **architect**. La aprueba, junto
> con el plan, el **orquestador Claude** bajo la HITL delegada del epic-006
> (`docs/epics/epic-006-opencode-concurrency/execution.md`), o el dueño. El architect no aprueba su propia
> propuesta.
>
> - **Contrato:** `docs/epics/epic-006-opencode-concurrency/plan.md` (sha256 `a8e415f7…`, §1-§7, AC-1..AC-8).
> - **Base:** el discovery recibido y revisado (`docs/specs/006-001-opencode-concurrency-reliability/discovery.md`,
>   sha256 `1118e794…`, §3 borrador y §4 plan). Se resuelve por referencia y se aplican los siete ajustes
>   obligatorios del encargo.
> - **Repo:** HEAD `e435698`. Adaptador sha256 `1f3d63d6…`; interfaz `b47366dd…`; referencia `420c15a1…`.
> - **Numeración:** las postcondiciones se numeran **PD-n**, como en las specs 005-0xx. El render del
>   paquete por tarea solo extrae `PD|INV|D` de la ficha (`cdad_packet.py:3293-3316`); una `PC-n` dejaría
>   vacío el «Applicable contract». El §3.1 da el mapa PC del discovery → PD.
> - **Anonimización:** sin rutas personales, ids crudos, endpoints, puertos ni nombres de proveedor, de
>   modelo o de otros proyectos (`<provider>`, `<VAR>`, `<ROOT>`, `<url>`).

# Spec — 006-001-opencode-concurrency-reliability

**Feature ID:** `006-001-opencode-concurrency-reliability` · **Epic:** `epic-006-opencode-concurrency` ·
**Estado:** borrador (etapa 2).

## 1. Descripción funcional

El adaptador OpenCode (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`) hoy hace cuatro cosas que
esta feature corrige:

- elige el modo por la sola presencia de `server` en la config (`:772`, `:269-273`);
- no comprueba la versión del servidor;
- pierde la correlación en timeout (`:848`, `:878-885`);
- mata solo al hijo directo (`:287-299`), sondea cada 50 ms después de que sale el cliente (`:97`,
  `:467-482`) y no mira intentos previos.

La feature entrega cinco cosas:

1. **Selección de ejecución explícita y verificable.** Un `mode` declarado, compatible hacia atrás y sin
   fallback, más un preflight del modo servidor.
2. **Procedencia por intento.** Se registra en el ledger I8 sin cambiar su esquema cerrado.
3. **Espera proporcional.** Ningún sondeo mientras el cliente vive; después, backoff acotado.
4. **Recuperación que conserva la correlación.** La sesión elegida viaja en toda terminación posterior al
   despacho, los hijos propios terminan de forma ordenada y un intento previo vivo bloquea el nuevo.
5. **Referencia y config de ejemplo portables.**

**Lo que no hace:** no gestiona servidores ni la base. No elimina la contención del store compartido, que es
el riesgo residual declarado en §11.

## 2. Contrato observable

### 2.1 Config de ejecución (claves nuevas, todas opcionales; las vigentes no cambian)

| Clave | Valores | Default | Fixture (sugerido) |
|---|---|---|---|
| `mode` | `"server"` \| `"standalone"` | sin declarar → regla de compatibilidad (§2.2) | según el caso |
| `wait.poll_initial_seconds` | número > 0 | `1` | `0.05` |
| `wait.poll_max_seconds` | número ≥ `poll_initial_seconds` | `15` | `0.2` |
| `wait.settle_seconds` | número > 0 | `30` | `0.5` |
| `wait.terminate_grace_seconds` | número > 0 | `5` | `0.2` |
| `wait.preflight_timeout_seconds` | número > 0 | `5` | `1` |

- **Valor inválido** (tipo, signo, `mode` fuera del conjunto, `poll_max < poll_initial`): `blocked` antes del
  despacho, con un diagnóstico que nombra la clave. No se invoca nada.
- **Cota mínima:** `wait.timeout_seconds` sigue obligatorio y positivo (`:813-829`). Además debe ser mayor
  que la reserva fija `WAIT_RESERVE_SECONDS` (1,0 s, `:96`); si no, `blocked` antes del despacho.
- **Portabilidad:** los defaults no dependen del host. Un fixture puede bajar todos los valores, así que
  cada focal nuevo termina en pocos segundos.

### 2.2 Selección de modo

| `mode` | `server` en config | Modo efectivo | Registro (`mode requested` → `effective`) |
|---|---|---|---|
| `server` | URL válida | servidor + preflight | `server` → `server` |
| `server` | ausente o inválida | ninguno: `blocked` antes del despacho | `server` → `none` |
| `standalone` | cualquiera | standalone; `server` se ignora y se registra | `standalone` → `standalone` |
| sin declarar | URL válida | servidor + preflight (compatibilidad) | `undeclared` → `server` |
| sin declarar | ausente | standalone (compatibilidad) | `undeclared` → `standalone` |

- **URL válida:** `http`/`https`, con host y **sin userinfo**.
- **Nunca** se invoca sin `--server`/`--standalone`; eso activaría el servicio de fondo (discovery D2).
- **Nunca** se cambia de modo por un fallo, se buscan servidores ni se usa otro usuario.

### 2.3 Preflight del modo servidor (antes de `run`, dentro de la cota)

1. **Versión del cliente.** `binary --version`, con salida acotada. Se extrae el primer token semver
   `\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?`; el runtime real imprime `opencode v<semver>` (observado).
   Solo en modo servidor (D-2).
2. **`GET <server>/api/info`.** Timeout `preflight_timeout_seconds` (acotado por la cota restante).
   - **Credencial:** Basic `opencode:<password>`. La contraseña se toma del entorno en el **mismo orden que
     el cliente**: `OPENCODE_PASSWORD` y, si no está, `OPENCODE_SERVER_PASSWORD`. Si no hay ninguna, no se
     manda cabecera. El valor nunca se registra.
   - **Respuesta esperada:** JSON con `version` de texto.
3. **Resultados.**

| Hecho | Terminación | Diagnóstico (causa + acción siguiente) |
|---|---|---|
| Conexión rechazada, timeout o error de red | `transport-error` | «servidor configurado no alcanzable»; preparar un servidor compatible o declarar `mode: standalone` |
| 401/403 | `blocked` | «credencial ausente o rechazada»; nombra las dos variables de entorno, nunca su valor |
| 404, no JSON o sin `version` | `blocked` | «servidor sin información V2 compatible» |
| `version` ≠ versión del cliente, o ≠ `binary_version` si la config la declara y es parseable | `blocked` | nombra las dos versiones y la acción siguiente |
| Versión no parseable en algún lado | `blocked` | «versión no verificable» |
| Todo coincide | sigue a `run --server <url>` | — |

### 2.4 Espera y clasificación después del despacho

- **Cliente.** Se lanza con `Popen` en un grupo de procesos propio (`start_new_session`). Mientras el
  cliente vive, el adaptador espera al proceso: **cero lecturas del store**.
- **Lecturas tras la salida.** La primera, inmediata. Después, intervalos `poll_initial_seconds`, que se
  duplican hasta `poll_max_seconds`. Cada intervalo se recorta a la cota restante.
  - El esquema se valida en la primera lectura exitosa del intento y no se repite.
  - Un `locked`/`busy` cuenta como lectura y sigue el mismo calendario.
  - Las lecturas son solo `mode=ro`.
- **Cota de lecturas.** Para una ventana posterior a la salida de W segundos:
  `R ≤ 2 + ⌈log2(poll_max/poll_initial)⌉ + ⌈W/poll_max⌉`. Con los defaults y W = 3600 s, R ≤ 246;
  la espera actual podía llegar a unas 72.000 vueltas (discovery D4).

| Estado observado tras la salida del cliente | Standalone | Servidor |
|---|---|---|
| Fila idle `succeeded` con texto final | `completed` (como hoy) | ídem |
| Fila idle `failed` | `blocked` con el `error` durable (PD-7) | ídem |
| Fila idle `interrupted` / desconocido | `cancelled` / `unknown` (como hoy, `:720-727`) | ídem |
| Sin fila, rc≠0 | `transport-error` inmediato (como hoy, `:477-478`) | ídem |
| Sin fila, rc=0 | `unknown` al cumplirse `settle_seconds` («posible store distinto del configurado») | ídem |
| Fila no idle | `unknown` al cumplirse `settle_seconds` (con salida normal del cliente, su servidor privado ya terminó; tras un SIGKILL es VERIFY (c), §10) | sigue la espera durable hasta la cota → `timeout` |
| La cota vence antes de la regla anterior | `timeout` | `timeout` |
| La cota vence con el cliente vivo | `timeout`; terminación ordenada del grupo propio: SIGTERM, gracia efectiva, SIGKILL | `timeout`; mismo trato al cliente, y el diagnóstico avisa que el worker del servidor puede seguir |

### 2.5 Reserva y gracia (D-3)

- **Gracia efectiva:** `g = min(terminate_grace_seconds, 0,25 × (timeout_seconds − WAIT_RESERVE_SECONDS))`.
- **Presupuesto interno:** `timeout_seconds − WAIT_RESERVE_SECONDS − g`. Cubre preflight, cliente y espera
  posterior. La terminación ordenada usa `g` y `receive` usa la reserva fija.
- Con la cota de 2 s de los fixtures vigentes, `g` = 0,25 s y el presupuesto interno = 0,75 s; hoy son
  1,0 s internos (`:485-488`).

### 2.6 Procedencia por intento (esquema I8 sin cambios)

- **Alcance.** El adaptador registra **su** intento de worker en el ledger I8 en **toda** terminación
  posterior a cargar `REQUEST.json`. Usa `_register_dispatch` (`:526-560`), hoy reservado a `completed`
  (`:645`).
- **Claves.** Son las cinco del esquema cerrado (`cdad_packet.py:2371-2375`). `provenance` solo anota esos
  campos, con valores de texto no vacío (`:2433-2445`). La procedencia nueva va en el texto libre
  (precedente `:518-521`), con pares `clave=valor` separados por `; `:
  - **`provenance.runtime`:** `execution config (--exec-config): runtime; mode_requested=<server|standalone|undeclared>; mode_effective=<server|standalone|none>; client_version=<v|unknown>; server_version=<v|same-binary(standalone)|unknown>`.
  - **`provenance.session`:** `<durable session row (exec-config: sessions_db): session_v2.id | chosen by adapter | not dispatched>; store=configured sessions_db; row=<present|absent|unknown>; store_reads=<N>; prior_check_reads=<M>`.
  - **Qué cuenta cada contador:** `store_reads` cuenta solo las lecturas posteriores a la salida del cliente, que son las que acota §2.4. `prior_check_reads` cuenta las lecturas de la comprobación previa de §2.7.
- **Si el registro falla** en un camino no `completed`, la terminación no cambia y el diagnóstico agrega
  «worker record not written: <causa acotada>».

### 2.7 Comprobación del intento previo (antes de `run`)

1. Se leen los registros `.cdad/executions/<execution-id>/dispatches/*.json` cuyo `packet_id` es el del
   paquete y cuyo `session` no es nulo. Allí están tanto los de la interfaz (`cdad_delegate.py:275-276`)
   como los del worker.
2. Para cada sesión se lee su fila (`mode=ro`). Si **alguna fila existe y no está idle**: `blocked`, sin
   invocar nada. El diagnóstico nombra la sesión y la acción siguiente: reconciliar
   (`cdad_continuity.py reconcile`) y esperar a que termine, o preparar un paquete nuevo
   (`--replace-packet`) solo después de reconciliar.
3. Una fila idle o ausente no bloquea.
4. **Sin reintentos automáticos** en ningún camino.

**Límite declarado:** la comprobación solo ve intentos ya registrados en el ledger del mismo paquete. Un
despacho concurrente del mismo paquete todavía en curso, o un paquete reemplazado, no se ve (deuda DT-3).

### 2.8 Lo que no cambia

- La interfaz `cdad_delegate.py`, su `OUTPUT_KEYS` y su vocabulario de terminación (`:48-51`).
- El esquema I8; la identidad durable (`:228-245`); el transporte byte-idéntico por stdin (`:287`); `PWD`
  igual a la raíz del proyecto (`:284-285`); `--auto` por config (`:773`); `receive` con
  `semantic_status: pending`.

## 3. Postcondiciones (numeradas y verificables)

Todas se verifican con el binario falso, un servidor HTTP de fixture en loopback y stores SQLite
descartables. PD-6 exige además el recorrido real (§5, D-8).

**PD-1 (AC-1, AC-6). Selección de modo.**
- El argv de `run` lleva **exactamente una** de `--server <url>` o `--standalone`, según la tabla §2.2.
- `mode: server` sin URL válida, un `mode` inválido o una clave `wait.*` inválida → `blocked` sin invocar
  nada.
- Ningún fallo cambia el modo efectivo.
- La matriz completa se verifica en un solo focal.

**PD-2 (AC-1, AC-6). Preflight del modo servidor.**
- En modo efectivo servidor (declarado o por compatibilidad), cada fila de §2.3 produce la terminación
  indicada sin invocar `run`; el diagnóstico nombra la causa y la acción siguiente.
- La contraseña se lee en el orden `OPENCODE_PASSWORD` → `OPENCODE_SERVER_PASSWORD`. Si las dos están
  definidas y son distintas, gana la primera; el servidor de fixture acepta solo esa.
- Las únicas invocaciones del binario son `--version` y `run`. Ningún argv lleva `serve`, `service` ni
  `reload`: CDAD no arranca, recarga ni detiene servidores.

**PD-3 (AC-1). Procedencia en toda terminación.**
- Cada camino (preflight fallido, intento previo vivo, `blocked`, `transport-error`, `timeout`, `unknown`,
  `completed`) deja un registro de worker con las claves I8 cerradas.
- La procedencia lleva los pares de §2.6. `unknown` se usa para lo no observado, nunca `0` ni vacío.
- `store_reads` coincide con las lecturas del fixture: un contador instrumentado en el store de fixture o
  la traza del focal.

**PD-4 (AC-2). Mismo encargo en ambos modos.** En modo servidor se cumple lo mismo que hoy se verifica en
standalone:
- el sha256 de stdin es igual al de `PACKET.md`;
- `--agent cdad-<role>`, `--session <elegida>`, `--model` si está configurado y `--auto` según la config;
- `PWD` igual a la raíz del proyecto;
- identidad durable verificada;
- `completed` → `receive` con `semantic_status: pending`.

**PD-5 (AC-1, AC-2). Sin secretos en las salidas.**
- Con una contraseña centinela en el entorno, ni ella ni la URL configurada aparecen en: envelope de la
  interfaz, diagnóstico, registros I8 (interfaz y worker), stderr del adaptador y recibo.
- La URL aparece **solo** en el argv de `run`, como hoy exige `test_005_010_t2_load_mode_invocation.py:361-385`.
- Un stderr del cliente que contenga la URL se redacta a «servidor configurado» antes de entrar al
  diagnóstico (hoy `:870-876` copia hasta 300 caracteres).
- La contraseña nunca va en argv.

**PD-6 (AC-3). Concurrencia útil en la topología elegida.**
- **Escenario.** Dos delegaciones concurrentes desde dos proyectos descartables, contra el mismo store
  descartable y, en topología servidor, el mismo servidor descartable.
- **Resultado esperado:**
  - las dos terminan `completed`;
  - el recibo de cada una lleva su propia sesión elegida;
  - `session_v2.directory` de cada fila es su proyecto;
  - cada encargo pide un nonce propio, y el nonce de A aparece solo en los resultados de A (y el de B solo
    en los de B);
  - los archivos cambiados de cada proyecto están dentro de su `.cdad/` y su `docs/.cdad-state.json`, y
    ninguno contiene el nonce del otro.
- **Doble evidencia.** El fixture (binario falso con escrituras SQLite transaccionales reales) es la
  regresión permanente. La **aceptación** exige además el recorrido **real** en modo servidor de §5. El
  recorrido real standalone concurrente es complementario.
- **Registro.** Se anotan versión, config anonimizada y carga (dos sesiones). No se generaliza a otras
  cargas ni versiones.

**PD-7 (AC-4). Fallo y ausencia de resultado.** Tras la salida del cliente rige la tabla de §2.4:
- **Fila idle `failed`.** `blocked`, con `error.type`/`error.message` del último `session_message` de tipo
  `idle` de la sesión (forma observada: discovery `:64`), acotados a 200 caracteres. El diagnóstico dice
  que el worker terminó y que el store no identifica la causa. Si no hay error durable: «sin error durable
  registrado».
- **Sin fila, rc=0** → `unknown` tras `settle_seconds`.
- **Fila no idle en standalone** → `unknown` tras `settle_seconds`.
- **Fila no idle en servidor** → `timeout` al vencer la cota.
- **Sin fila, rc≠0** → `transport-error`.
- En ningún caso hay recibo.

**PD-8 (AC-4). Correlación y terminación ordenada.**
- En toda terminación posterior al **arranque** de `run` (`Popen` exitoso; incluidos `timeout`,
  `unknown`, `transport-error` y `blocked`), el envelope lleva `session` = la sesión elegida. El registro
  de la interfaz la conserva.
- Antes del despacho, o si el binario no arranca, `session` sigue en `null`, como exigen hoy
  `test_005_009_t2_opencode_adapter.py:1320-1323`, `test_005_010_t2_load_mode_invocation.py:208-211` y
  `test_005_010_reviewfix.py:245-248` y `:308-311`.
- En `timeout` con el cliente vivo:
  - **standalone:** tras la respuesta del adaptador no queda vivo ningún proceso del grupo propio. El
    fixture `hangs` lanza un nieto y registra su pid;
  - **servidor:** el diagnóstico avisa que el worker puede seguir en el servidor.
- Sin recibo.

**PD-9 (AC-4). Intento previo y sin reintentos.**
- Con un registro previo del mismo paquete cuya fila existe sin idle → `blocked`, sin ninguna invocación
  del binario (el registro de llamadas del fake queda vacío).
- Con la fila previa idle o ausente se despacha normalmente.
- Cada invocación de la interfaz produce **como máximo una** invocación `run`.

**PD-10 (AC-5). Espera proporcional.**
- Mientras el cliente vive, `store_reads` = 0 (fixture con un cliente que tarda y luego deja la fila idle).
- Tras la salida, `store_reads` ≤ la cota de §2.4 para la ventana medida.
- Con el store bloqueado por un escritor del fixture (rollback journal, `BEGIN EXCLUSIVE` durante un tiempo
  acotado), el adaptador reintenta según el calendario y termina `completed` cuando se libera, sin escribir
  el store: el mtime y el contenido solo cambian por el escritor del fixture.

**PD-11 (AC-5). El adaptador responde dentro de la cota.**
- Con `timeout_seconds` chico, el adaptador responde siempre antes de la cota de la interfaz, incluida la
  gracia efectiva de §2.5. El envelope es del adaptador, nunca el `did not answer within`
  (`cdad_delegate.py:146-149`).
- Se verifica en las variantes `hangs`, `no-idle` y `transport-error`, con una ejecución por variante y
  cota ≤ 2 s. El presupuesto total del focal es ≤ 10 s.
- Una cota ≤ `WAIT_RESERVE_SECONDS` → `blocked` sin despacho.

**PD-12 (AC-8). Config de ejemplo ejecutable y portable.**
- Existe `skills/cdad-cycle/assets/opencode-exec-config.example.json`:
  - cada clave es una que el adaptador lee;
  - solo hay placeholders `<...>` y defaults de §2.1;
  - no hay rutas, puertos, proveedor ni modelo concretos.
- Con los placeholders reemplazados por valores de fixture, el adaptador la acepta y despacha.
- La actualización de `cli-delegation.md` no es postcondición: la juzga la review (plan T3), con la guarda
  `test_005_010_t3_references.py` verde como regresión.

### 3.1 Mapa PC del discovery → PD de esta spec

| Discovery §3 | Spec |
|---|---|
| PC-1 | PD-1 |
| PC-2 | PD-3 |
| PC-3, PC-13 | PD-2 (PC-13 queda como invariante INV-2 y aserción de argv) |
| PC-4 | PD-4 |
| PC-5 | PD-5, corregida: la URL sí va en argv, como exige el oráculo vigente |
| PC-6 | PD-6, con recorrido real obligatorio |
| PC-7, PC-9 | PD-7 |
| PC-8 | PD-8 |
| PC-10 | PD-9 |
| PC-11 | PD-10 |
| PC-12 | PD-11 |
| PC-14 | PD-12 (solo la config de ejemplo; la referencia, a review) |

### 3.2 Cobertura AC → PD

- **AC-1:** PD-1, PD-2, PD-3, PD-5.
- **AC-2:** PD-4, PD-5.
- **AC-3:** PD-6.
- **AC-4:** PD-7, PD-8, PD-9.
- **AC-5:** PD-10, PD-11.
- **AC-6:** PD-1, PD-2.
- **AC-8:** PD-12.
- **AC-7:** fuera de esta spec; recepción tras el despliegue autorizado (plan del epic §5 y §7).

## 4. Invariantes (verificables)

- **INV-1 (store ro).** El adaptador abre el store solo con `mode=ro`, nunca `immutable` ni escribible
  (`:424-426`). Verificable por PD-10.
- **INV-2 (sin modo por defecto ni gestión de servidores).**
  - El argv siempre lleva una de las dos flags.
  - No hay fallback de modo.
  - El producto no arranca, recarga ni detiene servidores ni el servicio de fondo. Solo el **test** del
    recorrido real lanza y detiene su servidor descartable.
- **INV-3 (sin reintentos automáticos).** Ver PD-9.
- **INV-4 (interfaz y esquemas intactos).** Sin cambios en `cdad_delegate.py`, `OUTPUT_KEYS`, el
  vocabulario de terminación ni el esquema I8. Verificable por `git diff` y por las regresiones de 005-009.
- **INV-5 (entrega ≠ gate).** Ver `receive` `pending`.
- **INV-6 (sin secretos ni valores del host).** Ni en el producto, ni en la documentación, ni en las salidas
  (PD-5). Ver también el barrido de saneamiento del cierre.
- **INV-7 (PD-15).** Un proceso o sesión separados no son un sandbox. `--auto` tampoco lo es.
- **INV-8 (single writer).** El adaptador no escribe `docs/.cdad-state.json` fuera del mecanismo reusado
  (`prepare --record-dispatch`).
- **INV-9 (desconocido ≠ cero).** Lo no observado se registra como `unknown`.

## 5. Recorrido real (aceptación de PD-6)

### 5.1 Topología

Modo servidor contra un `opencode serve --hostname 127.0.0.1 --port <libre>` descartable:
- lo lanza y lo detiene el test (SIGTERM, gracia, SIGKILL al grupo);
- la contraseña es aleatoria por corrida (`OPENCODE_SERVER_PASSWORD`, solo en el entorno de los procesos
  del test);
- el store queda aislado bajo `<ROOT>=$(mktemp -d)`;
- dos proyectos CDAD descartables, cada uno con su ejecución activa, sus agentes derivados publicados y su
  paquete preparado.

El recorrido standalone concurrente es complementario: mismo ROOT o uno nuevo, sin servidor.

### 5.2 Aislamiento

- `XDG_DATA_HOME`, `XDG_STATE_HOME` y `XDG_CACHE_HOME` van bajo `<ROOT>`. Se conserva la config global
  (discovery §4).
- **Guarda previa:** `opencode debug paths` con el mismo entorno. `db`, `data`, `state` y `log` deben caer
  bajo `<ROOT>`; si no, el test aborta sin despachar.
- El tmp del runtime no se mueve (discovery `:253`).
- La config global conservada hace que el servidor descartable cargue los MCP y plugins globales. Es un
  costo declarado: se registra si quedan procesos tras detener el servidor.

### 5.3 Credenciales del proveedor (ajuste 2, resuelto con evidencia de solo lectura)

**Hechos verificados (sin imprimir valores):**
- El proveedor del modelo configurado es uno propio con `npm: @ai-sdk/openai-compatible`. En la config
  global solo declara `baseURL`: **no** declara `apiKey`, ni por `{env:…}` ni por `{file:…}`.
- La clave existe como credencial de tipo `api` en `auth.json` del directorio de datos.
- El runtime 2.0.27 resuelve ese archivo desde `XDG_DATA_HOME` (`…join(XDG_DATA_HOME,"opencode","auth.json")`).
  Además, la migración `20260805200742_import_legacy_credentials` lo **copia** a la tabla `credential` de la
  base al migrar.
- Consecuencia: un `XDG_DATA_HOME` aislado arranca **sin credencial**, y aislar solo `OPENCODE_DB` copiaría
  la credencial a la base temporal (discovery §4). Ninguna de las dos sirve.

**Mecanismo soportado que fija esta spec:**
- El runtime sustituye `{env:VAR}` y `{file:ruta}` en la config (`ConfigVariable.substitute`, en el
  binario) y acepta una capa de config por `OPENCODE_CONFIG_CONTENT` (o un archivo por `OPENCODE_CONFIG`).
- El test pone en el entorno **del servidor descartable** (en modo servidor resuelve el servidor; en
  standalone, el servidor privado hereda el entorno del cliente):

  ```
  OPENCODE_CONFIG_CONTENT={"provider":{"<provider>":{"options":{"apiKey":"{env:<VAR>}"}}}}
  ```

  - `<provider>` sale del prefijo de `CDAD_OPENCODE_MODEL`.
  - `<VAR>` es el **nombre** de una variable que el operador u orquestador define en el entorno de la
    corrida. El test recibe el nombre en `CDAD_OPENCODE_KEY_ENV` y solo comprueba que esté definida, sin
    leer su valor.
- El test **nunca** lee ni copia `auth.json` ni la base viva, y nunca ejecuta comandos que impriman la
  config resuelta.
- Si la variable no está definida, el test se **omite con motivo**. Una omisión **no** acredita PD-6.

**Falta un mecanismo sin acción del operador; alternativa mínima que decide el orquestador:**
- **(A, recomendada)** El dueño u orquestador exporta la clave en `<VAR>` solo para el proceso del test,
  desde la fuente que elija, sin escribirla en disco ni en logs.
- **(B)** `{file:<ruta>}` hacia un archivo de clave del dueño, fuera de `<ROOT>` y del directorio de datos
  vivo.
- **(C, rechazada)** Copiar `auth.json` o aislar solo la base.
- **VERIFY resueltos por el primer despacho real:** que `{env:}` se sustituya también en la capa
  `OPENCODE_CONFIG_CONTENT`, que la capa se fusione con la definición global del proveedor y que su SDK use
  `options.apiKey`. Si falla, el síntoma es un error de autenticación
  de la sesión (`blocked` con el error durable). Se vuelve al orquestador con (B), o con definir el
  proveedor completo en la capa.

### 5.4 Registro

- Versión (`--version` y `/api/info`), config anonimizada, duración de cada sesión, terminaciones y
  `store_reads`.
- Procesos que quedan tras detener el servidor.
- Observaciones VERIFY de §10.

## 6. Decisiones (D-n) con fundamento y trade-off

- **D-1 (el preflight rige el modo servidor efectivo, también por compatibilidad).**
  - **Fundamento:** AC-6. Sin preflight, una config vieja con `server` seguiría sin control de versión;
    el cliente solo avisa (discovery D2).
  - **Costo:** cambia el oráculo `test_pd4_server_config_uses_server_without_standalone`
    (`test_005_010_t2_load_mode_invocation.py:361-385`), que usa una URL `fixture.invalid`
    (`:94`, TLD reservado, inalcanzable). Pasa a usar el servidor `/api/info` de fixture en loopback con la versión
    del fake.
- **D-2 (`--version` solo en modo servidor).**
  - **Fundamento:** en standalone el servidor es el mismo binario por construcción (discovery D2).
    Llamar a `--version` siempre rompería tres oráculos de llamada única
    (`test_005_010_t2_load_mode_invocation.py:287`, `test_005_009_t2_opencode_adapter.py:1139`, `:1400`).
  - **Costo:** en standalone, `client_version` registra el `binary_version` configurado o `unknown`.
- **D-3 (gracia efectiva con tope proporcional).**
  - **Fundamento:** reservar 5 s fijos dejaría sin presupuesto a los fixtures de 2 s
    (`test_005_009_t2_opencode_adapter.py:417`, `:1086`).
  - **Costo:** con cotas chicas la gracia real es corta. Con las cotas operativas (3600 s) rige el valor
    configurado.
  - **Efecto colateral esperado:** el margen interno sube de ~0,2 s a ~1,25 s con la cota de 2 s, lo que
    ataca la carrera registrada en `test_005_009_t2_opencode_adapter.py:242-250`. Es VERIFY en T2, no
    promesa.
- **D-4 (rc≠0 sin fila sigue siendo `transport-error` inmediato).**
  - **Fundamento:** el cliente que falló ya no puede crear la fila. Así se conserva el oráculo vigente.
  - **Costo:** el asentamiento solo se aplica a rc=0 sin fila y a filas no idle en standalone.
- **D-5 (procedencia en texto libre y registro de worker en toda terminación).**
  - **Fundamento:** el esquema I8 es cerrado (`cdad_packet.py:2371-2445`) y la interfaz no se toca
    (INV-4).
  - **Costo:** dos registros por intento (interfaz y worker), como ya pasa en `completed`.
    `assert_attempt_is_in_ledger` tolera registros extra (`test_005_009_t1_interface.py:464-484`).
    Verificar en el RED de T1.
- **D-6 (intento previo por paquete).** Lo pide el contrato («mismo paquete»). Ampliarlo a toda la ejecución
  bloquearía por sesiones viejas de otros roles. Límite y deuda: DT-3.
- **D-7 (credenciales por sustitución de config).** Ver §5.3: evita copiar credenciales, al costo de una
  acción del operador.
- **D-8 (aceptación de PD-6 en servidor y real).**
  - **Fundamento:** es la topología preferida en operación habitual, la que reduce escritores por
    despacho (discovery D3).
  - El fixture no prueba el runtime real.
  - El standalone real complementa, no sustituye.

## 7. Alcance y fuera de alcance

**Incluido:**
- adaptador OpenCode;
- tests focales nuevos y oráculos declarados;
- `cli-delegation.md`;
- config de ejemplo en `assets/`;
- recorrido real aislado;
- candidato instalable en raíz aislada.

**Fuera de alcance:**
- identificar al tenedor del bloqueo;
- mantenimiento de la base viva;
- actualización del runtime y correcciones upstream (`busy_timeout = 5000` fijo, `LockTimeoutError`
  `isRetryable`);
- abortar sesiones del servidor;
- verificar el contenido de las instrucciones cargadas;
- límite global de agentes, sandbox o store por proyecto;
- cambiar la interfaz común;
- AC-7.

## 8. Deuda con condición de cierre

- **DT-1.** Ruta de abort de sesiones en el servidor. Se cierra cuando una versión del runtime documente o
  exponga una ruta verificada.
- **DT-2.** Frescura de agentes en un servidor de larga vida. Se cierra con la observación de T3 (§10) y, si
  hay caché, con una decisión del dueño sobre `reload`, reservado al dueño.
- **DT-3.** Intento previo a nivel de ejecución o de despacho concurrente del mismo paquete (lock por
  paquete). Se cierra si la recepción (AC-7) o un incidente muestran duplicación por esa vía.
- **DT-4.** `instruction_state` como prueba de contenido del agente. Se cierra con una verificación de
  esquema en otra feature.
- **DT-5.** Permisos pendientes con el cliente muerto en modo servidor. Se cierra con una observación
  dirigida.

## 9. Referencias (archivo:línea)

- **Adaptador** (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`):
  - modo e invocación: `:96-97`, `:251-304`, `:772-778`;
  - store y espera: `:409-482`, `:485-488`;
  - I8: `:494-560`, `:645`;
  - clasificación: `:697-727`;
  - flujo: `:813-914`.
- **Interfaz** (`skills/cdad-cycle/scripts/cdad_delegate.py`): `:48-51`, `:131-162`, `:177-193`,
  `:252-283`.
- **I8:** `skills/cdad-cycle/scripts/cdad_packet.py:2371-2445`, `:2501-2582`.
- **Ficha y render:** `cdad_packet.py:3018-3086`, `:3089-3282`, `:3291-3316`.
- **Referencia:** `skills/cdad-cycle/references/cli-delegation.md:112-158`, `:172-183`.
- **Oráculos:**
  - `tests/test_005_010_t2_load_mode_invocation.py:94`, `:287`, `:361-385`;
  - `tests/test_005_009_t2_opencode_adapter.py:242-250`, `:399`, `:417`, `:879-880`, `:1086`, `:1139`,
    `:1400`;
  - `tests/test_005_009_t1_interface.py:100`, `:464-484`.
- **Discovery:** D1-D5 (`:47-167`), §4 (`:243-316`), §5 (`:318-327`).

## 10. VERIFY (resueltos o declarados)

- **Resuelto en el draft:** mecanismo de credenciales (§5.3); salida de `--version` (`opencode v<semver>`,
  observado con XDG aislado); orden de contraseñas del cliente (binario).
- **A resolver en el recorrido real de T3** (se registran como observaciones y no cambian el contrato
  salvo que lo contradigan):
  - (a) forma de `version` en `/api/info`;
  - (b) que la sustitución `{env:}` alcance la capa `OPENCODE_CONFIG_CONTENT` (verifiqué la función, no
    que cubra esa capa), que la capa se fusione con el proveedor global y que el SDK use
    `options.apiKey` (§5.3);
  - (c) si `serve --stdio` termina al morir su cliente por SIGKILL;
  - (d) si un servidor ya usado toma un agente derivado cambiado (marcador A → B) en un segundo despacho.
- **Abiertos, a deuda:** `wal_autocheckpoint` y `busy_timeout` del runtime; conexiones por servidor;
  escritores fuera del namespace visible; DT-1, DT-4 y DT-5.

## 11. Riesgos con mitigación

- **Riesgo residual (ajuste 6).**
  - **Qué queda:** esta feature **no elimina** la contención del store compartido. Siguen N≥3 escritores
    de larga vida y un `busy_timeout` de 5 s fijo en el runtime.
  - **Mitigación:** reducir escritores por despacho cuando el operador prepara un servidor compatible
    (modo servidor), no duplicar intentos (PD-9) y no perder la correlación (PD-8). Un único éxito real
    no prueba que la contención desapareció.
- **Worker que sigue tras un timeout en modo servidor.** El diagnóstico lo avisa, y PD-9 bloquea el
  re-despacho mientras la fila no esté idle.
- **Agentes en caché en el servidor.** Observación de T3 y DT-2. Recargar lo decide el dueño.
- **Costo del recorrido real.** Gasta tokens del proveedor, carga MCP y plugins globales, y puede instalar
  paquetes en la caché aislada. Se ejecuta una vez, en T3, con autorización del orquestador.
- **Flakiness de tiempos.** D-3 y los valores chicos de fixture. PD-11 cubre las tres variantes de
  carrera.

## 12. Método y evidencia del draft

Todo fue de solo lectura sobre el repo.
- **Fuentes leídas:** el paquete, el contrato de unidad (sha256 `13f7db14…`, coincide), el discovery, el
  plan del epic, `execution.md`, el adaptador, la interfaz, la referencia, `cdad_packet.py` (I8 y
  plan-tasks) y los tests citados.
- **Configuración del runtime:** analicé la config global con un script propio que reporta solo el tipo
  de cada `apiKey` (ausente, `{env:}`, `{file:}` o literal), la existencia de las variables y las claves de
  `options`. Para el proveedor del modelo configurado: sin `apiKey`, solo `baseURL`.
- **Archivo de credenciales:** comprobé solo dos cosas, sin volcar ningún valor: si el proveedor tiene
  entrada (sí) y de qué tipo es (`api`).
- **Binario:** ventanas de texto acotadas sobre las `strings` del binario, en el scratchpad. Evidencias:
  `ConfigVariable.substitute` (`{env:}`/`{file:}`), el resolutor de `auth.json` por `XDG_DATA_HOME`, la
  migración `import_legacy_credentials` con la tabla `credential`, el orden
  `OPENCODE_PASSWORD` → `OPENCODE_SERVER_PASSWORD`, `/api/info` y el aviso de versión.
- **Ejecución del runtime:** una sola, `opencode --version` con `XDG_DATA/STATE/CACHE_HOME` en el
  scratchpad, que salió `opencode v<semver>`, rc=0. Solo escribió un log dentro del scratchpad. No hubo
  despachos, ni `serve`, ni lecturas de la base viva.
- **Repo:** sin cambios de producto. `git status` muestra solo el `docs/.cdad-state.json` que ya venía
  modificado.

## 13. Aprobación

Pendiente. La decide el orquestador bajo la HITL delegada del epic-006, junto con el plan. Esta spec no
lleva marca de aprobación.

## 14. Decisión del orquestador (2026-10-16)

Aprobada con plan, bajo la HITL delegada de epic-006, después de verificar contra el código las referencias de §2, §6 y §9 que se muestrearon (adaptador `:96-97`, `:269-273`, `:287`, `:645`, `:772`, `:848`, `:878-885`; oráculos `test_005_010_t2_load_mode_invocation.py:94`, `:361-385`; fake `test_005_009_t2_opencode_adapter.py:879-880`; extractor de ids de ficha `cdad_packet.py:3295`).

- **Gate en la misma familia, declarado.** El architect y el orquestador son Claude. La review de código del final la hace otra familia, distinta también de la del implementer.
- **Credencial del recorrido real (§5.3).** La alternativa se decide en T3, antes de despachar el recorrido real. Ningún valor se escribe en disco, en logs ni en docs. Si exige una acción que esté reservada al dueño, PD-6 queda en BLOQUEO declarado.
- **Cambios de oráculos.** Quedan autorizados solo los dos del plan §3.

Status: Approved by Claude orchestrator (HITL delegated by Pablo for epic-006) on 2026-10-16
