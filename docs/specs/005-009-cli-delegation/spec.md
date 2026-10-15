> Spec **aprobada** (2026-10-10) junto con el plan. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado con el flujo (receive + materialize create-only) por el orquestador
> (ADR-003); aprobada por el **orquestador OpenCode** bajo la delegación HITL de epic-005
> (`execution.md`). Decisiones **D1–D10** aprobadas tal como se proponen en §7; los VERIFY de §8
> quedan registrados y se cierran o se declaran en T2/T4. Insumo verificado: `docs/specs/005-009-cli-delegation/discovery.md`
> (mapa archivo:línea, ausencia del dispatcher previo, riesgo del modo de carga). Contrato:
> `docs/epics/epic-005-real-operation/plan.md` (fila de orden 5, `:38`). Criterios de origen:
> `docs/epics/epic-005-real-operation/priority-perl-cli-plan-2026-10-10.md` §4. Formato de
> referencia de este epic: `docs/specs/005-008-project-path-capabilities/spec.md`.

## Spec — 005-009-cli-delegation

**Feature ID:** `005-009-cli-delegation` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobada (2026-10-10, orquestador OpenCode, HITL delegada epic-005).

```yaml
feature_id: 005-009-cli-delegation
feature_name: Delegación externa interoperable entre CLI (interfaz común y primer adaptador OpenCode)
created_at: 2026-10-10
status: approved
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-10
```

### 1. Descripción funcional

El resultado no es un motor de jobs ni un sandbox: es que **un agente autorizado (coordinador)
pueda encargar un paquete CDAD ya preparado a una sesión de rol en OTRO CLI, y recibir su
entrega por el flujo CDAD existente**, con proyecto, rol, configuración, entrega y re-entry
verificables. El recorrido común es:

`agente autorizado → encargo canónico → adaptador del CLI destino → sesión de rol → resultado durable → re-entry del responsable`

La pieza nueva es **una interfaz común de delegación externa con un adaptador por destino**
(no un script por pareja de herramientas). La interfaz es agnóstica del CLI destino: recibe
**proyecto**, **paquete canónico**, **rol** y **configuración de ejecución**, y devuelve la
**entrega final durable**, la **identidad de intento/sesión** cuando exista y la **causa de
terminación**. El primer adaptador implementa el destino **OpenCode**; el primer recorrido real
es **Claude (coordinador) → OpenCode (worker) → recepción CDAD**.

Tres hechos del discovery (`docs/specs/005-009-cli-delegation/discovery.md`) definen el diseño:

- **El mecanismo ya existe y debe reutilizarse:** `prepare` (paquetes canónicos), el registro de
  despacho I8 (`--record-dispatch`), el ledger `.cdad/executions/<id>/dispatches/`, los recibos
  (`cdad_result.py receive`) y la reconciliación (`cdad_continuity.py reconcile`/`resume`). El
  state del ciclo tiene un único escritor (el orquestador). La pieza faltante es el
  **transporte**: **no existe un dispatcher/adaptador previo como script en el producto**
  (discovery §3); el despacho real se hizo a mano.
- **El modo de carga del rol en OpenCode es el punto más delicado:** los roles se generan con
  `mode: subagent` y el orquestador con `mode: all` (`sources/agents/adapters/opencode.md:14`).
  Hay evidencia local de que una entry `mode: subagent` en un CLI **cuelga en silencio** y que
  existen agentes **no-Cdad** en el mismo namespace (riesgo de fallback silencioso a un agente
  genérico). El adaptador debe **verificar el modo soportado y fallar cerrado**.
- **La configuración efectiva de una sesión no tiene hoy lector de producto:** solo se infiere
  del registro I8. El adaptador registra lo **configurado/observado o `unknown`** honestamente.

La terminación del proceso y la suficiencia de la entrega son **hechos distintos**: «completado»
no equivale a «gate aprobado». El responsable del ciclo hace el re-entry.

### 2. Contrato

**Contrato bidireccional (la interfaz ↔ el destino ↔ el responsable).**

- **Lo que la interfaz recibe:** `proyecto` (explícito, independiente del directorio del
  coordinador), `paquete canónico` (publicado por `prepare`), `rol`/`substage` (del paquete),
  `configuración de ejecución` (CLI destino, binario/versión, modelo, política de espera/tiempo,
  ubicación de logs) y el `destino` (id de adaptador).
- **Lo que la interfaz devuelve:** la **entrega final durable** (o una declaración explícita de
  «sin entrega suficiente»), la **identidad de intento/sesión** cuando exista (si no, `null`/
  `unknown` explícito) y la **causa de terminación**.
- **Lo que el rol devuelve:** su **texto final** y **evidencia referenciada**, sin esperar
  mensajes de subagentes que no creó ni encadenar sesiones nuevas fuera de su mandato.
- **Salida legítima ante bloqueo:** diagnóstico accionable (qué falta y cómo seguir), **sin**
  fallback silencioso a un agente genérico, **sin** reintentos sin cambio de condiciones y
  **sin** fabricar una entrega.

**Observabilidad (cómo se verifica el contrato).** Las postcondiciones se comprueban sobre
**artefactos durables y comportamiento observable**: los bytes del paquete transportados, el
registro I8 en `.cdad/executions/<id>/dispatches/<attempt>.json`, el recibo durable
(`.cdad/runtime/results/<exec>/<packet>/receipt.json`) y la clasificación de `reconcile`. En
tests, un **destino de prueba** (módulo por convención) y un **binario OpenCode falso** permiten
comprobar la interfaz y el adaptador **sin un runtime vivo**. La mediación real del runtime y el
recorrido Claude→OpenCode son la **aceptación** (T4), no un test determinista.

**Superficie que 005-009 toca (sin controlador nuevo de ciclo, sin otro state):**

- **Nuevo (producto, fuente canónica):** `skills/cdad-cycle/scripts/cdad_delegate.py` — la CLI
  común de delegación; y `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` — el adaptador del
  destino OpenCode. La interfaz **resuelve el adaptador por convención de módulo**
  (`cdad_delegate_<id>.py` en el mismo directorio), de modo que **agregar un destino no edita la
  interfaz** (criterio 1: un adaptador por destino, no un script por pareja).
- **Nuevo (repo, invocación local):** `scripts/cdad_delegate.py` — wrapper `runpy` del canónico
  (patrón de `scripts/cdad_packet.py`). El árbol `cdad-cycle` viaja completo al instalar
  (`install.sh:1006-1020`, `sync_skill_to` copia cada archivo), así que el canónico se distribuye.
- **Nuevo (metodología):** `skills/cdad-cycle/references/cli-delegation.md` — el contrato de la
  interfaz (esquema de entrada/salida, vocabulario de terminación, ubicación de la configuración,
  regla «un adaptador por destino», procedimiento para otro coordinador y límites honestos).
- **Modificado (fuentes + generados, reconciliación de la prohibición de spawn):**
  `skills/cdad-cycle/SKILL.md` (SPAWN GUARD conservado + distinción de la delegación externa),
  `sources/roles/orchestrator.md` (anti-recursión conservada + distinción + escritor único del
  state), `skills/cdad-cycle/references/claude-code-delegation.md` (distinción), y los generados
  `agents/cdad-orchestrator.md` / `agents/claude-code/cdad-orchestrator.md` (regenerados por
  `make agents`; salidas declaradas, nunca editadas a mano).
- **Nuevo (tests):** `tests/test_005_009_t1_interface.py`,
  `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_005_009_t3_spawn_reconciliation.py`,
  `tests/test_005_009_t4_acceptance.py`.
- **Sin cambios:** `prepare` (paquetes), el esquema cerrado del registro I8, `cdad_result.py`
  (receive/recibo), `cdad_continuity.py` (reconcile/resume), el clasificador, el guard CC y el
  mecanismo de publicación atómica. **No** se crea otro state del ciclo ni otro ledger.

**Postcondiciones (numeradas y verificables).**

**PD-1 (interfaz común con un adaptador por destino).** El producto expone **una** interfaz de
delegación agnóstica del destino. Invocada con (proyecto, paquete canónico, rol, configuración,
destino), devuelve un resultado que declara: la **entrega final durable** (o «sin entrega
suficiente»), la **identidad de intento/sesión** cuando exista (si no, `null`/`unknown`) y la
**causa de terminación**. El adaptador se resuelve por `destino` (convención de módulo); agregar
un destino **no** edita la interfaz. Verificable: la CLI existe; con un **destino de prueba**
devuelve el esquema de salida; el adaptador se resuelve por id; no hay un script por pareja.

**PD-2 (reutiliza; no crea otro state ni reescribe las reglas del paquete).** La interfaz
reutiliza el paquete publicado (`prepare`), el registro I8 (`prepare --record-dispatch`), el
ledger, el recibo (`receive`) y la reconciliación (`reconcile`). **Transmite el `PACKET.md`
íntegro y byte-idéntico** (sin re-render ni plantilla paralela); **no** crea otro archivo de
state, **no** habilita un segundo paquete activo y **no** escribe `docs/.cdad-state.json`.
Verificable: los bytes entregados al adaptador == el `PACKET.md` publicado; el registro vive en
`.cdad/executions/<id>/dispatches/<attempt>.json` (mismo ledger, `cdad_packet.py:2388-2389`); el
state no cambia (comparación antes/después).

**PD-3 (proyecto explícito e independiente; rol/configuración/versión esperados).** El proyecto
es explícito y se resuelve con `--project-root`, **independiente del cwd del coordinador**; el
worker usa el rol/substage y la configuración declarados por el paquete y la config de ejecución;
la interfaz registra `runtime`, `model_configured`, `model_reported`, `session`, `started_at` con
`provenance` (esquema cerrado, `cdad_packet.py:2209-2213`), tomando `execution_id`/`packet_id`/
`role`/`substage` **del paquete publicado, nunca del documento de observación**
(`cdad_packet.py:2379-2386`). Verificable: correr desde un cwd no relacionado con el proyecto
resuelve el paquete de ESE proyecto; el registro I8 tiene la forma cerrada y su `provenance` mapea
cada campo a su fuente.

**PD-4 (modo de carga soportado verificado; SIN fallback silencioso a un agente genérico).** El
adaptador **verifica el modo de carga soportado** para una entry no-interactiva contra los agentes
derivados publicados del proyecto; si la entry no es un agente soportado (p. ej. una entry
`mode: subagent` como agente principal), **falla cerrado** con diagnóstico nombrado y **NO** cae a
un agente genérico. Verificable: con un fixture cuya entry es `mode: subagent`, el adaptador
rechaza (rc≠0, el diagnóstico nombra el modo/agente) y **no** despacha sesión; jamás selecciona un
agente no-Cdad (`general`/`coder`/…).

**PD-5 (espera/finalización realmente soportada y probada; sin señales inventadas ni sondeo en bucle).**
La interfaz espera sobre una **señal durable soportada** (base de sesiones / recibo durable), **no**
sobre el rc del cliente de invocación; no inventa señales de finalización, no sondea en bucle y, si
no existe callback, **no lo promete**. Verificable: la espera es acotada y basada en señal/evento;
un cliente que retorna **antes** de que el rol termine **no** produce terminación `completed`; el
test fija que la terminación se deriva de la señal durable.

**PD-6 (vocabulario de terminación; entrega ≠ gate; timeout ≠ ausencia de cambios; reconciliar antes de repetir).**
El resultado distingue `completed`, `blocked`, `transport-error`, `timeout`, `cancelled` (y
`unknown`). `rc=0` **no** aprueba un gate: el recibo queda `semantic_status:"pending"`
(`cdad_result.py:574`) y la interfaz **no** escribe el state. Un `timeout` **no** prueba ausencia de
cambios; tras una interrupción, los efectos se **reconcilian** (`reconcile`) antes de repetir, y
`_classify` distingue `dispatched-unknown` (no fallo) de éxito
(`cdad_continuity.py:965-991`). Verificable: cada terminación se clasifica desde los hechos
materiales; el recibo queda `pending`; `reconcile` no autoriza repetir y no fabrica entrega; el
state no se escribe.

**PD-7 (contexto suficiente y acotado; texto final + evidencia referenciada; sin esperar subagentes ajenos ni encadenar sesiones).**
El worker recibe **solo** el paquete y sus insumos declarados (no la conversación del coordinador);
devuelve su **texto final** y **evidencia referenciada**; la interfaz **no** espera mensajes de
subagentes que el worker no creó y **no** encadena sesiones nuevas fuera del mandato. Verificable:
el prompt transportado == el paquete (acotado); la salida lleva el texto final + ref durable; no se
lanza una cadena de sesiones anidadas.

**PD-8 (configuración portable; configurado/observado/desconocido; SIN valores de este VPS).**
Selección de modelo, binarios, logs, servidores y tiempos viven en el **nivel correcto**
(configuración de ejecución/local o flags), **nunca** hardcodeados en el producto ni en contratos
públicos; la interfaz registra **configurado/observado o `unknown`**; **ningún** valor de este VPS
(rutas absolutas, proveedor, modelo concreto, servidor, tiempos) aparece en el producto ni en
contratos públicos. Verificable: un barrido de los archivos de producto no encuentra rutas
absolutas de host / proveedor / modelo concreto / servidor; la config llega por archivo/flags; los
campos no observados se marcan `null`/`unknown` con provenance.

**PD-9 (prohibición heredada de spawn reconciliada).** La prohibición heredada se **conserva**
donde el runtime **no** soporta el spawn nativo de sub-subagentes (anti-recursión:
`skills/cdad-cycle/SKILL.md:136-143`, `sources/roles/orchestrator.md:74-76`,
`references/claude-code-delegation.md:63-69`) y se **distingue** de la delegación externa
autorizada (coordinador→worker entre CLIs, que **no** es recursión de subagentes dentro del mismo
runtime). Primer aterrizaje: coordinador→worker, devolución al coordinador, **sin** recursión
automática. Una delegación **no** amplía autoridad ni permite al worker escribir el state.
Verificable: el texto del SPAWN GUARD permanece; existe la distinción en fuentes/agentes; el
orquestador sigue siendo el único escritor de `docs/.cdad-state.json`.

**PD-10 (primer recorrido real Claude → OpenCode → recepción CDAD desde la instalación elegida).**
Una delegación pequeña real, desde un coordinador Claude real a un worker de rol en OpenCode real,
vuelve por `receive` con evidencia durable, desde la instalación elegida para la aceptación; el
coordinador hace el re-entry. Verificable: evidencia registrada del recorrido real (I8 + recibo +
re-entry), corrida por el orquestador con el dueño; una prueba que solo llama al script desde un
shell **no** demuestra por sí sola la orquestación desde Claude.

### 3. Invariantes (verificables)

- **INV-1.** El **orquestador es el único escritor** de `docs/.cdad-state.json`; la interfaz, el
  adaptador y el worker **nunca** lo escriben (criterios 1 y g).
- **INV-2.** **Un adaptador por destino**; no hay un script por pareja; la interfaz es
  agnóstica del destino (PD-1).
- **INV-3.** El **paquete canónico se transporta íntegro**; **no** hay plantilla paralela que
  reescriba las reglas del paquete (PD-2).
- **INV-4.** Una delegación **no amplía autoridad ni alcance**; el worker **no** edita fuera del
  `write_scope` del paquete ni escribe el state (criterios 2 y g).
- **INV-5.** **`rc=0` no es aprobación de gate**; el recibo es `semantic_status:"pending"`; el
  gate lo decide el responsable en el re-entry (PD-6).
- **INV-6.** **No** se inventan señales de finalización; **no** se promete callback inexistente;
  **no** se sondea en bucle (PD-5).
- **INV-7.** **Sin valores de este VPS** en producto ni en contratos públicos; la configuración
  es local (PD-8).
- **INV-8.** Un **proceso/sesión separada NO es un sandbox**; cambiar de CLI **no** garantiza otra
  familia de modelo ni aislamiento de información (límites honestos).
- **INV-9.** **No** se construye un scheduler, ni instalación automática de CLI, ni un sandbox; **no**
  se implementan todos los destinos; la dirección inversa y otros CLI son incrementos posteriores.
- **INV-10.** **No** cambian el alcance ni los criterios de epic-005; **activar versiones**,
  **cambios en HOME**, la **confianza de carpeta de Claude Code** y la **operación de producción**
  siguen **reservados al dueño** (`execution.md:19-23`).

### 4. Criterios de aceptación

- [ ] **PD-1/INV-2**: la interfaz común existe, es agnóstica del destino y resuelve el adaptador
      por id; con un destino de prueba devuelve el esquema de salida; no hay un script por pareja.
- [ ] **PD-2/INV-3**: el `PACKET.md` se transporta byte-idéntico; el registro I8 usa el ledger
      existente; la interfaz no crea otro state ni escribe `docs/.cdad-state.json`.
- [ ] **PD-3**: el proyecto es explícito e independiente del cwd; el registro I8 toma
      `role`/`substage` del paquete y `provenance` mapea cada campo a su fuente.
- [ ] **PD-4**: con una entry `mode: subagent`, el adaptador **falla cerrado** y **no** cae a un
      agente genérico.
- [ ] **PD-5/INV-6**: la espera es sobre señal durable; un cliente que retorna temprano no produce
      `completed`; no hay sondeo en bucle ni callback inventado.
- [ ] **PD-6/INV-5**: se distinguen las cinco causas de terminación; `rc=0` no aprueba un gate
      (recibo `pending`); `timeout` no prueba ausencia de cambios; `reconcile` clasifica
      `dispatched-unknown` sin autorizar repetición.
- [ ] **PD-7**: el worker recibe contexto acotado y devuelve texto final + evidencia referenciada;
      no espera subagentes ajenos ni encadena sesiones fuera del mandato.
- [ ] **PD-8/INV-7**: la configuración es portable; se registra configurado/observado/`unknown`;
      no hay valores de este VPS en producto ni en contratos públicos.
- [ ] **PD-9**: el SPAWN GUARD se conserva y se distingue de la delegación externa; el orquestador
      sigue siendo el único escritor del state.
- [ ] **PD-10**: recorrido real Claude → OpenCode → recepción CDAD registrado como evidencia, con
      re-entry del coordinador, desde la instalación elegida.
- [ ] **Suite completa verde al cierre** y `make validate` sin fallos nuevos (los FAIL
      preexistentes, si los hay, no se atribuyen a este diff).

### 5. Fuera de alcance

- **Scheduler**, **instalación automática de CLI** y **sandbox** (INV-9).
- **Implementar todos los destinos**: solo el primer adaptador (OpenCode); la **dirección inversa**
  y otros CLI (Codex, Pi) son incrementos posteriores (VERIFY-7).
- **Cambios en HOME**, **activación de versiones**, **confianza de carpeta de Claude Code** y
  **operación de producción** (reservado al dueño).
- **Un segundo state del ciclo**, **otro ledger** o **reescribir las reglas del paquete** (INV-1/INV-3).
- **Medición** de contexto (005-002); **capacidades de rutas** (005-008, ya cerrada);
  **orientación** al retomar (005-003); roles nativos en Claude Code (005-004); planificación
  progresiva (005-007).

### 6. Contexto técnico (verificado)

**Mecanismo reutilizable (archivo:línea, discovery §2).**

- **`prepare`:** `skills/cdad-cycle/scripts/cdad_packet.py:3290` (`def prepare`); parser y opciones
  `:3470-3500`; el paquete se publica en `.cdad/packets/<packet_id>/` (`REQUEST.json` + `PACKET.md`).
- **Registro I8:** `OBSERVATION_KEYS`/`OBSERVATION_TEXT_FIELDS` `cdad_packet.py:2209-2213`;
  `_load_observation_document` (esquema cerrado) `:2248-2284`; `_record_dispatch` `:2339`;
  forma del registro `:2379-2386`; ruta del intento `:2388-2389`; transición `prepared → dispatched`
  `:2400-2408`; publicación atómica `:2294-2334`.
- **Recibos:** `cdad_result.py:493` (`def receive`); exige el paquete `dispatched` `:526-530`; forma
  del recibo `:549-577`; `semantic_status:"pending"` `:574`; `RESULTS_RELPATH`
  `.cdad/runtime/results/…` `:60-61`; idempotencia `:501-507`.
- **Reconciliación:** `cdad_continuity.py:915` (`_has_dispatch`), `:929` (`_receipt_signal`),
  `:965` (`_classify` → `expired-authority|unknown|already-closed|received|dispatched-unknown|not-started`),
  `:994` (`_run_reconcile`, read-only), `:1229` (`_run_resume`).
- **State (único escritor):** `references/continuity.md:9-11`; `agents/cdad-orchestrator.md:146`.
- **Patrón de ejecución externa acotada (precedente, no runner genérico):**
  `cdad_result.py:1316` (`run_python_unittest`): argv + snapshots before/after + reconciliación;
  **especializado** a `python3 -m unittest` (`RUN_ARGV_PREFIX` `:105`) — sirve de **patrón**,
  no de adaptador listo (VERIFY-5).

**Modo de carga del rol (documentado vs probado, discovery §4).**

- Fuente canónica: `sources/agents/adapters/opencode.md:11-14` — layout
  `~/.config/opencode/agents/cdad-<role>[-odoo].md`; roles `mode: subagent`, **orquestador
  `mode: all` + `permission: allow`**; `model:` emitido desde `scripts/cdad-models.sh`;
  `steps: 300` en cada subagente.
- Generados: `agents/cdad-architect.md:3` → `mode: subagent`; `agents/cdad-orchestrator.md:3` →
  `mode: all`. Generador: `scripts/cdad-generate.py` (`make agents`).
- **Probado (evidencia local, 2026-09-29):** `opencode run --agent <rol mode: subagent>` **cuelga
  en silencio**; la entry debe ser un agente `mode:all`/primary
  (`docs/specs/opencode-read-map-and-steps-2026-09-29/spec.yaml:53`;
  `evidence/results.md:32`). **Riesgo de fallback:** existen agentes no-Cdad en el namespace
  (`general`, `coder`, `reviewer`, `scribe`, …) — el contrato lo prohíbe explícitamente.
- **Espera:** `results.md:39` — «esperar sobre la base de sesiones, no sobre el cliente
  `opencode run`, que puede volver antes de que el rol termine».

**Proyecto/versión (discovery §5).**

- El proyecto se fija con `--project-root` en los CLIs (`cdad_result.py:1462-1466`).
- Manifiesto derivado `.opencode/agents/.cdad-derived.json` (`source_dir` + `source_version`);
  `cdad-version-check.py:24-29` (`COHERENT`/`DRIFT`/`NO-PROJECT-AGENTS`/`UNKNOWN`; cualquier no-cero
  = versión NO verificada coherente).
- **Configuración efectiva:** hoy solo se infiere del registro I8 (provenance campo→fuente);
  **no** existe un lector de sesión de producto (VERIFY-2).

**Prohibición de spawn (texto exacto, discovery §7).**

- `skills/cdad-cycle/SKILL.md:136-143` (SPAWN GUARD); `sources/roles/orchestrator.md:74-76`
  (anti-recursión); `references/claude-code-delegation.md:63-69`; generado
  `agents/cdad-orchestrator.md:163`.

**Distribución del nuevo script (verificado).**

- `install.sh:1006-1020` (`sync_skill_to`): el árbol `cdad-cycle` se copia **archivo por archivo**,
  así que un script nuevo bajo `skills/cdad-cycle/scripts/` **viaja con la skill** sin cambiar el
  manifiesto. El wrapper de `scripts/` es solo para invocación local del repo (patrón
  `scripts/cdad_packet.py`, wrapper `runpy` de 330 bytes).

### 7. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | La interfaz común es un CLI nuevo `cdad_delegate.py` en `skills/cdad-cycle/scripts/` (+ wrapper en `scripts/`); los destinos se resuelven por **convención de módulo** (`cdad_delegate_<id>.py`), de modo que agregar un destino **no edita** la interfaz. | Viaja con la skill (`install.sh:1006-1020`); «un adaptador por destino, no un script por pareja» (criterio 1/PD-1). Ubicación natural junto a los CLIs canónicos (VERIFY-1 del discovery). |
| **D2** | La interfaz **reutiliza** `prepare`, `--record-dispatch` (I8), el ledger, `receive` y `reconcile`; **nunca** escribe el state ni crea otro ledger. | Criterio 1; `docs/.cdad-state.json` tiene único escritor (INV-1). |
| **D3** | El registro I8 se alimenta con `runtime`, `model_configured`, `model_reported`, `session`, `started_at`, `provenance`; los campos no observados son `null`/`unknown` con provenance. | Esquema cerrado (`cdad_packet.py:2209-2213`); «registrar configurado/observado o desconocido» (criterio 6); no inventar (VERIFY-2). |
| **D4** | Vocabulario de terminación = {`completed`, `blocked`, `transport-error`, `timeout`, `cancelled`, `unknown`}; `completed` (entrega) ≠ gate aprobado. | Criterio 4; el recibo queda `pending` (INV-5). |
| **D5** | El chequeo del **modo de carga soportado** falla cerrado; **sin** fallback a un agente genérico. | Criterio 2; riesgo R-1/R-2 del discovery; VERIFY-3 (la entry soportada depende de la versión vigente). |
| **D6** | Esperar sobre una **señal durable** (base de sesiones / recibo), **no** sobre el rc del cliente; acotado; **sin** callback si no existe. | Criterio 5; `results.md:39`; VERIFY-4 (superficie concreta a fijar en T2). |
| **D7** | **Portabilidad de configuración:** modelo/binario/logs/servidor/tiempos desde la config de ejecución (local, git-ignorada) o flags; el producto no lleva valores del VPS. | Criterio 6; findings «Qué pertenece a cada nivel»; INV-7. |
| **D8** | Reconciliar la prohibición de spawn: **conservar** donde el runtime no soporta el spawn nativo y **distinguirla** de la delegación externa; primer aterrizaje coordinador→worker, sin recursión automática. | Criterio g; `priority-perl-cli-plan` §4 cierre; R-6. |
| **D9** | El **recorrido real** Claude → OpenCode → recepción es el **gate de integración/aceptación**, corrido por el orquestador + dueño; aporta el R2 pendiente de 005-006 y la aceptación de interoperabilidad. | Criterio 7; plan §5; VERIFY-8. |
| **D10** | **Frontera explícita:** no scheduler, no instalación automática de CLI, no sandbox; no todos los destinos; la dirección inversa y otros CLI, después. | `priority-perl-cli-plan:173,196-197`; findings «Fuera»; INV-9. |

### 8. VERIFY del discovery §12 — estado y resolución propuesta

| # | VERIFY | Estado en el draft | Resolución / dueño y cuándo |
|---|---|---|---|
| 1 | Ubicación y forma del adaptador | **RESUELTO por D1** (propuesta) | CLI nuevo en `skills/cdad-cycle/scripts/` + wrapper; destinos por convención de módulo. |
| 2 | Configuración efectiva (agente/modelo/proyecto cargados) | **ABIERTO** | La interfaz registra desde el runtime **si expone** un identificador de sesión/modelo; si no, `unknown` honesto (D3). No se construye un lector de sesión (005-002, pausada). Se cierra en T2/T4. |
| 3 | Modo de carga soportado (versión vigente) | **ABIERTO** | La evidencia es de 1.18.32/2.0.16 (2026-09-29); puede haber cambiado. El adaptador **verifica** el modo y falla cerrado; la entry soportada se confirma en T2 contra la versión en uso. |
| 4 | Espera soportada (superficie concreta) | **ABIERTO** | Señal durable/base de sesiones; la superficie concreta se fija en T2 (D6). |
| 5 | Reutilización de `run-python-unittest` | **RESUELTO parcialmente** | Se reutiliza el **patrón** (argv + snapshots + reconciliación), **no** el runner especializado a unittest (D2). |
| 6 | `install.sh` y publicación | **RESUELTO parcialmente** | El script viaja con el árbol `cdad-cycle` (`install.sh:1006-1020`); si `--check`/staging necesita algo más, se registra (deuda de `__pycache__` ya anotada, `priority-perl-cli-plan:231-234`). |
| 7 | Segundo destino / dirección inversa | **FUERA de esta entrega** | Incremento posterior; el diseño lo admite (D1/D10). |
| 8 | Aceptación conjunta (R2) | **ABIERTO** | El recorrido real (PD-10) aporta el R2 pendiente de 005-006 y la aceptación de interoperabilidad; se construye sobre una versión estable (la sucesora que incluye 005-008 para la aceptación conjunta). |

### 9. Fronteras y no-cambio de alcance

- **Frontera con 005-008** (rutas de proyecto, ya cerrada). 005-008 entrega la corrección de
  permisos que la **aceptación conjunta** del consumidor aprovecha; 005-009 **no** la reabre.
- **Frontera con 005-006** (arranque guiado). El recorrido real aporta su **R2 pendiente**; no se
  repite su bootstrap ni se duplica su procedimiento.
- **Frontera con 005-002** (medición de contexto). Fuera: **no** se construye un lector de sesión;
  la configuración efectiva se registra desde lo que el runtime exponga o `unknown` (VERIFY-2).
- **Frontera con 005-004** (roles nativos en Claude Code). 005-009 usa Claude como **coordinador**
  de un worker externo; **no** da soporte nativo de la metodología a Claude Code.
- **No cambia el alcance ni los criterios del epic-005** (INV-10); activación de versiones, cambios
  en HOME, confianza de carpeta y producción siguen **reservados al dueño** (`execution.md:19-23`).

### 10. Aprobación

- **Estado: aprobada (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL del
  epic-005 (`execution.md`), con las decisiones **D1–D10** de §7 aprobadas tal como se proponen. La
  aprobación de la spec es **no delegable por defecto**; bajo la delegación HITL del epic-005 la
  ejerce el orquestador OpenCode. El architect no aprobó su propia propuesta (anti-sesgo).
- **VERIFY** de §8: 2, 3, 4 y 8 se cierran o se declaran en T2/T4 (config efectiva, modo de carga
  vigente, superficie de espera, aceptación conjunta R2); 1 y 5 quedan resueltos por D1/D2; 6 queda
  parcialmente resuelto y 7 fuera de esta entrega.
- El `sha256` del archivo materializado vivirá en el `state` (pin `contract_path` +
  `contract_sha256`), no dentro del archivo.
