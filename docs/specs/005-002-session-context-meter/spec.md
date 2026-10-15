> Spec **en borrador** (2026-10-11), texto del **architect** (subetapa `draft`, etapa 2) para su
> materialización por el orquestador (ADR-003). **NO aprobada**: el architect no aprueba su propia
> propuesta (anti-sesgo); la decisión es del orquestador/usuario. **Ronda acotada de corrección
> (draft-002)**: corrige C1–C5 sobre el draft 001 (recibido, materializado y revisado); el resto del
> draft 001 se conserva íntegro. Insumo verificado e **intacto**:
> `docs/specs/005-002-session-context-meter/discovery.md` (mapa archivo:línea + sondas read-only;
> no se repite; **no se reescribe**). Insumo obligatorio del dueño:
> `docs/specs/005-002-session-context-meter/draft-inputs-2026-10-11.md`. Contrato:
> `docs/epics/epic-005-real-operation/plan.md` (fila de orden 7, `:40`, y sección «Ajuste de los
> ciclos pendientes — decisión del dueño, 2026-10-11», `:45-85`, que prevalece sobre una lectura más
> estrecha de la fila). Dirección de fondo:
> `findings/agent-operation-strategy-2026-10-11.md`. Formato de referencia:
> `docs/specs/005-010-real-opencode-delegation/spec.md`. **Sin valores de este VPS** en producto ni en
> contratos publicables: la prohibición cubre **rutas del host, ruta del store, nombres de proveedor y
> de modelo e identificadores de sesión**; el **tamaño del store** y los **agregados** ya publicados
> en el discovery y en el plan del epic se citan **por referencia**, sin agregar valores nuevos
> (INV-7/PD-10).

## Spec — 005-002-session-context-meter

**Feature ID:** `005-002-session-context-meter` · **Epic:** `epic-005-real-operation` ·
**Estado:** borrador (2026-10-11).

```yaml
feature_id: 005-002-session-context-meter
feature_name: Formato de medición neutral de contexto, opcional, con primer lector OpenCode read-only
created_at: 2026-10-11
status: approved
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-11
```

### 1. Descripción funcional

El resultado **no es un motor de evaluación de sesiones, ni un dashboard, ni un scheduler**: es un
**formato de medición neutral respecto del runtime y opcional para la metodología**, que distingue
datos **observados, estimados y desconocidos**, más su **primer adaptador**: un lector de **solo
lectura** de las sesiones de OpenCode que informa, **por sesión y por rol**, tokens de
entrada/salida, lecturas de archivos, llamadas a herramientas y el momento del **primer `resume`**.
La medición es **opcional**: el desarrollo sigue aunque el entorno no exponga tokens (plan fila 7).
El registro neutral es el **contrato**; el adaptador **traduce** y es el único que conoce los
nombres de tablas/columnas del runtime (neutralidad; R6).

El **delta del dueño (2026-10-11)** amplía el resultado con la **orientación y el resultado**, no
solo el volumen de tokens: medir para mejorar resultados, contexto y atención humana; menos tokens o
una sesión que termina antes no demuestran mejora si no entregó lo necesario. En consecuencia la
medición:

1. **Conserva** el formato neutral, el lector OpenCode read-only y la distinción
   observado/estimado/desconocido.
2. **Distingue dos hitos separados y observables**: (a) el **primer `resume`** del CLI de
   continuidad y (b) el **primer despacho de trabajo de rol** cuando la traza lo permita. Excluye
   llamadas de ayuda (`--help` y análogos), distingue **sesión nueva de reanudada** y, si el evento
   **no existe** en la sesión, lo informa como **ausente/desconocido**, no lo inventa. Un despacho
   **no prueba** utilidad ni resultado aceptado, y **no se infiere** un despacho exitoso solo porque
   el texto del comando lo menciona.
3. **Expone las medidas de orientación** junto a los hitos: **tiempo hasta cada hito**, **llamadas
   y lecturas previas**, **volumen de salidas** (total y máximo) y **input por paso, acumulado y
   caché** con su semántica, reusando los datos ya relevados, con **unidades, intervalo y
   procedencia** declarados.
4. **Separa tres magnitudes** que el plan exige no confundir: *contexto cargado por paso*
   (**proxy declarado** = `input + cache.read + cache.write` del paso, **no** la ventana real),
   *procesamiento acumulado* (suma de pasos) y *costo*.
5. **Vincula métricas con resultado/evidencia** mediante un **informe de aplicación**: una
   **anotación referenciada por el orquestador** que declara un límite (entrega aceptada / bloqueada
   / pendiente / desconocida según el registro disponible). **No** es una nueva clasificación
   semántica del lector ni una aprobación automática. Al combinar coordinador y workers **no suma
   dos veces** el mismo costo: declara **qué sesiones** están incluidas y **qué relaciones** se
   observaron; los enlaces entre CLI **no verificables** quedan `unknown`.
6. **No equipara** input reportado con consumo facturado ni con capacidad máxima de contexto; un
   costo nulo o no reportado **no** demuestra gratuidad.

Dos hechos verificados del discovery definen el diseño y lo endurecen:

- **La deriva de esquema ya ocurrió.** El comentario de un lector previo documentaba una forma de
  `state` **sin** `error`; hoy `state.error` existe en el caso de error
  (`discovery §1.4, §5`). Un lector que asuma una forma fija se rompe **en silencio**. Por eso el
  adaptador **falla cerrado** ante un esquema desconocido, y **nunca fabrica métricas** (precedente
  exacto: `skills/cdad-cycle/scripts/cdad_continuity.py:29-31` — bytes nunca se convierten a tokens;
  sin límite fabricado; `unknowns[]` explícito).
- **`cache_write` no es un cero real.** El proveedor configurado **no lo reporta**: en el directorio
  CDAD `tokens_cache_write > 0` = **0 de 496 sesiones** medidas (`discovery §1.6, §4`). Un `0` ahí
  puede significar «no reportado», no «cero real» → `unknown`, nunca `0`.

La medición es **opcional para la metodología**: el formato y el procedimiento viven en la skill
(**schema asset + reference**) y **no se enganchan en los gates** (`prepare`, `validate-state`,
`validate-request`, review, merge). El ciclo no los exige; se invocan a demanda para medir, como hoy
el CLI de continuidad se usa cuando corresponde (plan fila 7: «opcional para la metodología»).

**Frontera de la unidad (delta punto 7).** Clasificar **repeticiones innecesarias de suites**,
**fricción de permisos**, **correcciones tras review** e **intervenciones humanas** exige **juicio**
→ **no se atribuye al parser**. El análisis cualitativo se separa del instrumento determinista y
queda **fuera del primer incremento** (o como anotación declarada). Quedan fuera de alcance: motor de
evaluación de sesiones, dashboard, scheduler, plataforma de usabilidad, espera improductiva,
cuotas/ETA y calidad semántica.

### 2. Contrato

**Registro neutral (runtime-agnostic; el contrato).** El adaptador emite **un documento JSON**
(`contract: context-meter-v1`) con la forma:

- `schema_version`: **1** — versión del **registro neutral** (distinta de la ausencia de
  `schema_version` en la **fuente**, §PD-2).
- `meter`: `"context-meter-v1"`.
- `run`: `{ store_ref, runtime_version, schema: "recognized"|"unknown" }` — `store_ref` es la
  referencia **hasheada/omitida** al store (privacidad); `runtime_version` es la versión observada.
- `window`: `{ criterion, start_ref, end_ref, cutoff }` — la **ventana y el corte usados**,
  explícitos y reproducibles (PD-5).
- `sessions[]`: por sesión `{ session_ref (hasheado), role, model (parseado o unknown), parent_ref,
  runtime_version, window, milestones { first_resume, first_dispatch }, measures, buckets
  { observed, estimated, unknown } }`.
- `roles[]`: **agregado por rol** `{ role, sums, distributions }` (sumas y distribuciones).
- `application` (**opcional**): anotación referenciada (PD-9), no producida por el juicio del parser.
- `unknowns[]`: causas explícitas de lo no observable.

**Claves requeridas del registro neutral (contrato observable; C2).** El **esquema neutral es el
contrato** y el adaptador **solo traduce**. Las claves se nombran **sin** tablas/columnas del
runtime (neutralidad). **Obligatorio** = el documento **no** valida contra el asset si falta;
**opcional** = puede omitirse.

- **`milestones`** (**obligatorio**; por sesión/tramo). Dos hitos, ambos como **clave presente**
  (aunque uno quede ausente/desconocido): `first_resume` y `first_dispatch`. Por hito:
  - `status` (**obligatorio**) ∈ `observed | absent | unknown` — si está observado o ausente/desconocido.
  - `position` (**obligatorio si `status=observed`**): **posición en la traza** del tramo (índice de
    llamada/mensaje y su `seq`).
  - `time_relative` (**obligatorio si `status=observed`**): **tiempo relativo** al inicio del tramo
    (en minutos).
  - `cause` (**obligatorio si `status ∈ {absent, unknown}`**): causa observable de la ausencia.
- **`measures`** (**obligatorio**; por sesión/tramo). Cada medida es
  `{ value, unit, provenance, bucket }` con `unit` (**obligatorio**), `provenance` (**obligatorio**;
  de dónde sale el dato) y `bucket` (**obligatorio**; ver la regla de cubos). `value` puede ser
  `null` → `unknown` con causa. Claves mínimas requeridas:
  - `time_to_first_resume`, `time_to_first_dispatch` — **minutos**; procedencia: tiempos del
    registro, relativo al inicio del tramo.
  - `previous_calls` — **conteo**; llamadas de herramienta previas al hito.
  - `previous_reads` — **conteo**; llamadas `read` previas al hito.
  - `total_output` — **caracteres Unicode** (suma de `len(text)` de la salida de herramienta).
  - `max_output` — **caracteres Unicode** (mayor salida individual).
  - `input_per_step` — **tokens** (por paso; lista/distribución declarada).
  - `accumulated` — **tokens** (suma de pasos).
  - `cache` — **tokens** (`cache.read` observado; `cache.write` **`unknown`** cuando el proveedor
    no lo reporta).
  Unidad y procedencia de cada una son **obligatorias**; el valor puede ser `null` → `unknown`.
- **`buckets`** (**obligatorio**): `{ observed, estimated, unknown }`. **Regla de asignación**
  (**obligatoria y explícita**): cada métrica vive en **exactamente uno** de los tres cubos —
  `observed` = leído **directamente** del registro (tokens reportados, `cost` reportado, conteos de
  llamadas, posiciones, tiempos, tamaño de salida); `estimated` = **proxy declarado** (contexto
  cargado por paso = `input + cache.read + cache.write`, **no** la ventana real); `unknown` =
  nulo/ausente/no reportado **con causa**, **nunca** `0`. El asset declara la regla y los tests la
  verifican (ninguna métrica aparece en dos cubos).

**Reglas del contrato neutral.**
- **Sin nombres de tablas/columnas del runtime** en el registro neutral: `session_v2`,
  `session_message`, etc. aparecen **solo** en el adaptador (PD-1).
- **Cubos explícitos** `observed` / `estimated` / `unknown`, **nunca mezclados**: una métrica vive en
  **exactamente uno** (PD-1; regla de `buckets`).
- **Un valor nulo/ausente/no reportado → `unknown` con causa**, nunca `0` (PD-4).
- **Sin conversión bytes→tokens** y **sin límite de contexto fabricado** (PD-3).
- **JSON como único modo de salida**; `--json` es no-op aceptado (PD-11).

**Superficie de invocación del medidor (contrato observable; C1).** Los tests invocan
**`scripts/cdad_context_meter.py`** (el **wrapper fino**; el canónico es
`skills/cdad-cycle/scripts/cdad_context_meter.py`). La interfaz es **mínima** — **sin** motor de
reportes, **sin** dashboard, **sin** scheduler:

- **(a) Store de sesiones.** Flag explícito `--store PATH`. Si se omite, se resuelve de una **fuente
  de config/entorno declarada como tal**: la variable de entorno `CDAD_CONTEXT_METER_STORE`. Si
  **ni** el flag **ni** la variable están presentes → **fallo cerrado** con diagnóstico que
  **nombra el insumo faltante** y `rc != 0`. **Nunca** una ruta **hardcodeada** y **sin valores de
  este VPS**.
- **(b) Sesiones a medir.** `--session REF` (**repetible**: **una o varias**). **Modo acotado:**
  `--limit N` (mide como máximo `N` sesiones del store cuando **no** se da `--session`; `N` con
  **default declarado** `20`; `--limit 0` → no mide ninguna y **falla cerrado**). La selección es
  **explícita y acotada** (nunca un barrido sin límite).
- **(c) Corte.** `--idle-threshold MINUTES` (**umbral de inactividad**; **default declarado**:
  `60` minutos). Es el umbral del corte de tramo (PD-5).
- **(d) Salida.** **JSON por stdout**; `--json` se **acepta como no-op** (PD-11).
- **(e) Códigos de salida.** `0` en **éxito**; `rc != 0` en el **fallo cerrado**, con el
  **diagnóstico por stderr** (PD-2).

**Piezas que quedan para la implementación (declarado).** El contrato **no** fija: los **nombres
internos** de funciones/clases/módulos, el **texto exacto** del diagnóstico (solo que **nombre** el
elemento faltante), el **SQL** concreto, ni la **precedencia fina** de resolución del store más allá
de lo declarado (**flag → variable de entorno → fallo cerrado**). El contrato **no** las necesita
porque los tests observan **comportamiento** (flags aceptados, JSON por stdout, `rc`, diagnóstico que
nombra), no la estructura interna.

**Superficie que 005-002 toca (sin motor nuevo, sin otro state):**

- **Nuevo (producto, fuente canónica):**
  `skills/cdad-cycle/scripts/cdad_context_meter.py` — el **adaptador OpenCode** + emisor del
  **registro neutral**: lector SQLite en **solo lectura** (`?mode=ro`), detección de esquema por
  **columnas requeridas + tipos de fila** (fallo cerrado), hitos, medidas y anotación.
- **Nuevo (producto, wrapper fino):** `scripts/cdad_context_meter.py` — `runpy.run_path(CANONICAL, …)`
  (convención verificada: `scripts/cdad_continuity.py:10-11`).
- **Nuevo (metodología, formato neutral):** `skills/cdad-cycle/assets/context-meter.schema.json`
  (draft 2020-12; convención `run-evidence.schema.json`, `guard-trace.schema.json`).
- **Nuevo (metodología, procedimiento):** `skills/cdad-cycle/references/context-meter.md` (convención
  `*.md`, **no** cargado por defecto → **opcional**).
- **Nuevo (tests):** `tests/test_005_002_t1_neutral_record.py`,
  `tests/test_005_002_t2_milestones.py`, `tests/test_005_002_t3_application_privacy.py`,
  `tests/test_005_002_t4_acceptance.py`.
- **Sin cambios:** los gates (`prepare`, `validate-state`, `validate-request`, review, merge), el
  state (`docs/.cdad-state.json`), el esquema I8, el CLI de continuidad, el generador de agentes,
  `install.sh` (el directorio de la skill **viaja** con `install_skills()`; el script canónico, el
  asset y el reference no requieren cambio de instalador), `docs/cdad-policy.json`.

**Postcondiciones (numeradas y verificables).**

**PD-1 (registro neutral, sin nombres del runtime, con cubos explícitos).** El adaptador emite un
**registro neutral** por sesión y **agregado por rol** que **no contiene nombres de tablas/columnas**
del runtime y que separa **`observed` / `estimated` / `unknown`** de forma explícita; ninguna métrica
aparece en dos cubos. El **esquema neutral es el contrato**; el adaptador **solo traduce**.
Verificable: el asset `context-meter.schema.json` declara los tres cubos y la **regla de asignación**;
el documento emitido para una sesión conocida valida contra el asset; `session_v2`/`session_message`
aparecen **solo** en el adaptador (grep sobre asset y reference: ausentes); el agregado por rol
existe.

**PD-2 (fallo cerrado ante esquema desconocido, con diagnóstico nombrado y SIN número).** El
adaptador valida el esquema de la fuente por **columnas requeridas** (`PRAGMA table_info`) y por el
**tipo de las filas** (`assistant`/`tool`), **nunca** por un marcador de versión (la fuente **no**
tiene `schema_version`). Si falta una columna/tipo requerido, **falla cerrado**: `rc != 0`, un
**diagnóstico que nombra el elemento faltante** (por **stderr**), y **ningún número** de métrica (ni
`0` ni vacío ambiguo). Verificable: contra un store fixture con una columna requerida ausente, la
salida es un diagnóstico que la nombra con `rc != 0` y **sin** campos numéricos de métrica; un store
válido produce métricas; el error **no** es una excepción no capturada.

**PD-3 (sin métricas fabricadas).** Ningún campo **convierte** bytes/caracteres a tokens; **ningún
límite de contexto/ventana** se fabrica; donde una magnitud no puede observarse, queda `unknown` con
causa. Verificable: el adaptador no contiene constante/razón de conversión; el registro no porta un
`context_limit` derivado del input; `unknowns[]` nombra la causa.

**PD-4 (`cache_write` y semántica de nulo/ausente: desconocido, nunca cero).** Un campo de tokens o
costo que el proveedor **no reporta** (p. ej. `cache_write`, que es 0 en **todas** las sesiones CDAD
medidas, o un `cost` nulo) se informa como **`unknown` con causa**, **nunca** como `0` ni como
«gratuito». El **input reportado no se equipara** con consumo facturado ni con capacidad máxima de
contexto. Verificable: para la muestra del proveedor que no reporta, `cache_write` es `unknown`
(**no** `0`); un `cost` nulo es `unknown`; el registro declara que input reportado ≠ facturado ≠
capacidad máxima.

**PD-5 (corte explícito y reproducible; borde del tramo y «último paso» fijados).** La
**ventana/corte** de cada medición es **explícita** y reproducible desde el store **por sí solo**.
Para reproducir la línea base, la ventana es el **primer tramo contiguo** de la sesión. **Criterio
del borde (cerrado, sin ambigüedad; la elección cambia el número pinneado):**

- **Qué mensajes entran:** los mensajes/eventos de la sesión ordenados por `seq`/tiempo; el **primer
  tramo** arranca en el **primer** mensaje de la sesión.
- **Cómo se cuenta la brecha:** la **inactividad** entre dos mensajes consecutivos = diferencia entre
  el **inicio** del siguiente y el **fin** (`time_updated`) del anterior; el tramo **cierra** en el
  **primer** intervalo **mayor** que `--idle-threshold` (default `60` min).
- **Dónde cierra el tramo:** en el **último mensaje anterior a la brecha**. El **«último paso»** es
  ese **último mensaje del tramo** — el mensaje `assistant` que **cierra** el tramo, que puede **no**
  tener llamada de herramienta propia; el tramo cierra en el evento `idle` con `outcome succeeded`
  que **precede** a la brecha.
- **Qué pasa si no hay brecha:** sin brecha > umbral, **toda** la sesión es **un solo tramo**
  (sesión completa = tramo).
- **Sin promediar:** las métricas se reportan **por tramo**; nunca se promedian tramo y sesión.

**Borde fijado (la PRIMERA definición es la usada).** La **ventana** del tramo = **primer
`time_created` → último `time_updated` del tramo**; el **proxy del último paso** = `input +
cache.read + cache.write` de ese **último mensaje del tramo**. Para la muestra 1 esto da **12,55 min**
(12,5471) y **203.276 tok** (`input` 1.164 + `cache.read` 202.112). **La otra definición NO es la
usada** y se hace **visible**: si el borde se tomara en el **último mensaje CON llamada de
herramienta**, el resultado sería **12,40 min** y **202.222 tok**. Verificable: la muestra 1 bajo el
corte declarado → **12,55 min**, **101 llamadas**, mayor salida **51.243 car.**, proxy del último paso
**203.276 tok**; el último paso es el mensaje que **cierra** el tramo (sin llamada de herramienta
propia) y el cierre es el `idle` `succeeded` previo a la brecha de ~66,4 h; medida sobre **toda** su
extensión la **misma** sesión **no** coincide (**121** llamadas) y esa diferencia se **muestra**; la
muestra 2 bajo el corte → primer `resume` = llamada **#19**.

**PD-6 (dos hitos separados: primer `resume` y primer despacho).** El registro reporta **dos hitos
distintos**: (a) **primer `resume` real** del CLI y (b) **primer despacho de trabajo de rol**
observable en la traza. Cada uno es **observado** (posición/paso y tiempo) o **ausente/desconocido
con causa**; **nunca** se confunden entre sí. Se **excluyen** las llamadas de ayuda (`--help`/`-h` y
análogos) y se distingue **sesión nueva de reanudada**. Un despacho **no** se infiere exitoso por el
texto del comando: es un **evento registrado**, no prueba de utilidad ni de resultado aceptado.
Verificable: muestra 2 → primer `resume` en la llamada **#19**; el `resume --help` de la llamada
**#10** **no** cuenta; muestra 1 → **sin** `resume` real (ausente, no inventado); un comando que
**solo menciona** «resume» en sus argumentos/contenido (p. ej. el contenido de un `write`) **no**
cuenta; S-BOOT-04 → primer despacho en la herramienta `subagent`.

**PD-7 (definición cerrada de «lecturas de orientación previas al `resume`» — resuelve V1).** La
spec fija el criterio: **«lectura de orientación» = llamada a la herramienta `read`** (no `glob`,
`grep` ni `shell`) ejecutada **antes** del primer `resume` real. El registro expone **a la vez** el
**total de llamadas** antes del hito y el **conteo de `read`**, de modo que la diferencia sea
**visible** y **nunca** promediada; también expone los `glob`/`shell` para no ocultar el resto.
Verificable: muestra 2 → **18** llamadas antes de #19, de las cuales **8** son `read` (más **2**
`glob` y **8** `shell`); el total de `read` de la **sesión** es **9** (la novena es la #24,
**posterior** al `resume`). Ambos números (total de sesión y previo al hito) aparecen etiquetados.

**PD-8 (medidas de orientación y tres magnitudes, con unidades/procedencia).** El registro expone,
junto a cada hito: **tiempo hasta el hito**, **llamadas previas**, **lecturas previas**, **volumen de
salidas** (total y máximo), **input por paso**, **acumulado** y **caché**, cada uno con **unidad**,
**intervalo** y **procedencia** declarados (claves requeridas de `measures`; C2). Distingue **tres
magnitudes**: (i) *contexto cargado por paso* = **proxy** `tokens.input + cache.read + cache.write`
del paso (marcado `estimated`; **no** la ventana real), (ii) *procesamiento acumulado* = suma de pasos
(`observed`), (iii) *costo* (`observed` o `unknown`). Verificable: muestra 1 → proxy del último paso =
**203.276** tok (`input` 1.164 + `cache.read` 202.112 + `cache.write` 0); acumulado y costo aparecen
**separados**; cada magnitud lleva su etiqueta de procedencia y su unidad; las salidas se miden en
**caracteres Unicode** del texto de `state.content[].text`.

**PD-9 (informe de aplicación: anotación referenciada; forma fijada; no es un juez semántico).** El
registro puede portar una **anotación `application` referenciada**. **Forma del campo (fijada):** un
objeto `application` con:

- `ref` (**obligatorio**): una **referencia durable** — **ruta/commit/recibo** — a la evidencia de
  aplicación; **NO** una **copia** del contenido (no embebe el texto).
- `limit` (**obligatorio**): el límite declarado ∈ `{accepted, blocked, pending, unknown}`, derivado
  de **hechos observables del registro** (p. ej. evidencia/recibo **presente y coincidente** →
  `accepted`; **bloqueo registrado** → `blocked`; **paquete abierto sin recibo** → `pending`; **sin
  registro** → `unknown`). El límite **no** sale del **juicio del lector**: sale de hechos
  observables.
- `basis` (**obligatorio**): los **hechos observables** que sustentan el límite (qué recibo/evento se
  observó).
- `included_sessions` / `relations` (**opcionales**): qué sesiones están incluidas y qué relaciones
  se observaron.

Es una **anotación**, **no** una nueva clasificación semántica del lector ni una aprobación
automática: el **lector nunca aprueba nada** (ni gates ni resultados). Al combinar **coordinador y
workers**, el registro declara **qué sesiones** están incluidas y **qué relaciones** se observaron, y
**no suma dos veces** el mismo costo; los **enlaces entre CLI no verificables** quedan `unknown`.
Verificable: `application.ref` es una **referencia** (ruta/commit/recibo) y **no** una copia del
contenido; `limit` se deriva de hechos observables; la anotación es un campo/sección **referenciada**,
no una entrada de gate; un par padre/hijo **no** duplica costo; un enlace no verificado es `unknown`.

**PD-10 (privacidad: omitir/hashear rutas e identificadores; sin valores de este VPS).** La salida
**omite o hashea** rutas absolutas e identificadores; el adaptador **nunca** imprime prompts crudos
ni salidas de herramientas. La **prohibición** cubre: **rutas del host**, **ruta del store**,
**nombres de proveedor**, **nombres de modelo** e **identificadores de sesión**; esos valores **no**
se copian a **contratos publicables** (spec, plan) ni al producto. El **tamaño del store** y los
**agregados** ya publicados en el discovery y en el plan del epic se citan **por referencia**, **sin
agregar valores nuevos** (no son «valores de este VPS» prohibidos: son datos ya publicados). Los
**identificadores reales de sesión** se resuelven en **registros locales** existentes (p. ej.
`.cdad/local/orientation-analysis-005-003-2026-10-10.json` para S-BOOT-04) y **no** se copian a
**contratos publicables**. Verificable: el registro emitido no contiene ruta absoluta, ni texto de
prompt/salida; un grep de spec/plan/producto **no** encuentra ruta de host, ruta de store, proveedor,
modelo concreto ni identificador de sesión.

**PD-11 (solo lectura, acotado, stdlib, JSON único, determinista).** El adaptador abre el store con
**URI de solo lectura** (`?mode=ro`), **acota** las consultas por sesión/ventana (los flags de la
«Superficie de invocación» son el contrato de acotamiento), **nunca** checkpoint-ea ni escribe (store
de **4,67 GB** con WAL de **543 MB**; tamaños **citados por referencia** del discovery, C5). Usa
**solo la biblioteca estándar de Python**; **JSON es el único modo de salida** (`--json` aceptado como
no-op); **determinismo**: la misma entrada produce **los mismos bytes**. Verificable: abrir **no**
cambia tamaño/mtime del store ni de su WAL/SHM y no crea archivos nuevos; dos corridas sobre el mismo
fixture dan salida **byte-idéntica**; `--json` se acepta; no hay dependencias fuera de stdlib.

**PD-12 (salida lo bastante chica para 005-003).** La salida por defecto es **compacta** (acotada),
suficiente para que 005-003 **distinga orientación de ejecución** y **consulte la evidencia
original** (referencia a sesión + paso/seq) **sin** inyectar toda la sesión al contexto. Verificable:
el documento emitido para la muestra 1 está **por debajo** de un límite de bytes declarado y porta
**referencias** (sesión + paso/seq) a los eventos originales; **no** embebe el transcript completo.

**PD-13 (formato en la skill, no enganchado en gates; medición opcional).** El formato y el
procedimiento viven en la skill (**schema asset** + **reference**) y **no** están cableados a ningún
gate; la medición es **opcional**: el ciclo **sigue** cuando el entorno **no expone tokens**. El
adaptador es **canónico** en `skills/cdad-cycle/scripts/` con **wrapper fino** en `scripts/`.
Verificable: ningún gate referencia el asset/reference nuevos; una sesión **sin** datos de tokens
produce un registro **válido** con cubos `unknown`; el reference **no** se carga por defecto;
`scripts/cdad_context_meter.py` solo resuelve y ejecuta el canónico.

**PD-14 (sesión de cierre de 005-001 — V6, resuelta honestamente).** El lector **documenta el
criterio** usado para identificar la **sesión de cierre de 005-001** (la muestra «~4 h, 13
subagentes, máx ~310 mil», medida por Codex). Si la identidad **se puede establecer por evidencia**,
registra el **criterio** y la sesión; si **no**, la declara **`unknown` con causa** y la deja como
**ítem abierto/deuda**. **Nunca** la fabrica. Verificable: la spec/registro contiene **o bien** el
criterio documentado + la sesión resuelta, **o bien** un `unknown` explícito con causa y una entrada
de ítem abierto; ninguna sesión se presenta como la de cierre sin criterio.

**PD-15 (superficie de invocación: contrato observable; C1).** `scripts/cdad_context_meter.py`
acepta la interfaz mínima de §2 («Superficie de invocación»): `--store PATH` (o la variable de
entorno `CDAD_CONTEXT_METER_STORE`; sin ninguno → **fallo cerrado** que **nombra el insumo
faltante**); `--session REF` (repetible) y `--limit N` (**default declarado** `20`); `--idle-threshold
MINUTES` (**default declarado** `60`); **JSON por stdout** con `--json` aceptado como no-op; `rc = 0`
en **éxito** y `rc != 0` en **fallo cerrado** con **diagnóstico por stderr**. **Sin** motor de
reportes, **sin** dashboard, **sin** scheduler. Verificable: los tests invocan el **wrapper** con
esos flags y observan el JSON por stdout, `rc` y el diagnóstico; sin store ni variable, `rc != 0` y
el diagnóstico nombra el insumo; `--json` no cambia la salida; ninguna ruta hardcodeada.

**PD-16 (claves requeridas del registro neutral; C2).** El documento emitido contiene las claves
**requeridas** de `milestones` (`status`, y `position`/`time_relative` cuando `observed`, `cause`
cuando ausente/desconocido), de `measures` (las ocho medidas mínimas con `value`/`unit`/`provenance`/
`bucket`) y de `buckets` (`observed`/`estimated`/`unknown` con la **regla de asignación**), **sin**
nombres de tablas/columnas del runtime. El **esquema neutral sigue siendo el contrato**; el adaptador
**solo traduce**. Verificable: el asset declara las claves y sus obligatoriedades; un documento sin
una clave **obligatoria** **no** valida; una métrica vive en **exactamente un** cubo; las claves
requeridas se nombran **sin** tablas/columnas del runtime.

### 3. Invariantes (verificables)

- **INV-1.** El adaptador es **read-only**: **nunca** escribe el store del runtime, su WAL, el repo ni
  el state; la apertura es `?mode=ro` y sin checkpoint (PD-2/PD-11).
- **INV-2.** **No** se fabrican números: bytes **nunca** se convierten a tokens y **ningún** límite
  de contexto se inventa (extiende `cdad_continuity.py:29-31`; PD-3).
- **INV-3.** El **registro neutral no contiene** nombres de tablas/columnas del runtime; el
  **adaptador es el único** traductor (PD-1; R6).
- **INV-4.** `observed`/`estimated`/`unknown` **nunca** se mezclan; un valor nulo/ausente/no reportado
  es **`unknown`**, **nunca** `0` (PD-1/PD-4; regla de `buckets`, C2).
- **INV-5.** La medición es **opcional**: **ningún** gate depende de ella (PD-13).
- **INV-6.** **Python stdlib only**; **JSON** es el único modo de salida (PD-11).
- **INV-7.** **Sin valores de este VPS** en producto ni en contratos publicables: **rutas del host,
  ruta del store, nombres de proveedor y de modelo e identificadores de sesión** (PD-10). El
  **tamaño del store** y los **agregados** ya publicados (discovery, plan del epic) se citan **por
  referencia**, sin agregar valores nuevos.
- **INV-8.** **No** cambian contratos ya aprobados (plan del epic y specs de otras features); **no** se
  construye motor de evaluación de sesiones, dashboard, scheduler ni plataforma de usabilidad.
- **INV-9.** Un **despacho registrado no prueba** utilidad ni resultado aceptado; el lector **no**
  aprueba gates (PD-6/PD-9).
- **INV-10.** Quedan **fuera** de esta unidad: calidad semántica, espera improductiva, cuotas/ETA, y
  la clasificación de repeticiones de suites / fricción de permisos / correcciones tras review /
  intervenciones humanas (exige juicio; PD-12/§5).

### 4. Criterios de aceptación

- [ ] **PD-5**: bajo el corte explícito y con el **borde fijado** (último mensaje del tramo = el
      `assistant` que cierra el tramo, sin llamada de herramienta propia; cierre en el `idle`
      `succeeded` previo a la brecha), la muestra 1 reproduce **12,55 min / 101 llamadas / 51.243
      car. / 203.276 tok** (proxy del último paso); el borde alternativo (último mensaje **con**
      herramienta → 12,40 min / 202.222 tok) se hace **visible** y se declara **NO usado**; la misma
      sesión medida en toda su extensión **difiere** (continuada tras ~66,4 h) y esa diferencia se
      **muestra**, sin promediar.
- [ ] **PD-6/PD-7**: muestra 2 → primer `resume` = llamada **#19**; **18** llamadas antes; de ellas
      **8** `read` (**2** `glob`, **8** `shell`); total `read` de sesión = **9** (la #24 es posterior);
      `resume --help` (#10) excluida; la diferencia se hace visible.
- [ ] **PD-6 (entrada adicional opcional)**: S-BOOT-04 cubre el **primer despacho** = llamada
      **#576** (mensaje), herramienta `subagent` (tool-call **#73**, 72 previas), sesión hija creada
      ~**57 ms** después; se usa solo si ayuda y sin publicar identificadores.
- [ ] **PD-15 (C1)**: el **wrapper** acepta `--store`/`--session`/`--limit`/`--idle-threshold`/`--json`;
      emite **JSON por stdout**; `rc = 0` en éxito y `rc != 0` con **diagnóstico por stderr** en el
      fallo cerrado; sin store ni variable de entorno, el diagnóstico **nombra el insumo faltante**;
      ninguna ruta hardcodeada.
- [ ] **PD-16 (C2)**: el registro contiene las claves **requeridas** de `milestones`/`measures`/
      `buckets` (con obligatoriedades declaradas), valida contra el asset, y cada métrica vive en
      **exactamente un** cubo; **sin** nombres de tablas/columnas del runtime.
- [ ] **PD-2/PD-3**: esquema desconocido → **fallo cerrado** con diagnóstico que **nombra** el
      faltante, **sin número** y `rc != 0`; **sin** conversión bytes→tokens ni límite fabricado.
- [ ] **PD-4**: `cache_write` (y cualquier nulo/ausente) es **`unknown`**, **nunca** `0`; input
      reportado ≠ facturado ≠ capacidad máxima.
- [ ] **PD-1/PD-8**: registro neutral validado por el asset; **tres magnitudes** separadas
      (proxy/estimado, acumulado/observado, costo) con unidad, intervalo y procedencia.
- [ ] **PD-9 (C4)**: anotación `application` **referenciada** con `ref` (referencia durable,
      **no** copia), `limit` en `{accepted, blocked, pending, unknown}` derivado de hechos
      observables y `basis`; **sin** doble conteo coordinador+workers; enlaces no verificables
      `unknown`; el lector **no** aprueba.
- [ ] **PD-12**: salida por debajo del límite declarado, con **referencias** a la evidencia original.
- [ ] **PD-14**: sesión de cierre de 005-001 → criterio documentado **o** `unknown` con causa +
      ítem abierto/deuda; nunca fabricada.
- [ ] **PD-10/INV-7 (C5)**: la salida omite/hashea rutas e identificadores; spec y plan **sin** rutas
      del host, ruta del store, proveedor, modelo ni identificadores de sesión; el tamaño del store y
      los agregados se citan **por referencia**.
- [ ] **PD-11/PD-13**: `?mode=ro`, sin checkpoint, stdlib, JSON único, determinista (byte-idéntico);
      formato en la skill y **no** enganchado en gates; **suite completa verde al cierre** y
      `make validate` sin fallos nuevos (los FAIL preexistentes, si los hay, no se atribuyen a este
      diff).

### 5. Fuera de alcance

- **Motor de evaluación de sesiones**, **dashboard**, **scheduler**, **plataforma de usabilidad**,
  **espera improductiva**, **cuotas/ETA** y **calidad semántica** (plan «Ajuste», `:45-85`; delta
  punto 7).
- **Clasificar** repeticiones innecesarias de suites, fricción de permisos, correcciones tras review
  e intervenciones humanas: **exige juicio**, no se atribuye al parser (puede quedar como anotación
  cualitativa declarada, fuera del primer incremento).
- **Cambiar contratos ya aprobados** (plan del epic, specs de otras features) o construir **otro
  state** del ciclo.
- **Instalar en HOME**, **activar versiones**, **push** y **operar producción** (reservado al dueño).
- **Comparaciones entre modelos**, CI, sandbox (fuera del epic, `plan.md:25-27`).
- **Repetir el discovery** ni **repetir desarrollos completos** para comparar (plan «Ajuste»).

### 6. Contexto técnico (verificado)

**Superficie existente (archivo:línea).**

- **Precedente de lectura RO:** `docs/specs/003-003-progress-guards/evidence/t5/recorder.py:35`
  (`DEFAULT_DB = "file:/…/opencode.db?mode=ro"`) y
  `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/opencode-session-scan.py:21`
  (`sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)`).
- **Fail-closed / sin fabricar:** `skills/cdad-cycle/scripts/cdad_continuity.py:29-31` (bytes nunca a
  tokens; sin límite fabricado; `unknowns[]`); `:55-58` (`--max-bytes`, sin truncar).
- **Wrapper fino:** `scripts/cdad_continuity.py:10-11` (`runpy.run_path(CANONICAL, …)`); idéntico en
  `scripts/cdad_packet.py`, `scripts/cdad_result.py`, `scripts/cdad_guard.py`,
  `scripts/cdad_delegate.py`.
- **JSON único:** `skills/cdad-cycle/scripts/cdad_continuity.py:66` («JSON is the only output
  mode»); `--json` no-op `:67`.
- **Schemas de la skill:** `skills/cdad-cycle/assets/*.schema.json` (draft 2020-12; ver
  `run-evidence.schema.json:1-2`); son contratos documentados, **no** validados por un gate de
  código (grep: `guard-trace`/`guard-event` solo referenciados en comentarios de `cdad_guard.py`).
- **Instalación:** `install.sh:1036` `install_skills()` sincroniza el **directorio** de la skill
  (el script canónico, el asset y el reference **viajan** con ella; **sin** cambio de instalador).
- **Política de rutas:** `docs/cdad-policy.json` (`implementation_roots` incluye `skills`/`scripts`;
  `test_roots = tests`); `skills/cdad-cycle/scripts/cdad_continuity.py:60-64` la usa como fuente
  única de clasificación.
- **Tests:** convención `tests/test_<feature>_t<n>_<tema>.py`; el CLI se invoca por el **wrapper**
  (`tests/test_003_004_t1_resume.py:80` → `REPO_ROOT/"scripts"/"cdad_continuity.py"`).

**Superficie de la fuente (verificada en el discovery §1-§2; re-verificada en este draft).**

- Store SQLite del runtime; tablas `session_v2` (una fila por sesión) y `session_message` (una fila
  por evento; `type`, `seq`, `data` JSON). **Sin `schema_version`**; el versionado vive en
  `__drizzle_migrations`/`migration`. Formas de `data`: `assistant` (con `tokens.{input,output,
  reasoning,cache:{read,write}}`, `cost`, `agent`, `model`, `content[]`), `user`, `agent-switched`,
  `model-switched`, `idle`, `compaction`, `synthetic`/`system`. Partes `tool`:
  `{type:"tool", name, state:{status,input,content,metadata,error?}, time}`; el tamaño de salida =
  suma de `len(text)` de `state.content[]`. **Rol** = `session_v2.agent`; **modelo** =
  `session_v2.model` (string JSON, parsear con fallback a string). `cache_write` = 0 en las 496
  sesiones CDAD. `resume_attempts` = 0 en toda la DB; `time_idle`/`idle_outcome` **no** registran el
  `resume` del CLI → el hito se observa como llamada `shell` que invoca el subcomando `resume`.

**Muestras y valores verificados (re-verificados read-only para este draft).**

| Muestra | Ventana/corte | Valores verificados |
|---|---|---|
| **005-001, primera sesión** | primer **tramo contiguo** (borde fijado en PD-5: cierra en el `idle` `succeeded` previo a la brecha; brecha real ~66,4 h) | **12,55 min** (primer `time_created` → último `time_updated` del tramo); **101** llamadas (`read` 25, `shell` 72, `execute` 1, `edit` 2, `write` 1); mayor salida **51.243 car.**; proxy del último paso **203.276 tok** (`input` 1.164 + `cache.read` 202.112 + `cache.write` 0), donde el último paso es el mensaje `assistant` que **cierra** el tramo (sin llamada de herramienta propia). Borde alternativo (**NO usado**): último mensaje **con** herramienta → 12,40 min / 202.222 tok. Medida en **toda** su extensión: **121** llamadas (continuada tras la brecha) → el corte debe ser explícito. |
| **003-007, sonda 2** | sesión completa (2,61 min; 29 llamadas) | primer `resume` real = llamada **#19**; **18** llamadas antes: **8** `read`, **2** `glob`, **8** `shell`; total `read` de la sesión = **9** (la #24 es posterior); `resume --help` = llamada **#10** (excluida). |
| **S-BOOT-04** (entrada adicional **opcional**) | corte declarado en el registro local | primer despacho = llamada **#576** (mensaje), herramienta `subagent` (tool-call **#73**, 72 previas); sesión hija creada ~**57 ms** después. |

**Discrepancia verificada (V1).** El enunciado del encargo y el discovery §2.2 afirman «9 son `read`»
antes del `resume`. La re-verificación read-only da **8** `read` antes de #19 (8 `read` + 2 `glob` +
8 `shell` = 18); el **noveno** `read` de la sesión es la llamada **#24**, **posterior** al `resume`.
El criterio de PD-7 fija la definición (`read` antes del hito) y expone **ambos** números, de modo que
la diferencia queda **visible** y reproducible con independencia de la etiqueta.

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | El **registro neutral** vive en un **schema asset** (`context-meter.schema.json`) + un **reference** (`context-meter.md`); **no** se engancha en gates. El adaptador **traduce**. | discovery §6/§7/V12; neutralidad (R6); opcionalidad (fila 7). |
| **D2** | **Adaptador canónico** `skills/cdad-cycle/scripts/cdad_context_meter.py` + **wrapper fino** `scripts/cdad_context_meter.py` (`runpy`). | convención verificada (`cdad_continuity.py:10-11`); `install_skills` lo despliega. |
| **D3** | **Fallo cerrado** por **columnas requeridas + tipos de fila** (no hay `schema_version`); diagnóstico que **nombra** el faltante y **ningún número**; `rc != 0`. | discovery §5; deriva ya ocurrida (§1.4); riesgo del epic (`plan.md:112-113`). |
| **D4** | **Corte explícito con el borde fijado**: ventana declarada por medición; para la línea base, **primer tramo contiguo** cortado en la primera brecha > umbral configurable (default `60` min); **último paso = el mensaje `assistant` que cierra el tramo** (sin llamada de herramienta propia); cierre en el `idle` `succeeded`; **métricas por tramo**, sin promediar. | PD-5 (C3); la muestra 1 fue continuada (~66,4 h) y debe reproducirse con borde visible; la elección del borde cambia el número (12,55 vs 12,40). |
| **D5** | **Detección de hitos**: `resume` = `shell` cuyo `command` invoca el subcomando `resume` del CLI de continuidad, **excluyendo** ayuda (`--help`/`-h`); `dispatch` = primer evento de despacho de rol observable (herramienta que abre sesión worker, p. ej. `subagent`) cuando la traza lo tiene; ausente → `unknown`. | discovery §1.7/V2; sonda 2 #10 vs #19; S-BOOT-04. |
| **D6** | **Tres magnitudes** con fórmulas/unidades/procedencia: proxy `input+cache.read+cache.write` (estimated), acumulado (observed), costo (observed/unknown). | plan fila 7 (`:40`); delta punto 5; discovery §1.6. |
| **D7** | **Desconocido ≠ cero**: nulo/ausente/no reportado → `unknown` con causa; input reportado ≠ facturado ≠ capacidad máxima. | delta punto 6; `cache_write` (V5); precedente `cdad_continuity.py:29-31`. |
| **D8** | **Informe de aplicación** = **anotación referenciada** con **forma fijada** `{ ref (referencia durable, no copia), limit ∈ {accepted, blocked, pending, unknown} desde hechos observables, basis (hechos observables), included_sessions/relations opcionales }`; el lector **nunca** aprueba; declarar sesiones incluidas y relaciones; sin doble conteo. | delta puntos 4-5; `plan.md:59-62`; PD-9 (C4). |
| **D9** | **Privacidad**: omitir/hashear rutas e identificadores; resolver ids reales en registros locales; **sin** rutas del host, ruta del store, proveedor, modelo ni identificadores de sesión en spec/plan/producto. | discovery R3; regla de anonimización del workspace; delta «Aceptación»; PD-10 (C5). |
| **D10** | **Salida**: `?mode=ro`, acotada por sesión/ventana, stdlib, JSON único, determinista; **no** enganchada en gates. | discovery §7/§9/V10; precedentes. |
| **D11** | **Superficie de invocación mínima** del medidor (flags `--store`/`--session`/`--limit`/`--idle-threshold`/`--json`; JSON por stdout; `rc` y diagnóstico por stderr); sin motor de reportes, dashboard ni scheduler. | PD-15 (C1); el test-writer no ve la implementación y necesita el contrato observable. |
| **D12** | **Claves requeridas** del registro neutral (`milestones`/`measures`/`buckets`) con obligatoriedades y **regla de cubos** (una métrica en exactamente uno). | PD-16 (C2); neutralidad; AP-13. |

### 8. VERIFY del discovery §11 — estado y resolución propuesta

| # | VERIFY | Estado en el draft | Resolución / dueño y cuándo |
|---|---|---|---|
| V1 | Definición de «lectura de orientación» | **RESUELTO por PD-7/D5** (propuesta) | «`read` antes del hito»; se exponen total y `read` (y `glob`/`shell`). **Discrepancia 8 vs 9** señalada (§6): 8 antes de #19, 9 en la sesión. Se confirma en T2. |
| V2 | `resume` real vs `--help` | **RESUELTO por PD-6/D5** | Excluir ayuda; la #10 de la sonda 2 no cuenta. Confirmar en T2. |
| V3 | Formas de invocación del CLI | **PARCIAL por PD-15/D11** | La **superficie del medidor** (flags propios) queda fijada (PD-15). El **detector** reconoce el **subcomando** `resume`, no la ruta exacta del CLI instalado → sigue **abierto** para la ruta exacta; se confirma en implementación/T2. |
| V4 | Semántica de `resume_attempts`/`time_idle`/`idle_outcome` | **ABIERTO → `unknown`** | Permanecen `unknown` con causa (0/null); no se les atribuye el `resume`. |
| V5 | `cache_write` (no reportado) | **RESUELTO por PD-4/D7** | `unknown`, nunca `0`. Confirmar en T1. |
| V6 | Sesión de cierre de 005-001 | **RESUELTO por PD-14** | Criterio documentado **o** `unknown` + deuda; nunca fabricada. Confirmar en T4. |
| V7 | Columnas/tipos requeridos | **RESUELTO por PD-2/D3** (runtime) + **PD-16/D12** (claves neutrales) | Conjunto de columnas/tipos del runtime declarado en el asset/adaptador; claves neutrales requeridas fijadas; `unknown-schema` en T1. |
| V8 | Una sesión = un rol | **RESUELTO (verificado)** | `session_v2.agent`; `agent-switched` **ausente** en las muestras CDAD; se declara. |
| V9 | Sesiones solo-legacy | **RESUELTO por PD-2** | No soportadas → **fallo cerrado** que las declara no soportadas. |
| V10 | RO con WAL grande | **RESUELTO por PD-11/D10** | `?mode=ro`, acotado, sin checkpoint, sin `immutable=1`. |
| V11 | Campo de ruta de `read` | **ABIERTO** | `path` (observado) vs `filePath`/`file_path`; verificar por versión en implementación; el conteo de `read` no depende del campo de ruta. |
| V12 | Forma y ubicación del registro neutral | **RESUELTO por D1** | Schema asset + reference; sin enganche en gates. |

### 9. Riesgos con mitigación

- **R1 (alto) — el esquema del store no es contrato público.** Puede cambiar entre versiones.
  **Mitigación:** D3/PD-2 (validar columnas/tipos requeridos, fallar cerrado con diagnóstico); no
  depender de marcador de versión; variante `unknown-schema` en T1.
- **R2 (medio) — una sola sonda por variante → medición indicativa, no estadística** (riesgo del
  epic). **Mitigación:** el registro **declara la muestra**; **no** promedia (PD-5/PD-7).
- **R3 (alto) — privacidad**: la fuente trae rutas absolutas, prompts y salidas de herramientas.
  **Mitigación:** PD-10/D9 (omitir/hashear; sin rutas del host, ruta del store, proveedor, modelo ni
  identificadores de sesión en publicables).
- **R4 (medio) — tamaño**: store de 4,67 GB + WAL de 543 MB (tamaños **citados por referencia** del
  discovery). **Mitigación:** PD-11/D10 (RO, acotado, sin checkpoint).
- **R5 (medio) — ambigüedad de métrica** («lectura de orientación», «momento del resume», **borde del
  tramo**). **Mitigación:** definiciones cerradas (PD-5/PD-6/PD-7) y discrepancia 8 vs 9 **visible**;
  borde del tramo fijado (C3) con el alternativo declarado NO usado.
- **R6 (medio) — neutralidad**: si el adaptador filtra nombres de tablas al registro neutral.
  **Mitigación:** PD-1/D1 (registro sin nombres del runtime; adaptador único traductor).
- **R7 (bajo) — doble conteo de costo coordinador+workers.** **Mitigación:** PD-9 (declarar sesiones
  incluidas y relaciones; enlaces no verificables `unknown`).

### 10. Fronteras

- **005-002 MIDE** (plan fila 7): lector read-only + formato neutral. **No** arranca proyectos ni
  reduce orientación.
- **Frontera con 005-003** (reducción de orientación): 005-002 es su **insumo** (salida compacta +
  referencias), **no** su sustituto; la base «18» de la sonda 2 y la meta numérica se fijan en 005-003
  con los datos de 005-002.
- **Frontera con 005-006** (arranque guiado): 005-006 resuelve el arranque; 005-002 mide sesiones
  históricas y luego las del arranque real.
- **Frontera con 005-009/005-010** (delegación): 005-002 **no** despacha; mide las sesiones que otros
  recorridos producen.
- **Frontera con 005-004** (roles en Claude Code): el formato es **neutral** y debe seguir marcando
  `unknown` donde un runtime no exponga tokens; **no** implementa ese soporte aquí.
- **No** cambia el alcance ni los criterios del epic-005; activación de versiones, cambios en HOME,
  confianza de carpeta y producción siguen **reservados al dueño**.

### 11. Aprobación

- **Aprobada (2026-10-11)** por el **orquestador OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`; delegación vigente, alcance: aprobar specs y
  planes de las features del epic). El architect **no** aprobó su propia propuesta (anti-sesgo).
  **Decisiones adoptadas: D1–D12** tal como se proponen en §7. **Sin enmiendas al aprobar**: la ronda
  acotada **draft-002** resolvió C1–C5 en el propio draft (superficie de invocación PD-15, claves
  requeridas PD-16, borde del tramo PD-5, forma de la anotación PD-9, alineación de privacidad
  PD-10/INV-7) y conservó íntegro el resto del draft 001.
  **Verificación del orquestador antes de aprobar** (proporcional, con evidencia propia): sonda
  read-only sobre el store de sesiones que confirmó las cifras pinneadas (muestra 1: 101 llamadas en
  el tramo, 12,55 min, mayor salida 51.243 car., proxy del último paso 203.276; borde alternativo
  12,40 min / 202.222 declarado NO usado; sonda 2: primer `resume` #19, 8 `read` antes y 9 en la
  sesión); validación del bloque `plan-tasks` con el validador del CLI instalado (4 tareas, sin
  ciclos); verificación de los archivos citados; grep de privacidad sin identificadores de sesión,
  rutas del host, proveedor ni modelo.
- **VERIFY de §8**: V1/V2/V5/V6/V7/V8/V9/V10/V12 resueltos por propuesta; V3 (ruta exacta del CLI)
  **parcial** por PD-15; V4/V11 quedan como **abiertos** (V4 como `unknown` declarado) y se confirman
  en T2/T4.
- El `sha256` del archivo materializado vivirá en el `state` (pin `contract_path` +
  `contract_sha256`), no dentro del archivo.
- Status: Approved by orquestador OpenCode (HITL delegada epic-005) on 2026-10-11
