# Discovery — 005-011-common-entry (etapa 1: mapeo técnico y brainstórming)

**Rol:** architect (solo lectura). **Feature:** fila 11 del plan de `epic-005-real-operation`.
**Contrato:** `docs/epics/epic-005-real-operation/plan.md` (`sha256 63dda3b8…059a6`, verificado).
**Insumos ya medidos (citados, no re-medidos):** `docs/specs/005-007-progressive-planning/acceptance.md` §7
(línea base OpenCode) y `docs/specs/005-004-claude-code-roles/t5-acceptance.md` §7 (línea base Claude Code).
**Autoridad:** `docs/epics/epic-005-real-operation/execution.md` (HITL delegada; el despliegue es del dueño).
No propongo el contrato: eso es la subetapa draft.

Nota de método: las magnitudes propias de este informe se midieron en solo lectura con `wc -c`, `sha256sum`
y ejecución acotada de los CLI del repo; se declaran abajo. Se anonimiza con `<home>`, `<repo>`, `<tmp>`,
`<ses-…>`.

---

## 1. Entidades verificadas (archivo:línea)

### Eje 1 — la entrada actual de cada skill que orienta

**`cdad-cycle` (skill orquestadora).**
- `skills/cdad-cycle/SKILL.md:249-251` — **Step 1 «Detect state»**: la primera acción prescripta es
  «Load `references/state-detection.md` and apply the logic»; el único CLI que nombra es `resume`
  (y sólo para una ejecución activa). **No menciona la vista compacta ni `status`** (verificado:
  `SKILL.md` no contiene «compact view» ni `cdad_packet.py status`; sus únicas menciones del CLI son
  `render` en Step 4, `:268`, y la fila de tabla `:460`).
- `skills/cdad-cycle/SKILL.md:447-469` — tabla **«How to read the references»**. Fila
  `state-detection.md` = «At the start of every turn in orchestrator mode» (`:453`); fila
  `project-start.md` = «When a brief instruction starts a project from rest…» (`:454`);
  `project-execution.md` (`:460`) y `continuity.md` (`:461`) traen el CLI instalado con `<skill-dir>`.
  **`orientation.md` NO figura en la tabla** (grep de «orientation» en `SKILL.md` = 0 coincidencias).
- `skills/cdad-cycle/references/state-detection.md:1-10` (nota de dueño canónico, PD-13) y
  `:16-18` — **Step 1: «Does `docs/.cdad-state.json` exist? If it exists, read it»**, con el subset de
  campos. Es la instrucción que produce la lectura del state completo (ver §3).

**`cdad-epic` (skill coordinadora de epic).**
- `skills/cdad-epic/SKILL.md:56-58` — **Step 1 «Detect epic state»**: «Load `references/state-detection.md`».
  La skill **no menciona ningún CLI** (grep `cdad_packet` = 0).
- `skills/cdad-epic/SKILL.md:200-209` — tabla **«How to load the references»**; fila
  `state-detection.md` = «At the start of every turn» (`:204`). **`orientation.md` tampoco figura.**
- `skills/cdad-epic/references/state-detection.md:9-25` — Step 1 lee los campos de epic del state
  (`active_epic`, `epic_stage`, `epic_features`).

**Los pasos equivalentes en las referencias.**
- `skills/cdad-cycle/references/project-start.md:223-240` — **§11 «Orient first — the compact view,
  then expand on a concrete need»**: manda consultar **primero** `cdad_packet.py status` y ampliar sólo
  ante una necesidad concreta. Pero está **al final** del documento y su gatillo es acotado
  (`:1-16`: «when a brief instruction must start a project from rest»). La sección cita `orientation.md` §1.
- `skills/cdad-cycle/references/orientation.md:14-35` — **§1 «The compact view first (read-only)»**:
  «The first orientation action is the compact operational view». Es el único texto que fija la regla
  general «vista primero», y **no está indexado por ninguna de las dos tablas de las SKILL.md**.
  `:57-66` trae la tabla de operaciones frecuentes (incluida la fila `open-unit`, `:66`);
  `:68-75` la asimetría de raíz relativa; `:102-128` la disposición de versión.
- `skills/cdad-cycle/references/project-start.md:7-11` compone por referencia los cinco dueños
  (`state-detection.md`, `project-execution.md`, `continuity.md`, `bootstrap.md`,
  `cdad-epic/references/state-detection.md`); `:74-128` §6 (cadena a la primera comisión, con los
  comandos `prepare`/`validate-*`/`begin`/`--record-dispatch`); `:134-152` §6.1 `open-unit`;
  `:154-158` §7 (resume sólo con ejecución activa); `:160-167` §8 (diagnóstico de configuración
  bloqueada); `:184-211` §10 (el único chequeo de versión).

**El contrato de la vista compacta y la entrada `next-unit`.**
- `docs/specs/005-003-orientation-reduction/spec.md:70-107` (§2.1, forma de la vista: subcomando
  `status` de `cdad_packet.py`, campos `project/epic/feature/execution/packet/authority/version/next/entry/unknowns[]`,
  límite 16.384 B, read-only, determinista, sin `stage_history`).
- `docs/specs/005-003-orientation-reduction/spec.md:109-138` (§2.2, mapa explícito de `entry`:
  `continuity-reconcile | next-unit | diagnosis`, con el caso real «`current_stage=discovery` y
  `active_packet.status=prepared`»; «trabajo pendiente» sin campo nuevo; F2 reposo/historia).
- Implementación: `skills/cdad-cycle/scripts/cdad_packet.py:3911-3927` (`_entry_selection`),
  `:3930-3949` (`_next_route`), `:3965-4087` (`status_view`), constantes `:114-117`
  (`ENTRY_CONTINUITY_RECONCILE/NEXT_UNIT/DIAGNOSIS`), `:108` (`ACTIVE_PACKET_STATUSES`).
- `skills/cdad-cycle/references/project-start.md:233-240` describe `entry`/`next`; §6-§7 son el destino
  de la ruta `next-unit` (`:3948-3949`: «next unit: run `cdad_packet.py open-unit` (project-start.md §6)»).

**Otras skills.** No hay más Step 1 que lea estado: grep de `Step 1` en `skills/*/SKILL.md` sólo devuelve
las dos de arriba. Las skills de rol con stack (`skills/odoo-architect`, `odoo-reviewer`, `odoo-expert`,
`odoo-test-writer`, `odoo-make-env`) son de dominio y **no** leen el state (verificado en
`skills/odoo-architect/SKILL.md`: sólo menciona «state of an implementation»). Los cuatro `skills/*.md`
sueltos (`epic-planning.md`, `feature-handoff.md`, `handoff-prompts.md`, `re-entry.md`) son **stubs de
referencia, no skills instalables** (`install.sh:14-15`, `:419-420`), y no son entrada.

### Eje 2 — el CLI: raíz absoluta vs relativa

- **`cdad_packet.py` (el que rechaza la raíz relativa).**
  - `:673-677` `_absolute_existing_directory(raw, label)`: exige `is_absolute()` **y** `is_dir()`;
    si no, `PolicyError("--project-root must be an absolute existing directory: <raw>")`.
  - `:4294-4304` `main`: si `--project-root` es `None` → `Path.cwd().resolve()` (`:4297-4298`);
    si el comando es `status` → `_status_project_root` (`:4302`); **cualquier otro comando** →
    `_absolute_existing_directory` (`:4304`). Es decir: **todos los subcomandos** comparten el rechazo
    (`validate-state`, `validate-policy`, `render`, `validate-request`, `validate-packet`, `prepare`,
    `open-unit`, `validate-metric`) y `status` tiene su propio helper con el mismo rechazo **más** el
    diagnóstico de asimetría (`:3776-3791`, comentario C4/PD-5).
  - **Matiz verificado:** `--project-root` es **opcional** en todos los subcomandos
    (`:4099`, `:4103`, `:4108`, `:4114`, `:4158`, `:4163`, `:4167`): sin la bandera se usa el cwd y
    funciona. El rechazo sólo aplica a una raíz **explícita y relativa**.
  - Contraste interno: `--execution-context` **sí** se resuelve contra el cwd
    (`_cwd_path`, `:1048-1050`; `main:4378-4380`). Es decir, dentro del mismo CLI, el root debe ser
    absoluto pero el contexto de ejecución puede ser relativo.
- **Los demás CLI aceptan la raíz relativa.**
  - `cdad_continuity.py`: `--project-root` es `required=True` (`:1303,1314,1320,1328`) pero se usa
    crudo: `root = Path(args.project_root)` (`:623,995,1155,1230`); sin chequeo de absolutez.
  - `cdad_result.py:1508-1511`: `Path(args.project_root).resolve()` (relativa → cwd) + `is_dir()`;
    error `«--project-root must be an existing directory»` (sin exigir absoluta).
  - `cdad-version-check.py:189-192`: `expanduser()` + `is_dir()`.
  - `cdad_guard.py:691,725,806,890`: `Path(args.project_root)`, sin chequeo.
  - `cdad_delegate.py:253-256` y `cdad_delegate_opencode.py:755-758`: `.resolve()`.
  - `cdad_context_meter.py:1786-1815`: **no tiene `--project-root`** (usa `--store`/`CDAD_CONTEXT_METER_STORE`).
- **Evidencia viva en `<repo>`** (comandos exactos y su rc):
  - `python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root .` → **rc=2**, sin proyección,
    `ERROR: --project-root must be an absolute existing directory: . — root-relative asymmetry between
    CLIs: cdad_continuity.py resolves a relative --project-root against the cwd … while cdad_packet.py
    rejects it; recovery: pass an absolute --project-root`.
  - `python3 … cdad_packet.py status` (sin bandera) → **rc=0** (usa el cwd).
  - `python3 … cdad_continuity.py resume --project-root . --execution-context .cdad/executions/<id>/execution.json`
    → **rc=0** (con `state: no-checkpoint`).
- **Documentación que hoy afirma la asimetría** (quedaría falsa si (b) la elimina):
  `skills/cdad-cycle/references/orientation.md:68-75`, `skills/cdad-cycle/references/project-execution.md:49`
  («which must be an absolute existing directory»), y el asset
  `skills/cdad-cycle/assets/orientation-examples.json` (los ejemplos `status-view` y `open-unit` usan
  el placeholder `--project-root <ABS>`).
- **Qué costaría aceptar la raíz relativa de forma consistente** (sin cambiar ninguna otra validación
  ni la doctrina «cada CLI resuelve su raíz»): sustituir el cuerpo de `_absolute_existing_directory`
  (y unificar `_status_project_root`) por «resolver contra el cwd y exigir `is_dir()`», igual que
  `cdad_result.py:1508-1511`. No toca la validación de política (`_project_path`/`classify_path`,
  `:168-320`), ni el hashing del contrato, ni la publicación de agentes derivados, ni el default cwd
  (`:4297-4298`). La doctrina se **conserva**: `cdad_packet.py` seguiría resolviendo **su propia** raíz,
  como los demás. **Lo que sí costaría**: el diagnóstico C4 (`:3776-3791`) queda sin causa, y hay que
  actualizar el texto de `orientation.md`/`project-execution.md` y **el oráculo de 005-003** (ver §6.4).

### Eje 3 — versión y siguiente acción en la vista

- **De dónde sale el veredicto de versión.** `status_view` llama `_version_verdict`
  (`cdad_packet.py:3815-3842`), que ejecuta el único chequeo `cdad-version-check.py`
  (`:3821-3831`) y proyecta `{verdict, verified: rc==0}`; con `rc≠0` agrega `cause` y lo empuja a
  `unknowns[]` (`:4049-4052`). El chequeo compone **cuatro patas**
  (`cdad-version-check.py:4-22,211-236`):
  - **project** — `source_version` del manifiesto de agentes derivados
    (`<repo>/.opencode/agents/.cdad-derived.json`; `:55,164-176`);
  - **agents** — `version.txt` en la raíz de instalación detrás de esos agentes (`:88-98,206-207`);
  - **CLI** — `version.txt` en la raíz de instalación del árbol que hospeda el script (`:101-121,208-209`);
  - **Claude Code** (aditiva) — `version.txt` de la raíz CC, resuelta por el registro de activación
    (`.cdad/activation.json` → `adopted_root`) o por `<home>/.claude/agents` (`:124-161,196-197,226-228`);
    sin instalación CC detectable, los cuatro veredictos y sus rc no cambian.
  - Veredictos (`:29-40,220-236`): `COHERENT`/0, `DRIFT`/1 (incoherencia), `NO-PROJECT-AGENTS`/4
    (nada cargado aún), `UNKNOWN`/3 (falta una marca). Cualquier `rc≠0` = «no verificado coherente».
- **Qué dice hoy cada veredicto y cada `unknown`.** La vista emite `version.verdict` + `version.verified`
  y, con `rc≠0`, `version.cause = "version not verified as coherent (verdict X, rc N); any non-zero rc
  reads as not verified"`, además de la misma cadena en `unknowns[]` (`:3837-3842`, `:4050-4052`).
  **No distingue el caso legítimo del ilegítimo**: para `DRIFT` la causa es idéntica en forma a la de
  `UNKNOWN`/`NO-PROJECT-AGENTS`, y **no nombra ninguna acción**.
- **Por qué un `DRIFT` legítimo de agentes derivados de proyecto no dice qué lo resuelve.** El `DRIFT`
  legítimo nace de la pata **project**: los agentes derivados quedaron con el `source_version` de la
  instalación **anterior** (`cdad-version-check.py:164-176`), mientras agents/CLI traen la instalación
  vigente. La resolución **existe y está verificada**: `prepare` **republica** los agentes derivados del
  proyecto y escribe `source_version = _installation_version(source_dir)`
  (`cdad_packet.py:2874`, con `DERIVED_RELPATH`/`DERIVED_MANIFEST_NAME` en `:89-93`, publicación en
  `:2843-2874`); `project-execution.md:143-146` lo documenta; y el caso real está observado en
  `docs/specs/005-004-claude-code-roles/t5-acceptance.md:102-105` («project da `9d89a4b…`, los agentes
  derivados del proyecto, **que el próximo `prepare` republica**»). **Nada de eso llega hoy a la salida
  de `status`**: la vista sólo dice «no verificado coherente». Eso es lo que produjo las llamadas 22-30
  de la línea base (investigación guiada por un DRIFT sin acción).
  - Evidencia viva en `<repo>`: `cdad-version-check.py --project-root <repo>` → project = agents =
  claude-code = `905c3e1…`, CLI = «(no version.txt found)» (checkout de desarrollo) → **`UNKNOWN` rc=3**
  — es **ausencia**, no incoherencia; coincide con `project-start.md:205-208` y con `orientation.md:104-117`.
- **Qué dice hoy la ruta con un paquete `prepared`.** `_next_route` (`:3932-3949`): con
  `packet.status == "prepared"` → `route: "reconcile the pending packet (--replace-packet if the
  contract changed)"`, `source: docs/.cdad-state.json:active_packet.status` (`:3936-3939`); con
  `dispatched` → `"reconcile the dispatched packet before repeating (resume)"` (`:3933-3935`); con
  `next-unit` → `open-unit` (`:3948-3949`); con `diagnosis` → `project-start.md §8` (`:3942-3944`).
  El contrato de reemplazo vigente dice que `--replace-packet` es **sólo** para un paquete `prepared`
  **nunca despachado** y **genuinamente obsoleto** (`project-execution.md:164-182`), y que un paquete
  `prepared` es exactamente el que **está listo para despacharse** (`project-start.md:74-128`). Por eso
  «reconcile the pending packet» **no es la acción natural** de un `prepared`: la natural es
  **despacharlo** (validar → `begin` → `--record-dispatch`), y `--replace-packet` es la rama
  **condicional** (contrato cambiado).
  - Evidencia viva en `<repo>` (paquete activo `dispatched`): `entry=continuity-reconcile`,
    `next.route="reconcile the dispatched packet before repeating (resume)"`, `packet.status="dispatched"`,
    `version.verdict=UNKNOWN` con causa, `unknowns` con esa única causa; vista = **1.690 B** con
    `rc=0` (frente a un state de **491.576 B**).

### Eje 4 — qué carga realmente una sesión nueva antes de actuar

- **Orden de carga verificado por construcción del repo:** (i) la skill se carga **por invocación**
  (su `SKILL.md` entra completo al contexto); (ii) las referencias se cargan **cuando la skill las manda
  leer** (tabla «How to read the references», `SKILL.md:447-469`). Con el texto actual:
  `cdad-epic` SKILL (13.425 B) + `cdad-cycle` SKILL (38.185 B) → Step 1 de cada una →
  `state-detection.md` (6.387 B; epic: 4.279 B) → **Step 1 de `state-detection.md` manda leer el state**
  (`:16-18`).
- **La lectura que produce la exploración manual observada** es esa: leer `docs/.cdad-state.json`
  **completo** (hoy **491.576 B**). Coincide con las líneas base citadas: OpenCode llamada 3 = state
  completo (59 mil car., truncado) antes de cualquier operación del CLI
  (`005-007/acceptance.md:137`); Claude Code llamada 2 = state completo, **antes** de `status`
  (llamada 7) (`005-004/t5-acceptance.md:85`).
- **Dónde el texto manda a leer el state completo y dónde manda a explorar el CLI.**
  - Manda a **leer el state**: `state-detection.md:16-18` (Step 1) + `SKILL.md:453` y
    `cdad-epic/SKILL.md:204` («at the start of every turn»).
  - Manda a **consultar la vista**: sólo `project-start.md:223-240` (§11) y `orientation.md:14-35` (§1)
    — **ambos no indexados** por las tablas de las SKILL.md (project-start.md sólo con el gatillo
    «arranque desde reposo»; orientation.md sin fila). La ruta compacta **existe pero no es la primera**:
    compite con el Step 1 que manda a leer el state.
  - Manda a **explorar el CLI/versiones**: `project-start.md:184-211` (§10) y `orientation.md:102-128`
    (§4), más la ausencia de acción ante `DRIFT` (§Eje 3).
  - El agente orquestador (`agents/cdad-orchestrator.md:37-43`, «Boot-at-rest path») manda **cargar
    primero `cdad-cycle`** y luego seguir `references/project-start.md`; **no menciona `status`**
    (grep de `status` en `agents/cdad-orchestrator.md` y en `sources/roles/orchestrator.md` = 0).

### Eje 5 — frontera con lo que NO es de esta feature

Del plan (`plan.md:44` fila 11 y `:143-154` cambios del 2026-10-13) y de la ejecución del epic
(`execution.md:48-63`): quedan **fuera** 005-012 (registro de transiciones) y 005-013 (contrato por
unidad) — no se anticipan; el **adaptador Claude Code** y la **medición del lado CC** siguen fuera
(`005-004/t5-acceptance.md:80`, D-4); no se reabren los contratos de 005-003/005-004/005-007 (sólo se
**corrige** lo que la fila 11 manda); sin CI, sin WebUI, sin sandbox, sin plataforma de jobs; sin tocar
HOME (reservado al dueño, `execution.md:19-23`).

### Eje 6 — aceptación y medición disponibles

- **Medidor de 005-002** (`skills/cdad-cycle/scripts/cdad_context_meter.py`; contrato en
  `skills/cdad-cycle/references/context-meter.md`): informa **por sesión** y **por rol**.
  - Invocación: `--store PATH` (o `CDAD_CONTEXT_METER_STORE`); sin ninguno **falla cerrado**
    (`context-meter.md:16-28`). Evidencia viva: sin store → **rc=1** con diagnóstico que nombra el insumo.
  - Por sesión emite `role`, `model`, `milestones` (`first_resume`, `first_dispatch`),
    `measures` (`previous_calls`, `previous_calls_by_tool`, `previous_reads`, `tool_calls`,
    `session_reads`, `total_output`, `max_output`, `accumulated`, `input_per_step`, `cache`, `cost`,
    `segment_duration`, `time_to_first_resume`, `time_to_first_dispatch`) y `window` (corte por
    inactividad). Verificado en vivo contra el store de OpenCode con `--limit 1`.
  - Por rol: `roles[]` con **cobertura declarada** `{sessions_reporting, sessions_total, cause}`
    (`context-meter.md:132-154`); un subtotal parcial nunca se presenta como total.
  - Despacho: `reader.dispatch_tools = ["subagent","task"]`; `--delegation-dispatch` agrega la
    invocación real de `cdad_delegate.py` (`context-meter.md:156-197`). Verificado en vivo:
    `first_dispatch: absent` con causa declarada (el lector reconoce sólo `subagent`/`task` sin el flag).
- **Qué se puede medir hoy:** sesiones de OpenCode (per sesión y per rol), incluido el **primer
  `resume`**, el **primer despacho** (con `--delegation-dispatch`), las llamadas/lecturas/salida
  previas y el tiempo hasta el primer despacho.
- **Qué queda desconocido:** el **lado Claude Code** (el medidor **no tiene adaptador CC**, D-4);
  la **primera acción de orientación** de una sesión no es un hito del medidor (en 005-003 se declaró
  como propuesta: `005-003/acceptance.md:53-54`); y `cache_write`/`cost` pueden no estar reportados por
  el proveedor (unknown con causa, nunca 0).

---

## 2. Recorrido de uso concreto — HOY (de la petición del dueño a la primera acción útil)

### Variante OpenCode (línea base `005-007/acceptance.md:135-147`)
1. **Dueño:** instrucción breve («Seguí con el epic…») — sin explicar el recorrido.
2. El orquestador carga `cdad-epic` y `cdad-cycle` (llamadas 1-2, ≈54 mil car.).
3. **Step 1 de ambas skills → `state-detection.md` → «read it»** → lee `docs/.cdad-state.json`
   completo (llamada 3, 59 mil car., truncado).
4. **Llamadas 4-19:** exploración manual del state, el plan, la ejecución y los paquetes.
5. **Llamada 20:** `status --project-root .` **rechazado** (raíz relativa; §Eje 2).
6. **Llamada 21:** `status` válido → señala `open-unit` **y** `unknowns: version DRIFT` **sin acción**.
7. **Llamadas 22-30:** investiga versiones, manifiestos y el código del comprobador de versión.
8. Recién entonces: `prepare` → validaciones → `begin` → `--record-dispatch` → **primer despacho**
   (llamada 71; total **70 llamadas / 304.054 car.** previas).

### Variante Claude Code (línea base `005-004/t5-acceptance.md:80-85`)
1. **Dueño:** petición breve; el coordinador es Claude con el agente `cdad-orchestrator` (o las skills).
2. **Llamada 2:** lee el **state completo** — **antes** de `status` (llamada 7). Misma entrada que corrige
   esta feature (mismo Step 1 → `state-detection.md`).
3. **Llamada 23:** primer `Agent` (despacho). 47 llamadas totales; 105 mil car. de salida previa;
   8,7 min. El medidor **no tiene adaptador CC**, así que esa medición es de otro instrumento.

---

## 3. Recorrido objetivo (qué cambia; sin proponer contrato)

### OpenCode
1. **Dueño:** instrucción breve.
2. Las skills se cargan; **Step 1 = la vista `status`** (con raíz relativa aceptada) → proyección
   acotada (1.690 B hoy) **antes** de leer el state.
3. `entry`/`next` dan la acción: `next-unit` → `open-unit`; si hay `DRIFT` **legítimo**, la salida dice
   **qué lo resuelve** (el próximo `prepare` republica los agentes derivados) en vez de invitar a
   investigar.
4. Con un paquete `prepared`, la ruta nombra la acción natural (**despacharlo**), con
   `--replace-packet` como rama condicional.
5. `prepare` → validaciones → `begin` → `--record-dispatch` → **primer despacho**, sin leer el state
   completo ni explorar versiones/manifiestos/código del CLI.

### Claude Code
Misma entrada compartida (las SKILL.md son el texto común): el paso 2 aplica igual. La verificación
del lado CC queda **declarada desconocida** por la frontera (sin adaptador).

---

## 4. Comparación breve de enfoques (qué problema resuelve cada uno, fuentes, límites)

**(a) «Todas las skills empiezan por `status`».**
- **A1 — Reescribir el Step 1 de las dos SKILL.md (y las filas de tabla) para que la primera acción sea
  `status`, dejando `state-detection.md` como ampliación condicional.** Resuelve la causa raíz medida
  (Step 1 manda leer el state). Fuentes: `SKILL.md:249-251,447-469`, `cdad-epic/SKILL.md:56-58,200-209`,
  `project-start.md:223-240`, `orientation.md:14-35`. Límites: edita texto que **tests existentes
  vigilan por ventana** (`tests/test_005_006_t1_start_procedure.py:535-569` exige que el Step 1 siga
  enunciando la rama `resume`; `:188-204` exige la fila `project-start.md` en la tabla); hay que
  conservar ambos. No agrega documentos.
- **A2 — Crear una referencia nueva «common entry» e indexarla.** Rechazado: agrega **mantenimiento
  documental** sin corregir el Step 1 (la causa), y duplica una regla que ya vive en `orientation.md`
  §1 y `project-start.md` §11 → viola «fuente única».
- **A3 — Cambiar sólo el agente `cdad-orchestrator`.** Insuficiente: el plan nombra **las skills**; el
  agente no es el texto compartido entre runtimes y su directiva es «cargar la metodología primero».

**(b) «`status` acepta una raíz relativa como los demás CLI».**
- **B1 — Unificar la resolución de `--project-root` en `cdad_packet.py` (resolver contra el cwd +
  `is_dir()`), como `cdad_result.py:1508-1511`.** Resuelve la llamada 20 y la asimetría. Fuentes:
  `cdad_packet.py:673-677,3776-3791,4294-4304`; `cdad_continuity.py:623`; `cdad_result.py:1508-1511`;
  `cdad-version-check.py:189-192`; `cdad_guard.py:691`. Límites: vuelve **obsoleto** el diagnóstico C4
  (`:3776-3791`), el texto de `orientation.md:68-75` y `project-execution.md:49`, y **el oráculo de
  005-003** `tests/test_005_003_t1_compact_view.py:414-441` (afirma rc≠0 + diagnóstico con raíz
  relativa). Costo bajo y acotado: no toca ninguna otra validación.
- **B2 — Mantener la exigencia de absoluta y sólo mejorar el mensaje.** Rechazado: no resuelve la
  llamada 20 ni la asimetría; el plan pide explícitamente aceptarla.

**(c) «Versión y siguiente acción claras».**
- **C1 — Enriquecer la proyección de versión: cuando el veredicto es `DRIFT`, decir qué lo resuelve,
  distinguiendo la pata que diverge (project vs agents/CLI).** Resuelve las llamadas 22-30. Fuentes:
  `cdad_packet.py:3815-3842,4049-4052`; `cdad-version-check.py:211-236`; `cdad_packet.py:2874`;
  `t5-acceptance.md:102-105`. Límites: hay que **no inventar** (sólo afirmar lo verificado: `prepare`
  republica los derivados del proyecto) y **no confundir ausencia con incoherencia** (005-003 §2.4).
- **C2 — Cambiar la ruta de `prepared` para que nombre la acción natural (despachar), con
  `--replace-packet` como rama condicional.** Fuentes: `cdad_packet.py:3936-3939`,
  `project-execution.md:164-182`, `project-start.md:74-128`. Límite: es texto de la vista, no cambia
  el mapa de `entry` (sigue `continuity-reconcile` para `prepared`, que es correcto: hay trabajo
  pendiente); no hay test que afirme la cadena literal de `next` (verificado).

---

## 5. Propuesta mínima elegida (dirección para el draft; **no** es el contrato)

Una sola palanca por causa, sobre las fuentes que ya existen, sin documento nuevo y sin segunda copia:

1. **(a) → A1.** Step 1 de `cdad-cycle` y `cdad-epic` = consultar primero la vista `status`; `state-detection.md`
   pasa a ampliación condicional (fila de tabla con gatillo), e **indexar `orientation.md`** en la tabla
   de `cdad-cycle` (hoy no figura). La regla se **referencia** (`orientation.md` §1 + `project-start.md` §11
   como composición canónica), no se re-escribe. Conserva las guardas de 005-006/005-010.
2. **(b) → B1.** Resolución de `--project-root` consistente en `cdad_packet.py` (cwd + `is_dir()`),
   retirando el rechazo especial de `status`; corregir el texto que quedaría falso (`orientation.md`,
   `project-execution.md`) y actualizar el oráculo C4 de 005-003 **bajo la autoridad de la fila 11**
   (declarado, no silencioso).
3. **(c) → C1 + C2.** La vista, ante `DRIFT`, dice qué lo resuelve (republicar los agentes derivados por
   el próximo `prepare`), distinguiendo la pata que diverge; y con un paquete `prepared` nombra la
   acción natural (despacharlo), con `--replace-packet` como rama condicional.

Lo que **no** se propone: documento nuevo, segunda copia de la regla de la vista compacta, control
nuevo, test que decida el sentido de un párrafo por listas de palabras, ni cambios en `entry`/`next`
fuera del texto de la ruta.

---

## 6. Plan legible por el humano

### 6.1 Objetivo
Que una sesión nueva entre al proceso por una **ruta breve y común** —`status` primero— antes de leer
el state o explorar, en los dos runtimes, y que la vista diga **versión y siguiente acción** claras,
incluido un `DRIFT` legítimo que se resuelve solo con el próximo `prepare`.

### 6.2 Recorrido (el de §3)
Instrucción breve → `status` (raíz relativa OK) → `entry`/`next` con la acción natural → preparar/
validar/`begin`/`record-dispatch` → primer despacho, sin leer el state completo ni investigar versiones.

### 6.3 Unidades y orden (candidatas; el draft fija el contrato)
- **U1 — (b) Raíz relativa consistente en `cdad_packet.py`** (+ texto que quedaría falso + oráculo C4).
  Va **primero**: la entrada de (a) usa una raíz relativa en el recorrido real.
- **U2 — (a) Entrada común de las skills** (Step 1 de las dos SKILL.md, filas de tabla, indexar
  `orientation.md`), conservando las guardas de 005-006/005-010.
- **U3 — (c) Versión y siguiente acción en la vista** (`DRIFT` legítimo con su resolución; ruta de
  `prepared` con la acción natural).
- Cierre/aceptación: una sesión nueva por runtime, sin contexto previo (la de CC se declara desconocida
  por frontera), medida con el medidor.

### 6.4 Decisiones y riesgos
- **Decisión pendiente (tensión real):** (b) **supersede** el comportamiento C4 de 005-003
  («diagnosticar la asimetría en la salida»). La autoridad es la fila 11 del plan (registrada el
  2026-10-13, aprobada) — pero el orquestador/el dueño deben **autorizar explícitamente** actualizar
  `tests/test_005_003_t1_compact_view.py:414-441`, para que no se lea como debilitamiento silencioso
  de un test congelado.
- **Riesgo 1:** tocar el Step 1 de `cdad-cycle` rompe guardas por ventana de 005-006
  (`test_005_006_t1_start_procedure.py:535-569`, `:188-204`) y de 005-010
  (`:607-658`); mitigación: conservar la rama `resume` y la fila `project-start.md`, y correr esos
  focales en U2.
- **Riesgo 2:** que el texto de la vista prometa de más. Mitigación: la causa de `DRIFT` afirma **sólo**
  lo verificado (el próximo `prepare` republica los derivados del proyecto) y distingue ausencia de
  incoherencia.
- **Riesgo 3:** que (a) se lea como «prohibido leer el state». Mitigación: la regla es «vista primero,
  ampliar ante una necesidad concreta **con motivo registrado**» (`project-start.md:233-240`), no una
  prohibición.
- **Riesgo 4:** el despliegue (activar la versión nueva) es del dueño; la aceptación no puede correr
  sobre el repo sin desplegar → se declara **bloqueo**, no fallo ni éxito
  (`005-003/acceptance.md:7-10`).

---

## 7. Plan de aceptación proporcional

| Insumo / artefacto | Productor | Actor evaluador | Evidencia de cierre |
|---|---|---|---|
| Spec + plan de la feature | architect (draft) | orquestador (HITL delegada; **no** el propio architect) | rutas + sha256; aprobación registrada |
| (b) `status --project-root .` → rc=0; `status` sin bandera → rc=0; `cdad_continuity` sin cambios de conducta | implementer | orquestador (gate) + reviewer | salida real + `PIPESTATUS`/sin tubería; focales nuevos + regresión de 005-003/005-005 |
| (a) Step 1 de ambas skills con la vista primero; `orientation.md` indexado | implementer | orquestador + reviewer | focales de 005-006/005-010 verdes (guardas conservadas) + revisión del texto por **sentido**, no por listas de palabras |
| (c) `DRIFT` legítimo dice su resolución; ruta de `prepared` con la acción natural | implementer | orquestador + reviewer | salida de `status` en un caso `DRIFT` y en un caso `prepared` (fixtures), sin fabricar valores |
| Recorrido de uso, OpenCode | orquestador (sesión nueva real, sin contexto previo) | orquestador; review del informe | medidor de 005-002 sobre el store de OpenCode, `--delegation-dispatch`, per sesión y per rol; informe con el conteo por llamada |
| Recorrido de uso, Claude Code | **desconocido** (sin adaptador CC) | — | declarado unknown con causa; si el dueño corre una sesión CC, se mide con conteo propio (otro instrumento) |
| Suite completa | — | closer (una sola vez, en worktree fijado al commit de cierre) | `make validate` + suite; sin fallos nuevos |

**Meta numérica (orientación, no umbral):** la línea base OpenCode de `005-007/acceptance.md` §7
(70 llamadas, 304.054 car. previas) y la de Claude Code de `005-004/t5-acceptance.md` §7 (llamada 23,
105 mil car.). La aceptación **observa** (primera acción = `status`; sin leer el state completo antes;
sin explorar versiones/manifiestos/código del CLI) y **no** convierte la cifra en demostración automática
(`005-003/acceptance.md:56-60`).

---

## 8. Medidas de seguimiento disponibles

- **Medidor (por sesión y por rol):** `first_resume`, `first_dispatch` (con `--delegation-dispatch`),
  `previous_calls`, `previous_reads`, `tool_calls`, `session_reads`, `total_output`,
  `time_to_first_dispatch`, con cobertura declarada y `unknown` con causa. Store de OpenCode, `mode=ro`.
- **Tamaño:** state (`docs/.cdad-state.json` = **491.576 B** hoy) vs vista (`status` = **1.690 B**, rc=0);
  la relación se mide por inspección del artefacto.
- **Conteo propio sobre el transcript** (partes `tool`) para la primera acción de orientación y para el
  lado CC, que el medidor no cubre.
- **Desconocidos conservados (con causa):** adaptador/medición CC (D-4); hito «primera acción del
  encargo» en el medidor (propuesta, no asumida); `cache_write`/`cost` no reportados por el proveedor.

---

## 9. VERIFY (no verificado desde el repo; se marca, no se asume)

- **V1.** Que la versión desplegada al momento de la aceptación incluya (a)(b)(c): el despliegue es del
  dueño; sin desplegar, la aceptación queda bloqueada.
- **V2.** El orden exacto de carga de la skill y sus referencias **en Claude Code** (la ruta de carga
  del runtime no es la misma que en OpenCode) — fuera de alcance por la frontera.
- **V3.** Qué pata exacta produce el `DRIFT` en la corrida real de aceptación (project vs agents/CLI):
  debe **leerse** de las líneas del chequeo, no inferirse.
- **V4.** Si algún consumidor fuera de `tests/test_005_003_t1_compact_view.py` depende del mensaje
  genérico de rechazo de raíz absoluta: grep no encontró ninguno (sólo `project-execution.md:49` y
  `orientation.md:68-75` como texto, y el asset con `<ABS>`), pero es un borde a confirmar en el draft.
- **V5.** El efecto de (a) sobre la línea base de Claude Code no se puede medir con el medidor actual;
  sólo con conteo propio si el dueño corre esa sesión.

---

## 10. Fronteras (resumen)

No se anticipan 005-012 ni 005-013; el adaptador CC y la medición CC siguen fuera; no se reabren
005-003/005-004/005-007 salvo la corrección que la fila 11 manda (y su oráculo C4, **declarado**); sin
CI, sin WebUI, sin sandbox, sin plataforma de jobs; sin tocar HOME. Fuente única: la spec **referencia**
las reglas existentes (vista compacta 005-003, planificación/unidad 005-007, procedencia 005-005); toda
extensión es **aditiva y declarada**.

---

### Evidencia de este informe

- **Archivos modificados en el repo:** ninguno (rol de solo lectura). `git status` sin cambios de producto.
- **Comandos exactos ejecutados (solo lectura, acotados):**
  - `sha256sum skills/cdad-cycle/packets/{common.md,roles/architect.md,substages/architect-discovery.md}` → coinciden con los `sha256` de `instruction_sources` del paquete; `sha256sum docs/epics/epic-005-real-operation/plan.md` → `63dda3b8…059a6` (contrato verificado).
  - `python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root "$PWD"` → rc=0, 1.690 B.
  - `python3 … cdad_packet.py status --project-root .` → rc=2 (diagnóstico de asimetría, sin proyección).
  - `python3 … cdad_packet.py status` (sin bandera) → rc=0.
  - `python3 … cdad_continuity.py resume --project-root . --execution-context .cdad/executions/<id>/execution.json` → rc=0 (`state: no-checkpoint`).
  - `python3 … cdad-version-check.py --project-root "$PWD"` → `UNKNOWN` rc=3 (CLI sin `version.txt` en el checkout).
  - `python3 … cdad_context_meter.py --store <home>/.local/share/opencode/opencode.db --limit 1 --json` → rc=0, 1 sesión, `roles[cdad-reviewer]`, `milestones` y `measures` presentes.
  - `python3 … cdad_context_meter.py --json` (sin store) → **rc=1** (fallo cerrado que nombra el insumo).
  - `wc -c` sobre SKILL.md y referencias (magnitudes de §1).
- **Commit:** no aplica (rol de solo lectura; sin escrituras en el repo).
- **Transporte:** los mismos bytes de este texto en `<tmp>/opencode/discovery-005-011.md`.
