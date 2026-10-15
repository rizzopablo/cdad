# Discovery — 005-002-session-context-meter

**Rol:** architect (etapa 1, discovery). **Solo lectura.** No se modificó el repo
(`git status` del repo anidado sin cambios; ver §12).
**Contrato:** `docs/epics/epic-005-real-operation/plan.md` (fila 4, `plan.md:36`),
aprobado por Pablo (`plan.md:6-7`). Este documento **no** propone el contrato: eso
es la subetapa *draft*.
**Nota de layout (verificada):** el repo de desarrollo es un repo Git **anidado**;
su raíz es `<repo>` (`git rev-parse --show-toplevel`).
Todas las rutas de este informe son relativas a esa raíz, que es donde el packet
resuelve `docs/epics/...`, `findings/...`, `skills/...`, `scripts/...`, `tests/...`.

---

## 0. Resultado exigido (texto del contrato, `plan.md:36`)

Un **formato de medición neutral respecto del runtime y opcional para la
metodología**, que distinga **observados / estimados / desconocidos**; el
desarrollo sigue aunque el entorno no exponga tokens. **Primer adaptador:** lector
de **solo lectura** de las sesiones de OpenCode que informe, por sesión y por rol:
tokens de entrada/salida, lecturas de archivos, llamadas a herramientas y momento
del primer `resume`. Distingue **contexto cargado por paso, procesamiento
acumulado y costo**. Se aplica a las sesiones de 005-001 y a la sonda 2 de 003-007,
con **salida reproducible**. Muestras: primera sesión de 005-001 y sesión de cierre
de 005-001. Línea base a reproducir: ~12,5 min, 101 llamadas a herramientas, salida
>51 mil caracteres, ~203 mil de entrada reportada en el último paso (caché
incluida).

Riesgo declarado por el epic (`plan.md:55-56`): el esquema de `opencode.db` **no es
un contrato público**; 005-002 debe **fallar cerrado** ante un esquema desconocido.
Advertencia de insumo (`findings/session-guided-start-friction-2026-10-10.md:103-104`):
la sesión del intento 1 está en `session_v2`/`session_message`, **no** en las tablas
legacy `session`/`message`/`part`; un esquema no soportado se diagnostica.

---

## 1. La base de sesiones de OpenCode en ESTA instalación

### 1.1 Ubicación y runtime (verificado)

- **DB:** `~/.local/share/opencode/opencode.db` (SQLite). Tamaño **4,67 GB** + WAL
  de **543 MB** (`ls -la ~/.local/share/opencode/`). El WAL es relevante: la
  apertura read-only no debe checkpoint-ear ni escribir (§11, V10).
- **Runtime real:** `~/.opencode/bin/opencode --version` → **`opencode v2.0.26`**
  (el `opencode` del PATH no resuelve, `which opencode` → vacío). El informe de
  esquema del insumo se hizo con `2.0.26`
  (`findings/session-guided-start-friction-2026-10-10.md:3`).
- **SQLite del host:** `sqlite3 3.46.1` (2024-08-13), usado para todas las sondas
  de este informe con URI `file:...?mode=ro`.
- **Precedente de lectura RO:** `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py:21`
  (`sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)`) y
  `docs/specs/003-003-progress-guards/evidence/t5/recorder.py:35`
  (`DEFAULT_DB = "file:/…/opencode.db?mode=ro"`).

### 1.2 Tablas y esquema actual (verificado con `sqlite_master`)

`__drizzle_migrations`, `migration`, `session_v2`, `session_message`, `session`,
`message`, `part`, `event`, `event_sequence`, `kv`, `project`,
`project_directory`, `workspace`, `worktree`, `account*`, `credential`,
`permission`, `todo`, `session_share`, `session_inbox`, `session_pending`,
`instruction_*`.

**`session_v2`** (una fila por sesión; el esquema actual):
`id`, `project_id`, `workspace_id`, `parent_id`, `fork_session_id`,
`fork_boundary`, `slug`, `directory`, `path`, `title`, `version`, `share_url`,
`summary_additions/deletions/files/diffs`, `metadata`, `cost`,
**`tokens_input`**, **`tokens_output`**, **`tokens_reasoning`**,
**`tokens_cache_read`**, **`tokens_cache_write`**, `revert`, `permission`,
**`agent`**, **`model`**, `time_created`, `time_updated`, `time_compacting`,
`time_archived`, `time_suspended`, **`resume_attempts`**, `time_idle`,
`time_viewed`, **`idle_outcome`**.

**`session_message`** (una fila por mensaje/evento de sesión):
`id`, `session_id` (FK → `session_v2.id`), **`type`**, **`seq`**, `time_created`,
`time_updated`, **`data`** (JSON en texto).

**Legacy (aún presentes):** `session`, `message`, `part` (mismo patrón pero
`part` cuelga de `message_id`). Conteos actuales:
`session=3051`, `message=77552`, `part=331165`, `session_v2=4334`,
`session_message=110997`.

**Versionado de esquema:** no hay columna `schema_version`; el versionado vive en
`__drizzle_migrations` (nombres tipo `20260519…`/`20260227…`) y en `migration`
(`id`, `time_completed`). La forma detectable es la **presencia de columnas**
(`PRAGMA table_info`), no un número (§5).

### 1.3 `session_message.type` — valores presentes (verificado)

`assistant` (98145), `user` (8355), `system` (2010), `idle` (1613),
`synthetic` (450), `agent-switched` (342), `compaction` (57), `model-switched` (21),
`location-switched` (4).

Formas de `data` (verificadas):
- **`assistant`:** `{time:{created,streamed,completed}, agent, model,
  content:[…], snapshot, finish, rawFinish, cost, tokens:{input, output,
  reasoning, cache:{read, write}}}`.
- **`user`:** `{time, text}`.
- **`agent-switched`:** `{time, agent, previous}` (cambio de rol **dentro** de una
  sesión).
- **`model-switched`:** `{time, model, previous}`.
- **`idle`:** `{time, outcome}`.
- **`compaction`:** `{status, reason, summary, recent, time}`.
- **`synthetic`/`system`:** `{text, time[, description]}`.

### 1.4 Partes de contenido de un mensaje `assistant`

`content[]` puede tener `type` ∈ `reasoning` | `text` | `tool`.
Una parte **`tool`** (verificada):
`{type:"tool", id, name, executed, state:{status, input, content, metadata[, error]},
time:{created, ran, completed}}`.
- **Salida de la herramienta:** `state.content = [{type:"text", text:…}]` → el
  tamaño de salida = suma de `len(text)`.
- **Código/estado:** `state.metadata = {status, truncated, exit}`.
- **Error:** `state.error = {type, message}` (p.ej. `tool.execution`).
- El comentario de `recorder.py:16-21` describía `state` sin `error` y timing a
  nivel de parte; hoy **conviven ambas formas** (parte con `time`, `state.error` en
  el caso de error). Es evidencia directa de **deriva de esquema entre versiones**
  (§5, V7).

### 1.5 Rol y modelo (verificado)

- **Rol:** `session_v2.agent` (string: `cdad-orchestrator`, `cdad-architect`,
  `cdad-test-writer`, `cdad-implementer`, `cdad-reviewer`, `cdad-scribe`; también
  roles no-Cdad). El mismo valor aparece en `data.agent` de cada mensaje
  `assistant`. Los subagentes CDAD son **sesiones separadas** con
  `session_v2.parent_id` no nulo. `agent-switched` permite que una sesión
  interactiva cambie de rol en el tiempo (no es el patrón de los paquetes CDAD).
- **Modelo:** `session_v2.model` es un **string JSON** (no un escalar):
  `{"id":"deepseek-v4.1-flash","providerID":"mofgw"[,"variant":"high"]}`. El
  mismo objeto aparece en `data.model` de cada mensaje. En el directorio CDAD hay
  10 formatos distintos (mofgw, openrouter, localhost) — el parser debe
  JSON-parsear con fallback a string.

### 1.6 Tokens, costo, herramientas y lecturas (verificado)

- **Tokens por paso:** `data.tokens = {input, output, reasoning, cache:{read,write}}`
  en cada mensaje `assistant`. **`data.cost`** por mensaje.
- **Tokens acumulados por sesión:** columnas de `session_v2` (`tokens_input`,
  `tokens_output`, `tokens_reasoning`, `tokens_cache_read`, `tokens_cache_write`,
  `cost`). **Son acumulados sobre los pasos, no la ventana de contexto** (el plan
  lo exige distinguir, `plan.md:36`; el insumo lo advierte,
  `findings/session-guided-start-friction-2026-10-10.md:25-27`).
- **Llamadas a herramientas:** partes `type=="tool"` en mensajes `assistant`;
  `name` = herramienta (`read`, `shell`, `glob`, `grep`, `edit`, `write`,
  `execute`, `task`, …); `state.input` = argumentos; `state.metadata.exit`/`status`
  = resultado.
- **Lecturas de archivos:** herramienta `read` con `state.input.path` (en los
  casos observados el campo es `path`; `recorder.py:102-107` acepta también
  `filePath`/`file_path` — a **VERIFY** cuál emite cada versión). `glob`/`grep`
  también leen (con `pattern`/`path`), pero no son `read`.
- **`cache_write`:** presente en el esquema; global suma 6.460.490 (máx 4.600.532),
  pero **en el directorio CDAD `tokens_cache_write>0` = 0 de 496 sesiones** →
  el proveedor `mofgw` no lo reporta (§4).

### 1.7 Momento del primer `resume` (verificado, con matiz)

- La columna `session_v2.resume_attempts` **existe pero vale 0 en toda la DB**
  (`select count(*) … where resume_attempts>0` → 0); `time_idle`/`idle_outcome`
  no registran el `resume` del CLI. La tabla `event` solo tiene
  `message.part.updated.1`, `message.updated.1`, `session.updated.1`,
  `session.created.1` — **sin evento de resume**.
- Por lo tanto el "primer `resume`" del plan es la **invocación del CLI de
  continuidad** (`cdad_continuity.py resume`), observable como **llamada `shell`
  cuyo `command` ejecuta `resume`**. Verificado en la sonda 2: la primera
  invocación real es la **llamada #19**, y su comando ejecuta
  `python3 skills/cdad-cycle/scripts/cdad_continuity.py resume --project-root . …`.
- **Trampa verificada:** la llamada **#10** de esa sesión es
  `cdad_continuity.py resume --help` (ayuda), que **no** es un `resume` real. La
  detección debe excluir `--help` (y análogos) — **V2**.

---

## 2. Recorridos concretos (medidos por sondas propias, read-only)

Se reprodujeron ambas muestras con un script read-only de un solo paso
(`/tmp/opencode/meter_demo.py`), sin escribir en la DB ni en el repo.

### 2.1 Muestra 1 — primera sesión de 005-001

`<ses-107>` · rol `cdad-orchestrator` · modelo
`mofgw/deepseek-v4.1-flash#high` · runtime `2.0.22` · `directory =
<repo-parent>` · `parent_id = null`.

| Medida | Valor medido | ¿Coincide con la línea base? |
|---|---|---|
| Duración (primer→último mensaje) | **12,55 min** | ✅ ~12,5 min |
| Llamadas a herramientas | **101** | ✅ 101 |
| Mayor salida individual | **51.243 car.** | ✅ >51 mil |
| Entrada del último paso (+caché) | **203.276 tok** | ✅ ~203 mil |
| Herramientas por nombre | `shell:72, read:25, execute:1, edit:2, write:1` | — |
| Lecturas `read` | 25 (18 rutas distintas) | — |
| Tokens acumulados (mensajes) | in=210.052 · out=17.585 · reasoning=62.701 · cache_read=11.718.400 · cache_write=0 | — |
| Totales `session_v2` | in=210.175 · out=17.604 · reasoning=62.769 · cache_read=11.718.912 · cache_write=0 · cost=0,229814 | — |
| Primer `resume` del CLI | **ninguno** (la sesión hace el `prepare`, no `resume`) | — |

**Conclusión:** la línea base de la fila 4 es **reproducible** desde la DB con
solo lectura, y la métrica "mayor salida" se computa sobre `state.content[].text`.

### 2.2 Muestra 2 — sonda 2 de 003-007

`<ses-279>` · rol `cdad-orchestrator` · modelo
`mofgw/deepseek-v4.1-flash` · runtime `2.0.22` · `directory` = worktree
desechable · `parent_id = null`.
Coincide con `docs/specs/003-007-living-continuity/dispatch-ledger.md:26` y
`evidence/discovery-probe-2.md:3`.

| Medida | Valor medido |
|---|---|
| Duración | 2,61 min |
| Llamadas a herramientas | 29 (`shell:18, read:9, glob:2`) |
| Primer `resume` del CLI | **llamada #19** (18 llamadas antes) |
| Lecturas `read` | 9 |
| Tokens acumulados | in=96.153 · out=5.701 · reasoning=11.527 · cache_read=1.310.976 · cache_write=0 |
| Mayor salida individual | 51.226 car. |

**Conclusión:** "**18 lecturas de orientación antes de `resume`**"
(`plan.md:37`, `evidence/discovery-probe-2.md:30`) se reproduce como **18 llamadas
de herramienta antes de la llamada #19**; pero de esas 18, solo 9 son la
herramienta `read` (más 2 `glob` y 7 `shell`). **La definición exacta de
"lectura de orientación" no está fijada** — **V1**.

---

## 3. Fronteras (del contrato; no se proponen optimizaciones)

- **005-002 MIDE** (`plan.md:36`): lector read-only + formato neutral. No arranca
  proyectos ni reduce orientación.
- **005-006** = arranque guiado (`plan.md:35`); **005-003** = reducción de lecturas
  previas al `resume`, con base **18** de la sonda 2 (`plan.md:37`). 005-002 es
  insumo de 005-003, no su sustituto.
- Fuera de alcance del epic: CI, ANON-1, R2-STAGE, POLICY-CLASS, comparaciones
  entre modelos (`plan.md:25-27`).

---

## 4. Observado / Estimado / Desconocido en este esquema

**OBSERVADO** (campos leídos directamente, sin inferencia):
- Por mensaje `assistant`: `tokens.{input,output,reasoning,cache.read,cache.write}`,
  `cost`, `time.{created,streamed,completed}`, `agent`, `model`, `finish`.
- Por parte `tool`: `name`, `state.input`, `state.status`, `state.metadata.exit`,
  `state.content[].text` (tamaño de salida), `state.error.type`.
- Por sesión `session_v2`: `agent`, `model`, `parent_id`, `version`, `directory`,
  `time_created`, `time_updated`, columnas `tokens_*`, `cost`, y los totales.
- Eventos: `session_message.type`/`seq`, `agent-switched`, `model-switched`,
  `idle`, `compaction`.
- El **momento del primer `resume`** del CLI (llamada `shell` que ejecuta
  `cdad_continuity.py resume`).

**ESTIMADO** (proxy declarado, no medición independiente):
- **"Contexto cargado por paso"** = `tokens.input + cache.read + cache.write` del
  paso (el plan ya lo llama "proxy" del máximo; el insumo,
  `findings/session-gu…-2026-10-10.md:21,25-27`). No es la ventana de contexto.
- **"Lecturas de orientación antes del `resume`"**: clasificación de llamadas; su
  definición precisa no está fijada (**V1**).
- Cualquier **conversión bytes→tokens**: prohibida (`cdad_continuity.py:29-31`
  "Bytes are never converted into tokens and no limit is fabricated").

**DESCONOCIDO** (debe declararse, nunca fabricarse):
- **`cache_write` cuando el proveedor no lo reporta.** En CDAD `mofgw` reporta 0 en
  las 496 sesiones → 0 puede significar "no reportado", no "cero real" (**V5**).
- **La ventana de contexto real** y los tokens **no expuestos** por un runtime
  distinto de OpenCode (p.ej. Claude Code) — el formato debe seguir y marcar
  `unknown`.
- **Sesiones sin `resume`** (p.ej. Muestra 1): "primer resume" = *no aplica*; debe
  informarse como desconocido/ausente, no inventarse.
- Semántica de `session_v2.resume_attempts`/`time_idle`/`idle_outcome` (siempre
  0/null; ¿son del `resume` de OpenCode y están sin uso? **V4**).

---

## 5. Fallar cerrado ante un esquema desconocido (requisito del epic)

Evidencia que habilita el fail-closed:
- **No hay `schema_version`** en las tablas; el versionado está en
  `__drizzle_migrations`/`migration` y, sobre todo, en la **forma de las tablas**
  (`PRAGMA table_info`). La detección debe ser por **columnas requeridas**
  presentes (p.ej. `session_v2.tokens_input`, `session_message.data`,
  `session_message.type`) y por el **tipo de las filas** (`assistant`/`tool`).
- **La deriva ya ocurrió**: `recorder.py:16-21` documenta una forma de `state` sin
  `error`; hoy `state.error` existe en el caso de error. Un lector que asuma una
  forma fija se rompe en silencio.
- **Prohibición de inventar números**: precedente exacto en `cdad_continuity.py:29-31`
  (bytes nunca se convierten a tokens; sin límite fabricado; `unknowns[]` explícito).

**Comportamiento exigido por el epic (a especificar en draft, no ahora):** ante un
esquema no reconocido → **diagnóstico nombrando el faltante** y **ningún número**
(no `0`, no vacío ambiguo), rc≠0; y nunca fabricar métricas.

---

## 6. Dónde vive la metodología (para que la medición sea OPCIONAL y NEUTRAL)

Estructura verificada del repo:
- **Documento de registro:** `CDAD_metodologia.md` (153 KB; TOC en
  `CDAD_metodologia.md:21-37`). No se carga por defecto; es consulta.
- **Skill del ciclo:** `skills/cdad-cycle/SKILL.md` + `skills/cdad-cycle/references/*.md`
  (carga bajo demanda) + `skills/cdad-cycle/assets/*.schema.json` + scripts en
  `skills/cdad-cycle/scripts/`.
- **Fuentes de roles:** `sources/roles/*.md` (los agentes son salida declarada de
  `scripts/cdad-generate.py`; ver `Makefile:1-6`).
- **Política de rutas:** `docs/cdad-policy.json` (`documentation_roots=docs`,
  `implementation_roots=[agents,skills,scripts,sources,build]`, `test_roots=tests`).

**Puntos de extensión candidatos (sin proponer la solución):**
- **Formato neutral:** un *schema asset* nuevo bajo
  `skills/cdad-cycle/assets/*.schema.json` (convención: `run-evidence.schema.json`,
  `guard-trace.schema.json`, etc.), p.ej. `context-meter.schema.json`.
- **Definición/procedimiento (observado/estimado/desconocido):** un *reference*
  nuevo bajo `skills/cdad-cycle/references/` (convención `*.md`, no cargado por
  defecto → **opcional**).
- **Adaptador OpenCode:** script bajo `skills/cdad-cycle/scripts/` (canónico) con
  **wrapper fino** en `scripts/` (convención verificada en
  `scripts/cdad_continuity.py:10-11`: `runpy.run_path(CANONICAL, …)`).
- **Instalación:** `install_skills()` (`install.sh:1036`) despliega el directorio
  de la skill (el script viaja con ella). `install.sh` es `implementation_files`
  del packet.
- **Tests:** `tests/` (convención `test_<feature>_t<n>_<tema>.py`; el CLI se
  invoca por el wrapper: `tests/test_003_004_t1_resume.py:80`).

**Cómo queda OPCIONAL:** el formato/procedimiento vive en un reference y un schema
que **no** se enganchan en los gates (`prepare`, `validate-state`, `validate-request`,
review, merge). El ciclo no debe exigirlo: se invoca a demanda para medir, igual
que hoy `cdad_continuity.py resume` es una herramienta que el orquestador usa
cuando corresponde. La fila 4 lo pide explícitamente ("opcional para la
metodología").

**Cómo queda NEUTRAL respecto del runtime:** separar (a) el **registro neutral**
(por sesión/rol: observado/estimado/desconocido, sin nombres de tablas) de
(b) los **adaptadores** por runtime (OpenCode primero). El registro neutral no
depende de `opencode.db`; el adaptador traduce.

---

## 7. Forma de la salida reproducible

Convenciones verificadas que acotan la forma:
- **JSON como único modo de salida** (`cdad_continuity.py:66` "JSON is the only
  output mode"); `--json` es no-op aceptado.
- **Determinismo** exigido a los artefactos CDAD (el `recorder.py` canonicaliza
  argumentos para que llamadas idénticas den bytes idénticos, `recorder.py:12-14`).
- **Python stdlib only** (`README.md:3-4`, `cdad_continuity.py:69`).

Contenido mínimo que la salida reproducible debe poder citar como evidencia
(antes/después de 005-003, criterio 3 del epic `plan.md:48-49`):
- **Identidad del run:** ruta de la DB (o su hash), versión del runtime, resultado
  de la **detección de esquema** (reconocido/no reconocido).
- **Por sesión:** `session_id`, rol (`agent`), modelo (parseado), `parent_id`,
  runtime `version`, `directory` (o hash, por privacidad), ventana temporal.
- **Por rol (agregado):** sumas y distribuciones (tokens in/out, llamadas,
  lecturas, primer `resume`).
- **Tres cubos explícitos:** `observed`, `estimated`, `unknown` (nunca mezclados).
- **Distinción de las tres magnitudes:** *contexto por paso* (proxy máximo),
  *procesamiento acumulado* (suma de pasos) y *costo*.
- **Momento del primer `resume`** (o `unknown`/`n-a` si no hubo).

---

## 8. Sesiones concretas a medir (identificadores)

Deducibles de la DB (verificado), no solo del registro local:
- **005-001, primera sesión:** `<ses-107>` (coincide con la
  línea base; §2.1).
- **003-007, sonda 2:** `<ses-279>` (coincide con
  `dispatch-ledger.md:26`; §2.2).
- **005-001, sesión de cierre:** **no queda pinneada en el repo.** Candidatas por
  métricas: `<ses-317>` (205 llamadas; 7 hijas) y
  `<ses-318>` (17 hijas). Ninguna coincide con "13
  subagentes" (`plan.md:36`) — **V6**.
- La primera sesión de 005-001 y la sonda 2 están **solo** en
  `session_v2`/`session_message` (0 filas en legacy `session`), confirmando el
  insumo.

---

## 9. Convenciones aplicables (verificadas)

- Python **stdlib only**; sin servicios ni agentes permanentes
  (`cdad_continuity.py:69`, `README.md:3-4`).
- **Wrapper fino** en `scripts/` sobre el canónico en `skills/cdad-cycle/scripts/`
  (`scripts/cdad_continuity.py:10-11`).
- **JSON only** y `--json` no-op (`cdad_continuity.py:66-67`).
- **Fail-closed** y `unknowns[]` explícito, sin fabricar límites
  (`cdad_continuity.py:29-31,55-58`).
- **Read-only** con URI `?mode=ro` (precedentes en §1.1).
- **Path policy** única en `docs/cdad-policy.json` (usada por `cdad_continuity.py:60-64`).
- Schemas en `skills/cdad-cycle/assets/*.schema.json` (draft 2020-12; ver
  `run-evidence.schema.json:1-2`).

---

## 10. Riesgos

- **R1 (del epic):** `opencode.db` no es contrato público; puede cambiar entre
  versiones (`plan.md:55-56`). Mitigación exigida: detección de esquema + fail
  cerrado (§5).
- **R2 (del epic):** una sola sonda por variante → medición **indicativa, no
  estadística** (`plan.md:57`). El formato debe declarar la muestra, no un promedio.
- **R3 (privacidad):** la DB contiene **rutas absolutas, prompts y salidas de
  herramientas** que pueden incluir datos privados (el insumo lo señala,
  `findings/session-gu…-2026-10-10.md:61-64,117-118`). La salida debe **omitir o
  hashear** rutas/identificadores; regla general de anonimización del workspace.
- **R4 (tamaño):** DB de 4,67 GB + WAL de 543 MB; lecturas deben ser **acotadas**
  (por sesión/ventana) y nunca escribir/checkpoint-ear (§11, V10).
- **R5 (ambigüedad de métrica):** "lectura de orientación" y "momento del resume"
  no están definidos de forma cerrada → riesgo de números no reproducibles
  (**V1/V2/V3**).
- **R6 (neutralidad):** si el adaptador filtra nombres de tablas al registro
  neutral, el formato deja de ser neutral respecto del runtime.

---

## 11. Elementos abiertos a VERIFY

- **V1.** Definición cerrada de **"lectura de orientación antes del `resume`"**
  (¿solo `read`? ¿`read`+`glob`+`grep`? ¿toda llamada de herramienta?). En la
  sonda 2: 18 llamadas antes de #19, de las cuales 9 son `read`.
- **V2.** Distinguir un **`resume` real** de `resume --help`/lecturas de
  documentación (la sonda 2 tiene `--help` en #10).
- **V3.** Enumerar las **formas de invocación** del CLI instalado (canónico
  `…/skills/cdad-cycle/scripts/cdad_continuity.py`, wrapper `scripts/…`, alias
  `cdad-continuity`). Confirmar cuál emite la versión instalada.
- **V4.** Semántica real de `session_v2.resume_attempts`, `time_idle`,
  `idle_outcome` (hoy 0/null; ¿sin uso?).
- **V5.** Semántica de `cache_write`: distinguir "no reportado" (mofgw → 0) de
  "cero real". Debe mapear a `unknown`, no a `0`.
- **V6.** Identificar la **sesión de cierre de 005-001** ("13 subagentes", ~4 h,
  máx ~310 mil) — no pinneada en el repo.
- **V7.** Definir el conjunto de **columnas/tipos requeridos** para declarar el
  esquema "reconocido" y cómo diagnosticar la deriva (`recorder.py:16-21` vs forma
  actual).
- **V8.** Confirmar que en los paquetes CDAD **una sesión = un rol** (rol por
  `session_v2.agent`) y que `agent-switched` no aplica al flujo de paquetes.
- **V9.** Sesiones **solo-legacy** (3051 en `session`, 77552 `message`, 331165
  `part`): ¿el adaptador las soporta o falla cerrado declarándolas no soportadas?
- **V10.** Lectura RO segura con WAL grande (4,67 GB + 543 MB): acotar consultas,
  no checkpoint-ear, no bloquear.
- **V11.** Nombre exacto del campo de ruta de `read` por versión
  (`path` vs `filePath` vs `file_path`; `recorder.py:102-107`).
- **V12.** Forma del registro neutral y dónde vive (schema asset + reference) y su
  no-enganche en gates (decisión de la subetapa draft).

---

## 12. Evidencia de ejecución (comandos, sin modificar el repo)

- `git -C cdad rev-parse --show-toplevel` → `<repo>`.
- `git -C cdad status` → única modificación: `docs/.cdad-state.json` (preexistente,
  **no** tocada por este discovery; el architect no escribe).
- `~/.opencode/bin/opencode --version` → `opencode v2.0.26`.
- `sqlite3 "file:$HOME/.local/share/opencode/opencode.db?mode=ro" "select sql from
  sqlite_master where name='session_v2'"` (y `session_message`, `session`, `message`,
  `part`, `event`, `kv`) → esquemas de §1.2.
- `sqlite3 … "select type,count(*) from session_message group by type"` → §1.3.
- `sqlite3 … "select … from session_v2 where directory like '%projects/cdad%'"` →
  rol/modelo/tokens/versión por sesión.
- `python3 /tmp/opencode/meter_demo.py` → métricas de §2 (Muestras 1 y 2),
  reproduciendo la línea base.
- `python3 /tmp/opencode/final_probe.py` → comando completo de las llamadas #19,
  #20 y #23 de la sonda 2 (`cdad_continuity.py resume/reconcile`).
- `git -C cdad check-ignore`/`ls-files findings/` → `findings/` está **trackeado**
  (los insumos son archivos reales del repo).

**Archivos del repo modificados por este discovery: ninguno.** El único archivo
escrito es el de transporte `/tmp/opencode/discovery-005-002.md` (fuera del repo,
según ADR-011). **Commit: n/a** (rol read-only, write_scope vacío).
