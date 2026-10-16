> Spec **v2 (etapa 2, subetapa `draft`, enmienda 001), SIN APROBAR.** La redacta el **architect**. La
> aprueba, junto con el plan, el **orquestador Claude** bajo la HITL delegada del epic-006
> (`docs/epics/epic-006-opencode-concurrency/execution.md`), o el dueño. El architect no aprueba su
> propia propuesta.
>
> - **Contrato:** `docs/epics/epic-006-opencode-concurrency/plan.md` (sha256 `a8e415f7…`, §1-§7,
>   AC-1..AC-8) y el cambio de alcance aprobado por el dueño (`execution.md`, «Cambio de alcance
>   aprobado por el dueño — 2026-10-16»): `mode: "service"` configurado.
> - **Contrato de unidad:** `.cdad/packets/006-001-opencode-concurrency-reliability-architect-draft-002/UNIT-CONTRACT.md`
>   (sha256 `13f7db14…`, coincide).
> - **Base:** spec v1 y plan v1 aprobados (docs/specs/006-001-opencode-concurrency-reliability/{spec,plan}.md),
>   el discovery (sha256 `1118e794…`) y los informes de T1 GREEN (`t1-green.md`, commits `4bc8934`,
>   `a96c2d8`) y T2 RED (`t2-red.md`, commit `8447443`). La enmienda **no reescribe** lo entregado:
>   conserva PD-1..PD-12 con un diff conceptual por PD (§14) y suma T1b.
> - **Repo:** HEAD `25e669b`. Adaptador tras T1: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`.
> - **Numeración:** postcondiciones **PD-n** (el render de la ficha solo extrae `PD|INV|D`,
>   `cdad_packet.py:3293-3316`). **Tope respetado: 14 PDs en total.**
> - **Anonimización:** sin rutas personales, ids crudos, endpoints, puertos ni nombres de proveedor, de
>   modelo o de otros proyectos (`<provider>`, `<VAR>`, `<ROOT>`, `<url>`, `<bin>`, `<state>`, `<config>`, `<log>`).

# Spec — 006-001-opencode-concurrency-reliability (v2)

**Feature ID:** `006-001-opencode-concurrency-reliability` · **Epic:** `epic-006-opencode-concurrency` ·
**Estado:** borrador (etapa 2, enmienda 001).

## 1. Descripción funcional

El adaptador OpenCode (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`) hoy hace cuatro cosas que
esta feature corrige:

- elige el modo por la sola presencia de `server` en la config (`:772`, `:269-273`);
- no comprueba la versión del servidor;
- pierde la correlación en timeout (`:848`, `:878-885`);
- mata solo al hijo directo (`:287-299`), sondea cada 50 ms después de que sale el cliente (`:97`,
  `:467-482`) y no mira intentos previos.

La feature entrega seis cosas:

1. **Selección de ejecución explícita y verificable.** Un `mode` declarado, compatible hacia atrás y sin
   fallback silencioso, más un preflight del modo servidor.
2. **Modo servicio configurado (enmienda 001, aprobado por el dueño).** `mode: "service"` es el camino
   normal recomendado: antes de despachar, CDAD comprueba si el servicio de fondo corre y si su versión es
   compatible con el cliente; si corre y es compatible, despacha **sin `--server`/`--standalone`** y el
   cliente usa el servicio como lo diseña el runtime.
3. **Procedencia por intento.** Se registra en el ledger I8 sin cambiar su esquema cerrado, con el modo
   solicitado, el efectivo, la causa de un fallback y el modo de despacho.
4. **Espera proporcional.** Ningún sondeo mientras el cliente vive; después, backoff acotado.
5. **Recuperación que conserva la correlación.** La sesión elegida viaja en toda terminación posterior al
   despacho, los hijos propios terminan de forma ordenada y un intento previo vivo bloquea el nuevo.
6. **Referencia y config de ejemplo portables.**

**Lo que no hace:** no gestiona servidores **ni el servicio de fondo** —no lo arranca, no lo reinicia, no
lo detiene y no lo configura—, no escribe la base y no elimina la contención del store compartido, que es
el riesgo residual declarado en §11.

## 2. Contrato observable

### 2.1 Config de ejecución (claves nuevas, todas opcionales; las vigentes no cambian)

| Clave | Valores | Default | Fixture (sugerido) |
|---|---|---|---|
| `mode` | `"server"` \| `"service"` \| `"standalone"` | sin declarar → regla de compatibilidad v1 (§2.2) | según el caso |
| `service.require` | booleano | `false` | `true` en la variante estricta |
| `wait.poll_initial_seconds` | número > 0 | `1` | `0.05` |
| `wait.poll_max_seconds` | número ≥ `poll_initial_seconds` | `15` | `0.2` |
| `wait.settle_seconds` | número > 0 | `30` | `0.5` |
| `wait.terminate_grace_seconds` | número > 0 | `5` | `0.2` |
| `wait.preflight_timeout_seconds` | número > 0 | `5` | `1` |

- **Valor inválido** (tipo, signo, `mode` fuera del conjunto, `poll_max < poll_initial`, `service.require`
  no booleano): `blocked` antes del despacho, con un diagnóstico que nombra la clave. No se invoca nada.
- **Cota mínima:** `wait.timeout_seconds` sigue obligatorio y positivo (`:813-829`, hoy `:1196-1204`).
  Además debe ser mayor que la reserva fija `WAIT_RESERVE_SECONDS` (1,0 s, `:101`); si no, `blocked`
  antes del despacho.
- **`service.require`** solo tiene efecto con `mode: service` (y con el modo servicio efectivo por
  declaración). En los demás modos se ignora y se registra como no aplicable. **D-10.**
- **Portabilidad:** los defaults no dependen del host. Un fixture puede bajar todos los valores.

### 2.2 Selección de modo

| `mode` | `server` en config | Servicio | Modo efectivo | Registro (`requested` → `effective`) |
|---|---|---|---|---|
| `server` | URL válida | — | servidor + preflight | `server` → `server` |
| `server` | ausente o inválida | — | ninguno: `blocked` antes del despacho | `server` → `none` |
| `service` | cualquiera (`server` se ignora y se registra) | corre y compatible | **sin flags** (servicio) | `service` → `service` |
| `service` | cualquiera | corre y **no** compatible o no verificable | ninguno: `blocked` | `service` → `none` |
| `service` | cualquiera | **no corre**, `service.require: false` | standalone + fallback declarado | `service` → `standalone` (`fallback=service-unavailable`) |
| `service` | cualquiera | **no corre**, `service.require: true` | ninguno: `blocked` | `service` → `none` |
| `standalone` | cualquiera | — | standalone; `server` se ignora y se registra | `standalone` → `standalone` |
| sin declarar | URL válida | — | servidor + preflight (compatibilidad v1) | `undeclared` → `server` |
| sin declarar | ausente | — | standalone (compatibilidad v1) | `undeclared` → `standalone` |

- **URL válida:** `http`/`https`, con host y **sin userinfo**.
- **Regla de default (D-9):** `mode` sin declarar mantiene la **compatibilidad v1** (si hay `server`, modo
  servidor; si no, standalone). No se pasa a `service` por defecto: un cambio de topología hacia un
  servidor compartido es una decisión del consumidor y debe ser explícita. Costo declarado: las configs
  del consumidor que hoy omiten `server` y `mode` siguen abriendo un servidor privado por despacho hasta
  que declaren `mode: "service"` (acción de la recepción, AC-7).
- **`service` ignora `server`** (igual que `standalone`): si el `server` declarado está presente, no se
  usa, no se comprueba y se registra como presente.
- **Nunca** se cambia de modo por un fallo (INV-2). La **única** transición admisible es el fallback
  declarado `service` → `standalone` cuando `service status` informa que el servicio **no corre** (§2.3b).
- El servicio de fondo solo se usa por el **despacho sin flags**; eso ocurre únicamente después de la
  comprobación de §2.3b.

### 2.3 Preflight del modo servidor (antes de `run`, dentro de la cota)

Sin cambios respecto de v1:

1. **Versión del cliente.** `binary --version`, con salida acotada; primer token semver
   `\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?`; el runtime real imprime `opencode v<semver>` (observado).
   Solo en el modo servidor efectivo (D-2).
2. **`GET <server>/api/info`.** Timeout `min(preflight_timeout_seconds, presupuesto restante)`.
   - **Credencial:** Basic `opencode:<password>`, contraseña del entorno en el **mismo orden que el
     cliente**: `OPENCODE_PASSWORD` y, si no está, `OPENCODE_SERVER_PASSWORD`. Si no hay ninguna, no se
     manda cabecera. El valor nunca se registra.
   - **Respuesta esperada:** JSON con `version` de texto.
3. **Resultados.** Tabla de v1 (conexión rechazada/timeout → `transport-error`; 401/403 → `blocked`;
   404/no JSON/sin `version` → `blocked`; versiones distintas o no parseables → `blocked`; todo coincide →
   `run --server <url>`).

**Invocaciones del binario (ajuste de la enmienda).** En el modo servidor efectivo siguen siendo
**exactamente** `--version` y `run`. En el modo servicio efectivo, `service status`, `--version` (solo si
el servicio corre) y `run`. `service status` **no** se invoca en modo servidor ni en standalone. Ningún
argv lleva `serve`, `service <start|stop|restart|get|set|unset>` ni `reload` (INV-2).

### 2.3b Preflight del modo servicio (nuevo, enmienda 001)

Se ejecuta solo cuando el modo efectivo es `service` (o cuando `mode: service` resolvió a `blocked`/
fallback por el camino de abajo). Todo dentro de la cota y del presupuesto restante.

1. **Estado del servicio: `opencode service status`** (subcomando de solo lectura; **no arranca nada**).
   - Salida acotada a una línea, con timeout `min(preflight_timeout_seconds, presupuesto restante)`.
   - **Interpretación (cerrada):**
     - una URL `http`/`https` con host y sin userinfo → **corre**;
     - el literal `stopped` → **no corre**;
     - cualquier otra salida, salida vacía, más de una línea, rc ≠ 0 o timeout → **respuesta inesperada**
       → `blocked` («no se puede afirmar que el servicio no corre»). Nunca standalone.
   - La URL que imprime `service status` **no se usa, no se guarda y no entra en ninguna salida**: en el
     modo servicio CDAD no necesita la URL (el cliente encuentra el servicio solo) ni `/api/info`. El
     subproceso se lee y se descarta salvo el discriminante.
2. **Compatibilidad de versión** (solo si corre):
   - **Versión del cliente:** `binary --version`, igual que §2.3 punto 1.
   - **Versión del servicio:** por el mecanismo declarado en **D-11** (lector que proyecta solo la clave
     `version` del registro del servicio, nunca el documento, nunca la contraseña, nunca la URL).
   - **Igual** → sigue al despacho sin flags.
   - **Distinta**, o **no verificable** (archivo ausente/no parseable/clave ausente o no textual) →
     `blocked`, con las dos versiones (o «no verificable») y la acción siguiente: preparar un servicio
     compatible, o declarar `mode: standalone` o `mode: server` explícitamente. **Nunca standalone** (el
     servicio corre: un standalone al lado sería un escritor más sobre el mismo store).
3. **Servicio que no corre:**
   - `service.require: true` → `blocked`, con la acción siguiente: que el operador o el dueño arranque el
     servicio (CDAD **no** ejecuta `service start`) o declare `mode: standalone`.
   - `service.require: false` → **standalone** con el fallback declarado y **contable**:
     `mode_requested=service; mode_effective=standalone; fallback=service-unavailable`.
4. **Despacho sin flags** (servicio que corre y compatible):
   `run --agent cdad-<role> --session <elegida> [--auto] [--model <m>]`, **sin** `--server` ni
   `--standalone`; `provenance.runtime` registra `dispatch_flags=none`.
5. **Ventana de carrera (declarada, D-13).** El servicio puede detenerse entre `service status` y el
   despacho; el cliente entonces **lo arrancaría** (`run` sin flags hace `ensure` del servicio). El
   binario del runtime **no ofrece** forma soportada de impedirlo: no hay flag (`run --help` solo expone
   `--standalone` y `--server`), no hay variable de entorno (`OPENCODE_*` no incluye ninguna de servicio)
   y la única setting relacionada (`service.get/set`) no controla ese comportamiento. Mitigación: la
   comprobación se hace lo más tarde posible antes de la invocación; la procedencia registra
   `service_status=running` y `dispatch_flags=none` para poder correlacionar. Es **riesgo residual**
   (§11): un servicio que se cae en esa ventana y el cliente lo levanta es comportamiento del runtime, no
   una acción de gestión de CDAD.

### 2.4 Espera y clasificación después del despacho

Sin cambios respecto de v1 (cliente con `Popen` en grupo propio; cero lecturas del store mientras vive;
lecturas `mode=ro` con backoff `poll_initial_seconds` duplicado hasta `poll_max_seconds`, acotadas por
`R ≤ 2 + ⌈log2(poll_max/poll_initial)⌉ + ⌈W/poll_max⌉`; tabla de clasificación de v1). Se aplica igual en
los tres modos efectivos.

### 2.5 Reserva y gracia (D-3)

Sin cambios: `g = min(terminate_grace_seconds, 0,25 × (timeout_seconds − WAIT_RESERVE_SECONDS))`;
presupuesto interno `timeout_seconds − WAIT_RESERVE_SECONDS − g`, que cubre el preflight (de servidor o
de servicio), el cliente y la espera posterior.

### 2.6 Procedencia por intento (esquema I8 sin cambios)

- **Alcance.** El adaptador registra **su** intento de worker en el ledger I8 en **toda** terminación
  posterior a cargar `REQUEST.json`, por `_register_dispatch`. Igual que v1.
- **Claves.** Son las cinco del esquema cerrado (`cdad_packet.py:2371-2375`). La procedencia nueva va en
  el texto libre (precedente `:518-521`), con pares `clave=valor` separados por `; `, **preservando el
  orden de v1** y **agregando los pares nuevos al final**:
  - **`provenance.runtime`:**
    `execution config (--exec-config): runtime; mode_requested=<server|service|standalone|undeclared>; mode_effective=<server|service|standalone|none>; client_version=<v|unknown>; server_version=<v|same-binary(standalone)|unknown>; dispatch_flags=<--server|--standalone|none>; service_status=<running|stopped|unexpected|not-checked>; fallback=<none|service-unavailable>`.
  - **`provenance.session`:** sin cambios de forma:
    `<durable session row (exec-config: sessions_db): session_v2.id | chosen by adapter | not dispatched>; store=configured sessions_db; row=<present|absent|unknown>; store_reads=<N>; prior_check_reads=<M>`.
    (`store_reads=` y `prior_check_reads=` quedan al final: el RED de T2 parsea `store_reads=`…`;`.)
- **Valores.** `mode_requested` agrega `service`; `mode_effective` agrega `service`; `server_version` en el
  modo servicio lleva la versión observada del servicio; `service_status` es `not-checked` fuera del modo
  servicio; `fallback` es `none` salvo el camino declarado de §2.3b punto 3.
- **Si el registro falla** en un camino no `completed`, la terminación no cambia y el diagnóstico agrega
  «worker record not written: <causa acotada>».

### 2.7 Comprobación del intento previo (antes de `run`)

Sin cambios respecto de v1 (lectura de los registros `.cdad/executions/<execution-id>/dispatches/*.json`
del mismo `packet_id` con `session` no nulo; fila existente no idle → `blocked`; fila idle o ausente no
bloquea; sin reintentos automáticos). **Cláusula nueva (precisión del dueño):** esto aplica **igual**
después de un `timeout` en modo **servicio** o **servidor**, donde el worker puede seguir vivo; no se
abre un `standalone` «para destrabar» y ningún camino de recuperación re-despacha solo.

**Límite declarado:** la comprobación solo ve intentos ya registrados en el ledger del mismo paquete
(deuda DT-3).

### 2.8 Lo que no cambia

- La interfaz `cdad_delegate.py`, su `OUTPUT_KEYS` y su vocabulario de terminación (`:48-51`).
- El esquema I8; la identidad durable (`:228-245`); el transporte byte-idéntico por stdin (`:287`); `PWD`
  igual a la raíz del proyecto (`:284-285`); `--auto` por config (`:773`); `receive` con
  `semantic_status: pending`.
- Los modos `server` y `standalone` de v1 y su matriz de oráculos.

## 3. Postcondiciones (numeradas y verificables)

Todas se verifican con el binario falso, un servidor HTTP de fixture en loopback y stores SQLite
descartables. PD-6 exige además el recorrido real (§5, D-8), y en la enmienda también el recorrido real
**contra el servicio vivo**.

**PD-1 (AC-1, AC-6). Selección de modo.**
- El argv de `run` lleva **exactamente una** de `--server <url>` o `--standalone` **[dif. enmienda: o
  ninguna, solo en el modo servicio efectivo, tras §2.3b]**, según la tabla §2.2.
- `mode: server` sin URL válida, `mode: service` con el servicio corriendo pero incompatible (o no
  verificable), `mode: service` sin servicio con `service.require: true`, un `mode` inválido o una clave
  `service.*`/`wait.*` inválida → `blocked` sin invocar nada (más allá de la comprobación de §2.3b cuando
  corresponda).
- Ningún fallo cambia el modo efectivo; la única transición es el fallback declarado de §2.3b.
- La matriz completa (incluidas las filas nuevas) se verifica en dos focales: T1 (v1) y T1b (servicio).

**PD-2 (AC-1, AC-6). Preflight del modo servidor.**
- En modo efectivo servidor (declarado o por compatibilidad), cada fila de §2.3 produce la terminación
  indicada sin invocar `run`; el diagnóstico nombra la causa y la acción siguiente.
- La contraseña se lee en el orden `OPENCODE_PASSWORD` → `OPENCODE_SERVER_PASSWORD`.
- Las únicas invocaciones del binario son `--version` y `run`; ningún argv lleva `serve`, `service` ni
  `reload`, **y `service status` no se invoca en este modo** [dif. enmienda].

**PD-3 (AC-1). Procedencia en toda terminación.**
- Cada camino deja un registro de worker con las claves I8 cerradas.
- La procedencia lleva los pares de §2.6, con los valores nuevos `service` y los pares
  `dispatch_flags=`, `service_status=` y `fallback=` **[dif. enmienda]**; `unknown` para lo no observado,
  nunca `0` ni vacío.
- `store_reads` coincide con las lecturas del fixture.

**PD-4 (AC-2). Mismo encargo en los modos soportados.**
- En modo servidor y **en modo servicio (despacho sin flags)** [dif. enmienda] se cumple lo mismo que hoy
  se verifica en standalone: sha256 de stdin = `PACKET.md`; `--agent cdad-<role>`, `--session <elegida>`,
  `--model` si está configurado y `--auto` según la config; `PWD` = raíz del proyecto; identidad durable
  verificada; `completed` → `receive` con `semantic_status: pending`.

**PD-5 (AC-1, AC-2). Sin secretos en las salidas.**
- Con una contraseña centinela en el entorno, ni ella ni la URL configurada aparecen en: envelope de la
  interfaz, diagnóstico, registros I8 (interfaz y worker), stderr del adaptador y recibo.
- La URL aparece **solo** en el argv de `run --server`, como hoy exige
  `test_005_010_t2_load_mode_invocation.py:361-385`.
- Un stderr del cliente que contenga la URL se redacta a «servidor configurado» antes del diagnóstico.
- **Dif. enmienda:** la salida de `service status` (que contiene la URL del servicio) se descarta salvo el
  discriminante; ni la URL del servicio ni el secreto del servicio (registro/config del servicio) entran
  en argv, diagnóstico, registros I8, stderr del adaptador ni recibo. La contraseña nunca va en argv.

**PD-6 (AC-3). Concurrencia útil en la topología elegida.**
- **Escenario.** Dos delegaciones concurrentes desde dos proyectos descartables, contra el mismo store
  descartable y, en topología servidor, el mismo servidor descartable.
- **Resultado esperado:** las dos terminan `completed`; el recibo de cada una lleva su propia sesión;
  `session_v2.directory` de cada fila es su proyecto; cada encargo pide un nonce propio y el nonce de A
  aparece solo en los resultados de A (y el de B solo en los de B); los archivos cambiados de cada
  proyecto están dentro de su `.cdad/` y su `docs/.cdad-state.json`, y ninguno contiene el nonce del otro.
- **Triple evidencia [dif. enmienda].** (a) el fixture con escrituras SQLite transaccionales reales es la
  regresión permanente; (b) la **aceptación** exige el recorrido **real** en modo servidor de §5; (c) la
  enmienda exige además el recorrido **real en modo servicio contra el servicio VIVO** (§5.5): un despacho
  y luego dos concurrentes, con encargo mínimo, uso normal del servicio, **sin** reiniciarlo ni cambiar su
  configuración.
- **Registro.** Versión, config anonimizada, carga, terminación, modo efectivo, tiempos y errores. No se
  generaliza a otras cargas ni versiones. **La eliminación de bloqueos no se demuestra** (AC-7, §5.5).

**PD-7 (AC-4). Fallo y ausencia de resultado.** Tras la salida del cliente rige la tabla de §2.4:
fila idle `failed` → `blocked` con el `error.type`/`error.message` del último `session_message` `idle`
(acotados a 200 caracteres); sin fila y rc=0 → `unknown` tras `settle_seconds`; fila no idle en standalone
→ `unknown` tras `settle_seconds`; fila no idle en servidor → `timeout` al vencer la cota; sin fila y rc≠0
→ `transport-error`. En ningún caso hay recibo.
- **Dif. enmienda:** con el modo efectivo **servicio**, una fila no idle sigue la espera durable hasta la
  cota → `timeout` (como servidor); el diagnóstico avisa que el worker puede seguir vivo en el servicio.
  Tras un `timeout` en modo servicio o servidor **no se abre un standalone**.

**PD-8 (AC-4). Correlación y terminación ordenada.**
- En toda terminación posterior al **arranque** de `run` (`Popen` exitoso; incluidos `timeout`, `unknown`,
  `transport-error` y `blocked`), el envelope lleva `session` = la sesión elegida; el registro de la
  interfaz la conserva. Antes del despacho, o si el binario no arranca, `session` sigue `null`.
- En `timeout` con el cliente vivo: en standalone no queda vivo ningún proceso del grupo propio; en
  servidor **y en servicio** el diagnóstico avisa que el worker puede seguir [dif. enmienda]. Sin recibo.
- CDAD **no** toca el servicio ni su proceso: la terminación ordenada del grupo propio alcanza solo al
  cliente del adaptador.

**PD-9 (AC-4). Intento previo y sin reintentos.**
- Con un registro previo del mismo paquete cuya fila existe sin idle → `blocked`, sin ninguna invocación
  de `run` (el registro de llamadas del fake queda sin `run`).
- Con la fila previa idle o ausente se despacha normalmente.
- Cada invocación de la interfaz produce **como máximo una** invocación `run`.
- **Dif. enmienda:** aplica **igual** tras un `timeout` en modo servicio o servidor (el worker puede
  seguir vivo); el camino de intento previo **nunca** produce un standalone ni un re-despacho automático.

**PD-10 (AC-5). Espera proporcional.**
- Mientras el cliente vive, `store_reads` = 0.
- Tras la salida, `store_reads` ≤ la cota de §2.4 para la ventana medida.
- Con el store bloqueado por un escritor del fixture (rollback journal, `BEGIN EXCLUSIVE` acotado), el
  adaptador reintenta según el calendario y termina `completed` cuando se libera, sin escribir el store:
  el mtime y el contenido solo cambian por el escritor del fixture.
- **Dif. enmienda (cláusula explícita):** las relecturas del store ante un lock siguen siendo **solo
  lectura** (`mode=ro`), acotadas y con backoff, y **no suman presión de escritura** sobre el store
  compartido.

**PD-11 (AC-5). El adaptador responde dentro de la cota.**
- Con `timeout_seconds` chico, el adaptador responde siempre antes de la cota de la interfaz, incluida la
  gracia efectiva de §2.5. El envelope es del adaptador, nunca el `did not answer within`
  (`cdad_delegate.py:146-149`).
- Se verifica en las variantes `hangs`, `no-idle` y `transport-error`, con cota ≤ 2 s.
- Una cota ≤ `WAIT_RESERVE_SECONDS` → `blocked` sin despacho.
- **Dif. enmienda:** el preflight del modo servicio (`service status` + versión) también está acotado por
  el presupuesto restante; con el presupuesto agotado → `blocked`, nunca una invocación sin cota.

**PD-12 (AC-8). Config de ejemplo ejecutable y portable.**
- Existe `skills/cdad-cycle/assets/opencode-exec-config.example.json`: cada clave es una que el adaptador
  lee; solo hay placeholders `<...>` y defaults de §2.1; no hay rutas, puertos, proveedor ni modelo
  concretos.
- **Dif. enmienda:** la config de ejemplo declara la fila `mode: "service"` y la clave `service.require`,
  con su comentario de uso (o la fila equivalente si el formato no admite comentarios: las claves van con
  placeholders y valores por defecto, sin valores del host).
- Con los placeholders reemplazados por valores de fixture, el adaptador la acepta y despacha.
- La actualización de `cli-delegation.md` no es postcondición: la juzga la review (plan T3), con la guarda
  `test_005_010_t3_references.py` verde como regresión.

**PD-13 (AC-1, AC-6) [NUEVA, enmienda]. Modo servicio: estado, despacho sin flags, fallback declarado y
sin gestión.**
- Con `mode: service`, el adaptador invoca `service status` **exactamente una vez** antes del despacho.
- **Servicio que corre** (salida con URL) y versión compatible → el argv de `run` **no** lleva `--server`
  ni `--standalone`; `dispatch_flags=none`, `service_status=running`, `fallback=none`,
  `mode_requested=service`, `mode_effective=service`.
- **Servicio que no corre** (`stopped`) con `service.require: false` → despacho `--standalone` **con**
  `mode_requested=service; mode_effective=standalone`, `fallback=service-unavailable; service_status=stopped`,
  y el diagnóstico nombra la causa («servicio no disponible»).
- **Servicio que no corre** con `service.require: true` → `blocked` antes de invocar `run`, con la acción
  siguiente (arrancarlo lo decide el operador o el dueño).
- **Respuesta inesperada** de `service status` (rc ≠ 0, timeout, salida no reconocible) → `blocked`;
  nunca standalone.
- **Ninguna** invocación del binario lleva `serve` ni `service start|stop|restart|get|set|unset` ni
  `reload`, en ningún modo. La única invocación de `service` es `service status`.
- La variante estricta se declara con `service.require` (§2.1, D-10) y se registra.

**PD-14 (AC-1, AC-6) [NUEVA, enmienda]. Compatibilidad de versión del servicio.**
- Con el servicio corriendo, la versión del servicio se observa por el mecanismo declarado en D-11.
- Versión del servicio **igual** a la del cliente observada → se despacha sin flags.
- Versión **distinta** → `blocked`; el diagnóstico nombra las dos versiones y la acción siguiente
  (servicio compatible, o `mode` explícito). **Nunca** standalone: el servicio corre.
- Versión **no verificable** (registro ausente, no parseable, clave ausente o no textual) → `blocked`
  («versión del servicio no verificable»), nunca standalone.
- La observación de la versión **no** lee ni emite la contraseña del servicio, **no** usa la URL del
  servicio y **no** abre conexiones: es una proyección de una sola clave (§D-11).
- `server_version` en la procedencia lleva la versión del servicio observada (o `unknown`).

### 3.1 Mapa PC del discovery → PD de esta spec

| Discovery §3 | Spec |
|---|---|
| PC-1 | PD-1 (v1) + PD-1 (fila `service`, enmienda) |
| PC-2 | PD-3 (v1) + PD-3 (pares nuevos, enmienda) |
| PC-3, PC-13 | PD-2 (v1); **PC-13 se reformula en INV-2 (enmienda): «nunca arrancar ni gestionar el servicio/servidores; el despacho sin flags solo tras comprobar que el servicio corre»** |
| PC-4 | PD-4 |
| PC-5 | PD-5, corregida y extendida: la URL sí va en argv de `--server`; la URL del servicio no entra en ninguna salida |
| PC-6 | PD-6, con recorrido real obligatorio (servidor y, enmienda, servicio vivo) |
| PC-7, PC-9 | PD-7 |
| PC-8 | PD-8 |
| PC-10 | PD-9 |
| PC-11 | PD-10 |
| PC-12 | PD-11 |
| PC-14 | PD-12 (solo la config de ejemplo; la referencia, a review) |
| — | PD-13, PD-14 (nuevos de la enmienda) |

### 3.2 Cobertura AC → PD

- **AC-1:** PD-1, PD-2, PD-3, PD-5, **PD-13, PD-14**.
- **AC-2:** PD-4, PD-5.
- **AC-3:** PD-6.
- **AC-4:** PD-7, PD-8, PD-9.
- **AC-5:** PD-10, PD-11.
- **AC-6:** PD-1, PD-2, **PD-13, PD-14**.
- **AC-8:** PD-12.
- **AC-7:** fuera de esta spec; recepción tras el despliegue autorizado (§5.5).

## 4. Invariantes (verificables)

- **INV-1 (store ro).** El adaptador abre el store solo con `mode=ro`, nunca `immutable` ni escribible
  (`:449`). Verificable por PD-10.
- **INV-2 (sin gestión del servicio ni de servidores; despacho sin flags solo tras la comprobación).**
  [**Reescrita por la enmienda**]
  - El producto **no** arranca, reinicia, detiene ni configura el servicio de fondo ni ningún servidor:
    ninguna invocación del binario lleva `serve`, `service start|stop|restart|get|set|unset` ni `reload`.
  - La única invocación de `service` es `service status` (solo lectura; no arranca nada: el propio
    subcomando imprime la URL o `stopped` y no gestiona).
  - El **despacho sin flags** (que deja que el cliente use el servicio) ocurre **solo** después de
    comprobar que el servicio corre y es compatible (§2.3b).
  - No hay fallback de modo salvo el declarado y contado `service` → `standalone` cuando el servicio **no
    corre**. Nunca se abre un standalone con el servicio corriendo (INV-10).
  - El **test** del recorrido real es el único que lanza y detiene su servidor descartable; el servicio
    vivo lo usa en modo normal, sin reiniciarlo ni reconfigurarlo.
- **INV-3 (sin reintentos automáticos).** Ver PD-9.
- **INV-4 (interfaz y esquemas intactos).** Sin cambios en `cdad_delegate.py`, `OUTPUT_KEYS`, el
  vocabulario de terminación ni el esquema I8. Verificable por `git diff` y por las regresiones de 005-009.
- **INV-5 (entrega ≠ gate).** Ver `receive` `pending`.
- **INV-6 (sin secretos ni valores del host).** Ni en el producto, ni en la documentación, ni en las
  salidas: contraseñas, URL del servidor (salvo el argv de `run --server`), **URL del servicio y secreto
  del servicio** [dif. enmienda], rutas personales, ids crudos, puertos. Ver PD-5 y el barrido de cierre.
- **INV-7 (PD-15).** Un proceso o sesión separados no son un sandbox. `--auto` tampoco lo es.
- **INV-8 (single writer).** El adaptador no escribe `docs/.cdad-state.json` fuera del mecanismo reusado
  (`prepare --record-dispatch`).
- **INV-9 (desconocido ≠ cero).** Lo no observado se registra como `unknown`.
- **INV-10 (un servicio vivo no admite otro escritor por esta vía) [NUEVA].** Ningún camino de selección,
  fallback o recuperación abre un `standalone` mientras el servicio corre, y ninguno re-despacha solo,
  arranca el servicio ni abre otro servidor; las relecturas ante lock son `mode=ro` y no escriben.
  Verificable por PD-9, PD-10, PD-13, PD-14.

## 5. Recorrido real

### 5.1 Topología (modo servidor, aislada)

Modo servidor contra un `opencode serve --hostname 127.0.0.1 --port <libre>` descartable: lo lanza y lo
detiene el test (SIGTERM, gracia, SIGKILL al grupo); contraseña aleatoria por corrida
(`OPENCODE_SERVER_PASSWORD`, solo en el entorno de los procesos del test); store aislado bajo
`<ROOT>=$(mktemp -d)`; dos proyectos CDAD descartables con su ejecución activa, sus agentes derivados
publicados y su paquete preparado. El recorrido standalone concurrente es complementario.

### 5.2 Aislamiento

- `XDG_DATA_HOME`, `XDG_STATE_HOME` y `XDG_CACHE_HOME` bajo `<ROOT>`. Se conserva la config global
  (discovery §4).
- **Guarda previa:** `opencode debug paths` con el mismo entorno; `db`, `data`, `state` y `log` deben caer
  bajo `<ROOT>`; si no, el test aborta sin despachar. (Observado con XDG aislado: `db`, `log`, `state`,
  `cache`, `config` bajo `<ROOT>`.)
- El tmp del runtime no se mueve (discovery `:253`).
- La config global conservada hace que el servidor descartable cargue los MCP y plugins globales. Es un
  costo declarado: se registra si quedan procesos tras detener el servidor.

### 5.3 Credenciales del proveedor (ajuste 2, resuelto con evidencia de solo lectura)

Igual que v1:
- El proveedor del modelo configurado es uno propio con `npm: @ai-sdk/openai-compatible`. En la config
  global solo declara `baseURL`: **no** declara `apiKey`, ni por `{env:…}` ni por `{file:…}`.
- La clave existe como credencial de tipo `api` en `auth.json` del directorio de datos; el runtime la
  resuelve desde `XDG_DATA_HOME` y la migración `20260805200742_import_legacy_credentials` la **copia** a
  la tabla `credential` de la base al migrar. Un `XDG_DATA_HOME` aislado arranca **sin credencial**, y
  aislar solo `OPENCODE_DB` copiaría la credencial a la base temporal.
- **Mecanismo soportado:** el runtime sustituye `{env:VAR}` y `{file:ruta}` (`ConfigVariable.substitute`)
  y acepta una capa de config por `OPENCODE_CONFIG_CONTENT` (o `OPENCODE_CONFIG`). El test pone en el
  entorno del servidor descartable
  `OPENCODE_CONFIG_CONTENT={"provider":{"<provider>":{"options":{"apiKey":"{env:<VAR>}"}}}}`;
  `<provider>` sale del prefijo de `CDAD_OPENCODE_MODEL`; `<VAR>` es el **nombre** de una variable que el
  operador define y el test recibe por `CDAD_OPENCODE_KEY_ENV`, sin leer su valor.
- El test **nunca** lee ni copia `auth.json` ni la base viva. Sin variable definida, el test se **omite
  con motivo**, y una omisión **no** acredita PD-6 (BLOQUEO declarado).
- Alternativas (A) env del operador (recomendada), (B) `{file:}` a un archivo del dueño, (C, rechazada)
  copiar `auth.json`. VERIFY resueltos por el primer despacho real (§10).

### 5.4 Registro

Versión (`--version` y `/api/info`), config anonimizada, duración de cada sesión, terminaciones,
`store_reads`, procesos que quedan tras detener el servidor y las observaciones VERIFY de §10.

### 5.5 Recorrido real contra el servicio VIVO (nuevo, enmienda 001)

Distinto del recorrido aislado: aquí se usa el **servicio de fondo en uso normal**, sin reiniciarlo ni
cambiar su configuración. Lo corre el orquestador o el dueño.

1. **Precondición.** `opencode service status` informa que el servicio corre (URL). Se registra la versión
   del cliente y la del servicio según D-11.
2. **Un despacho real.** Desde un **proyecto descartable** (fuera del repo de la feature), con un encargo
   **mínimo** y `mode: "service"`, se despacha un CDAD real contra el servicio vivo.
3. **Dos concurrentes.** Luego, dos despachos con encargo mínimo desde dos proyectos descartables, con el
   mismo almacén que el servicio usa.
4. **Registro por despacho:** terminación, **modo efectivo** (`service` sin flags), `mode_requested`,
   `service_status`, `server_version`, `fallback`, tiempos, errores, `store_reads` y, si aplica, la fila
   durable correlacionada.
5. **Atribución a servicio (AC-1).** Se verifica por: (a) la **fila durable** — `session_v2` incluye la
   columna `version` (texto, NOT NULL; observado en el store vivo igual a la versión del runtime), que
   permite leer la versión efectiva del runtime que produjo la fila; (b) el **inventario de procesos** —
   durante el despacho no aparece ningún `serve --stdio` (servidor privado de standalone) ni un
   `serve --service` nuevo, y `service status` sigue informando la misma URL antes y después; (c) el
   **log del runtime** (`<log>/opencode.log`, líneas `timestamp= level= run= message= version= channel=
   local= args= role=`) leído de forma acotada por id de sesión, como en el discovery. El límite de (a) se
   declara: la columna prueba la **versión efectiva** observada, no por sí sola **qué proceso** sirvió la
   sesión; la atribución de proceso la dan (b) y (c).
6. **Declaración obligatoria.** La **eliminación de bloqueos no se demuestra** con este recorrido: queda
   como **observación empírica** en la recepción (AC-7) y después. Un único éxito no prueba que la
   contención desapareció (§11).
7. **Costo y límites.** Consume tokens del proveedor y usa el store vivo; por eso lo corre quien tiene la
   autoridad (orquestador o dueño) y con autorización previa. No reinicia, no recarga y no reconfigura el
   servicio; si el recorrido exigiera algo reservado al dueño, PD-6 queda en BLOQUEO declarado.

### 5.6 Observaciones VERIFY del recorrido aislado

Se conservan las de v1 ((a) forma de `version` en `/api/info`; (b) que `{env:}` alcance
`OPENCODE_CONFIG_CONTENT`; (c) si `serve --stdio` termina al morir su cliente por SIGKILL; (d) si un
servidor ya usado toma un agente derivado cambiado), y se agregan:
- (e) si `session_v2.version` de la fila correlacionada la escribe el **servidor** o es la versión
  declarada por el cliente (resuelve el alcance de la señal (a) de §5.5);
- (f) si `service status` mantiene el formato de una línea (URL o `stopped`) en el runtime que se use.

## 6. Decisiones (D-n) con fundamento y trade-off

- **D-1 (el preflight rige el modo servidor efectivo, también por compatibilidad).** Fundamento: AC-6.
  Costo: el oráculo `test_pd4_server_config_uses_server_without_standalone` pasa a servir `/api/info` en
  loopback con la versión del fake.
- **D-2 (`--version` solo cuando aporta).** En standalone el servidor es el mismo binario (nunca
  `--version`); en servidor, siempre; **en servicio, solo si el servicio corre** (para la comparación de
  D-11) [dif. enmienda]. Fundamento: conserva los oráculos de llamada única y no inventa una versión donde
  el mismo binario la garantiza. Costo: en el fallback a standalone, `client_version` registra el
  `binary_version` configurado o `unknown`.
- **D-3 (gracia efectiva con tope proporcional).** Sin cambios (costos de cota chica; VERIFY en T2).
- **D-4 (rc≠0 sin fila sigue siendo `transport-error` inmediato).** Sin cambios.
- **D-5 (procedencia en texto libre y registro de worker en toda terminación).** Sin cambios; el esquema
  I8 sigue cerrado (`cdad_packet.py:2371-2445`) y la interfaz no se toca (INV-4).
- **D-6 (intento previo por paquete).** Sin cambios (límite y deuda DT-3).
- **D-7 (credenciales por sustitución de config).** Ver §5.3.
- **D-8 (aceptación de PD-6 en servidor, real, y en servicio vivo).** Fundamento: la topología servidor es
  la preferida; la enmienda agrega el uso normal del servicio (§5.5). El fixture no prueba el runtime real
  y el standalone real complementa, no sustituye.
- **D-9 (regla de default: se conserva la compatibilidad v1) [nueva].**
  - **Fundamento:** (a) un cambio de topología hacia un servidor **compartido** es una decisión del
    consumidor, no un default silencioso: la feature existe para que la selección sea explícita (PD-1);
    (b) preserva la matriz de oráculos de T1 ya entregada (no hay retrabajo del focal ni de sus oráculos);
    (c) la enmienda pide conservar lo entregado y la compatibilidad v1 de T1.
  - **Costo declarado:** las configs del consumidor que hoy omiten `server` y `mode` siguen abriendo un
    servidor privado por despacho hasta que declaren `mode: "service"`. **Acción de la recepción (AC-7):**
    declarar `mode: "service"` en cada config de consumidor.
  - **Alternativa registrada:** si el dueño u orquestador decide que el default sea `service`, es un cambio
    de una fila de §2.2 y del focal de T1 (el test-writer ajusta la fila `sin declarar`), con el costo de
    cambiar la topología de configs que hoy no declaran nada.
- **D-10 (modo servicio: liveness por `service status`, despacho sin flags, fallback declarado, clave
  estricta `service.require`) [nueva].**
  - **Fundamento:** el runtime está diseñado para que el cliente, sin flags, use el servicio de fondo; el
    hecho verificado es que `service status` imprime la URL o `stopped` con rc=0 y **no arranca nada**
    (ventana del binario `cli.service.status`: `process.stdout.write((r?.url ?? "stopped") + EOL)`, con
    `discover({...ku(), version: void 0})`), así que sirve como comprobación de solo lectura. El fallback
    a standalone cuando el servicio no corre conserva el comportamiento de hoy y lo hace **visible y
    contable** en la procedencia.
  - **Clave de la variante estricta:** `service.require` (booleano, default `false`). Con `true`, el
    servicio que no corre termina `blocked`. Se eligió una clave propia bajo `service.*` (mismo estilo que
    `wait.*`) en vez de sumar valores a `mode`, para que `mode` siga siendo el conjunto cerrado de modos.
  - **Costo:** una invocación extra (`service status`) y un camino de fallback con dos resultados; ambos
    acotados y testables.
- **D-11 (fuente de la versión del servicio) [nueva, decisión del orquestador].**
  - **Hecho (evidencia de solo lectura sobre el binario, sin ejecutar nada prohibido):** el cliente en modo
    por defecto obtiene la credencial del servicio leyendo el **registro del servicio** (esquema observado
    `{id, version, url, pid, password}`; lector `readFileString` sobre el archivo de registro, con la
    setting `password` en el archivo de config del servicio); con ese `password` arma
    `Authorization: Basic base64("opencode:" + password)`. **Sí compara versión, pero el CLI `run` no se
    lo pide:** `cli.server-connection.resolve` hace `mismatch = e.mismatch ?? "ignore"` y
    `run` (comando `commands.run`) llama al resolver **sin** `mismatch`, así que cae en `"ignore"` →
    `discover` sin versión → `ensure` con `version: undefined`. El error
    `Background server version does not match this client` existe, pero solo se alcanza con un `mismatch`
    distinto de `"ignore"`/`"replace"`, y **ningún flag ni variable del CLI lo produce**. La única setting
    relacionada (`opencode service get/set`) tiene un **conjunto cerrado** de claves
    (`disabled`, `remote`, `hostname`, `port`, `password`, `cors`, `env`) que **no** controla la versión ni
    el arranque automático.
  - **(A, recomendada) Lector de una sola clave.** Leer el **registro del servicio** (`<state>/service.json`
    por defecto) proyectando **solo** la clave `version` y descartando el resto: nunca el documento
    completo, nunca la contraseña, nunca la URL, sin conexiones de red. Comparar con la versión observada
    del cliente.
    - **Costo:** CDAD abre un archivo que también contiene la contraseña. **Mitigación:** el lector es una
      proyección: devuelve `version` (o `unknown`) y nada más; ninguna otra clave llega a una variable que
      escape, y nada del documento entra en argv, diagnóstico, registros ni recibo (INV-6, PD-5).
    - **Riesgo de acoplamiento:** la ruta y el nombre del archivo de registro **no** son contrato público
      (deuda DT-6). `absent`/no parseable/clave ausente → `unknown` → `blocked` (fail closed).
  - **(B) Alternativa sin secreto.** Sin lectura de versión: el modo servicio se limita a la liveness y
    registra `server_version=unknown`; la versión efectiva se observa **después** en la fila
    (`session_v2.version`). **Trade-off:** con un servicio corriendo de versión distinta, CDAD despacharía
    igual (el runtime hace `ignore`), lo que **contradice** la precisión del dueño («versión distinta con
    el servicio corriendo → blocked»). Solo es admisible si el dueño lo acepta; en ese caso, quien quiera
    gate de versión usa `mode: server <url>` con `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD`.
  - **(C, rechazada) `GET <url>/api/info` con la credencial.** Requiere leer la contraseña **y** usar la
    URL para el mismo hecho que (A) obtiene localmente: más exposición, mismo resultado.
  - **(D, rechazada)** Copiar/leer el documento completo del registro o el archivo de credenciales.
  - **Decisión:** la ratifica el orquestador **antes** del GREEN de T1b. Si no la ratifica, T1b se
    **detiene** y vuelve al orquestador (mismo patrón que la decisión de credencial de T3).
- **D-12 (atribución de AC-1 en el servicio) [nueva].** Señal durable `session_v2.version` + inventario de
  procesos (sin `serve --stdio`/`serve --service` nuevos) + log acotado, con el límite declarado en §5.5.5.
- **D-13 (ventana de carrera) [nueva].** No hay forma soportada en el runtime de impedir que el cliente
  arranque el servicio si este se cae entre la comprobación y el despacho (no hay flag, no hay variable de
  entorno, y la setting `disabled` no lo evita: solo redirige a un standalone). Se declara **riesgo
  residual** (§11) con la mitigación de comprobar lo más tarde posible.

## 7. Alcance y fuera de alcance

**Incluido:**
- adaptador OpenCode (selección de modo, preflight de servidor y de servicio, procedencia, secretos, espera,
  recuperación);
- tests focales nuevos y oráculos declarados;
- `cli-delegation.md`;
- config de ejemplo en `assets/`;
- recorrido real aislado y recorrido real contra el servicio vivo;
- candidato instalable en raíz aislada.

**Fuera de alcance:**
- identificar al tenedor del bloqueo;
- mantenimiento de la base viva;
- actualización del runtime y correcciones upstream;
- **gestionar el servicio de fondo**: arrancarlo, reiniciarlo, detenerlo o configurarlo
  (`service start|stop|restart|get|set|unset`), reservado al dueño/operador;
- abortar sesiones del servidor;
- verificar el contenido de las instrucciones cargadas;
- límite global de agentes, sandbox o store por proyecto;
- cambiar la interfaz común;
- cambiar el default de `mode` para configs que no lo declaran (D-9);
- AC-7.

## 8. Deuda con condición de cierre

- **DT-1.** Ruta de abort de sesiones en el servidor. Se cierra cuando el runtime documente o exponga una
  ruta verificada.
- **DT-2.** Frescura de agentes en un servidor de larga vida. Se cierra con la observación de T3 y, si hay
  caché, con una decisión del dueño sobre `reload`, reservado al dueño.
- **DT-3.** Intento previo a nivel de ejecución o de despacho concurrente del mismo paquete (lock por
  paquete). Se cierra si la recepción (AC-7) o un incidente muestran duplicación por esa vía.
- **DT-4.** `instruction_state` como prueba de contenido del agente.
- **DT-5.** Permisos pendientes con el cliente muerto en modo servidor.
- **DT-6 (nueva).** El **registro del servicio** (ruta, nombre y esquema `{id, version, url, pid,
  password}`) es un hecho observado, **no un contrato público**: D-11 depende de él para la versión. Se
  cierra cuando el runtime exponga una vía soportada para consultar la versión del servicio sin leer su
  secreto (por ejemplo, una salida de `service status` con la versión, o un `service get version`).
- **DT-7 (nueva).** El fallback `service` → `standalone` como camino habitual. Se vigila con el contador
  de la procedencia (`fallback=service-unavailable`); si en la recepción domina, se decide con el dueño
  (declarar `service.require`, o cambiar el default, D-9).

## 9. Referencias (archivo:línea y ventana del binario)

- **Adaptador** (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`, tras T1):
  - modo e invocación: `:110`, `:274-311`, `:549-599`, `:1100-1129`, `:1206-1260`;
  - store y espera: `:432-505`;
  - I8 y procedencia: `:793-879`, `:1131-1148`;
  - clasificación: `:1024-1054`;
  - flujo: `:1081-1365`.
- **Interfaz** (`skills/cdad-cycle/scripts/cdad_delegate.py`): `:48-51`, `:131-162`, `:252-283`.
- **I8:** `skills/cdad-cycle/scripts/cdad_packet.py:2371-2445`; ficha y render `:3018-3086`, `:3293-3316`.
- **Referencia:** `skills/cdad-cycle/references/cli-delegation.md:112-183`.
- **Oráculos v1:** `tests/test_005_010_t2_load_mode_invocation.py:94`, `:287`, `:361-385`;
  `tests/test_005_009_t2_opencode_adapter.py:242-250`, `:417`, `:879-880`, `:1139`, `:1400`;
  `tests/test_005_009_t1_interface.py:100`, `:464-484`.
- **Focales de esta feature:** `tests/test_006_001_t1_selection.py` (T1 GREEN; `NEVER_INVOKED_TOKENS`
  `:195`, uso `:648`; pares de procedencia `:960-966`), `tests/test_006_001_t2_wait_recovery.py` (T2 RED),
  `tests/test_006_001_t1b_service_mode.py` (nuevo, T1b), `tests/test_006_001_t3_*.py` (T3).
- **Binario del runtime (v2.0.27; ventanas de texto acotadas, sin valores):**
  - `cli.server-connection.resolve` (`chunk-4rr4bwys`): pares `--server and --standalone cannot be
    combined`, `mismatch`, `checkVersion`, `Warning: Server at <url> has version <v>; this client is <v>.
    Continuing anyway.`, `Background server version does not match this client`; cuerpo observado
    `if(e.standalone || (yield*Sf()).disabled===!0) return standalone; let r=e.mismatch??"ignore",
    n=yield*ku({checkVersion: r!=="ignore"}); return f({...n, onStart}, r)`, y
    `f`: `"replace"→ensure(e)`, `"ignore"→ensure({...e, version: void 0})`, otro → `discover(e)`, si no
    hay → `discover({version: void 0})` presente ⇒ `Error(...)`, si no → `ensure(e)`.
  - `cli.service.status`: `process.stdout.write((r?.url ?? "stopped") + EOL)` con
    `discover({...ku(), version: void 0})` (no arranca nada).
  - `ku` (descriptor del servicio): `{file, version: checkVersion ? <v-cliente> : void 0, env,
    command: [<entrypoint>, "serve", "--service"]}`.
  - `service.discover` / `service.ensure`: `discover` lee el registro (`readFileString`) y devuelve el
    endpoint solo si `state === "ready"`, `compatible` y pasa la compatibilidad de versión; `ensure`
    recluta/arranca.
  - Esquema del registro: `{id, version, url, pid, password}`; cabecera
    `Authorization: Basic base64("opencode:" + password)`.
  - `cli.service-config.read/write/password` y `cli.service-config.get/set/unset`: archivo de config del
    servicio con el conjunto cerrado `disabled | remote | hostname | port | password | cors | env`
    (`Unknown service config key` para el resto); **ninguna** controla versión ni arranque automático.
  - `h`: registro bajo el directorio de **estado** (`<state>/service.json` por defecto) y config bajo el
    de **config**; `legacyRegistrationFiles` incluye el nombre legado.
  - `serve --help`: flags `--service` y `--stdio`; par `--service and --stdio cannot be combined`.
  - `run --help`: `--standalone` («Run with a private server instead of the background service») y
    `--server` («Connect to a server URL instead of the background service»).
  - Servicio que se auto-vigila: pares `managed service registration replaced; shutting down`,
    `observedServiceID`, `observedServicePID`, `observedVersion`, `observedURL`.
  - Store: `session_v2` (`cdad_packet` no aplica; esquema del runtime) con la columna `version` TEXT NOT
    NULL; observado en el store vivo `2.0.27`.
  - Log: `<log>/opencode.log`, líneas `timestamp= level= run= message= version= channel= local= args=
    role=`.
- **Discovery:** D1-D5 (`:47-167`), §4 (`:243-316`), §5 (`:318-327`).
- **Cambio de alcance:** `docs/epics/epic-006-opencode-concurrency/execution.md:38-63`.

## 10. VERIFY (resueltos o declarados)

- **Resueltos en v1:** mecanismo de credenciales del proveedor (§5.3); salida de `--version`
  (`opencode v<semver>`); orden de contraseñas del cliente.
- **Resueltos en el draft-002 (enmienda), solo lectura:**
  - `service status` imprime la URL o `stopped` con rc=0 y **no arranca nada** (código del subcomando +
    corrida con entorno aislado en el scratchpad: `stopped`, rc=0);
  - el default del cliente sin flags es **`mismatch = "ignore"`**: reutiliza el servicio **sin comparar
    versión** y **sin escribir nada en stderr** (el aviso «Continuing anyway.» es exclusivo de `--server`);
  - **no existe** flag, variable de entorno ni setting del servicio que haga fallar al cliente por
    diferencia de versión, ni que le impida arrancar el servicio si no corre;
  - el conjunto cerrado de claves de `opencode service get/set` es
    `disabled|remote|hostname|port|password|cors|env`;
  - el cliente en modo por defecto obtiene la credencial del servicio del **registro del servicio**, cuyo
    esquema observado es `{id, version, url, pid, password}`;
  - `session_v2` incluye la columna `version` (observado igual a la versión del runtime).
- **A resolver en el recorrido real (T3):** (a)-(d) de v1, más (e) quién escribe `session_v2.version`, y
  (f) estabilidad del formato de una línea de `service status`.
- **Abiertos, a deuda:** `wal_autocheckpoint` y `busy_timeout` del runtime; conexiones por servidor;
  escritores fuera del namespace visible; DT-1, DT-4, DT-5, **DT-6, DT-7**.
- **No verificado en este ciclo (prohibido por el invariante):** el contenido del registro del servicio
  (claves sí, valores no). Por eso D-11 queda como decisión del orquestador.

## 11. Riesgos con mitigación

- **Riesgo residual de contención (ajuste 6).** Esta feature **no elimina** la contención del store
  compartido: siguen N≥3 escritores de larga vida y un `busy_timeout` de 5 s fijo en el runtime.
  Mitigación: reducir escritores por despacho con el modo servicio o un servidor compatible, no duplicar
  intentos (PD-9) y no perder la correlación (PD-8). Un único éxito real no prueba que la contención
  desapareció (PD-6, §5.5).
- **Ventana de carrera del modo servicio (D-13).** El servicio se cae entre la comprobación y el despacho
  y el cliente lo arranca. No hay forma soportada de impedirlo. Mitigación: comprobar lo más tarde
  posible; registrar `service_status`/`dispatch_flags`; declararlo como riesgo residual, no como fallo de
  CDAD.
- **El fallback se vuelve el camino habitual (DT-7).** El modo servicio caería a standalone casi siempre
  y seguiría habiendo un escritor por despacho. Mitigación: `fallback=service-unavailable` **contable** por
  intento, para verlo en la recepción; `service.require` para exigir el servicio; acción de la recepción
  (declarar `mode: "service"` en las configs del consumidor).
- **Un standalone junto a un servicio vivo.** Es exactamente el «escritor más» que se busca evitar.
  Mitigación: PD-13/PD-14/INV-10 lo prohíben explícitamente: con el servicio corriendo, cualquier fallo
  (versión, credencial, no alcanzable, respuesta inesperada) termina `blocked`, nunca standalone; y la
  recuperación tras un timeout no abre un standalone «para destrabar» (PD-9).
- **Exposición del secreto del servicio (D-11 A).** Un lector del registro podría filtrar la contraseña.
  Mitigación: proyección de una sola clave, sin red, sin URL, nada del documento en ninguna salida
  (PD-5, PD-14, INV-6); y la decisión pasa por el orquestador antes del GREEN.
- **Worker que sigue tras un timeout en modo servidor o servicio.** El diagnóstico lo avisa y PD-9
  bloquea el re-despacho mientras la fila no esté idle; no se abre un standalone.
- **Agentes en caché en el servidor/servicio.** Observación de T3 y DT-2.
- **Costo del recorrido real, aislado y contra el servicio vivo.** Gasta tokens del proveedor, carga MCP y
  plugins globales, usa el store vivo. Se ejecuta con autorización del orquestador y sin reiniciar ni
  reconfigurar el servicio. Si exige algo reservado al dueño, PD-6 queda en BLOQUEO declarado.
- **Flakiness de tiempos.** D-3 y los valores chicos de fixture; PD-11 cubre las tres variantes de carrera.

## 12. Método y evidencia del draft-002 (enmienda)

Todo fue de solo lectura sobre el repo y sobre el binario del runtime; sin editar archivos.

- **Fuentes leídas:** el contrato de unidad (sha256 `13f7db14…`, coincide), `execution.md` (§cambio de
  alcance), la spec y el plan v1, el discovery, `t1-green.md`, `t2-red.md`, el adaptador, la interfaz, la
  referencia, `cdad_packet.py` y los focal de T1 y T2 (`test_006_001_t1_selection.py:195`, `:648`,
  `:960-966`; `tests/test_006_001_t2_wait_recovery.py:645-675`, `:861-870`).
- **Binario:** `strings -n 6` a un archivo del scratchpad (una lectura, 1,7 s) y **ventanas de texto
  acotadas** con Python; ninguna ventana imprime la contraseña ni el contenido de `service.json`. Las
  afirmaciones de §9 citan el submódulo/identificador (`cli.server-connection.resolve`,
  `cli.service.status`, `service.discover`, `cli.service-config.*`) y el cuerpo observado.
- **Ejecución del runtime (con entorno aislado en el scratchpad):** solo `--version`, `service status`,
  `debug paths`, `service --help`, `service get|set|status --help`, `run --help`, `serve --help`,
  `service start --help`. **No** se ejecutó `service get`, `set`, `start`, `stop` ni `restart`, ni se leyó
  `service.json`, `auth.json` ni ningún archivo con contraseñas. `service status` con estado aislado
  devolvió `stopped` con rc=0; `debug paths` confirmó que `db`, `data`, `state`, `cache`, `log` y `config`
  caen bajo `<ROOT>`. Las corridas escribieron solo dentro del scratchpad.
- **Store vivo:** **una** consulta acotada de solo lectura (`mode=ro`, `LIMIT 3`, columnas
  `id, version, agent, time_created`) para resolver la semántica de `session_v2.version`: las tres filas
  dieron `2.0.27`. No se registran ids ni rutas.
- **Validación del bloque plan-tasks:** pasé el bloque por `_plan_tasks_from_contract`,
  `_check_plan_tasks` y `_check_plan_validation_plan`: **OK**, tareas T1, T1b, T2 y T3 con estrategia
  declarada; `_plan_task_applicable_ids(_plan_task_ficha(...))` no queda vacío para ninguna de las cuatro.
- **Repo:** sin cambios de producto. `git status` limpio; `git diff --stat` vacío.

## 13. Aprobación y puntos de decisión

Pendiente. La decide el orquestador bajo la HITL delegada del epic-006, junto con el plan. Esta spec no
lleva marca de aprobación.

Puntos que el orquestador debe resolver al aprobar:

1. **D-11 (fuente de la versión del servicio).** Ratificar la alternativa (A) (lector de una sola clave
   `version` del registro del servicio, sin red y sin secreto) o, en su defecto, (B) (sin gate de versión,
   con el conflicto declarado con la precisión del dueño). Sin esta decisión, T1b **no** debe empezar su
   GREEN.
2. **D-9 (regla de default).** Confirmar la compatibilidad v1 (recomendada) o pedir el cambio a `service`
   por defecto (implica ajustar la fila `sin declarar` del focal de T1).
3. **Oráculos y tokens.** Se mantiene que **no** hace falta cambiar los focal de T1 ni de T2:
   - T1 (`test_006_001_t1_selection.py`): su `NEVER_INVOKED_TOKENS = ("serve","service","reload")`
     (`:195`) se usa en el camino de **modo servidor** (`:648`), donde `service status` **no** se invoca:
     sigue verde sin cambios. El focal nuevo de T1b declara su **propio** conjunto refinado (permite
     `service status`; prohíbe `serve`, `service start|stop|restart|get|set|unset` y `reload`). No es una
     corrección de T1, es una precisión de alcance.
   - T2 (`test_006_001_t2_wait_recovery.py`): sus aserciones de procedencia parsean por subcadena
     (`store_reads=` … `;`) y el registro fabricado es propio del fixture; los pares nuevos van **al
     final** de `provenance.runtime` y `provenance.session` conserva su orden. **No requiere cambios.**
   - El único cambio ya autorizado de oráculos sigue siendo el de v1 (plan §3, oráculos 1 y 2).
4. **PD-6** exige ahora dos recorridos reales (§5.1 y §5.5) y el segundo usa el servicio vivo: confirmar
   la autorización operativa y quién lo corre.

## 14. Diff conceptual por PD (enmienda 001)

| PD | Qué cambia | Por qué |
|---|---|---|
| PD-1 | Se agregan a la matriz §2.2 las filas de `service` (corre+compatible → sin flags; no corre → standalone/`blocked`; corre+incompatible → `blocked`) y la regla de default se fija explícitamente en compatibilidad v1 (D-9). | El modo nuevo debe entrar por la misma selección explícita y sin fallback silencioso que el resto. |
| PD-2 | La lista de invocaciones del binario en **modo servidor** queda igual (`--version`, `run`) y se explicita que `service status` **no** se invoca en ese modo. | Agregar el modo servicio no debe aflojar el oráculo de llamada única del modo servidor. |
| PD-3 | Se agregan los pares `dispatch_flags=`, `service_status=`, `fallback=` **al final** de `provenance.runtime`, y el valor `service` a `mode_requested`/`mode_effective`. | Hacer visible y contable el fallback y el modo de despacho, sin tocar el esquema I8 ni el orden que parsea T2. |
| PD-4 | El «mismo encargo» pasa a verificarse también en el **despacho sin flags** del modo servicio. | AC-2 rige en todos los modos soportados. |
| PD-5 | Se extiende a la **URL del servicio** y al **secreto del servicio**: la salida de `service status` se descarta salvo el discriminante; ninguna salida lleva la URL del servicio. | El modo servicio introduce una fuente nueva de URL y de secreto que hoy no existía. |
| PD-6 | La aceptación suma el **recorrido real contra el servicio VIVO** (un despacho y luego dos concurrentes, encargo mínimo, sin reiniciar ni reconfigurar) y declara que la eliminación de bloqueos **no** se demuestra. | Es la verificación que pidió el dueño en el cambio de alcance; la mitigación no se promete. |
| PD-7 | Se explicita que en modo **servicio** una fila no idle espera hasta la cota (`timeout`), y que tras un `timeout` en servicio o servidor **no** se abre un standalone. | Precisión del dueño: la recuperación no debe reconstruir la situación que se corrige. |
| PD-8 | En `timeout` con el cliente vivo, el aviso de «worker que puede seguir» cubre también el modo **servicio**; CDAD no toca el proceso del servicio. | El worker vive en el servicio, no en el adaptador. |
| PD-9 | Se explicita que el bloqueo por intento previo aplica **igual** tras un `timeout` en servicio o servidor, y que ningún camino de recuperación re-despacha solo ni abre un standalone. | Precisión del dueño. |
| PD-10 | Cláusula explícita: las relecturas del store ante lock son `mode=ro`, acotadas, con backoff y **sin** presión de escritura. | Dejar escrito que la recuperación no agrega escritores. |
| PD-11 | El preflight del modo servicio (`service status` + versión) entra en el presupuesto acotado; presupuesto agotado → `blocked`. | No introducir una invocación sin cota. |
| PD-12 | La config de ejemplo declara `mode: "service"` y `service.require`. | AC-8: la config de ejemplo debe cubrir el camino normal nuevo. |
| PD-13 | **Nueva.** Modo servicio: una `service status`, despacho sin flags, fallback declarado solo si `stopped`, `blocked` con `service.require`, `blocked` ante respuesta inesperada, sin ninguna gestión del servicio, ventana de carrera declarada. | Es el núcleo del cambio de alcance aprobado. |
| PD-14 | **Nueva.** Gate de compatibilidad de versión del servicio con el mecanismo de D-11, `blocked` ante versión distinta o no verificable, **nunca** standalone con el servicio corriendo, sin leer ni emitir el secreto ni usar la URL. | La precisión del dueño exige que una diferencia de versión con el servicio corriendo no produzca un escritor extra. |


## 15. Decisión del orquestador sobre la enmienda 001 (2026-10-16)

Aprobada junto con el plan v2, bajo la HITL delegada de epic-006 y por el cambio de alcance que aprobó el dueño (`execution.md`).

- **D-11: se ratifica (A).** Un lector proyecta solo la clave `version` del registro del servicio. No toca red, contraseña ni URL, y si la clave falta falla cerrado. El acoplamiento a un archivo no público queda como deuda DT-6.
- **D-9: se confirma la compatibilidad v1** cuando `mode` no está declarado. El consumidor declara `mode: "service"` en la recepción.
- **Oráculos:** T1 y T2 siguen sin cambios. Los únicos cambios autorizados son los dos de v1.
- **PD-6 contra el servicio vivo:** lo corre el orquestador, con autorización del dueño (`execution.md`). Es uso normal del servicio, sin reiniciarlo ni configurarlo.
- **Entrega:** el draft lo produjo el architect en OpenCode (`deepseek-v4.1-flash`), en el tercer intento del mismo paquete.
  - El intento 1, un subagente Claude, terminó por HTTP 429.
  - El intento 2, otro subagente Claude, lo detuvo el orquestador por decisión del dueño: los roles van en OpenCode.
  - La disposición «abandoned» registrada después del intento 1 fue un error del orquestador. El paquete no se abandonó: se reintentó y se entregó.

Status: Approved by Claude orchestrator (HITL delegated by Pablo for epic-006) on 2026-10-16
