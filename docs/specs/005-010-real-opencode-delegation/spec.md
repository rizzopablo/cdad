> Spec **aprobada** (2026-10-11) por el orquestador Claude (ver §11). Texto del **architect** (subetapa `draft`,
> etapa 2) para su materialización por el orquestador (ADR-003). Aprueba el **orquestador
> Claude** bajo la excepción HITL de epic-005 (`docs/epics/epic-005-real-operation/execution.md`
> §«Excepción: 005-010 orquestada por Claude»). Insumo verificado:
> `docs/specs/005-010-real-opencode-delegation/discovery.md` (mapa archivo:línea + sondas reales
> de OpenCode v2.0.26). Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila de orden 6,
> `:39`). Fronteras/decisiones del orquestador declaradas en el encargo del draft. Formato de
> referencia: `docs/specs/005-009-cli-delegation/spec.md`. Sin valores de este VPS.

## Spec — 005-010-real-opencode-delegation

**Feature ID:** `005-010-real-opencode-delegation` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-11).

```yaml
feature_id: 005-010-real-opencode-delegation
feature_name: Continuación correctiva de 005-009 (el adaptador OpenCode completa un recorrido real)
created_at: 2026-10-11
status: approved
approved_by: orquestador Claude (excepción HITL de 005-010)
approved_at: 2026-10-11
```

### 1. Descripción funcional

El resultado no es un motor nuevo ni un lector de sesiones de producto: es que **el adaptador
OpenCode de 005-009 complete un recorrido real, no solo contra un doble de test**. 005-009 dejó
implementada la interfaz común de delegación y el adaptador del destino OpenCode, pero contra el
runtime real el adaptador es **inoperable**: (a) bloquea todo despacho porque los roles se
publican `mode: subagent` y el adaptador exige `mode: all`; (b) espera una señal durable que
**solo escribe el binario falso del fixture** (un JSON `<fake>/sessions.json`) y que OpenCode
real **no produce** — persiste sesiones en una base SQLite —; y contra esa base real lanza una
excepción **no capturada** (`UnicodeDecodeError`), de modo que ni falla cerrado con diagnóstico.
Además, la invocación se acopla al servicio de fondo del dueño (no pasa `--standalone`), no
correlaciona la sesión (`--session`), no habilita permisos no interactivos (`--auto`) y no
registra el modelo observado.

La feature **no crea otro state ni otro ledger**: reutiliza el paquete canónico, el registro I8,
el recibo (`receive`) y la reconciliación (`reconcile`) ya existentes, y **no modifica la
interfaz común** (`cdad_delegate.py`) ni el generador de agentes (`scripts/cdad-generate.py`).
El cambio vive **solo en el adaptador OpenCode** (`cdad_delegate_opencode.py`), en sus tests y en
dos referencias. El recorrido común sigue siendo:

`agente autorizado (coordinador) → encargo canónico → adaptador del CLI destino → sesión de rol (OpenCode) → resultado durable → re-entry del responsable`

Tres hechos verificados del discovery (`discovery.md` §3) definen el diseño:

- **La señal durable real existe y es correlacionable sin ambigüedad.** OpenCode v2.0.26 guarda
  las sesiones en una base **SQLite** (`session_v2`, `session_message`); con `--session <id>`
  elegido por el adaptador, la fila durable lleva **ese** `id` y `agent`, y la sesión pasa a
  *idle* con `idle_outcome ∈ {succeeded, failed, interrupted}` + `time_idle`; el texto final vive
  en el último mensaje `assistant` (`session_message.data.content[].text`). Es **solo lectura** y
  falla cerrado ante esquema desconocido (`discovery §4.1`, opción A).
- **En la versión instalada, `opencode run --agent <mode:subagent>` SÍ es una entrada no
  interactiva** (sonda `discovery §3.2`: los roles `mode: subagent` respondieron; un agente
  inexistente da error explícito, no cuelga). La premisa «cuelga en silencio» provenía del
  **binario legacy** en PATH, no del runtime v2. Por eso el chequeo de `mode: all` **deja de ser
  la barrera**; la identidad se verifica desde la fila durable
  (`session_v2.agent == "cdad-<rol>"`), sin fallback (`discovery §4.2`, opción A).
- **stdin transporta el paquete** (sonda `discovery §3.3`) y `run` acepta `--standalone`,
  `--server`, `--auto`, `--format json`. Falta que el adaptador los use según el nivel correcto
  (config/flag), nunca hardcodeados.

La terminación del proceso y la suficiencia de la entrega siguen siendo **hechos distintos**:
«completado» no equivale a «gate aprobado».

### 2. Contrato

**Contrato bidireccional (la interfaz ↔ el destino ↔ el responsable).**

- **Lo que el adaptador recibe** (por la interfaz ya existente, sin cambios): `proyecto`
  explícito, `paquete canónico` publicado, `rol`/`substage` (del paquete) y `configuración de
  ejecución` (runtime, modelo, binario/versión, store de sesiones, política de espera, y ahora
  `standalone|server` y `auto`).
- **Lo que el adaptador devuelve** (envelope de la interfaz, sin cambios): la **entrega final
  durable** (o «sin entrega suficiente»), la **identidad de sesión** desde la fila durable, y la
  **causa de terminación** en el vocabulario
  `completed | blocked | transport-error | timeout | cancelled | unknown`.
- **Lo que el rol devuelve:** su **texto final** y evidencia referenciada, sin encadenar sesiones
  nuevas fuera de su mandato.
- **Salida legítima ante bloqueo:** diagnóstico accionable (qué falta y cómo seguir), **sin**
  fallback a un agente genérico, **sin** fabricar una entrega y **sin** degradar un fallo cerrado
  ya conocido a un `timeout` por esperar de más.

**Observabilidad (cómo se verifica).** Las postcondiciones se comprueban sobre **artefactos
durables y comportamiento observable**: los bytes del paquete por stdin, la base SQLite del
fixture (esquema observado y sus variantes), el argv de la invocación, el registro I8
(`.cdad/executions/<id>/dispatches/<attempt>.json`), el recibo durable
(`.cdad/runtime/results/<exec>/<packet>/receipt.json`) y la clasificación de `reconcile`. La
mediación real del runtime y el recorrido Claude→OpenCode son la **aceptación** (T4), no un test
determinista.

**Superficie que 005-010 toca (sin controlador nuevo de ciclo, sin otro state):**

- **Modificado (producto, fuente canónica):** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`
  — el adaptador del destino OpenCode: lector de la base SQLite en **solo lectura** + correlación
  por `--session`; clasificación por `idle_outcome`; modo de carga por la versión instalada +
  identidad desde la fila durable; invocación con `--standalone`/`--server`/`--auto`; observación
  I8 con `model_reported`/`session` de la fila durable.
- **Modificado (tests):** `tests/test_005_009_t2_opencode_adapter.py` — el doble JSON
  (`sessions.json`) se **reemplaza** por un **SQLite real chico** con el esquema observado; el
  modo de carga pasa de «exige `all`» a «acepta `subagent` y verifica identidad desde la fila».
- **Nuevo (tests):** `tests/test_005_010_t1_durable_signal.py`,
  `tests/test_005_010_t2_load_mode_invocation.py`, `tests/test_005_010_t3_references.py`,
  `tests/test_005_010_t4_integration.py` (omitido por defecto).
- **Modificado (metodología):** `skills/cdad-cycle/references/cli-delegation.md` (contrato de la
  señal durable real, correlación, modos de carga y servidor/permisos) y
  `skills/cdad-cycle/references/opencode-delegation.md` (sección de modo de carga actualizada y
  **tabla de modelos obsoleta** reemplazada por el puntero a la única tabla de modelos).
- **Sin cambios:** la interfaz común `cdad_delegate.py`; el generador `scripts/cdad-generate.py`;
  `sources/agents/adapters/opencode.md`; `prepare`, el esquema cerrado del registro I8,
  `cdad_result.py` (receive/recibo), `cdad_continuity.py` (reconcile/resume), el guard CC y la
  publicación atómica. **No** se crea otro state del ciclo ni otro ledger.

**Postcondiciones (numeradas y verificables).**

**PD-1 (señal durable real y correlacionada sin ambigüedad).** El adaptador **elige** el id de
sesión y lo pasa en `--session <id>`; lee la **base de sesiones que declara la configuración de
ejecución** (campo `sessions_db`; ruta **configurable, nunca hardcodeada**) en **solo lectura**, y
correlaciona de forma inequívoca por ese `id`. Espera, dentro de la espera acotada
(`wait.timeout_seconds`), a que la fila `session_v2` de ese `id` tenga `time_idle`/`idle_outcome`
(idle material), y toma el texto final del **último mensaje `assistant`** de
`session_message` de esa sesión. **Nunca** usa el `rc` del cliente como señal de fin ni inventa
otra señal. Verificable: el argv de la invocación incluye `--session <id>`; la fila durable
correlacionada tiene ese id; un cliente que retorna `rc=0` **antes** de que la fila quede idle
**no** produce `completed`.

**PD-2 (fallo cerrado con diagnóstico ante esquema desconocido o archivo ilegible).** Si el store
no existe, no es legible, no es SQLite, le faltan las tablas/columnas esperadas, o su contenido
JSON no parsea, el adaptador **falla cerrado** con un **diagnóstico accionable** y terminación en
el vocabulario (`blocked`), **sin** fabricar entrega ni recibo y **sin** convertir el hecho ya
conocido en un `timeout` (no espera de más). El `UnicodeDecodeError` actual (leer la base como
JSON UTF-8) **deja de ser una excepción no capturada**: pasa a ser un fallo cerrado diagnosticado.
Verificable: contra un store con esquema incompleto (p.ej. sin `idle_outcome`) el adaptador
devuelve `blocked` con diagnóstico que nombra el esquema/columna; contra un archivo ilegible, igual
(nunca traza no capturada); no hay recibo.

**PD-3 (modo de carga por la versión instalada; SIN fallback a un agente genérico).** El adaptador
**deja de exigir `mode: all`**. Exige que el **agente derivado `cdad-<rol>` esté publicado**
(`.opencode/agents/cdad-<rol>.md`, como hoy) y **verifica la identidad del rol desde la fila
durable**: `session_v2.agent == "cdad-<rol>"`. Si el derivado no está publicado (pre-despacho) o
la fila durable declara **otro** agente, **falla cerrado** con diagnóstico nombrado y **NO** cae a
un agente genérico no-Cdad (`general`, `coder`, …). `scripts/cdad-generate.py` **no** se modifica
(los roles siguen `mode: subagent`, usables como subagente nativo). Verificable: con la entry
derivada `mode: subagent` publicada, el adaptador **sí** despacha; si la fila durable reporta un
agente distinto, **no** declara entrega; jamás selecciona un agente no-Cdad.

**PD-4 (transporte e invocación realmente soportados y configurables en el nivel correcto).** El
paquete se transporta **byte-idéntico por stdin** (ya verificado). La invocación usa
**`--standalone` por defecto** (servidor privado), con **`--server <url>` tomado de la
configuración** cuando el despliegue lo requiera (alternativa a `--standalone`, nunca a la vez), y
**`--auto` configurable por configuración, activado por defecto**, **documentado explícitamente
como auto-aprobación de permisos no denegados y NO como sandbox** (los deny-maps de path siguen
siendo la barrera). Verificable: con config por defecto, argv incluye `--standalone` y `--auto` y
no `--server`; con `server` en config, argv incluye `--server <url>` y no `--standalone`; con
`auto: false`, argv no incluye `--auto`.

**PD-5 (clasificación desde `idle_outcome`, no desde el `rc`).** El adaptador clasifica la
terminación desde el **hecho material** de la fila correlacionada: `succeeded → completed`
(con texto final presente; si falta, `blocked` con diagnóstico), `failed → blocked`,
`interrupted → cancelled`; **sin fila correlacionada o sin idle dentro de la espera acotada →
`timeout`**. `completed` es la **única** terminación que persiste la entrega por el `receive`
existente (recibo `semantic_status: "pending"`; entrega ≠ gate). Verificable: cada variante sale
de su hecho material; un cliente que falla en el transporte antes de cualquier fila
(`rc ≠ 0` sin señal) produce `transport-error`; ninguna terminación no-completada fabrica recibo.

**PD-6 (observación I8 con `model_reported` y `session` desde la fila durable).** En el registro
I8 que el adaptador escribe para el intento del worker, `model_reported` y `session` provienen de
la **fila durable** (`session_v2.model` y `session_v2.id`), con `provenance` que lo declara; si la
fila no trae modelo, `model_reported` queda `null` con provenance honesta. `runtime` y
`model_configured` siguen viniendo de la configuración de ejecución. La interfaz común **no** se
modifica: su registro mantiene `session` desde el envelope y `model_reported` honestamente
`null` (la interfaz no lee el store del destino). Verificable: el registro del intento del worker
tiene `session` == id elegido y `model_reported` derivado de la fila (o `null` con provenance);
el esquema cerrado del registro se conserva.

**PD-7 (doble de test fiel que reemplaza al JSON).** Los tests deterministas usan un **SQLite real
chico** con el **esquema observado** (`session_v2` + `session_message`) y cubren las variantes:
`succeeded`, `failed`, `interrupted`, `no-idle` (→ `timeout`), `unknown-schema` (falta
`idle_outcome` → fallo cerrado) y `transport-error` (`rc ≠ 0` sin señal). El binario falso lee el
paquete por **stdin**, registra su argv/invocación y escribe el store SQLite. **Ningún** test lee
la implementación (la frontera del proceso es el binario falso). Verificable: el doble escribe
SQLite (no `sessions.json`); las variantes producen las terminaciones declaradas.

**PD-8 (prueba de integración opcional contra el binario real).** Existe una prueba marcada y
**omitida por defecto**, **habilitada por variable de entorno** (p.ej. `CDAD_OPENCODE_INTEGRATION=1`)
y con el binario y la base de sesiones provistos por configuración. **Lo aislado es CDAD:** la
instalación (`CDAD_INSTALL_ROOT=<tmp>`) y el proyecto son temporales. **El runtime es el real**
que declara la configuración: corre con `--standalone` (servidor privado; **nunca** opera el
servicio de fondo del dueño), no escribe su configuración ni su HOME, y el adaptador lee su base
en solo lectura. Las sesiones que el propio runtime registra en su base son el **efecto declarado**
de una corrida real (las credenciales del runtime viven en esa base: un store vacío no autentica,
discovery §3). Si el binario, la base o la credencial no están disponibles, la prueba **se omite
con diagnóstico** (no fabrica un verde). Verificable: sin la variable, la prueba se omite; con la
variable, corre y correlaciona durablemente la sesión elegida.

**PD-9 (aceptación PD-10 de 005-009 en dos pasos).** (a) **Antes del despliegue:** instalación
aislada de la versión nueva (`CDAD_INSTALL_ROOT` temporal) y **recorrido real**
Claude → `cdad_delegate.py` → OpenCode → `receive` → re-entry sobre un **proyecto temporal**,
corrido por el **orquestador Claude**; (b) **después del despliegue del dueño:** confirmación
corta desde la **instalación global**. Se registra la evidencia (I8 + recibo durable + re-entry).
Verificable: evidencia registrada del recorrido real (paso a) y de la confirmación (paso b); una
prueba que solo llama al script desde un shell **no** demuestra por sí sola la orquestación desde
Claude.

**PD-10 (documentación de la delegación actualizada; sin valores del VPS).**
`references/cli-delegation.md` documenta el contrato de la **señal durable real** (store SQLite en
solo lectura, correlación por `--session`, fallo cerrado por esquema) y los modos de
servidor/permisos. `references/opencode-delegation.md` actualiza la **sección de modo de carga**
(`mode: subagent` es entry no interactiva en la versión instalada; la identidad se verifica desde
la fila durable; sin fallback) y **reemplaza la tabla de modelos obsoleta** por un puntero a la
**única** tabla de modelos (`scripts/cdad-models.sh` + perfil activo), sin nombres de modelo
concretos y sin valores de este VPS. Verificable: las referencias contienen el contrato durable y
el de modo de carga; no contienen rutas absolutas de host, proveedor concreto, modelo concreto ni
servidor.

### 3. Invariantes (verificables)

- **INV-1.** El **orquestador es el único escritor** de `docs/.cdad-state.json`; el adaptador y el
  worker **nunca** lo escriben (criterios de 005-009 conservados).
- **INV-2.** **Un adaptador por destino**: la interfaz común (`cdad_delegate.py`) y el generador
  (`scripts/cdad-generate.py`) **no** se modifican; el cambio se confina al adaptador OpenCode,
  tests y referencias (PD-3, plan fila 6).
- **INV-3.** La base de sesiones se abre **en solo lectura**; el adaptador **nunca** escribe el
  store del runtime ni la configuración del dueño (PD-1/PD-2).
- **INV-4.** **No** se inventan señales de finalización; **no** se promete callback inexistente;
  la espera es **acotada** por `wait.timeout_seconds` y no sondea sin fin (PD-1/PD-5).
- **INV-5.** **`rc=0` / «entregada» no es aprobación de gate**; el recibo es
  `semantic_status: "pending"`; el gate lo decide el responsable en el re-entry (PD-5).
- **INV-6.** **No** hay fallback a un agente genérico no-Cdad (PD-3).
- **INV-7.** **Sin valores de este VPS** en producto ni en contratos públicos: rutas, proveedor,
  modelo concreto, servidor y tiempos se resuelven por configuración de ejecución (local,
  git-ignorada) o flags (PD-4/PD-6/PD-10).
- **INV-8.** Un **proceso/sesión separada NO es un sandbox**; `--auto` auto-aprueba permisos no
  denegados pero **no** aísla; cambiar de CLI **no** garantiza otra familia de modelo.
- **INV-9.** **No** se construye un scheduler, ni instalación automática de CLI, ni un sandbox; **no**
  se implementan todos los destinos; la dirección inversa y otros CLI son incrementos posteriores.
- **INV-10.** **No** cambian el alcance ni los criterios de epic-005; **activar versiones**,
  **cambios en HOME**, la **confianza de carpeta de Claude Code** y la **operación de producción**
  siguen **reservados al dueño** (`execution.md`).

### 4. Criterios de aceptación

- [ ] **PD-1/INV-3/INV-4**: la señal es la base SQLite declarada por config, leída en solo
      lectura y correlacionada por `--session <id>`; la espera es acotada; un `rc=0` temprano **no**
      produce `completed`.
- [ ] **PD-2**: esquema desconocido o archivo ilegible → fallo cerrado con diagnóstico; el
      `UnicodeDecodeError` ya no es una excepción no capturada; sin recibo fabricado.
- [ ] **PD-3/INV-6**: la entry `mode: subagent` publicada **sí** despacha; la identidad se verifica
      desde la fila durable (`cdad-<rol>`); sin fallback genérico; `cdad-generate.py` sin cambios.
- [ ] **PD-4/INV-7**: `--standalone` por defecto; `--server` por config (alternativa); `--auto`
      configurable (activado por defecto) y documentado como no-sandbox; stdin byte-idéntico.
- [ ] **PD-5/INV-5**: `succeeded→completed`, `failed→blocked`, `interrupted→cancelled`, sin
      idle→`timeout`, fallo de transporte→`transport-error`; recibo `pending`; única entrega la
      de `completed`.
- [ ] **PD-6**: `model_reported`/`session` del registro del worker desde la fila durable, con
      provenance; esquema cerrado del registro conservado.
- [ ] **PD-7**: el doble es SQLite real chico con el esquema observado y sus variantes; reemplaza
      al JSON.
- [ ] **PD-8**: la prueba de integración se omite por defecto y se habilita por variable de
      entorno; instalación y proyecto aislados, runtime real con `--standalone`, base leída en
      solo lectura; nunca opera el servicio de fondo ni escribe la configuración del dueño.
- [ ] **PD-9**: recorrido real en dos pasos registrado como evidencia (pre-despacho aislado;
      post-despacho desde la instalación global).
- [ ] **PD-10/INV-7**: `cli-delegation.md` y `opencode-delegation.md` actualizados (señal durable,
      modo de carga, tabla de modelos obsoleta); sin valores de este VPS.
- [ ] **Suite completa verde al cierre** y `make validate` sin fallos nuevos (los FAIL
      preexistentes, si los hay, no se atribuyen a este diff).

### 5. Fuera de alcance

- **Cambiar `scripts/cdad-generate.py`** o el `mode` de los agentes: los roles siguen
  `mode: subagent` (INV-2, decisión del orquestador).
- **Cambiar la interfaz común** `cdad_delegate.py` ni el esquema de salida
  (`{attempt, session, termination, delivery_ref, diagnosis}`).
- **Construir un lector de sesiones de producto / medir contexto**: es 005-002 (pausada); aquí la
  lectura es interna al adaptador para una sola sesión correlacionada.
- **Scheduler**, **instalación automática de CLI** y **sandbox** (INV-9).
- **Implementar todos los destinos** o la dirección inversa; **El** binario legacy no se soporta.
- **Cambios en HOME**, **activación de versiones**, **confianza de carpeta de Claude Code** y
  **operación de producción** (reservado al dueño).
- **Un segundo state del ciclo**, **otro ledger** o reescribir las reglas del paquete (INV-1).

### 6. Contexto técnico (verificado)

**Superficie existente (archivo:línea).**

- **Adaptador OpenCode:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`
  (589 líneas). `:71` `SUPPORTED_LOAD_MODES = frozenset({"all"})`; `:134-159` `_check_load_mode`;
  `:165-181` `_invoke_destination` (argv `[binary, "run", "--agent", agent] (+ --model)`,
  `input=packet_bytes`, sin `--standalone/--auto/--session`); `:187-197` `_read_signal` (lee JSON
  `sessions_db`, captura solo `(OSError, json.JSONDecodeError)`); `:200-209` `_wait_signal`
  (poll 50 ms); `:221-240` `_observation` (`model_reported: None`); `:243-277` `_register_dispatch`
  (I8); `:305-394` `_run_receive`/`_persist_delivery` (`receive`, recibo `pending`);
  `:411-437` `_classify` (status JSON); `:478`/`:508`/`:535`/`:548` uso de `sessions_db`.
- **Interfaz común:** `skills/cdad-cycle/scripts/cdad_delegate.py` (298 líneas). `:48-51`
  vocabulario + claves de salida; `:115-128` `_parse_envelope`; `:131-162` `_run_adapter`
  (subproceso, `PACKET.md` en stdin, `--project-root/--packet-id/--destination[--exec-config]`);
  `:177-193` `_observation` de la interfaz (`model_reported: None`); `:252-283` `delegate()`.
- **Generador (no se toca):** `scripts/cdad-generate.py:391` emite literal `mode: subagent` para
  los roles; `:857` el orquestador `mode: all`. Fuente canónica
  `sources/agents/adapters/opencode.md:14` (roles `mode: subagent`; orquestador `mode: all`).
- **Instalación aislada:** `install.sh:45` `INSTALL_ROOT="${CDAD_INSTALL_ROOT:-${HOME:-}}"`.
- **Doble actual (a reemplazar):** `tests/test_005_009_t2_opencode_adapter.py` — plantilla
  `FAKE_BINARY_SOURCE` escribe `<fake>/sessions.json` (`{session,status,final_text,diagnosis}`).
- **Prueba PD-10 omitida (patrón a reutilizar):**
  `tests/test_005_009_t4_acceptance.py:301-329` (`self.skipTest(...)`).
- **Referencias a actualizar:** `skills/cdad-cycle/references/cli-delegation.md` (líneas
  `:93-104` «adapter must», `:110-117` Configuration); `opencode-delegation.md:18-36` (tabla de
  modelos obsoleta), `:121-167` (origen/versión/reload).

**Superficie durable real de OpenCode v2.0.26 (discovery §3.4-3.5; sondas con `--standalone`,
sin tocar HOME/servidor del dueño).**

- Store SQLite: tablas `session_v2` (relevante: `id, agent, model, time_idle, idle_outcome`) y
  `session_message` (`id, session_id, type, seq, data` JSON; tipos `user`, `assistant`, `system`,
  `idle`, …). `idle_outcome` observado: `succeeded|failed|interrupted|NULL`.
- Correlación: `opencode run --standalone --session <id> --agent <rol> …` → la fila `session_v2`
  lleva **ese** `id`, `agent` y `idle_outcome`. Texto final: último `session_message` `assistant`
  → `data.content[].text` (tipo `text`).
- CLI: stdin transporta el prompt (sin argumento posicional); `--format json` es superficie del
  cliente (no durable); `--standalone` = servidor privado; `--auto` = permisos no interactivos.
- `python3 -c "import sqlite3"` → módulo disponible (v3.46.1): el adaptador puede leer con la
  biblioteca estándar, sin binario externo.

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | Señal durable = store SQLite del runtime, abierto **en solo lectura** (`mode=ro`), papel que denota `sessions_db` (ruta **configurable**). Correlación por `--session <id>` elegido por el adaptador. Campo **opcional** `store` (por defecto `sqlite`); un `store` declarado desconocido falla cerrado. | discovery §4.1 opción A; superficie material y correlación inequívoca; forward-compat sin hardcodear. |
| **D2** | **Fallo cerrado por esquema/contenido**: validar tablas/columnas requeridas; ilegible/desconocido/garbage → `blocked` con diagnóstico; el `UnicodeDecodeError` pasa a fallo diagnosticado. | discovery §3.4/§4.1; el esquema **no** es contrato público (riesgo de epic-005). |
| **D3** | **Modo de carga:** dejar de exigir `mode: all`; exigir el derivado `cdad-<rol>` publicado y verificar la identidad desde la fila durable (`session_v2.agent == cdad-<rol>`), sin fallback; `cdad-generate.py` sin cambios. | discovery §3.2/§4.2 opción A; alinea con la versión instalada sin tocar la generación. |
| **D4** | **Transporte/invocación:** stdin (sin cambios); `--standalone` por defecto; `--server <url>` por config como alternativa; `--auto` por config, activado por defecto, documentado como **no-sandbox**. | discovery §3.3/§3.7/§3.8/§4.3-4.5; evita operar el servicio del dueño; permisos no interactivos. |
| **D5** | **Clasificación** por `idle_outcome`: `succeeded→completed` (con texto final), `failed→blocked`, `interrupted→cancelled`, sin idle→`timeout`; `completed` única entrega; recibo `pending`. | discovery §3.4; PD-5; entrega ≠ gate (INV-5). |
| **D6** | `model_reported`/`session` del registro **del worker** desde la fila durable, con provenance; la interfaz **no** cambia (su `model_reported` honesto `null`). | PD-6; mantiene INV-2 (interfaz/generador intactos); no inventar (provenance). |
| **D7** | **Doble de test** = SQLite real chico con el esquema observado + variantes; reemplaza el JSON `sessions.json`. | discovery §5.1; fidelidad del fixture al runtime real. |
| **D8** | **Prueba de integración opcional** contra el binario real: marcada y omitida por defecto, habilitada por variable de entorno, sobre instalación/store aislados (nunca el del dueño). | discovery §5.2; patrón `test_005_009_t4_acceptance.py:307-326`; PD-8. |
| **D9** | **Aceptación PD-10 en dos pasos** (pre-despacho aislado orquestado por Claude; post-despacho corto desde la instalación global). | plan fila 6; `execution.md` excepción 005-010; PD-9. |
| **D10** | **Documentación:** `cli-delegation.md` (señal durable real + servidor/permisos) y `opencode-delegation.md` (modo de carga; tabla de modelos → puntero a la única tabla, sin nombres concretos). | fila 6; INV-7; regla de inventario R1/R4 (nunca un modelo concreto en la fuente). |

### 8. VERIFY del discovery §8 — estado y resolución propuesta

| # | VERIFY | Estado en el draft | Resolución / dueño y cuándo |
|---|---|---|---|
| A | `run` sin `--standalone` (semántica del servicio de fondo) | **ESQUIVADO por D4** | `--standalone` por defecto; `--server` opcional por config; no se ejercita sin `--standalone`. Se confirma en T4 (integración/aceptación). |
| B | `--auto` en v2.0.26 (auto-rechazo sin `--auto`, evidencia 2.0.16) | **RESUELTO por D4** (propuesta) | `--auto` por config, activado por defecto; se confirma en T4. |
| C | **Texto final cuando el rol usa herramientas** / el idle del padre marca el subárbol | **ABIERTO → riesgo con mitigación** | Se toma el **último** mensaje `assistant` de la sesión correlacionada; si idle `succeeded` sin texto → `blocked` con diagnóstico. Confirmar en T4 (§9 R-C). |
| D | **Estabilidad/versión del esquema** | **RESUELTO por D2** (propuesta) | Validar columnas requeridas y fallar cerrado; **no** depender de un marcador de versión. `unknown-schema` en T1. |
| E | **Gating del `mode`** | **RESUELTO por D3** | El `mode` deja de condicionar la entry; la barrera es la identidad desde la fila durable. Confirmar en T2 + T4. |
| F | Restricciones del id de `--session` (charset/longitud) | **ABIERTO → riesgo con mitigación** | Se genera un id seguro con prefijo `ses_`; se confirma en T4 (§9 R-F). |
| G | **Lectura segura con el servicio vivo** (WAL/SHM) | **ABIERTO → riesgo con mitigación** | `mode=ro`, reintentos acotados dentro de la espera, **nunca** escritura; **no** usar `immutable=1` con el servicio vivo. Confirmar en T4 (§9 R-G). |

### 9. Riesgos con mitigación (cubre VERIFY-C, VERIFY-D y VERIFY-G)

- **R-C (VERIFY-C, medio) — texto final incompleto cuando el rol usa herramientas.** El rol puede
  emitir varios mensajes `assistant` (uno por paso) y el idle del padre podría no reflejar todo el
  subárbol. **Mitigación:** esperar el `idle_outcome` de la **sesión correlacionada** (no del
  subárbol), tomar el **último** `assistant` de esa sesión y, si `succeeded` sin texto, declarar
  `blocked` con diagnóstico (nunca `completed` sin texto). Se confirma en T4 con un rol que use
  herramientas.
- **R-D (VERIFY-D, medio) — el esquema de la base no es contrato público.** Puede cambiar entre
  versiones de OpenCode. **Mitigación:** D2 (validar columnas requeridas, fallar cerrado con
  diagnóstico); no depender de marcador de versión; la variante `unknown-schema` del doble (T1) y
  la prueba de integración (T4) lo cubren.
- **R-G (VERIFY-G, medio) — lectura con el servicio vivo (WAL/SHM).** Abrir en `mode=ro` mientras
  el servicio escribe puede fallar/bloquear. **Mitigación:** `mode=ro` + manejo de
  `sqlite3.OperationalError/DatabaseError` (locked/busy) con reintento **acotado** dentro de la
  espera; **nunca** `immutable=1` con el servicio vivo (enmascararía actualizaciones); **nunca**
  escritura. Se confirma en T4.
- **R-F (VERIFY-F, bajo) — restricciones del id de `--session`.** Charset/longitud no agotados.
  **Mitigación:** id con prefijo `ses_` y alfabeto seguro; validación en T4.
- **R-E (VERIFY-E, bajo) — coexistencia de binarios legacy.** Un binario legacy podría colgar.
  **Mitigación:** D3 + espera acotada (la identidad durable no aparece → `timeout`/`blocked`); el
  binario se toma de config (no de PATH).

### 10. Fronteras y no-cambio de alcance

- **Frontera con 005-009** (interfaz común + adaptador): 005-010 **corrige** el adaptador y su
  contrato durable; **no** crea otra interfaz, otro state ni otro ledger (INV-1/INV-2).
- **Frontera con 005-002** (medición de contexto, pausada): aquí la lectura del store es **interna
  al adaptador** para **una** sesión correlacionada; **no** se construye un lector de sesiones de
  producto.
- **Frontera con 005-004** (roles nativos en Claude Code): el recorrido real usa Claude como
  **coordinador** de un worker externo; **no** da soporte nativo de la metodología a Claude Code.
- **No cambia el alcance ni los criterios del epic-005** (INV-10); activación de versiones,
  cambios en HOME, confianza de carpeta y producción siguen **reservados al dueño**
  (`execution.md`).

### 11. Aprobación

- **Estado: borrador (2026-10-11).** Pendiente de aprobación del **orquestador Claude** bajo la
  excepción HITL de 005-010 (`execution.md`), con las decisiones **D1–D10** de §7 a resolver. El
  architect **no** aprueba su propia propuesta (anti-sesgo).
- **VERIFY de §8**: A/B/D/E resueltos por propuesta (D4/D2/D3); C/F/G quedan como **riesgos con
  mitigación** (§9) y se confirman en T4.
- El `sha256` del archivo materializado vivirá en el `state` (pin `contract_path` +
  `contract_sha256`), no dentro del archivo.

- **Aprobación (2026-10-11):** orquestador Claude, bajo la excepción HITL de 005-010. Se adoptan
  D1–D10. **Enmienda al aprobar:** PD-8 y su criterio se reescriben. El draft pedía un store y una
  credencial aislados, pero el discovery mostró que la credencial del runtime vive en su propia
  base, así que esa exigencia dejaba la prueba siempre omitida. Lo aislado es CDAD (instalación y
  proyecto); el runtime es el real con `--standalone`, sin operar el servicio del dueño ni escribir
  su configuración.
