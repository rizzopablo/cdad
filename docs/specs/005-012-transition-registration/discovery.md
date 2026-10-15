# Discovery — 005-012-transition-registration (etapa 1)

**Paquete:** `005-012-transition-registration-architect-discovery-001` · **Ejecución:** `exec-005-012-transition-registration-001` · **Rol:** architect · **Subetapa:** discovery.
**Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md` (sha256 `63dda3b8…59a6`), fila 12 y secciones que prevalecen sobre las filas (`plan.md:48-88`, `plan.md:141-154`).
**Autoridad del tramo:** `docs/epics/epic-005-real-operation/execution.md` — HITL delegada al orquestador OpenCode (`execution.md:8-23`), criterio de review vigente 2026-10-12 (`execution.md:48-56`), insumos de la review de Codex para 005-012 (`execution.md:83-88`).
**Modo:** discovery y mapeo técnico. **No se propone el contrato** (eso es la subetapa draft): las decisiones del contrato quedan planteadas como direcciones y dudas, no como postcondiciones.

---

## 0. Baseline, método y anonimización

### 0.1 Qué corre hoy y qué hay en el árbol (punto fino declarado)

| Pieza | Referencia verificada | sha256 |
|---|---|---|
| CLI **instalado** (el que corre en este ciclo) | `<home>/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py` == `git show 7212ead:skills/cdad-cycle/scripts/cdad_packet.py` | `776d1168252b777f621a5c02efa28f1d73728b9d3a50f57f74ea174816c90eb9` |
| CLI del **árbol del repo** (HEAD `58dedda`) | `skills/cdad-cycle/scripts/cdad_packet.py` | `1f06855fa98ff7eea821db96c781b95327fd4350a8e64d9669458a8d03ff3a44` |
| Paquete de esta ejecución | `.cdad/packets/005-012-…/PACKET.md` (`contract.sha256` = el del plan del epic) | — |

Diferencia `7212ead..HEAD` en producto: **3 archivos** — `skills/cdad-cycle/scripts/cdad_packet.py` (+829), `skills/cdad-cycle/references/project-execution.md` (+21), `skills/cdad-epic/assets/epic-plan-template.md` (+11) — más docs de 005-011/005-013, ADR y `tests/test_005_013_*.py`. Verificado con `git diff --stat 7212ead..HEAD`.

**Consecuencia práctica (declarada, no supuesta):**

- Lo que **hoy corre** (`7212ead`) **no** tiene el contrato de unidad: `cdad_packet.py --help` del instalado ofrece `{validate-state, validate-policy, render, validate-request, validate-packet, prepare, open-unit, validate-metric, status}`; el del repo **añade** `validate-unit-contract`, y `grep UNIT-CONTRACT.md` da **0** en el instalado y **2** en HEAD. Es decir: el instalado tiene `open-unit` (005-007) pero **no** la proyección de unidad ni `validate-unit-contract` (005-013).
- El **próximo despliegue llevará 005-013 y 005-012 juntas**: cualquier operación nueva de esta feature debe diseñarse sobre el **árbol del repo (HEAD)** y declararse como *no existente en la instalación* hasta el despliegue (deuda ya declarada por 005-013, `docs/specs/005-013-unit-contract/debt.md:71-77`).
- **Piezas que ya están en HEAD y se pueden reusar sin suposición:** el escritor único del state (`_ProjectLock` + `_publish_owned_atomically` + `_publish_generation`), `open-unit`, `prepare --record-dispatch`, `receive/validate-receipt/materialize` (no cambiaron en `7212ead..HEAD`), la continuidad (`begin/checkpoint/reconcile/resume`), el vocabulario de marcadores y la vista `status`.
- **Piezas que son suposición hasta el despliegue:** que el instalado reconozca una operación nueva; que un proyecto consumidor tenga el activo de anclas (005-013 O3, `debt.md:16-24`).

### 0.2 Anonimización

Este informe no contiene rutas absolutas del dueño ni ids crudos de sesión: usa `<repo>`, `<home>`, `<tmp>`, `<ses-…>`. No nombra proyectos de otros clientes; cuando el plan del epic cita un caso de consumo, se referencia por su unidad (**005-008**, «consumidor con tests anidados»).

### 0.3 Medidas deterministas disponibles (calculadas, no estimadas)

| Medida | Valor | Método |
|---|---:|---|
| `docs/.cdad-state.json` | **578.926 B** (4.544 líneas) | `len(path.read_bytes())` |
| `stage_history` | **525.285 B = 90,7 %** del state, **415 entradas** | `len(json.dumps(...,separators=(',',':')).encode())` |
| `epic_history` | 9.698 B, 15 entradas | idem |
| `epic_features` | 13 entradas (11 `done`, 005-012 `in-progress`) | idem |
| Scripts propios del orquestador que editan el state | **13** en `.cdad/local/` | `grep -ln "cdad-state\|stage_history" .cdad/local/*.py` |
| Glue propia de los dos últimos ciclos | **751 líneas** en 7 scripts | `wc -l` (ver §9) |

Estos números coinciden con el orden de magnitud ya declarado al cierre de 005-011 (~530 KB, ~486 KB en `stage_history`; `execution.md:92-95`) y lo precisan.

---

## 1. Inventario de las transiciones de un ciclo y quién las escribe hoy (eje 1)

La conclusión estructural, verificable en el código: **el CLI escribe muy poco del state y nunca escribe `stage_history`**. `grep -n 'stage_history' skills/cdad-cycle/scripts/*.py` sólo devuelve **lecturas** (`cdad_packet.py:1399-1410`, `1425`, y comentarios en `:119`, `:3948`, `:4558`). Por lo tanto **toda** transición que hoy consulta el LLM (`validate-state`, autorización de roles, pin de aprobación) entra al state **por script propio del orquestador**, y el CLI después la *lee*.

| # | Transición | Quién la escribe hoy | Evidencia que se exige | Qué se valida | Campos del state que toca |
|---|---|---|---|---|---|
| i | **Despacho / registro de un despacho** | **CLI**: `prepare` (publica paquete + binding) y `prepare --record-dispatch` (observación I8) | `--objective`; observación con `runtime/model_configured/model_reported/session/started_at` + `provenance` (`cdad_packet.py:2271-2274`, `project-execution.md:131-141`) | autorización por rol contra el contrato verificado (`_contract_approval_for`, `:1413-1486`); scopes contra la política; vigencia v2 (`_validate_v2_vigency`, `:1558-1624`) | `execution` (binding v2), `active_packet{id,role,substage,status:prepared}` (`:4381-4386`); `active_packet.status: dispatched` (`:2468-2470`) |
| ii | **Recepción de una entrega** | **CLI**: `receive` + `validate-receipt` (recibo durable); **el orquestador** escribe a mano el descriptor y **la transición** | parts staged bajo `.cdad/inbox` + descriptor `RESULT.json` (`re-entry.md:25-38`) | identidad/paquete (`cdad_result.py:513-526`), **paquete activo en `dispatched`** (`:527-531`), scopes (`:533-535`), digest y bytes por parte | **ninguno**: el recibo sólo pide `state_transition_requested: "received"` (`cdad_result.py:576`) y deja `semantic_status: pending` (`:575`) |
| iii | **RED** | **Script propio**: `.cdad/local/register.py` / `stage3.py` (`stage3.py:1-19`: prepare→validate→begin→record-dispatch→invoca→correlaciona→stage→receive→materialize) | commit `test:` + focal pegado (`re-entry.md:140-152`) | juicio del orquestador: fallo por aserción, `tests/` tocado | `stage_history += {stage:"tdd-red-tN"}`; `postconditions_status`; `tdd_substage:"green"`; `active_packet.status:"completed"`; `last_updated` |
| iv | **GREEN** | **Script propio** (`.cdad/local/005-013-register-tdd.py`) | commit `feat:` + focales y módulos tocados; `git diff -- tests/` vacío (`re-entry.md:154-172`) | juicio: AP-4, regresión proporcional | idem + `postconditions_status[n]="green"` |
| v | **REFACTOR / review-fix** | **Script propio** (`.cdad/local/005-013-register-tdd.py`, `…-register-review.py` como par RED/GREEN del bloqueante) | suite verde sin tocar `tests/`; commit `refactor:` (`re-entry.md:174-185`) | juicio: AP-11 | `stage_history += {stage:"tdd-red-b1"/"tdd-green-b1"}`; `review_status` con la disposición del bloqueante |
| vi | **Aprobación de un gate de etapa 3** | **Script propio** (`005-013-register-t4.py`) | `acceptance.md` + `closure-suite.md` + evidencia cruda no versionada | juicio del orquestador sobre la prueba decisiva | `stage_history += {stage:"tdd-t4-acceptance"}` y `{stage:"tdd-t4-gate"}`; `current_stage:"review"` |
| vii | **Aprobación de la spec y del plan (etapa 2)** | **Script propio** (`005-013-register-reapproval.py`) | `spec.md` + `plan.md` + review previa del orquestador Claude | **el CLI la lee después** con pin obligatorio (`_approved_spec_entries`, `:1398-1410`) | `stage_history += {stage:"specification", approved_by, contract_path, contract_sha256, plan_path, plan_sha256}`; `current_stage:"tdd"`, `tdd_substage:"red"` (`stage-2-specification.md:185`) |
| viii | **Review (etapa 4) y disposición de bloqueantes** | **Script propio** (`005-013-register-review.py`) | `review.md` + veredicto + buckets + abstenciones (`re-entry.md:210-226`) | juicio: priorización (capa 2) | `stage_history += {stage:"review", verdict, review_path, review_sha256, debt_path}`; `review_status{verdict,reviewer,review_path,review_sha256,criterion,disposition}` |
| ix | **Memory Bank (etapa 5)** | **Script propio** (`mb-state-005-011.py`, `005-013-register-memory.py`; deltas de `activeContext`/`progress` con `mb-activecontext-*.py`, `mb-progress-*.py`) | borradores del scribe + recibo; aprobación del orquestador (`stage-5-merge.md:163-178`; AP-10 `:195`) | juicio: fidelidad de los borradores | `stage_history += {stage:"merge-memory-bank", artifacts{}}`; `active_packet.status:"completed"` |
| x | **Cierre de feature** | **Script propio** (`005-013-register-closure.py`; `mb-state-005-011.py`) | `closure.md` + `debt.md` + gate 5 | juicio del orquestador | `stage_history += {stage:"feature-closure", closure_path, closure_sha256, debt_*}`; `epic_features[i].status="done"`, `closed_at`, `closure_evidence`; `active_feature=null`; `current_stage="idle"`; `postconditions_status={}`; `active_packet=null`; `last_updated` |
| xi | **Apertura de la unidad siguiente** | **CLI**: `open-unit` (**la única** transición de ciclo que hoy es una operación del CLI) | plan del epic (`epic_features` en orden) | reposo legítimo (`_validate_idle_coherence`), entrada `queued`, `depends_on` `done` (`:4459-4482`) | `epic_features[i].status="in-progress"`, `opened_at`; `active_feature`; `current_stage="discovery"`; `tdd_substage=null`; `active_packet=null`; `execution` (bootstrap v2) (`:4514-4532`) |

**Contabilidad de la fila 12.** De las once transiciones, **diez** terminan en una escritura a mano de `stage_history` (+ campos), y **una** (`open-unit`) es del CLI. El origen del trabajo manual no es un script mal escrito: es el **procedimiento canónico**, que instruye «update the state file» en cada etapa (`stage-1-discovery.md:71`, `stage-2-specification.md:185`, `stage-3-tdd.md:251`, `stage-4-review.md:172`, `stage-5-merge.md:163-178`, `re-entry.md:9`, `re-entry.md:57-63`).

**Evidencia del costo (válido como prueba, ya ocurrido):** en el último ciclo cerrado hay **6 scripts propios** de registro (`005-013-register-{tdd,review,reapproval,t4,memory,closure}.py`, 49-63 líneas cada uno) para **15 entradas** de `stage_history` de 005-013 (`docs/.cdad-state.json:4196-4349`). El cierre de 005-013 se hizo con **un script dedicado** (`005-013-register-closure.py`) que apaga `active_feature`, fija `current_stage="idle"` y marca `done`. 005-011 usó además deltas de Memory Bank armados a mano (`mb-activecontext-005-011.py`, `mb-progress-005-011.py`, `mb-state-005-011.py`).

---

## 2. La forma del state: qué escribe el CLI y qué escribe el orquestador a mano (eje 2)

**Escritura EXCLUSIVA del CLI** (verificado: el único archivo que contiene asignaciones a claves del state es `cdad_packet.py`; `cdad_result.py` y `cdad_continuity.py` sólo **leen** — `cdad_result.py:509`, `:841`, `:1152`; `cdad_continuity.py:142-144` lo declara invariante):

- `execution` (binding v2 de 7 campos) — `prepare` (`:4382`), `open-unit` (`:4531`), bootstrap (`:2224`).
- `active_packet` — `prepare` (`:4383-4386`, `prepared`), `--record-dispatch` (`:2470`, `dispatched`), `--replace-packet` (`:2097`), `open-unit` (`:4524`, `None`).
- `epic_features[].status` / `opened_at` — **sólo** `open-unit` (`:4514-4518`).
- `active_feature`, `current_stage`, `tdd_substage` — **sólo** `open-unit` (`:4521-4523`).

**Escritura EXCLUSIVA del orquestador (a mano, vía scripts propios)** — ninguno de estos campos es tocado por el CLI:

- `stage_history` (append de cada transición: `stage`, `substage`, `at`, `by`, `packet_id`, `approved_by`, `requested_by`, `evidence`, `contract_path`, `contract_sha256`, `plan_path`, `plan_sha256`, `dispatch_ref`, `receipt_ref`, `artifacts`, `note`, `verdict`, `review_*`, `closure_*`, `debt_*`) — 415 entradas, **la parte que produce los desvíos**.
- `epic_history` (mandato del epic; es la autorización del architect, `:1381-1395`).
- `postconditions_status`, `audit_status`, `review_status`.
- `epic_features[].status="done"`, `closed_at`, `closure_evidence`.
- `active_feature=null` + `current_stage="idle"` en el cierre (el CLI sólo los escribe en `open-unit`).
- `approver`, `hitl_delegation`, `delegation_history`, `epic_stage`, `last_updated`.

**Claves de entrada realmente usadas** (unión sobre las 415 entradas): `stage`(415), `feature`(414), `note`(406), `evidence`(373), `at`(257), `by`(226), `approved_by`(192), `completed_at`(158), `dispatch_ref`(86), `artifacts`(84), `receipt_ref`(80), `packet_id`(79), `verdict`(58), `requested_by`(51), `contract_path`/`contract_sha256`(24), `plan_path`/`plan_sha256`(20), `commit`(15), `review_path`/`review_sha256`(4), más claves de una sola aparición (`ref`, `packet`, `receipt`, `outcome`, `amendment`, `artifact_path`, `baseline_*`, `rectified_at`, `criterion`, `disposition`, `closure_*`, `debt_*`). No hay esquema cerrado: **cada script inventa las claves que necesita**.

**Señal de desvío ya visible en el state vigente:** `review_status` sigue conteniendo el veredicto, el reviewer y la disposición de **005-013** (`docs/.cdad-state.json:9-12`, `review_path: docs/specs/005-013-unit-contract/review.md`) mientras `current_stage` es `discovery` y `active_feature` es `005-012` (`:6-7`). El campo quedó **stale**: nadie lo limpia en el cierre. Es el tipo de desvío que la contabilidad del CLI debería hacer imposible o, al menos, detectable.

---

## 3. Piezas que ya existen: qué cubren y qué no (eje 3)

| Pieza | Qué **ya** cubre de una transición | Qué **NO** cubre (el hueco) |
|---|---|---|
| `prepare` (pin por digest + autorización por rol) | Resuelve el contrato y **pinea** su digest; valida autorización específica por rol (`:1413-1486`); publica todo o nada (`_publish_generation`, `:3981-4414`); escribe binding + `active_packet` | No registra ninguna transición de ciclo; no conoce el resto de `stage_history`; no cierra nada |
| `prepare --record-dispatch` (I8) | Registra la **observación** del despacho y **sólo** mueve `prepared→dispatched` (`:2460-2470`); repetición idéntica = idempotente byte a byte, con id reusado y datos distintos = falla cerrado (`:2453-2458`) | No registra resultados ni gates; no puede pasar a `completed`/`failed` (`:2411-2412`); no escribe `stage_history` |
| `receive` / `validate-receipt` / `materialize` | Liga las partes a un **recibo durable** con digests, exigiendo paquete `dispatched` (`cdad_result.py:527-531`); converge byte a byte en un reintento idéntico (`:501-507`, `:434-454`) e **impide sobrescribir** una finalización distinta; materializa con target declarado (create-only/CAS) y `approval_effect:false`; `materialize` re-verifica `semantic_status == "pending"` (`:822-825`) | **No aprueba nada** y **no escribe el state**: deja `state_transition_requested:"received"` pendiente (`:576`). El paso 4 del protocolo —**la transición**— es explícitamente del orquestador (`re-entry.md:57-63`) |
| `validate-state` | Valida binding v2, vigencia (feature abierta, epic, delegación activa y resoluble) y reposo (`:546-600`, `:1558-1624`, `:508-543`) | Es **una foto**, no un registro: no dice qué transición falta, no comprueba entregas requeridas ni aprobaciones por etapa |
| `open-unit` | **La** operación de transición que ya existe: selecciona la unidad por orden del plan, exige reposo, verifica `depends_on`, escribe de forma atómica bajo el mismo lock | Sólo abre. No acepta entregas, no aprueba, no cierra |
| Continuidad (`begin`/`checkpoint`/`reconcile`/`resume`) | `begin`/`checkpoint` congelan goala/decisiones/autoridad/next action con `seq` por ejecución y clave de idempotencia `(execution_id, packet_id, attempt)`; body idéntico bajo la misma clave = **no-op exitoso** (`cdad_continuity.py:636-660`); `reconcile` **clasifica** el trabajo de un paquete leyendo recibo/materialización/journal 002 | `reconcile` **exige `--packet`** (`:1312-1316`): **no hay reconciliación a nivel de ejecución**. `dispatched-unknown` (despacho sin recibo) **no autoriza repetir** y **no** propone una salida (`:984-988`). El CLI nunca escribe el state ni aprueba (`continuity.md:142-144`). La repetición idéntica de un `begin` sólo es no-op **mientras es la cabeza**; tras un append **falla cerrado** (deuda T2-R1, `continuity.md:48-56`) |
| Marcadores (`approval pending`, `packet obsolete`, `state incoherent`) | Vocabulario cerrado, mutuamente excluyente, accionable (`005-001/spec.md:71-73`, PD-12 `:99`; implementados en `:1442-1518`, `:1865`, `:1999`, `:522-540`) | Son diagnósticos de **rechazo**, no de **registro faltante**: hoy «falta registrar la transición» no tiene marcador |
| Vista `status` (005-003/005-011) | Selección explícita de entrada `continuity-reconcile`/`next-unit`/`diagnosis` (`_entry_selection`, `:4736-4752`) y `next.route` que **nombra la operación** natural (`:4755-4778`) | Es read-only y sólo orienta; no registra |

**Frontera con 005-013 (declarada allí):** la reconciliación de un paquete `dispatched` «no se define aquí (005-012)» (`project-execution.md:83-84`; `debt.md:41-43`). Es un pedido explícito, no un descubrimiento nuevo.

---

## 4. Los tres casos reales, en detalle (eje 4)

### 4.1 Caso 1 — 005-011: el cierre sin que la entrega del scribe pasara por `receive`

**Qué pasó (evidencia verificada, no re-medida).** La desviación está declarada en `docs/specs/005-011-common-entry/closure.md:45-47` y en el commit `767de01` (mensaje: «desviación de proceso declarada en el cierre … entrega preservada en el buzón»; `git show --stat 767de01` → **1 archivo, 1 línea: `docs/.cdad-state.json`**).

**Huella dura del conflicto, comprobada en el árbol:**

- `.cdad/executions/exec-005-011-common-entry-001/dispatches/005-011-scribe.json` **existe** (despacho observado, con `packet_id: 005-011-common-entry-scribe-memory-001`).
- `.cdad/runtime/results/exec-005-011-common-entry-001/` **no** contiene el directorio del paquete del scribe: **no hay recibo**.
- La entrega quedó preservada como bytes en el buzón: `.cdad/inbox/at-005-011-scribe-final-text.md` (texto final íntegro del scribe).
- El state quedó con la feature `done` y con `active_packet = {id: 005-011-common-entry-scribe-memory-001, status: "completed"}` **escrito a mano** por `mb-state-005-011.py:76-83` — es decir, el cierre **fabricó** el estado terminal del paquete sin recibo.

**Qué significa exactamente.** `active_packet.status="completed"` + `epic_features[].status="done"` afirman dos cosas que la evidencia no sostiene: que la entrega fue recibida y que el gate de etapa 5 se apoyó en ella. `validate-state` da `VALID` porque **no** comprueba la cadena entrega→recibo→transición (`closure.md:47` lo dice textual: «`validate-state: VALID` **no** demuestra que esa cadena esté completa»). La continuidad, en cambio, sí ve la asimetría: un despacho sin recibo se clasifica `dispatched-unknown` (`cdad_continuity.py:984-988`). Y `reconcile` exige `--packet`, así que la reconciliación **no** puede decir nada a nivel de ejecución (por ejemplo «hay un despacho de esta ejecución sin recibo»).

**Qué comprobación lo habría detectado y dónde actúa.** Una comprobación en **el cierre** (antes de escribir el state) que cruzara: (a) las entregas **requeridas** por el ciclo (los paquetes despachados de la ejecución) contra los **recibos durables** existentes bajo `.cdad/runtime/results/<exec>/<packet>/receipt.json`, y (b) las **aprobaciones** vigentes del gate. Habría fallado cerrado **antes** de aplicar la transición, con la salida explícita de entrega tardía (§6). Actúa **antes** de escribir el state; hoy actúa un juicio humano a posteriori que deja dos relatos incompatibles.

### 4.2 Caso 2 — 005-013: la ejecución huérfana y los registros con scripts sueltos

**Qué pasó.** `docs/specs/005-013-unit-contract/debt.md:58-69` declara los dos hechos; verificados en disco:

- `.cdad/executions/exec-005-013-unit-contract-001/execution.json` **existe y no lo referencia nadie**: no hay paquete con ese `execution_id`, no hay recibo, no está versionado (`git ls-files .cdad/executions/` → vacío). El contexto activo es `…-002`.
- Causa: `open-unit` crea el contexto v2 (`cdad_packet.py:4529-4532`, vía `_bootstrap_v2_execution`) y, **inmediatamente después**, `prepare --new-execution` **ignora** el contexto previo por construcción: `_select_execution` sólo busca un contexto anterior si **no** se pasó `--new-execution` (`:1721-1723`), y `_bootstrap_v2_execution` acuña un id nuevo con `_next_execution_id` (`:1627-1632`). No hay ninguna comprobación de «ya hay un contexto v2 abierto y sin usar».

**Por qué una ejecución huérfana es un defecto (y no sólo un archivo de más).** Lo que distingue dos ejecuciones de la misma feature es **únicamente el sufijo del id** (`…-001` vs `…-002`); nada más. Y **eso importa**, porque el id es la clave de partición de toda la evidencia operativa:

- continuidad: los cuerpos y `head.json` viven por `execution_id` (`cdad_continuity.py:_load_head(root, execution_id)`);
- despachos: `.cdad/executions/<exec>/dispatches/*.json`;
- recibos y materializaciones: `.cdad/runtime/results/<exec>/<packet>/…`.

Una ejecución huérfana es un **punto de partición vacío**: si alguien (o un `prepare` futuro) la toma como activa, la continuidad aparece vacía (`no-checkpoint`), los despachos «desaparecen» y `reconcile` de un paquete que sí tiene recibo puede responder `not-started`. Es el modo exacto en que se fabrican dos relatos: el mismo que el caso 1 deja ver en la continuidad. Además, como no está versionada ni referenciada, **no hay rastro durable** de que existió.

**Qué comprobación lo habría detectado y dónde actúa.** Un control en `prepare --new-execution` (o en la operación de registro) que **detecte un contexto v2 abierto y sin paquetes** y **rechace** nombrando el contexto ya abierto (la condición de cierre que 005-013 pidió, `debt.md:63-64`). Actúa **antes** de escribir (no se acuña el id) — y hoy el CLI, en cambio, escribe sin decir nada.

**El segundo hecho del caso 2** (registros con scripts del orquestador) no es un defecto del state —el state «queda bien y valida»— sino de **trazabilidad**: «el script que lo editó **no queda como evidencia durable**» (`debt.md:65-69`). Es el mismo eje que la fila 12.

### 4.3 Caso 3 — aprobaciones ACUMULATIVAS: una aprobación reemplazada sigue aceptándose

**Qué pasa hoy, en el código.** `_approved_spec_entries` (`cdad_packet.py:1398-1410`) devuelve **todas** las entradas de `stage_history` con `feature`, `stage=="specification"` y `approved_by` no vacío; y la habilitación de los roles de construcción se concede si **alguna** coincide (`:1463-1465`). No hay noción de «entrada vigente» ni de «entrada reemplazada».

**Por qué es un defecto real y no teórico.** 005-013 registró **dos** entradas `specification` (la segunda con una nota que dice, en prosa, que **reemplaza** a la primera: «ESTA APROBACION REEMPLAZA la registrada … aquella queda SUSTITUIDA y no vigente», `docs/.cdad-state.json:4211-4231`). La «sustitución» **no es mecánica**: si alguien presenta el digest de la spec vieja (`4a3da190e2…`), `_contract_approval_for` lo acepta, porque el pin nombra el path y su digest coincide con el archivo que se le presente. El registro durable de la sustitución es **prosa en un `note`** — exactamente la clase de control que el dueño prohíbe («no pidas tests que decidan el significado de un párrafo por listas de palabras»). La nota está para el humano; el CLI no la lee.

**Qué comprobación lo habría detectado.** La aprobación vigente debe ser **una**: la de mayor orden (o la declarada explícitamente como vigente) por `(feature, stage, contract_path)`; una entrada anterior **debe quedar marcada como reemplazada** por un campo estructural al registrarla la operación nueva, no por una nota. Actúa **al registrar la re-aprobación** (escritura), no al leerla.

---

## 5. Repetición tras una interrupción — fila 12 (c) (eje 5)

**Qué hace repetir hoy una transición.** El patrón de `stage_history` es **append-only** y no tiene clave de idempotencia: no hay campo que identifique «la misma transición». Un script propio re-ejecutado **duplica**: si el proceso murió después de escribir el state y se reintenta, se apila una segunda entrada idéntica (dos entradas con el mismo `stage`, `packet_id` y `at`), y nada lo detecta porque nadie lee `stage_history` con semántica de transición.

**Dónde la repetición ya es segura hoy:**

- `--record-dispatch`: byte-idéntico → no-op; mismo `attempt_id` con datos distintos → falla cerrado sin sobrescribir (`:2453-2458`).
- `receive`: con recibo durable previo, un reintento idéntico converge al **mismo recibo byte a byte** y el paquete puede haber avanzado ya (`cdad_result.py:501-507`, `:581-588`); un resultado **distinto** bajo la misma identidad falla cerrado (`:434-454`).
- `materialize`: journal por target con CAS/create-only; repetir converge y **no duplica** el efecto.
- `open-unit`: con una unidad ya abierta, **rechaza** sin escribir (`:4500-4504`).
- continuidad: clave de idempotencia `(execution_id, packet_id, attempt)`; body idéntico bajo la misma clave = **no-op** (`cdad_continuity.py:636-660`) — pero sólo **mientras esa clave es la cabeza**: tras el append de la siguiente, un `begin` idéntico **falla cerrado** (deuda T2-R1 declarada, `continuity.md:48-56`).

**Lo que falta, con precisión.** Para la transición de state no hay **ninguna** de esas tres cosas: ni clave de idempotencia, ni detección de duplicado, ni convergencia. `seq` es de la continuidad (un contador por ejecución, no por transición). `checkpoint` también exige la misma clave: no sirve como registro de la transición de etapa. Y `reconcile` **exige `--packet`**, así que «¿esta transición ya se aplicó?» no tiene hoy una respuesta a nivel de ejecución.

**Implicación para el diseño (planteada, no decidida).** Fila 12 (c) pide que repetir sea **no duplicar** y que una repetición **idéntica** se distinga de una transición **nueva**. Con las piezas de hoy eso exige, como mínimo: una **clave de identidad de la transición** (por ejemplo el par `(execution_id, packet_id, stage)` o un `attempt` declarado) y una **detección de la ya registrada** que devuelva el registro existente (no-op) en vez de apilar. La regla de dos intentos encaja donde ya vive: `re-entry.md:79-87` (un reintento responde a hipótesis/información nueva; la repetición idéntica sin información nueva dispara revisión de estrategia, no un tercer intento).

---

## 6. Entrega tardía después de una feature cerrada — fila 12 / entrega (eje 6)

**Qué permite y qué impide hoy el CLI, verificado:**

- `CLOSED_FEATURE_STATUSES = {"done","cancelled","canceled","closed","archived"}` (`cdad_packet.py:114`), aplicado en `_active_feature_entry` (`:1534-1538`), que se alcanza desde `_validate_v2_vigency` (`:1580`).
- `receive` llama a `validate_request` (`cdad_result.py:513`), que llama a `validate_state` (`cdad_packet.py:768`): con la feature cerrada **falla cerrado**.
- `materialize` llama a `validate_state` directamente (`cdad_result.py:841-842`): **también falla cerrado**.
- `prepare` en reposo (`active_feature: null`) no puede bootstrap: `_bootstrap_v2_execution` exige `active_feature` no nulo (`:1638-1640`).

O sea: **hoy el CLI no ofrece ninguna salida** para registrar una entrega tardía de una feature cerrada. La única salida que existió fue **manual y fuera del protocolo**: dejar los bytes en el buzón (`.cdad/inbox/at-005-011-scribe-final-text.md`) y declararlo en prosa en `closure.md:45-47` y en el commit `767de01`.

**Qué tiene que significar «registrar una entrega tardía sin reabrir»** (requisito de la review de Codex, `execution.md:85-88`): la operación

- **NO** cambia el estado de la feature (sigue `done`; no la reabre ni la pasa a `in-progress`);
- **NO** aprueba nada (el recibo sigue `semantic_status: pending`; no habilita roles ni gates);
- **deja traza** durable (recibo + referencia en el state o en un registro de la ejecución, según decida el draft).

**Decisión planteada (no tomada aquí).** ¿El buzón `.cdad/inbox/` **es** la salida y sólo hace falta *una operación que la reciba* (persistir el recibo y la traza) —lo que conservaría `receive` como está y le daría una puerta legítima sobre una feature cerrada—, o hace falta una operación **distinta** (una «recepción tardía» con su propio marcador)? La primera reusa todo lo verificado; la segunda crea una superficie nueva. Es el punto que la review de Codex llama «salida explícita» y que hay que resolver en el brainstorm.

---

## 7. Autoridad y juicio: la frontera que el CLI no puede cruzar (eje 7)

**Quién aprueba hoy.** El **orquestador OpenCode** bajo la `hitl_delegation` del epic-005: `delegated_to` = orquestador, `scope` = «alcance aprobado del epic, specs y planes de sus features, priorización de reviews, gates y aprobación de Memory Bank con evidencia», `expires` = al cerrar/cancelar/revocar el epic, `source` = `docs/epics/epic-005-real-operation/execution.md` (`docs/.cdad-state.json`, clave `hitl_delegation`; verificado contra `execution.md:8-23`). Reservado al dueño, siempre: activar versiones en el repo real, cambios en HOME, confianza de carpeta, cambios de alcance/criterios (`execution.md:19-23`).

**Cómo se registra:** `stage_history[].approved_by` (192 entradas lo traen), `approver` (state), `hitl_delegation` (state, verificado por `_validate_v2_vigency`), `execution.authority_ref` (apunta a `execution.md`), y el `by` de cada entrada (rol que produjo) más el `requested_by` (quién pidió).

**Qué puede comprobar el CLI por sí solo** (todo esto es mecánico y ya existe en parte):

- que la **evidencia referenciada exista** y que su **digest coincida** (es lo que ya hace con el contrato, `:1427-1486`, y con las partes del recibo, `cdad_result.py:550-578`);
- que la **autoridad vigente** exista y no esté revocada/vencida (`:1593-1624`), y que quien la ejerza sea quien el registro nombra;
- el **orden de etapas** (stage/substage válidos, `ROLE_SUBSTAGES`, `:60-66`) y que el paquete que la transición cita esté en el estado correcto (`prepared`/`dispatched`);
- las **entregas requeridas** (paquetes despachados de la ejecución) frente a los **recibos** existentes (hoy sólo lo hace `reconcile`, y por paquete);
- **cuál es la aprobación vigente** cuando hay varias (hoy no lo hace: §4.3).

**Qué NO puede y sigue siendo juicio del orquestador** (frontera explícita, coherente con el criterio del dueño y con `re-entry.md:249-255`):

- el **significado** de un texto (una spec, un plan, un `closure.md`) y la **calidad** de una entrega;
- si un bloqueante es bloqueante, si una deuda se acepta, si la priorización del reviewer es correcta (`re-entry.md:219-226`);
- si una entrega tardía **sirve** para algo (el CLI la registra; no la interpreta);
- toda decisión de alcance/autoridad reservada al dueño.

El CLI no debe, por tanto, decidir por listas de palabras ni por prosa: **estructura y digests sí; sentido de un párrafo, no**.

---

## 8. Cómo escribe hoy el state el CLI (para reusar el escritor único) (eje 8)

**Dónde están las escrituras:**

- `_ProjectLock` (`:1257-1380`): `flock` sobre `.cdad/.lock` (rendezvous **permanente**), con recuperación de transacciones previas.
- `_serialize_document` (`:2235-2240`): única serialización (`json.dumps(ensure_ascii=False, indent=2) + "\n"`). Nota: `--record-dispatch` serializa el state con una llamada **distinta** y equivalente (`:2472`).
- `_publish_owned_atomically` (`:2243-2266`): escribe temporales y `os.replace` uno por uno; usado por `open-unit`.
- `_publish_generation` (`:3981-4414`): la publicación **transaccional** de `prepare`/`--replace-packet`, con staging bajo `.cdad/.txn/<packet_id>` y manifiesto propio (nunca toca entradas ajenas); registra exactamente los archivos que escribió para el rollback.
- Las dos funciones que **ya registran** una transición: `open-unit` (`:4485-4551`) y `--record-dispatch` (`:2401-2483`).

**Qué es `active_packet` y su ciclo de vida.** Es el **único** paquete en vuelo (paralelismo fuera de alcance): `None` en reposo → `prepared` (`prepare`) → `dispatched` (`--record-dispatch`) → **`completed`/`failed`** — pero **nadie del CLI escribe `completed`/`failed`**: lo escribe el orquestador a mano al registrar la transición (por ejemplo `mb-state-005-011.py:76-83`). `VALID_PACKET_STATUSES` (`:44`) incluye los cuatro; `ACTIVE_PACKET_STATUSES` (`:115`), sólo los dos primeros. `_validate_idle_coherence` (`:508-543`) impide el reposo con un paquete en vuelo y exige `active_feature is None ⟺ current_stage == "idle"` (invariante cuyo dueño editable es `state-detection.md:34-37`).

**Qué parte del state NO toca nunca el CLI:** `stage_history`, `epic_history`, `postconditions_status`, `audit_status`, `review_status`, `approver`, `hitl_delegation`, `delegation_history`, `epic_stage`, `last_updated`, y `epic_features[].{status="done",closed_at,closure_evidence}` (§2).

**Trade-off de la superficie (planteado, no decidido — eso es el draft):**

| Forma | Problema que resuelve mejor | Límite / costo |
|---|---|---|
| **Subcomando nuevo** (p. ej. un `register-*` con `--stage/--packet`) | una sola superficie explícita, descubrible por `--help`, con su propio contrato y sus tests; simétrica a `open-unit` (que la fila 12/D-3 de 005-007 pide como espejo) | crece la interfaz; hay que decidir si valida cada etapa o una forma común; riesgo de convertirse en «segunda copia» de las reglas de cada etapa |
| **Subetapa de un comando existente** (p. ej. `prepare --record-transition`) | reusa el lock, la transacción y las validaciones que ya corren; menos superficie | `prepare` es el **productor de paquetes** (invariante 1); mezclar registro de transiciones cambia su rol y complica sus invariantes |
| **Operación dedicada sólo a la transición de la entrega** (extender `receive`/`materialize` o una «recepción tardía») | ataca el hueco más caro (el paso 4 del protocolo hoy es a mano) y el caso de la entrega tardía con la misma máquina | no cubre RED/GREEN/review/cierre, que son el resto del costo |
| **Contabilidad mínima en el CLI + operación para la transición** | cubre el ciclo completo y conserva el juicio | es la opción más grande; exige decidir dónde vive la **verificación de entregas requeridas** (¿en el cierre, en el registro, o en los dos?) |

---

## 9. Costo operativo reducido — medido sobre los ciclos reales (eje 9)

**Pasos manuales por transición (patrón real de 005-013, el ciclo cerrado más reciente):**

| Transición | Pasos propios de hoy | Qué se elimina si el CLI contabiliza |
|---|---|---|
| RED/GREEN de una tarea | escribir/ajustar un `register-*.py` (~50-60 líneas), correrlo, verificar el diff del state, commitear | el script entero: la transición pasa a ser una invocación con la evidencia |
| Review | script propio + copiar veredicto/buckets/paths/digests a `review_status` y a la entrada | el script; los campos derivables de `review.md` dejan de transcribirse a mano |
| Re-aprobación | script propio que además **declara en prosa** que reemplaza a la anterior | la prosa pasa a ser estructura (campo de vigencia) |
| T4 + gate | dos scripts propios (`-register-t4.py` cubre dos entradas) | idem |
| Memory Bank | `mb-state-005-013`/`mb-state-005-011.py` (95 líneas) + deltas de Memory Bank a mano | idem |
| Cierre | `005-013-register-closure.py` (57 líneas): apaga `active_feature`, fija `idle`, marca `done`, calcula digests | idem **y** se gana la comprobación de entregas/aprobaciones antes de aplicar (caso 1) |
| **Total glue del ciclo** | **751 líneas** en 7 scripts (`.cdad/local/`: `005-013-register-*.py` × 6, `register.py`, `stage3.py` 253, `flow-005-0xx.sh`, `mb-*-005-0xx.py`, `receive-*.sh`) | la parte de registro; `stage3.py` —el driver de despacho— **no** se elimina (hace prepare/validate/begin/record-dispatch/receive/materialize, que el CLI ya ofrece pero nadie encadena) |

**Lo que la fila 12 pide NO es más control, es menos trabajo.** La mejora se juzga por pasos manuales eliminados. Dos precauciones que el diseño debe respetar, tomadas del propio historial: (a) **no** compensar con «mantenimiento documental» (el caso 3 muestra que una nota en prosa no es un control: es deuda); (b) **no** añadir una segunda copia de reglas que ya viven en su dueño (§12). El punto de la review de Codex sobre el **cierre** (comprobar entregas y aprobaciones *antes* de aplicar) es el único control nuevo pedido, y es **el que elimina** el trabajo del caso 1 (dejar de fabricar a mano un `completed` que la evidencia no sostiene).

---

## 10. Aceptación disponible (eje 10)

**El patrón ya existe y está probado** (`docs/specs/005-013-unit-contract/acceptance.md:7-20`; `tests/product_staging.py`; `tests/test_004_002_t2_bootstrap.py:44-70`; `tests/test_005_007_t3_open_unit.py:20-41,236-241`):

- **Instrumento:** el CLI **real del repo** corrido como **subproceso** (`python3 skills/cdad-cycle/scripts/cdad_packet.py …`), sobre un **proyecto descartable** creado en `<tmp>`, con el **`HOME` del subproceso en un tempdir vacío**. **Nunca este repo, nunca HOME.**
- **Fixture mínimo ya probado** (buildable, offline): `docs/cdad-policy.json` válida; `.cdad/executions/<id>/execution.json` (v2 con snapshot de política); `.cdad/packets/<id>/{REQUEST.json,PACKET.md}`; `docs/.cdad-state.json` con `epic_features`/`epic_history`/`stage_history`/`hitl_delegation` y una `source` de autoridad existente; un plan del epic con la fila de la unidad.

**Plan de aceptación proporcional (productor → actor → evidencia):**

| Caso | Insumo y su productor | Actor que evalúa | Evidencia de cierre |
|---|---|---|---|
| **AC-1 — un ciclo representativo registrado SOLO con la operación nueva** | el **orquestador** produce el proyecto descartable y corre las invocaciones del CLI real; los paquetes/entregas son del fixture (dispatched + recibo reales vía `receive`) | el **orquestador** (HITL delegada) verifica `git diff` del fixture = **sólo** lo que escribió el CLI, `validate-state` verde, y **cero** ediciones manuales (comprobable: el state es byte a byte el producido por el CLI) | informe de la corrida + salida pegada + `sha256` del state antes/después |
| **AC-2 — entrega tardía sobre feature cerrada** | **orquestador** cierra el fixture con la operación nueva y luego entrega un texto final por el buzón | **orquestador** verifica: la feature **sigue `done`**, `semantic_status: pending`, **ninguna** aprobación nueva, y **hay traza** durable | recibo + entrada de traza + state con la feature sin cambios |
| **AC-3 — repetición tras una interrupción** | **orquestador** interrumpe entre la escritura y el commit (o repite la invocación idéntica) | **orquestador** verifica: **una sola** transición (no dos entradas), convergencia al mismo registro, y que una transición **distinta** sí se distingue | conteo de entradas de `stage_history` del fixture + bytes del state |
| **AC-4 — el cierre comprueba entregas y aprobaciones ANTES de aplicar** | **orquestador** reproduce el caso 1 (despacho sin recibo) y el caso 3 (aprobación reemplazada) en el fixture | **orquestador** verifica el **rechazo con diagnóstico que nombra la entrega/la aprobación faltante** y que el state **no** cambió | salida del rechazo + `rc` + state byte-idéntico |

**Lo que NO se puede prometer todavía (desconocido, declarado):** cuántas invocaciones tendrá el recorrido completo; si la operación nueva debe cubrir **todas** las etapas o sólo el subconjunto con evidencia mecánica; y si el fixture mínimo necesita además un **plan del epic del producto** (con anclas) para el pin de unidad — hoy no hay ciclo representativo del **path** de registro, sólo ciclos reales.

---

## 11. Frontera y fuera de alcance (eje 11)

- **No se amplía el alcance** a las candidatas de `execution.md:89-96`: *adopción de versión entre ciclos* (RD-a) y *estado operativo compacto con historia durable* (RD-b). **No tienen unidad ni prioridad** (decisión del dueño, 2026-10-13, `execution.md:78-79`). RD-b es la que **explicaría** el tamaño del state (90,7 % en `stage_history`, §0.3), pero es otra unidad: acá sólo se la cita como medida.
- **No se reabren** los contratos de 005-003/005-005/005-007/005-011/005-013 (`plan.md:141-154`, `docs/specs/005-011-common-entry/plan.md:46-48`).
- **La tabla de consecuencias por tipo de cambio de 005-013** (PD-6..PD-11, `docs/specs/005-013-unit-contract/spec.md`) **no es esta operación**: acá es contexto de la frontera «reconciliación de un paquete `dispatched` → 005-012» (`project-execution.md:83-84`, `debt.md:41-43`).
- **Fuera explícitamente:** CI, sandbox, plataforma de jobs, paralelismo (`active_packet` único), tocar HOME, push, despliegue.
- **Frontera de rol:** el CLI **no** decide el sentido de un texto (§7); el architect **no** aprueba su propia propuesta.

---

## 12. Fuente única (eje 12)

La spec de 005-012 **no** debe agregar una segunda copia de ninguna regla existente. Todo lo que hace falta **ya tiene dueño**, y la operación nueva debe **referenciar**:

- **vista compacta y selección de entrada** → `docs/specs/005-003-orientation-reduction/spec.md:109-120` (`entry` ∈ {`continuity-reconcile`,`next-unit`,`diagnosis`}) y su implementación `_entry_selection`/`_next_route` (`cdad_packet.py:4736-4778`);
- **protocolo de materialización y transición** → `re-entry.md:14-63` (hoy declara el paso 4 como del orquestador; la operación nueva **cambia ese paso**, no lo duplica: `re-entry.md` pasaría a **nombrar la operación**);
- **idempotencia y reconciliación** → `continuity.md:17-21,48-60` (y su deuda T2-R1 declarada);
- **procedencia** → `docs/specs/005-005-adoption-coherence/…` por referencia (versión/activación), sin re-declarar;
- **autoridad** → `execution.md` (HITL) y `_validate_v2_vigency`;
- **forma del state** → `state-detection.md:20-37` + `assets/state-template.json`;
- **planificación por unidad** → `docs/specs/005-007-progressive-planning/…` (D-3/`debt.md:11` es el pedido de simetría con `open-unit`).

Regla operativa: **toda extensión es aditiva y declarada**; ninguna sección de la spec de 005-012 reescribe el texto de sus dueños.

---

## 13. Recorrido de uso concreto, punta a punta (el caso real: registrar un GREEN y cerrar)

**Hoy — GREEN de una tarea (005-013 T1, evidencia en el state `:4232-4252`):**

1. `prepare --role implementer --substage green …` → paquete + `active_packet{status:"prepared"}` (CLI).
2. `validate-state` / `validate-request` / `validate-packet` (CLI).
3. `begin` con `--update` (continuidad) → checkpoint con `seq` (CLI).
4. `--record-dispatch` con la observación → `active_packet{status:"dispatched"}` (CLI).
5. El implementer corre y devuelve su texto final + evidencia (harness).
6. El orquestador **stagea** los bytes en `.cdad/inbox` y **escribe el descriptor a mano**.
7. `receive` → recibo durable, `semantic_status: pending`, `state_transition_requested: "received"` (CLI).
8. `materialize` con autorización (CLI) → copia los artefactos a su target.
9. **`.cdad/local/005-013-register-tdd.py <sha> <note>`** → **escribe a mano**: `stage_history += {stage:"tdd-green-t1", by, packet_id, packet_sha?, evidence: commit, dispatch_ref, receipt_ref, artifacts{}}`, `active_packet.status="completed"`, `postconditions_status`, `last_updated`.
10. Commit del orquestador con la evidencia.

**Paso 9 es exactamente el hueco**: un script de 49-63 líneas por transición, que **no queda como evidencia durable** (`debt.md:65-69`) y que **nada verifica** (ni la entrega, ni la aprobación, ni la duplicación).

**Hoy — cierre de feature (005-013, `005-013-register-closure.py`):**

1. Gate T4 aprobado (entrada escrita a mano por `005-013-register-t4.py`).
2. Review formal (entrada a mano por `005-013-register-review.py` + `review_status`).
3. Memory Bank: si el scribe falla el camino (caso 1), la entrega queda en el buzón **sin recibo**.
4. Suite de cierre una vez, por quien cierra (declarado: `acceptance.md:34`).
5. `005-013-register-closure.py <closure_sha> <debt_sha> <note>` → **a mano**: `stage_history += feature-closure`; `epic_features[005-013].status="done"` + `closed_at` + `closure_evidence`; `active_feature=null`; `current_stage="idle"`; `postconditions_status={}`; `active_packet=null`; `last_updated`.
6. Commit `docs(005-013): cierre …`.

**Nada del paso 5 comprueba** que las entregas requeridas tengan recibo (caso 1) ni que la aprobación vigente sea la última (caso 3). **Y el paso 5 tampoco limpia** campos como `review_status`, que hoy sigue apuntando a 005-013 mientras la feature activa es 005-012 (`docs/.cdad-state.json:9-12` vs `:6-7`).

**Recorrido deseado (dirección, no contrato):** pasos 1-4 idénticos (son del CLI), **paso 6-8** con el descriptor producido mecánicamente (la deuda D-10 de 005-004 pide «recepción de intervención cero»), y **pasos 9 y 5** reemplazados por **una invocación** que (i) compruebe la evidencia referenciada, (ii) compruebe las entregas/aprobaciones requeridas antes de aplicar, (iii) escriba el state en la forma existente con la transacción y el lock que ya existen, y (iv) no duplique si se repite.

---

## 14. Comparación de enfoques (qué problema resuelve cada uno, fuentes y límites)

| Enfoque | Problema que resuelve | Fuentes que lo sostienen | Límite |
|---|---|---|---|
| **A. Sólo documentar el protocolo** (que el orquestador siga escribiendo, pero con un procedimiento único) | el desvío por improvisación | `re-entry.md:57-63` ya lo documenta | **no reduce trabajo**: los 751 líneas de glue siguen; el caso 3 muestra que la prosa no controla nada |
| **B. Una operación nueva «registrar transición»** (subcomando del CLI, escritor único, idempotente) | el 90 % del costo manual (pasos 9/5) y la falta de traza durable | `open-unit` es el precedente exacto y su deuda D-3 pide la simetría (`005-007/debt.md:11`); el escritor único ya existe (`_ProjectLock`, `_publish_generation`) | hay que decidir **qué** comprueba cada etapa sin convertirse en un juez semántico; riesgo de superficie grande |
| **C. Extender la recepción** (`receive`/`materialize` + recepción tardía) | el paso 4 del protocolo (hoy manual) y la entrega tardía | `cdad_result.py` ya tiene recibo durable, convergencia e identidad con el paquete (`:501-531`); el buzón ya preserva los bytes (`.cdad/inbox/at-005-011-scribe-final-text.md`) | **no** cubre RED/GREEN/review/cierre; el `state_transition_requested` seguiría sin aplicarse |
| **D. Contabilidad de entregas en el cierre** (comprobar antes de aplicar) | **exactamente** el caso 1 y el requisito de Codex (`execution.md:85-88`) | `debt.md:41-43` + `closure.md:47` lo piden; `reconcile` ya clasifica despacho-sin-recibo (`cdad_continuity.py:984-988`) | si sólo se hace esto, el trabajo manual del resto del ciclo **no baja**: no cumple el criterio del dueño por sí solo |
| **E. Marca estructural de vigencia de aprobaciones** | el caso 3 (acumulativas) | `_approved_spec_entries` (`:1398-1410`) + la nota en prosa del state (`:4211-4231`) | toca una regla **existente** (005-001 D3/PD-18): hay que hacerlo **aditivo y declarado**, sin re-declarar el pin |
| **F. Reconciliación a nivel de ejecución** (además de `--packet`) | el caso 2 (huérfana) y «repetir tras interrupción» | `reconcile --packet` es hoy obligatorio (`cdad_continuity.py:1312-1316`); `continuity.md:17-21` declara el alcance por paquete | es una pieza de la continuidad, no de la contabilidad del state: hay que decidir si va acá o queda declarado |

**Conclusión de la comparación:** ninguna pieza sola cumple la fila 12. **D + E** atacan los dos defectos declarados (caso 1, caso 3) y son las que eliminan trabajo en el **cierre**; **B** (o C) es la que elimina trabajo en **todo el ciclo**. La discusión útil del brainstorm es **cuál es el mínimo que reduce el trabajo sin agregar controles frágiles**, y si B se acota a un registro genérico o se acepta que cubra sólo las transiciones con evidencia mecánica.

---

## 15. Propuesta mínima elegida (dirección — el contrato es del draft)

**Dirección elegida: una operación del CLI que registre la transición del orquestador, con la contabilidad mecánica mínima y el juicio intacto.** En concreto, y en este orden de prioridad:

1. **Una operación de registro** (subcomando del CLI, con el escritor único: `_ProjectLock` + `_publish_owned_atomically`/`_publish_generation`) que:
   - reciba la **decisión explícita** del orquestador (etapa/subetapa y la evidencia referenciada);
   - **exija la evidencia referenciada** (recibo durable del paquete citado — o el artefacto materializado — con su digest);
   - aplique la transición en la **forma existente** de `stage_history` + campos derivados, **sin esquema nuevo**, y sin escribir nada que el juicio reserve (§7);
   - sea **idempotente**: una repetición idéntica **no** duplica y se distingue de una transición nueva (§5).
2. **Comprobación en el cierre**: antes de aplicar la transición de cierre, verificar las **entregas requeridas** (paquetes despachados de la ejecución con recibo) y la **aprobación vigente**; si falta algo, **fallar cerrado nombrando la entrega/la aprobación** y ofrecer la salida del punto 3.
3. **Salida explícita de entrega tardía**: registrar una entrega de una feature cerrada **sin reabrir, sin aprobar, dejando traza** (§6).
4. **Vigencia estructural de la aprobación** al re-aprobar (una sola vigente por `(feature, stage, contract_path)`), **aditivo y declarado** sobre la regla D3/PD-18 existente (§4.3, §12).
5. **Documentar por referencia**: `re-entry.md:57-63` (paso 4) y la tabla de operaciones de `project-execution.md` pasan a **nombrar** la operación; no se copia la regla.

**Lo que la propuesta NO hace (deliberado):** no decide el sentido de un texto, no juzga la calidad de una entrega, no parsea prosa, no abre la puerta a `active_packet` múltiple, no toca CI/HOME/push/despliegue, y **no** entra en las candidatas RD-a/RD-b.

---

## 16. Plan legible por el humano

**Objetivo.** Que registrar una transición del ciclo —una entrega, una aprobación de gate, un avance de etapa, un cierre— deje de ser un script propio que edita el state, y pase a ser una operación del CLI que **comprueba los requisitos, aplica la transición de forma consistente y no duplica efectos**, conservando el juicio del orquestador. Se juzga por **trabajo manual menos**, no por controles más.

**Recorrido.** Discovery/draft con el architect → aprobación y registro (HITL delegada) → TDD con la operación nueva y sus comprobaciones → review formal → aceptación con el CLI real sobre proyecto descartable (AC-1..AC-4) → Memory Bank → cierre. (El detalle de tareas es del draft.)

**Unidades y orden (borrador de descomposición, a cerrar en el draft).**

| Orden | Unidad candidata | Por qué así |
|---|---|---|
| U1 | **La operación de registro** (superficie + escritura única + forma existente del state) | sin esto no hay nada que comprobar; es la que elimina el trabajo de todos los pasos manuales |
| U2 | **Idempotencia y distinción de repetición** (clave de identidad + no-op) | depende de U1; es fila 12 (c) y evita el daño de un reintento |
| U3 | **Comprobación de entregas y aprobaciones en el cierre** (caso 1 + requisito de Codex) | depende de U1; es el único control nuevo pedido y el que elimina el «completed fabricado» |
| U4 | **Entrega tardía sin reabrir** | depende de U1/U3; usa la misma máquina y el buzón ya existente |
| U5 | **Vigencia estructural de la aprobación** (§4.3) | transversal y aditiva sobre D3/PD-18; puede ir en la misma unidad que U1 si comparten archivo, o serializarse |
| U6 | **Documentación por referencia** (`re-entry.md` paso 4 y tabla de operaciones) | cierra la frontera §12; sin ella la regla queda en dos lugares |
| U7 | **Aceptación (gate)** | no es RED/GREEN de producto: es la prueba decisiva sobre proyecto descartable |

**Decisiones que el draft debe tomar (no las tomó el discovery):** la **forma de la superficie** (§8, cuatro opciones con su trade-off); si la operación cubre **todas** las etapas o un subconjunto con evidencia mecánica; **dónde** vive la comprobación de entregas (¿en el cierre, en el registro, o en ambos?); si la **reconciliación a nivel de ejecución** entra o se declara como deuda; y si la **vigencia** se implementa como campo nuevo en `stage_history` o como estado del paquete.

**Riesgos (con su mitigación declarada).**

| Riesgo | Consecuencia | Mitigación en el diseño |
|---|---|---|
| **Superficie grande / «segundo productor»** | duplicar el camino de recepción/registro (lo que 005-004 PD-10 prohíbe explícitamente) | reusar `receive`/`materialize` y el escritor único; no crear una segunda máquina de recibos |
| **Convertirse en juez semántico** | tests que deciden el sentido de un párrafo | admitir sólo estructura/digests/orden/entregas (§7) |
| **Fragilidad ante el estado histórico** | 415 entradas y claves ad hoc: una validación estricta rompería el state vigente | sólo **aditivo**: no exigir campos a las entradas viejas |
| **Drift de instalación** | la operación no existe hasta el despliegue (005-013 O3) | declararlo y diseñar sobre HEAD (§0.1); la aceptación corre el CLI **del repo** |
| **Prosa como control** | repetir el caso 3 con una nota nueva | prohibir que una nota sea la única traza de una sustitución |
| **`stage_history` crece (90,7 %) y la lectura completa cuesta** | el estado operativo se vuelve pesado (RD-b, fuera de alcance) | no empeorarlo: la entrada nueva debe ser **pequeña** y no agregar copias |
| **Continuidad fail-closed tras append** | «repetir tras interrupción» puede quedar bloqueado (T2-R1) | reconocer el límite y declararlo, en vez de prometer una idempotencia que la continuidad no da a nivel de ejecución |

---

## 17. Plan de aceptación proporcional (resumen ejecutable)

**Instrumento:** CLI real **del repo** como subproceso (`python3 skills/cdad-cycle/scripts/cdad_packet.py …`) sobre proyectos descartables en `<tmp>`, `HOME` del subproceso en tempdir vacío. Nunca este repo, nunca HOME. Arnés **fuera de git** (precedente: `.cdad/local/005-013-t4-acceptance.py`) con evidencia cruda en `.cdad/local/` (no versionada).

**Insumos y quién los produce:**

| Insumo | Productor |
|---|---|
| Proyecto descartable (política, plan del epic, `epic_features`, `hitl_delegation`, autoridad) | orquestador (fixture) |
| Paquete + despacho + recibo reales (camino legítimo del CLI) | orquestador, con el CLI |
| Entrega tardía (texto final por el buzón) | orquestador |
| Interrupción/reintento (matar entre la escritura y el commit, o repetir la invocación) | orquestador |
| Reproducción del caso 1 (despacho sin recibo) y del caso 3 (aprobación reemplazada) | orquestador (fixture dirigido) |

**Actor que evalúa:** el **orquestador** bajo la HITL delegada del epic-005 (`execution.md:10-12`); la **review formal** (etapa 4) juzga el contrato y el sentido de los textos, no los tests.

**Evidencia de cierre:** salida pegada de cada invocación con `rc`; `sha256` del state antes/después de cada caso; **conteo de entradas** de `stage_history` (para AC-3); `git diff --name-only` del fixture (para AC-1: sólo lo que escribió el CLI); informe del cierre.

**Desconocido que se conserva como desconocido:** el número de invocaciones del recorrido completo, el alcance exacto de la operación por etapa, y si el fixture necesita el plan del epic **con anclas** para el pin de unidad. No se promete ningún ahorro fuera de lo que se mida al cierre.

---

## 18. Medidas disponibles / desconocidos declarados

**Medido en este discovery** (método reproducible, §0.3): 578.926 B de state; 525.285 B (90,7 %) en `stage_history`; 415 entradas; 15 entradas de 005-011 y 15 de 005-013 con sus nombres de `stage`; 13 scripts propios que editan el state; 751 líneas de glue en 7 scripts; 6 scripts de registro para 005-013; instalado == `7212ead` (sha `776d1168…`) ≠ HEAD (sha `1f06855f…`); diff de producto `7212ead..HEAD` = 3 archivos.

**Citado, no re-medido** (declarado así en el encargo): la caída de llamadas/tiempo de la entrada común (005-011, `closure.md:17-21`); el costo de la entrada al proceso (005-007 `acceptance.md:110-151`); el recuento de 19 operaciones de estado en el cierre de 005-007 (`005-007/debt.md:11`); la suite 927 passed / 4 skipped de 005-011 (`closure.md:21`) y 960 passed de 005-013.

**Desconocido (declarado, no estimado):**

- **Cuánto bajaría el trabajo**: no se puede predecir sin construir la operación; se medirá por pasos/scripts eliminados en el próximo ciclo real (§9), no por una sonda sintética.
- **Si el path de registro puede cubrir las once transiciones** con evidencia mecánica homogénea, o si algunas (review/priorización, Memory Bank) quedan con juicio puro y sólo ganan traza.
- **El efecto del tamaño del state** sobre la operación nueva (RD-b mide, no resuelve).
- **La reconciliación a nivel de ejecución**: no existe hoy; su necesidad real se verá con la repetición tras interrupción (AC-3).
- **El `review_status` stale y otras claves huérfanas**: hoy no hay inventario de campos derivados sin dueño; el discovery lo señala pero no lo cuantifica.

---

## 19. Dudas acotadas para el brainstorm (no es el contrato)

1. **Superficie:** ¿un subcomando `register-*` nuevo, o extender `receive`/un comando existente? (§8/§14B-C). La recomendación técnica del discovery es **subcomando** (simetría con `open-unit`, escritor único, descubrible) — **decisión del dueño/orquestador**.
2. **Alcance por etapa:** ¿la operación cubre **todas** las transiciones, o sólo las que hoy tienen evidencia mecánica (entrega, gate, cierre) y las demás sólo ganan traza? El caso 1 y el caso 3 se cierran con las últimas.
3. **Entrega tardía:** ¿el buzón `.cdad/inbox` **es** la salida y sólo falta la operación que lo reciba, o hace falta una operación distinta con su propio marcador? (§6).
4. **Comprobación de entregas:** ¿en el cierre (antes de aplicar), en el registro, o en ambos? (§14D).
5. **Vigencia de aprobaciones:** ¿campo nuevo en la entrada de `stage_history`, o estado del paquete/proyección? Y ¿el registro de la re-aprobación **marca** la anterior, o la vigencia se **deriva** del orden? (§4.3 — lo aditivo sobre D3/PD-18 exige declararlo).
6. **Repetición:** ¿cuál es la clave de identidad de una transición (el par ejecución+paquete+etapa, o un `attempt` declarado)? ¿Y qué debe hacer la repetición **distinta** (falla cerrado o se registra como nueva)? (§5).
7. **Reconciliación a nivel de ejecución:** ¿entra en esta feature o se declara deuda con condición de cierre, dado que `reconcile` exige `--packet`? (§5).
8. **Frontera de 005-013:** el discovery lee `debt.md:41-43` («la reconciliación de un `dispatched` es territorio de 005-012») — ¿el alcance incluye **nombrarla** al menos (diagnóstico) o sólo declararla?

---

## 20. Evidencia de ejecución

**Archivos modificados del repo:** **ninguno** (rol de sólo lectura). `git status --porcelain` previo mostraba ` M docs/.cdad-state.json` (cambio **ajeno** a esta ejecución: es el registro del dispatch del propio paquete por el orquestador, hecho antes de despacharme). No edité ningún archivo: mi única escritura es el archivo de transporte `/tmp/opencode/005-012-discovery.md`.

**Comandos exactos ejecutados** (todos desde `<repo>`, sólo lectura; ninguno escribe el repo):

```
git log --oneline -8 ; git status --porcelain ; git rev-parse HEAD
git diff --stat 7212ead..HEAD
sha256sum <home>/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py
git show 7212ead:skills/cdad-cycle/scripts/cdad_packet.py | sha256sum
sha256sum skills/cdad-cycle/scripts/cdad_packet.py
grep -c "UNIT-CONTRACT.md" <home>/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py   # 0
grep -c "UNIT-CONTRACT.md" skills/cdad-cycle/scripts/cdad_packet.py                           # 2
python3 skills/cdad-cycle/scripts/cdad_packet.py --help
grep -n "^def \|^class \|add_parser" skills/cdad-cycle/scripts/cdad_packet.py | head -250
grep -n "stage_history" skills/cdad-cycle/scripts/{cdad_packet,cdad_result,cdad_continuity}.py
ls .cdad/executions/exec-005-011-common-entry-001/dispatches/ ; ls .cdad/runtime/results/exec-005-011-common-entry-001/
find .cdad/executions/exec-005-013-unit-contract-001 -type f ; ls .cdad/inbox/ | grep 005-011
git show --stat --oneline 767de01
python3  # medidas: state bytes, stage_history bytes/entradas, claves de stage_history, entradas por feature
grep -ln "cdad-state\|stage_history" .cdad/local/*.py | wc -l
wc -l .cdad/local/{mb-*-005-011.py,flow-005-011.sh,register.py,stage3.py,005-012-flow.sh,005-013-register-*.py}
```

**Salida relevante (recortada, tal como se obtuvo):**

```
# baseline
$ git rev-parse HEAD                      -> 58dedda9a1e264cfb25c7c2e58ada2dd397794a1
$ git diff --stat 7212ead..HEAD | tail    -> skills/cdad-cycle/scripts/cdad_packet.py | 829 +++
                                             skills/cdad-cycle/references/project-execution.md | 21 +
                                             skills/cdad-epic/assets/epic-plan-template.md | 11 +
                                             tests/test_005_013_t1_unit_projection.py | 1292 +  (etc.)
$ sha256sum <home>/…/cdad_packet.py        -> 776d1168252b777f621a5c02efa28f1d73728b9d3a50f57f74ea174816c90eb9
$ git show 7212ead:… | sha256sum           -> 776d1168252b777f621a5c02efa28f1d73728b9d3a50f57f74ea174816c90eb9
$ sha256sum skills/cdad-cycle/scripts/cdad_packet.py -> 1f06855fa98ff7eea821db96c781b95327fd4350a8e64d9669458a8d03ff3a44
$ <home>/…/cdad_packet.py --help          -> {validate-state,…,prepare,open-unit,validate-metric,status}
$ skills/…/cdad_packet.py --help          -> {…,status,validate-unit-contract}

# medidas
state bytes: 578926
stage_history entries: 415 json bytes: 525285 share %: 90.7
epic_history entries: 15 json bytes: 9698
epic_features entries: 13
# scripts que editan el state: 13    # glue de los dos últimos ciclos: 751 líneas en 7 scripts
# 005-011: 15 entradas | 005-013: 15 entradas

# caso 1
$ ls .cdad/executions/exec-005-011-common-entry-001/dispatches/  -> … 005-011-scribe.json …
$ ls .cdad/runtime/results/exec-005-011-common-entry-001/         -> 10 dirs, NINGUNO del scribe
$ ls .cdad/inbox/ | grep 005-011                                  -> at-005-011-scribe-final-text.md (entrega preservada)
$ git show --stat 767de01                                         -> docs/.cdad-state.json | 2 +-  (1 insertion)

# caso 2
$ find .cdad/executions/exec-005-013-unit-contract-001 -type f -> sólo execution.json (huérfana, no referenciada)
$ git ls-files .cdad/executions/                               -> (vacío: no versionada)

# estado vigente
$ grep -n '"review_status"\|"current_stage"\|"005-012-transition-registration"' docs/.cdad-state.json
7:  "current_stage": "discovery"
9:  "review_status": {
12:    "review_path": "docs/specs/005-013-unit-contract/review.md"
108:      "id": "005-012-transition-registration"
319:  "stage_history": [
```

**Commit:** ninguno (rol read-only; no hay cambios que commitear). El registro de esta transición lo hará el orquestador bajo la HITL delegada del epic-005.

**Archivo de transporte:** `/tmp/opencode/005-012-discovery.md` (mismos bytes que este informe).
