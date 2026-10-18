# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto. Este archivo se carga al inicio de cada sesión de agente.

## Capas y boundaries

- `agents/*.md` — definición de roles: frontmatter (permisos por path, bash
  allowlist, modelo) + directiva del rol. Thin shells: la lógica vive en
  skills, no en el agente. Desde 004-001 (2026-09-29) son salidas declaradas
  de `scripts/cdad-generate.py`: no se editan a mano, se regeneran desde
  `sources/` (PD-2/5).
- `skills/cdad-cycle/` — el ciclo: `SKILL.md` (contrato mínimo siempre
  cargado) + `references/stage-N-*.md` (profundización por etapa, se carga
  una a la vez).
- `skills/cdad-epic/` — coordinación multi-feature (planning light,
  deliberadamente sin descomposición exhaustiva).
- `skills/odoo-*/` — especialización por stack: variante `cdad-*-odoo` de
  cada agente + skills de conocimiento por rol + contrato make.
- `tests/` — validación estructural del framework (bash asserts).
- `docs/specs/<NNN-id>/` — spec + VALIDATION + review por feature.
- `install.sh` — única vía de instalación (copia, nunca symlink, sin --delete).

## Convenciones de código

### Naming

- Agentes: `cdad-<rol>` y variante `cdad-<rol>-odoo`.
- Skills: kebab-case con prefijo de dominio (`odoo-reviewer`).
- Specs: `NNN-feature-id/` (numeración correlativa).

### Organización de archivos

- Reference nueva vs. extensión: se decide por "¿es una etapa/flujo o una
  profundización?" (ver epic superpowers-gaps para los 5 casos resueltos).
- Todo artefacto de rol read-only lo materializa el orquestador (§5 del
  contrato de roles).

### Errores y excepciones

- Anti-patrones: `references/anti-patterns.md` (AP-N) — toda desviación se
  cita con su código.
- Anti-rationalization table: excusas ya refutadas por escrito; no se
  negocia con la excusa, se aplica la refutación.

## Patrones del framework

- Contrato de roles con invariantes anti-bias: reviewer en familia de modelo
  distinta al implementer; test-writer nunca ve `src/`; mapeo
  test↔postcondición auditado por sesión distinta.
- Delegación por orden de preferencia: sub-agentes nativos → handoff packet →
  inline (último recurso, con caveat de aislamiento registrado).
- Evidencia, no confianza: cada gate se cierra con output pegado.

### Guards de progreso — analizador read-only, juicio en el orquestador (epic 003, 2026-10-07)

- **`cdad_guard.py` es analizador, nunca orquestador.** Determinista, stdlib y
  read-only salvo `record` (escribe solo bajo `.cdad/executions/<id>/guards/**`).
  Expone `classify` (repetición sin progreso + polling sobre `trace-v1`), `preflight`
  (prevalidación **consultiva**), `record`/`budget` (durables) y el canal de escalado.
  El juicio semántico es del orquestador; el guard **nunca** cambia spec, autoridad ni
  prioridad y **nunca** escribe `docs/.cdad-state.json` (single-writer = orquestador,
  regla ya vigente desde 003-002).
- **Preflight consultivo (enmienda del dueño, 2026-10-06).** Salir de la raíz del
  proyecto está **habilitado por defecto** (`allow`, motivo honesto `outside project
  root: not governed by project policy`); `deny` **solo** con regla explícita de la
  política o del rol; herramienta sin destino resoluble ⇒ `unknown`, nunca un `deny` ni
  un `allow` fabricado. Lee `docs/cdad-policy.json`, no lo escribe.
- **Presupuesto/eventos durables keyed por `execution_id`.** Bajo
  `.cdad/executions/<id>/guards/**`, keyed por `execution_id+packet_id+attempt`; el
  `record` es create-exclusive (reescribir la misma clave = conflicto, bytes intactos);
  reanudar **no** reinicia contadores. Interfaces pensadas para no obstaculizar 003-004.
- **Frontier de honestidad:** un `progress_token` ausente/no-string es señal **no
  observada** (nunca fabrica un incidente); el guard **no** canonicaliza args (lo hace
  el grabador, declarado en el schema `trace-v1`); no repite efectos (reconcilia
  receipts de 002 y solo señaliza).
- **Cuidado de adopción (uso real T5):** el digest de progreso **por conjunto de rutas
  es demasiado grueso** → falsas alarmas; el registro de progreso debe ser por
  **contenido/diff** (deuda G1). Y un lanzamiento desacoplado (`&`/`nohup`/redirección)
  vuelve `ok` en la traza: es `unknown`, no éxito. Versión operativa adoptada para el
  uso: `939f501` (raíz aislada); el lector en vivo es deuda, no producto.

## Palanca `write: ask` y permisos de bash (cdad-010, ADR-009)

### Palanca `write: ask` (2026-09-12; enmienda de ubicación 2026-09-13)

Los 10 agentes declaran `permission.write: ask` — la clave `write` ANIDADA
dentro del bloque `permission:` del frontmatter (NO top-level: el KNOWN_KEYS
del clasificador no incluye `write` top-level y una palanca top-level es
inerte — el agente colapsa a read-only y `task` lo rechaza; verificado por
probe en cdad-010, enmienda registrada en el spec H1). Doble rol NO obvio: es
la palanca que hace al agente **task-able**. Motivo: el clasificador del
plugin de sub-agentes lee la clave `write` del bloque `permission:` anidado
para decidir si el agente es write-capable o read-only; el runtime NO la
evalúa (el tool `write` pide "edit" — cero evaluaciones `permission=write`
en logs). Mecánica: el agente queda task-able sin generar prompts de permiso.

**REGLA DE VIGILANCIA: si una versión futura de opencode empieza a evaluar
`write` en runtime, la palanca `write: ask` genera prompts de permiso en cada
escritura y hay que revisar los 10 agentes.** Checklist al migrar versión:
(1) grep de logs buscando `permission=write`; (2) si aparece, migrar la
palanca a otra vía y re-probar la clasificación task/delegate con los probes
de cdad-010 como baseline.

### Bloques `permission:` anidados y orden findLast

El clasificador del plugin lee SOLO el bloque anidado `permission:`
(edit/bash/read); las claves top-level caen en `options` — inertes en
runtime. Semántica del matcher: **catch-all primero, específicas después**
(findLast: la última regla que matchea gana). Una regla específica antes del
catch-all es un bug de config. Única excepción documentada de `ask`: la
palanca `permission.write: ask` (anidada).

### Política vigente de diseño — autonomía supervisada (2026-09-24)

[ADR-011](adr/ADR-011-autonomia-supervisada-limites-proporcionales.md) gobierna
los próximos contratos: capacidades suficientes dentro del encargo, principios
explicados y verificación al re-entry. El orquestador acepta decisiones dentro
del mandato, corrige causas de fricción y no cierra gates con evidencia inválida.
Repite solo trabajo afectado; no cada tarea completa por cualquier desvío.
La migración de configuraciones aterrizó en 004-001 (2026-09-29): agentes generados desde fuentes e instalación solo desde staging; los apartados históricos siguientes son referencia de cómo se llegó acá.

La regla histórica de demostrar un problema con una sola invocación no es un
criterio universal de riesgo: usar evidencia adecuada al efecto observado,
explicitar lo no comprobado y evitar probes innecesarios o inseguros. Los textos
siguientes documentan la implementación anterior, no un requisito de conservar
catch-all deny o pares de comandos durante la simplificación.

### Fuente única de agentes — generador determinista + staging (epic 004, 2026-09-29)

- **Agentes como salidas declaradas:** los 22 archivos de `agents/` se
  generan con `scripts/cdad-generate.py` desde `sources/` (Markdown con
  delimitadores); misma entrada produce bytes idénticos (PD-2). Cierre
  verificado en 004-001 (criterio 2): regeneración con stack/perfil
  registrados en el manifest idéntica a los 22 archivos. **Nadie edita un
  agente a mano** (personas ni agentes); cambiar una regla canónica y
  regenerar actualiza a los consumidores (PD-5) y `install.sh --check`
  detecta la copia instalada que difiere de staging.
- **Generación ≠ instalación:** el generador escribe en staging con manifest
  (sha256, fuentes, comando de regeneración, stack/perfil); el instalador
  **nunca lee `sources/`** (PD-18; `tests/test_install_ownership.py`) y
  registra propiedad de archivos: primera instalación sin borrar nada (PD-6),
  conflicto de hash reportado sin sobrescribir (PD-7), uninstall solo lo
  propio (PD-8). El exceso del techo del bloque estático produce error
  explícito, no una salida mezclada (PD-19; `tests/test_static_block_ceiling.py`).
- **Política bash permisiva con barreras por ruta:** la política por rol es
  derivable de la fuente canónica con efecto declarado por regla (PD-1,
  T4, review-4 approved). Las listas FORBIDDEN se retiraron por decisión del
  dueño (`80f9b90`) y el control quedó como comprobación semántica con
  trazabilidad (PD-10; `tests/pd10_permission_semantics.py`, con la
  mutación M6 el checker pasa de 27/27 a 26/27 con el FAIL trazado, verificado
  en la review del orquestador). Las barreras de
  path se prueban en ambas direcciones (PD-12): operación legítima con éxito
  y fuera de rol bloqueada por el mecanismo declarado (`path-guard.sh`
  instalado, exit 2 / 0).
- **Orquestación con construcción delegada y verificación propia:** el
  orquestador delega la construcción a los roles CDAD (sesiones aisladas,
  registro PD-17 por tarea) y no acepta un reporte como evidencia: revisa el
  artefacto y reproduce lo verificable ("reproducido" en closure.md =
  corrido por el orquestador). La review encuentra evidencia engañosa (p. ej.
  mutaciones que no mataban su reemplazo) que el reporte del agente no muestra.
- **Alcance del recorrido vivo:** la prueba de capacidad desde el producto
  instalado (5 roles, 39 llamadas, 0 denegaciones) demuestra capacidad
  operativa por el camino legacy (sin paquetes); el ciclo con paquetes y
  contexto reducido se verifica en 004-002.

### Ejecución por proyecto v2 — política, derivados y guard (epic 004, 2026-10-02)

- **Política única del proyecto:** `docs/cdad-policy.json` (solo
  `schema_version`, `path_policy`, `temporary_roots`). Clasifica raíces,
  archivos exactos, tests co-ubicados, temporales y `private_paths`; ningún rol
  la edita; es la fuente de scopes y derivados (PD-1/2/7).
- **Paquetes v2 e identidad lógica:** `.cdad/executions/<execution-id>/execution.json`
  + `dispatches/<attempt-id>.json`; `execution_id` estable entre roles, runtimes
  y sesiones; runtime/modelo/sesión son observaciones (unknown=`null`).
- **Aplicación por runtime:** OpenCode usa agentes derivados de proyecto
  `.opencode/agents/` (I9, manifiesto `.cdad-derived.json`); Claude Code usa el
  guard dinámico `path-guard.sh` que clasifica con el CLI instalado (I10).
- **Barrera viva por ruta = `read` (OpenCode).** `read` resiste variantes
  absoluta/relativa/`..` y el listado de directorio muestra nombres, no
  contenido. `grep`/`glob` se evalúan por patrón, no por ruta (W-2); `edit`/`write`
  no acotados en vivo en 2.0.16 (W-3). La disciplina de escritura es instrucción
  + auditoría del orquestador (`git diff --name-only` contra `write_scope`) —
  regla general de límites L-1 en los 22 prompts generados.
- **`private_paths`:** la única barrera nueva deliberadamente obvia; deny en
  `read` para todos los roles en OpenCode y bloqueo de herramientas mediadas en
  el guard CC; no sustituye instrucción ni auditoría.
- **R5 aceptado:** el guard cuesta ~252 ms/llamada con política v2 (vs 32 ms
  legacy, N=20), sin caché.

### Autorización por rol pineada y reemplazo con conservación (epic 005, 2026-10-09)

- **La aprobación de contrato es por rol y con la fuente correcta (PD-1..PD-6).** El
  **architect** se habilita con la aprobación del **plan del epic** (`epic_history`
  `{epic|epic_id, stage: "epic-plan", approved_by}`; **sin** pin de hash — D2: el plan es
  mandato vivo, se edita después de aprobado y la autorización sigue vigente).
  **test-writer/implementer/reviewer** exigen una entrada `stage_history` `specification`
  que **nombre el contrato**: `contract_path == contract["path"]` **y**
  `contract_sha256 == sha256` verificado (C1/PD-18; INV-8). El enforcement vive en
  `validate_request` (donde se conoce el `role` y el sha ya está verificado contra el
  archivo); `_validate_v2_vigency` conserva la coherencia de estado (feature/epic/
  delegación). Una entrada histórica no conforme (rectificada, de otro vocabulario, sin pin,
  o con path ajeno) **no habilita** autoridad (INV-6/PD-6/PD-18). Editar la spec deriva su
  sha → la aprobación deja de coincidir (PD-4) y se **re-registra** (el pin anterior queda
  superado).
- **Reemplazo de un paquete preparado y no despachado (PD-7..PD-11, PD-16;
  `--replace-packet`).** Solo el `active_packet` con `status: "prepared"` es reemplazable;
  un `dispatched` exige **reconciliación** (PD-10) y uno terminal no se toca. Exige
  obsolescencia verificable (sha del contrato o revisión de política cambiados; PD-8) y
  `--reason` no vacío (PD-9). Re-resuelve el contrato del día y publica el sucesor **solo**
  con la aprobación vigente (PD-11: nunca inventa autorización). El paquete anterior queda
  **byte a byte idéntico** (INV-3) y se escribe `.superseded.json` durable. Ninguna entrada
  de `stage_history`/`epic_history` se crea o modifica (INV-2).
- **El reemplazo conserva el encargo y admite correcciones explícitas (C2/PD-19..PD-24;
  INV-7; D7).** Sin opciones de corrección, el `REQUEST.json` nuevo conserva campo a campo
  el anterior (`execution_id, role, substage, objective, inputs, read_scope, write_scope,
  invariants, expected_output, evidence_required`); **no** recomputa defaults. Las opciones
  `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` reemplazan
  la lista/campo **entero** (el centinela `-` como único valor la deja vacía; `-` mezclado →
  rc=2). Los pisos obligatorios del rol (`DEFAULT_INVARIANTS`/`DEFAULT_EVIDENCE`) se
  re-agregan siempre (PD-21). Las correcciones pasan las **mismas validaciones** que un
  `prepare` normal (PD-22; diagnóstico campo/motivo/opción). El argv mezclado se rechaza
  antes de cualquier lock o escritura (PD-23). `.superseded.json` suma
  `conserved_fields`/`changed_fields` disjuntos y exhaustivos (PD-24).
- **Marcadores de bloqueo distinguibles y accionables (PD-12).** `approval pending` (falta
  la aprobación o su pin no nombra el contrato), `packet obsolete` (contrato o política
  cambiados) y `state incoherent` (el state se contradice: binding, feature/epic, idle) son
  mutuamente excluyentes por condición, salen por stderr con rc=2, nombran el registro/falta
  y la acción legítima siguiente, y no alteran el state ni publican archivos.
- **Reposo legítimo (PD-13..PD-15).** `active_feature == null ⟺ current_stage == "idle"`; se
  tolera `execution` remanente y `active_packet` terminal `completed|failed`; un paquete en
  vuelo (`prepared|dispatched`) con reposo → `state incoherent`. `validate-state` sale rc=0
  `VALID: idle`.
- **Referencia operativa:** `references/project-execution.md` §2 (autoridad) y §8
  (reemplazo); el contrato normativo es la spec de la feature
  (`docs/specs/005-001-idle-and-v7-bootstrap/spec.md`, PD-1..PD-24).

### Coherencia de la adopción — política única de evidencia y procedencia declarada (epic 005, 2026-10-09)

- **Una sola política de evidencia, con dueño canónico y consumidores que remiten
  (INV-6).** La política vive en **un único lugar** editable:
  `skills/cdad-cycle/references/stage-3-tdd.md` §**«Test evidence policy»**
  (regresión proporcional al cambio; suite completa **al cierre** de la feature o
  antes si se toca instalador/staging/renderer; reutilización de evidencia
  equivalente; **la metodología define la evidencia y el proyecto declara los
  comandos**; una condición local se registra y no se vuelve requisito). La regla
  de **equivalencia** conserva su dueño en `references/re-entry.md`
  §«Equivalence of a registered run». Los consumidores (paquetes de
  GREEN/refactor/review-fix, `packets/roles/implementer.md`, `SKILL.md`, las
  referencias de etapa) **referencian** la política y **no copian** su texto; la
  suite completa es gate de **cierre**, nunca «por GREEN».
- **El reemplazo valida el encargo resultante completo (005-005 PD-1..PD-7;
  INV-4).** `--replace-packet` valida **todo** el encargo resultante (conservado +
  corregido): cada `input` existe y cae dentro de algún `read_scope`; scopes
  clasificados por la política; `invariants`/`evidence_required`/`expected_output`
  no vacíos; diagnóstico **campo/motivo/opción**. El **camino normal de `prepare`
  no cambia** (la exigencia de existencia es propia del sub-modo; un `input`
  declarado inexistente en `prepare` normal sigue `rc=0`); una lista `inputs` vacía
  legítima (`--input -`) sigue válida.
- **La procedencia de la instalación se declara y no cambia en silencio (005-005
  PD-12..PD-14; INV-7).** `prepare` resuelve el origen de los agentes de proyecto
  en orden **`CDAD_OPENCODE_AGENTS_DIR` > registro de activación
  (`.cdad/activation.json`) → `<adopted_root>/.config/opencode/agents` > global
  (`$HOME/.config/opencode/agents`)**. Si el origen resuelto difiere del registro o
  del `source_dir` del manifiesto anterior, emite un **diagnóstico por stderr** que
  nombra el registro y las versiones en juego (caso real MIX-V6V7). El manifiesto
  publicado `.opencode/agents/.cdad-derived.json` declara `source_dir` y
  **`source_version`**, y el instalador escribe **`version.txt`** en la raíz
  instalada, de modo que **qué versión cargó una sesión es verificable desde el
  artefacto publicado**. `opencode reload` sobre un servidor ya iniciado queda
  **NO verificado** (se documenta el hecho del dueño y la comprobación aislada; no
  se afirma).
- **El cierre es un test de integración en raíz aislada (005-005 PD-18; INV-8).**
  La versión nueva del repo se instala en una raíz aislada (nunca HOME) y con su
  CLI se corre `prepare` → `--replace-packet` (validación completa) → despacho con
  validación proporcional; sin rodeos manuales y sin tocar HOME (guard estructural).
- **Referencia operativa:** `references/runtime-adoption.md` §«Procedencia de los
  agentes de proyecto»; `references/opencode-delegation.md` §«Reload, version and
  provenance»; contrato normativo en la spec de la feature
  (`docs/specs/005-005-adoption-coherence/spec.md`, PD-1..PD-18).

### Recepción, materialización y evidencia de artefactos (epic 003, 2026-10-06)

- **Herramientas de artefactos:** `skills/cdad-cycle/scripts/cdad_result.py`
  (+ wrapper `scripts/cdad_result.py` + entrypoint instalado equivalente) expone
  `receive`, `validate-receipt`, `materialize`, `run-python-unittest` y
  `validate-run-evidence`. Construyen sobre el runtime v2 (execution context,
  paquete renderizado, binding de autoridad, observación de dispatch I8); no
  redefinen sus esquemas.
- **Store operacional:** `.cdad/runtime/` (aditivo dentro de `.cdad/`,
  gitignored) guarda parts + bundle + receipt por `(execution_id, packet_id)`;
  el inbox de staged parts es `.cdad/inbox/`. Publicación atómica (temp + fsync
  + rename exclusivo); una sola finalización durable por execution/packet; el
  retry idéntico devuelve el receipt byte a byte.
- **Recibo mecánico que NUNCA aprueba:** `semantic_status` siempre `pending`,
  `approval_effect` siempre `false`; recepción, materialización y aprobación
  semántica son hechos distintos y ninguna operación cierra un gate.
- **Un solo escritor del state:** `docs/.cdad-state.json` lo cambia solo el
  orquestador. `receive`/`materialize`/`run-evidence` no lo tocan;
  `state_transition_requested=received` es una transición lógica que el
  orquestador mapea al estado de paquete `completed` (vocabulario de 001). La
  referencia de receipt en `stage_history` la agrega el orquestador (forma
  existente; sin cambio de esquema).
- **Política de artefactos (§7):** tabla cerrada `artifact_kind`/rol-subfase que
  fija la **raíz permitida**; el **target exacto** se declara en la autorización
  (create-only/CAS). Cierre rol↔kind fail-closed (`_allowed_kinds`). Los ADR
  (`docs/adr/`) **no** están en la tabla: su materialización sigue siendo del
  orquestador (ADR-003).
- **Evidencia de runner:** solo `python3 -m unittest` (argv sin shell);
  snapshots before/after calculados por la herramienta (no acepta digests del
  caller); `valid-current` exige exit 0, `tests_run>0`, al menos un test no
  skipped, cero failures/errors/runner exceptions, árbol no mutado y contract
  vigente. La ligadura `argv`↔selecciones es **fail-closed**: lo que no puede
  demostrarse degrada a `unknown` (whitelist cerrada de opciones invariantes).
- **Protocolo canónico:** `skills/cdad-cycle/references/re-entry.md`
  (RECEIVE → RECONCILE → MATERIALIZE → STATE TRANSITION), con el staging del
  TEXTO FINAL como paso mecánico previo del orquestador.

### Continuidad — checkpoint content-addressed + proyección on-demand + `reconcile` como oráculo (epic 003, 2026-10-07)

- **`cdad_continuity.py` es read-only sobre el producto.** `reconcile`, `resume` y
  `trigger` son deterministas y de solo lectura; `begin`/`checkpoint` escriben **solo**
  bajo `.cdad/executions/<id>/continuity/**`. El CLI **nunca** escribe
  `docs/.cdad-state.json`: el single-writer del state sigue siendo el orquestador
  (regla vigente desde 003-002/ADR-003) y el CLI **nunca aprueba**.
- **Checkpoint content-addressed (L2) = autoridad de delegación/decisiones/presupuesto.**
  Cuerpo canónico cuyo `sha256` es el propio digest, más `prev_checkpoint_sha256`, `seq`
  monotónico y `references[]` con digest. `resume`/`reconcile` verifican sha del cuerpo,
  eslabón previo y existencia+digest de cada referencia; cualquier fallo → rc≠0 con el
  delta exacto (sin truncar). `begin` con cuerpo idéntico al head es **no-op (rc 0)**;
  cabezas divergentes o igual-sha-con-cuerpo-distinto ⇒ **escalar** (sin `generation`).
- **Memoria activa = proyección on-demand (L1), no persistida.** No existe `ACTIVE.json`:
  la proyección se reconstruye desde la cabeza L2; su ausencia **no** es error de
  `reconcile` ni de `resume`. La historia es L3: se consulta **por referencia** (state/
  `stage_history`, receipts 002, eventos 003, dispatches I8, Memory Bank), nunca se embebe
  el transcript. `--max-bytes` (default 16 KiB) es un techo que **falla cerrado**, nunca
  trunca.
- **`reconcile` es el oráculo de efectos ya aplicados.** Antes de todo retry/resume
  consulta receipts/journal de 002, dispatch I8 y state: con receipt válido **no** ofrece
  repetir el efecto; una sesión desaparecida es `dispatched-unknown` (≠ fracaso ≠
  autorización de repetir, invariante 3). `continuity` **consume** el receipt de 002; **no
  materializa** (eso sigue siendo del orquestador con autorización explícita). Para
  clasificar `received` el flujo de despacho debe pasar la salida por `cdad_result`
  `receive` (deuda RU-2a).
- **`trigger` es señal, no límite.** Solo devuelve `prepare`/`rotate` con contador **y**
  límite enteros; en cualquier otro caso `trigger: unknown`, `context_*: null` y
  `unknowns[]`. **Prohibido** convertir bytes en tokens o presentar un proxy como límite
  (desconocido permanece desconocido). El presupuesto de intentos es durable (003) keyed
  `execution_id+packet_id+attempt`: reanudar **no** reinicia contadores.
- **Autoridad desde el estado estructurado.** Vigencia y `authority_ref` se leen de
  `hitl_delegation` en `docs/.cdad-state.json`; no se parsea la prosa del archivo de
  autoridad. Autoridad vencida puede reconstruir contexto pero **no** autorizar
  dispatch/materialize.

### Continuidad tolerante a documentos vivos — la clase la declara el escritor (epic 003, 2026-10-08)

- **La clase la declara la referencia, nunca la ruta (D2/P3).** `--update.references[]` acepta
  un string (compat: `class = contract`) o un objeto `{"path", "class", "fields"?}` con
  `class ∈ {contract, living}`. El CLI **no** deriva la clase de rutas fijas:
  ausente/desconocido ⇒ `contract` (**falla cerrado**). La clase resuelta se **estampa** en el
  body del checkpoint.
- **`contract` bloquea; `living` informa y nunca calla (P1/P2/D3).** Cada referencia visible en
  `resume`/`reconcile`/`trigger` se reporta `{path, class, sha256, current_sha256,
  state ∈ unchanged|changed|missing, legacy?}`. Deriva `contract` ⇒ `rc≠0` con `path` y delta
  exacto; deriva `living` ⇒ `rc 0` con `state: changed|missing` (jamás en silencio).
- **Proyección de autoridad del state con `fields` (D1/P4/BL-3).** `fields` (subconjunto de
  claves top-level de un JSON) hace que el digest cubra solo esa proyección; recomendado
  `hitl_delegation`, `approver`, `execution` (el resto —`stage_history`— es progreso, residuo
  **R-2** → deuda). `fields` sobre un archivo **no-JSON** o con **proyección vacía** ⇒ `rc≠0`
  **al escribir** (el digest se congela en el body; nunca un digest constante que dé cero
  integridad en silencio).
- **`checkpoint` ≠ `begin` (P5/P6/T4-CKPT).** El body gana `record` (`begin`|`checkpoint`); un
  `checkpoint` con la clave del head **apendea** un eslabón (`seq+1`, `prev`), no se rechaza
  como split-brain; un `begin` divergente con la misma clave sigue **cerrado**; un checkpoint
  idéntico re-ejecutado es **no-op**. `_detect_split_brain` = **≥2 bodies con
  `record != "checkpoint"` por clave** (huérfanos/legados pre-RU-2).
- **Legado por comparación (P7/D6/R-1).** Un cuerpo pre-003-007 sin `class`: digest igual al
  congelado ⇒ verificado `contract`; distinto/ausente ⇒ `changed` con `legacy: true` y **no
  bloquea**. **Excepción documentada:** la clase de legado **no está congelada**, así que el
  legado **informa** cualquier documento cambiado —incluida una decisión que en un checkpoint
  nuevo sería `contract`— en lugar de bloquearlo.
- **Regla de encargo + wiring en el orquestador (P10/D9/BL-1/R-4).** `sources/roles/orchestrator.md`
  expresa el encargo como **una unidad despachable** (una tarea del plan o una subfase TDD; los
  RED/GREEN como despachos separados la satisfacen), con postcondiciones trazadas a ≥1 test y un
  diff acotado y revisable; el bloque "Continuity wiring" declara explícitamente qué es `living`
  y qué `contract` (o un puntero estricto a la sección de clases de `continuity.md`); `make
  agents` regenera **solo** los dos agentes orquestador.
- **Límites declarados:** **MIX-V6V7** — la v6 leyendo un checkpoint v7 con `fields` digiere el
  archivo completo y falla cerrado ⇒ usar **una sola versión del CLI por ejecución**;
  **T2-R1** — un `begin` idéntico tras un append de su clave da `rc≠0` en lugar de no-op;
  sin detección de forks de checkpoint mismo-key (deuda).

### Activación por runtime — adopción por proyecto hacia una raíz aislada (epic 003, 2026-10-08)

- **Una sola versión operativa, en una raíz aislada versionada.** La versión de CDAD que
  cargan los runtimes se instala con `CDAD_INSTALL_ROOT=~/.cache/cdad-adopted-<rev>
  bash install.sh` y se registra en `docs/runtime-adopted-version.md` (tabla vigente +
  historial) con verificación de consumidor. La identidad se comprueba contra el
  `.cdad-install-manifest.json` de la raíz adoptada. Se adopta **solo en el límite de
  tarea/cierre y tras review independiente**; la versión anterior se conserva.
- **La activación es por proyecto y NUNCA escribe las configuraciones del HOME real
  (I1/I2).** `scripts/cdad-activate.py --project-root R --adopted-root A`
  (+ `references/runtime-adoption.md`) emite archivos **git-ignorados** que apuntan a `A`:
  OpenCode (`.opencode/opencode.jsonc`), Claude Code (`.claude/{agents,skills}`, con el
  `command:` del hook reescrito a `<A>/.claude/cdad-scripts/path-guard.sh <rol>`) y Codex
  (`.agents/skills`). Propiedades exigidas: **determinista** (mismo input → bytes
  idénticos), **`--dry-run` sin efectos**, **no-clobber** (destino divergente → error
  nombrado, nunca sobrescribe) y **contención de ruta** (`realpath` estricto bajo
  `realpath(R)`; un symlink que escapa → conflicto, rc≠0, todo-o-nada).
- **El hook de Claude Code fija el clasificador a la raíz adoptada (RU-1).** Se emite
  `command: CDAD_PACKET_CLI=<A>/…/cdad_packet.py <A>/…/path-guard.sh <rol>`; ningún
  `command:` emitido depende de `$HOME` (`path-guard.sh:134` resolvía la copia vieja de
  HOME → fail-closed). El fail-open de P5 vale solo **sin política o con script ausente
  (`exit 127`)**; con política presente y clasificador inválido, **falla cerrado**.
- **Límites declarados por runtime (no prometer paridad):** OpenCode carga la raíz
  adoptada ✓; **Claude Code** mezcla versiones (las skills de usuario ganan a las de
  proyecto) y los hooks del frontmatter no corren si la carpeta no es de confianza —
  mitigable despachando con `--setting-sources project,local`; **Codex** usa la copia de
  proyecto pero el catálogo también lista la vieja de HOME, sin adaptador de agentes.
- **`receive` en el ciclo y `continuity` cableados (complementa ADR-014/ADR-016).**
  `begin` (write-ahead), `checkpoint` (límite), `reconcile` (antes de retry/resume),
  `resume` (sesión nueva); `trigger` advisory, `classify` fuera (sin lector de sesiones).
  Fricción declarada: **T4-CKPT** (el checkpoint de límite comparte clave con el `begin`)
  y **T4-REF** (reanudación bloqueada si cambia una referencia a documento vivo) — deuda,
  no producto.
- **Activación no commiteada = producto pendiente de decisión del dueño.** Configs de
  activación git-ignoradas (I3); activar/apuntar a la raíz v6 es decisión del dueño. Sin
  CI: el gate es la suite local.

### Delegación externa — señal durable real, modo de carga y directorio del proyecto (epic 005, 2026-10-11)

- **La señal durable la produce el runtime, nunca el fixture.** El adaptador OpenCode espera la
  **base de sesiones SQLite** del runtime (`session_v2` + `session_message`), abierta en **solo
  lectura** (`mode=ro`) en la ruta que declara la config de ejecución (`sessions_db`; **ruta
  configurable, jamás hardcodeada**). Un store ausente/ilegible/no-SQLite/con esquema incompleto
  **falla cerrado** con diagnóstico que nombra el esquema/columna; el `UnicodeDecodeError` deja de
  existir. El esquema **no es contrato público**: se valida por columnas requeridas, no por marcador
  de versión; sin `immutable=1` con el servicio vivo; nunca se escribe el store.
- **Correlación inequívoca por `--session <id>`.** El adaptador **elige** el id y lo pasa; la fila
  durable lleva ese `id`, `agent` e `idle_outcome`; el texto final es el **último** `session_message`
  `assistant`. La terminación se clasifica desde `idle_outcome` (`succeeded→completed` con texto;
  `failed→blocked`; `interrupted→cancelled`; sin idle dentro de la espera acotada → `timeout`),
  **nunca** desde el `rc`; la espera es acotada (`wait.timeout_seconds`; su ausencia falla cerrado
  pre-despacho).
- **`mode: subagent` es entry no interactiva en la versión instalada.** La barrera deja de ser
  `mode: all`; la identidad se verifica desde la fila durable (`session_v2.agent == "cdad-<rol>"`),
  **sin fallback** a un agente no-Cdad. `cdad-generate.py` y la fuente de agentes **no** cambian.
- **OpenCode resuelve el directorio del proyecto desde `PWD`, no desde el cwd.** El adaptador fija
  `PWD` = raíz del proyecto explícito en la invocación. Invocación soportada: paquete byte-idéntico
  por **stdin**; `--standalone` por defecto (servidor privado); `--server <url>` por config como
  alternativa (nunca a la vez); `--auto` por config (activado por defecto, documentado como
  auto-aprobación de permisos **no-sandbox** —los deny-maps de path siguen siendo la barrera—).
- **Higiene del test:** un doble que **fabrica** la señal que el producto espera valida el contrato
  **contra sí mismo**. Los tests deterministas usan un **SQLite real chico** con el esquema observado;
  la aceptación real (instalación y proyecto aislados, runtime real con `--standalone`) es un gate
  **aparte**, omitido por defecto y habilitado por variable de entorno.
- **Referencia operativa:** `references/cli-delegation.md` y `references/opencode-delegation.md`;
  ADR-023 (**enmienda 2026-10-11**); contrato normativo en
  `docs/specs/005-010-real-opencode-delegation/spec.md`.

### Delegación externa — selección de modo explícita y servicio de fondo no gestionado (epic 006, 2026-10-17)

- **El modo de ejecución es explícito y no hay fallback silencioso.** `mode` ∈ {`server`, `service`,
  `standalone`}; con `mode` **sin declarar** rige la **compatibilidad v1** (`server` presente → servidor; si
  no, standalone) y **no** se pasa a `service` por defecto: cambiar a un servidor compartido es decisión del
  consumidor (D-9, ADR-031). Una config inválida (tipo, signo, `mode` fuera del conjunto, `poll_max <
  poll_initial`, `service.require` no booleano) → `blocked` **antes** de invocar nada.
- **CDAD no gestiona el servicio de fondo ni servidores.** La **única** invocación de `service` es `service
  status` (solo lectura, **exactamente una vez**, y sólo en modo servicio); ninguna argv lleva `serve`,
  `service start|stop|restart|get|set|unset` ni `reload` (INV-2). El servicio lo prepara y lo mantiene el
  **dueño/operador**; CDAD tampoco escribe el store (sólo `mode=ro`).
- **La recuperación nunca reconstruye el problema.** El **único** cambio de modo admisible es el **fallback
  declarado y contable** `service` → `standalone` cuando `service status` informa que **no corre**
  (`fallback=service-unavailable`); con el servicio **corriendo**, todo fallo (versión, credencial, respuesta
  inesperada) termina `blocked` y **nunca** standalone (INV-10). Tras un `timeout` en servicio o servidor
  ningún camino re-despacha solo ni abre un `standalone` «para destrabar».
- **La versión del servicio se lee como proyección de una sola clave.** El gate de compatibilidad proyecta
  **solo** `version` del registro del servicio, **sin red, sin contraseña y sin URL**, y **falla cerrado**
  (`blocked` con las dos versiones o «no verificable»); el registro y su esquema **no** son contrato público
  (DT-6). La salida de `service status` se descarta salvo el discriminante: ninguna salida lleva la URL del
  servicio.
- **Lo no observado es `unknown`, también en la recuperación.** El chequeo del intento previo es
  **innegociable**: un store **existente** cuya fila no se puede afirmar (ocupado o ilegible) **bloquea antes
  de cualquier invocación**, espejo del fail-closed de `service status`; un store **inexistente** es un hecho
  determinante distinto y **no** bloquea (§2.7).
- **Referencia operativa:** `skills/cdad-cycle/references/cli-delegation.md` y
  `skills/cdad-cycle/assets/opencode-exec-config.example.json`; **ADR-031**; contrato normativo en
  `docs/specs/006-001-opencode-concurrency-reliability/spec.md` (PD-1..PD-14, INV-1..INV-10). Aviso de cota:
  los fixtures de tiempos usan cotas de **2 s** y son frágiles bajo carga del host (**DT-9**).

### Delegación por capa — el mecanismo lo declara el agente del runtime, la skill es neutral y el adaptador sólo cruza runtimes (epic 006, 2026-10-18)

- **El mecanismo de despacho pertenece a la capa del runtime, no a la skill.** Cada orquestador generado
  declara su mecanismo **nativo** (`task` + `subagent_type: cdad-<rol>` en OpenCode; `Agent` +
  `subagent_type` en Claude Code), el mapeo rol→subagente con sufijo de stack, la **prohibición
  intra-runtime** del adaptador CLI y la declaración de familia (abajo). La regla vive en
  `sources/agents/adapters/{opencode,claude-code}.md` como bloque `<!-- cdad-section:delegation -->` y el
  generador la compone (`REQUIRED_ADAPTER_SECTIONS` en `scripts/cdad-generate.py`); **nadie edita
  `agents/**` a mano** (fuente única de agentes, epic 004).
- **La skill queda neutral: metodología, no herramientas.** `skills/cdad-cycle/SKILL.md` §4 conserva los
  **siete puntos** en abstracto (principio, orden, regla de adaptadores, invariantes de rol, spawn guard,
  recibo, paquete/reentrada independientes del transporte) **sin nombrar runtime ni modelo concreto**;
  `handoff-prompts.md` y `sub-agent-strategies.md` son plantillas. La ausencia se verifica con un oráculo de
  **formas de herramienta** (código en línea `` `task` ``, `` `delegate` ``, `` `Agent` ``; el token
  `subagent_type`; `opencode run`; `sessions_spawn`; `Agent tool`) y de **modelos concretos** — **nunca** con
  la palabra suelta *task* (prosa como «atomic task» no matchea). `references/context-meter.md` es
  **exclusión declarada**: nombra `task`/`subagent` como **datos de medición**, no como instrucción.
- **El adaptador sirve para otro runtime o para uno sin delegación propia.** Sirve para orquestar agentes de
  **otro** runtime o de uno **sin** delegación nativa; en cualquier otro caso se delega con el mecanismo
  nativo. La regla de elección **por transporte** salió de `references/cli-delegation.md`, que queda como
  **contrato del adaptador**; las dos referencias por runtime (`opencode-delegation.md`,
  `claude-code-delegation.md`) **salieron del árbol instalable** y su detalle histórico/verificación vive
  **no instalable** en `docs/evidence/runtime-delegation/` (byte-idéntico salvo el encabezado que declara
  «no instalable; la regla vigente no está aquí»). Nada instalable apunta a esa copia.
- **El modelo lo fija la configuración, nunca el orquestador ni el script.** `SKILL.md` §2 pierde la columna
  de familia de modelo y el párrafo de perfiles; el orquestador **pasa un modelo sólo si viene de la
  configuración del entorno** y **nunca lo elige ni lo inventa**. Con un perfil que **no** fija modelos
  (`basic`) la familia distinta del reviewer **no** está garantizada por construcción: se **declara** y se
  **registra el intento** (`runtime`, `model_configured`, `model_reported`, `session`; `null`/`unknown` lo no
  observado, y el gate de review escribe «invariante no garantizado» en vez de omitirlo). El script de
  comparación de familias, la config de delegación y la sustitución de ADR-007 son de **006-003**.
- **El paquete y el recibo son independientes del transporte.** El **mismo** `receive` cierra cualquier ruta:
  el despacho nativo devuelve **TEXTO FINAL** en la sesión del orquestador, que escenifica los **bytes
  exactos** bajo `.cdad/inbox` + `RESULT.json` y corre `receive` → `validate-receipt` → `materialize` →
  transición; el recibo queda **`semantic_status: pending`** (recibir no aprueba nada). La equivalencia está
  declarada en `references/re-entry.md` (protocolo de materialización) y **enlazada** desde §4 y desde cada
  sección `delegation`.
- **Disciplina de contexto del orquestador: cuatro reglas.** (1) orientarse con la vista compacta `status`
  **primero**, sin volcados de state/ledger/skill; (2) **rotar la sesión** en los bordes de tarea, no a mitad
  de unidad; (3) **no reparar por su cuenta** — re-despachar el rol nombrando el defecto; (4) lo que debe
  durar, dejar evidencia o leer otro proceso o rol va a **rutas estables del workspace** (`.cad/inbox` para el
  recibo). El **Ningún texto instalable nombra `/tmp`**: el dueño lo sacó de la metodología (enmienda 002 — el
  límite era de su servidor, no de la metodología) y el oráculo exige la regla de rutas estables **y** la
  ausencia del literal en `skills/**` y en los agentes generados. `references/orientation.md` §1 sigue siendo
  el **dueño** de «vista primero»: la fuente lo **cita** y no lo duplica.
- **Límite honesto:** el oráculo prueba que la regla **existe**, no que se **obedezca**. La única evidencia de
  comportamiento es el transcript de la corrida de aceptación —una sesión hija `cdad-reviewer` despachada por
  `task`, 56 comandos sin adaptador— y es una **muestra**; en esa misma corrida el orquestador leyó el código
  del CLI para resolver el arranque (contra el espíritu de la regla 1) y tomó notas de orquestación como
  mandato.
- **Referencia operativa:** `sources/agents/adapters/*.md`, `sources/roles/orchestrator.md`,
  `skills/cdad-cycle/SKILL.md` y `skills/cdad-cycle/references/re-entry.md`, `docs/evidence/runtime-delegation/`;
  **ADR-032**; contrato normativo en `docs/specs/006-002-delegation-by-layer/spec.md` (PD-1..PD-11,
  INV-1..INV-8, D-1..D-7, enmiendas 001/002).

### Modelos por configuración, archivos del usuario fuera del ownership y retiro de obsoletos propios (epic 006, 2026-10-18)

- **Los modelos se resuelven por configuración, y CDAD no los elige ni los verifica.** Este bloque **completa** el
  principio que ADR-032 dejó declarado («el modelo lo fija la configuración, nunca el orquestador ni el script»,
  cuyo script de familias y config de delegación eran «de 006-003»): el instalador y el generador **no tienen
  perfiles ni mapa de modelos** (`scripts/cdad-models.sh` retirado, `Makefile` sin `PROFILE`, `cdad-generate.py` sin
  `--profile`, staging sin la clave `profile`, **ningún agente con `^model:`**); los flags de perfil se **rechazan**
  nombrando el lugar donde se elige el modelo, y `--basic`/`CDAD_MODEL_PROFILE` sobreviven un ciclo como **alias
  deprecado sin efecto** (aviso de una línea, INV-7: nada silencioso). En la **delegación interna** el modelo lo fija
  la configuración del runtime; en la **externa**, `delegation.json` v1 —por **destino y rol**— es la **única**
  fuente, **sin fallback**: un rol sin entrada produce el destino **sin `--model`** y `model_configured: null`, y una
  clave `model` heredada en la exec-config se **ignora con aviso**. **El invariante de familia del reviewer no se
  exige ni se verifica** (decisión del dueño, A-5): la observación I8 (`model_configured`/`model_reported`) **solo
  registra** lo ocurrido; los demás invariantes anti-sesgo no cambian.
- **Los archivos de configuración del usuario no son propiedad del instalador.** `delegation.json` y
  `opencode-server.env.example` se crean **solo si no existen** (segunda instalación: bytes idénticos + aviso) y
  **no se registran en el manifiesto**: ni `--uninstall` ni el retiro de obsoletos pueden borrarlos (A-3). Regla
  general: el ownership del instalador cubre **lo que él desplegó**, no la configuración con la que el usuario
  completa el despliegue.
- **El instalador retira sus propios obsoletos, y la regla de retiro es una sola.** Un artefacto registrado,
  **no redesplegado** y con **sha256 igual al registrado** se **retira** del disco y del manifiesto; uno
  **modificado localmente** se **preserva**, se reporta como CONFLICT y **sigue registrado**; uno **no registrado
  nunca se lee**. La misma función decide en la instalación y en `--uninstall` (sin duplicar la regla) y
  `--dry-run` lista las bajas sin escribir. **Un registro con el digest vacío o `null` nunca es removible**
  (veredicto `unverifiable`): solo se retira lo propio **con sha256 sin cambios** (INV-2).
- **Los registros estructurados no se transportan como TSV leído por bash.** Lección medida (B-1 de la re-review de
  006-003): `IFS=$'\t' read` **colapsa las columnas vacías**, así que un registro con un campo vacío se
  reinterpreta como otro registro (y puede **retirar sin comparar el digest**). Los registros del manifiesto viajan
  **NUL-framed** con `read -r -d ''`; los streams que quedan en TSV los parsea **Python** (`split("\t", 2)`), que
  preserva campos vacíos. Un campo vacío que cambia el veredicto de un borrado es un defecto estructural, no un caso
  degenerado.
- **Referencia operativa:** `install.sh` (prune y arranque), `skills/cdad-cycle/scripts/cdad_delegate.py`
  (`delegation_model`, regla única de la base de config) y `cdad_delegate_opencode.py` (credencial),
  `skills/cdad-cycle/references/cli-delegation.md` § Configuration, `skills/cdad-cycle/assets/*`;
  **ADR-033**; contrato normativo en
  `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (PD-1..PD-8, INV-1..INV-7, D1..D8,
  A-1..A-4, A-5).

### Medición de contexto — registro neutral opcional, medidor read-only que nunca aprueba (epic 005, 2026-10-11)

- **El formato de medición es neutral respecto del runtime y opcional para la metodología.** El
  **registro neutral** (contrato `context-meter-v1`) vive en
  `skills/cdad-cycle/assets/context-meter.schema.json` y su procedimiento/semántica en
  `skills/cdad-cycle/references/context-meter.md`. **No está enganchado en ningún gate**
  (`prepare`, `validate-state`, `validate-request`, review, merge): el ciclo **sigue** aunque el
  entorno no exponga tokens. El **esquema neutral es el contrato**; el adaptador **solo traduce** y
  es el **único** que conoce los nombres de tablas/columnas del runtime (el registro neutral **no**
  los contiene).
- **El adaptador es canónico con wrapper fino, y lee en solo lectura.** El canónico es
  `skills/cdad-cycle/scripts/cdad_context_meter.py`; `scripts/cdad_context_meter.py` es un **wrapper
  fino** (`runpy.run_path`), convención del repo. El store se abre con **URI de solo lectura**
  (`?mode=ro`), **nunca** se escribe ni se checkpoint-ea, las consultas se **acotan** (sesión/
  ventana) y la salida es **JSON único, stdlib y determinista** (byte-idéntica).
- **Fallo cerrado con diagnóstico que nombra el faltante y sin números.** El esquema de la fuente se
  valida por **columnas/tabla requeridas** (la fuente **no** tiene marcador de versión); si falta
  algo, el medidor **falla cerrado** (`rc != 0`) con un diagnóstico que **nombra el elemento
  faltante** y **ningún número** de métrica. Nunca fabrica métricas (sin conversión bytes→tokens, sin
  límite de contexto inventado).
- **Regla de cubos: observado / estimado / desconocido; desconocido nunca es cero.** Cada métrica
  vive en **exactamente uno** de los tres cubos: `observed` = leído directamente del registro;
  `estimated` = **proxy declarado** (contexto cargado por paso = `input + cache.read + cache.write`,
  **no** la ventana real); `unknown` = nulo/ausente/no reportado **con causa**, **nunca** `0`. El
  input reportado **no** se equipara con consumo facturado ni con capacidad máxima.
- **Límite normativo de 16384 bytes por documento de sesión** (salida compacta con referencias a la
  evidencia original), declarado en `references/context-meter.md`.
- **El medidor NUNCA aprueba nada.** La anotación `application` es **referenciada** (una referencia
  durable —ruta/commit/recibo—, **no** una copia del contenido) y su `limit ∈ {accepted, blocked,
  pending, unknown}` deriva de **hechos observables**, no del juicio del lector; un despacho
  registrado **no** prueba utilidad ni resultado aceptado. El medidor no cierra gates.
- **Referencia operativa:** `references/context-meter.md`; contrato normativo en
  `docs/specs/005-002-session-context-meter/spec.md` (PD-1..PD-16, INV-1..INV-10).

### Orientación acotada — proyección read-only del estado, encargo autosuficiente (epic 005, 2026-10-12)

- **La orientación es una proyección, no una migración.** El subcomando **read-only** `status` de
  `cdad_packet.py` (`compact-view-v1`) emite **un único documento JSON** desde las fuentes **ya
  existentes** (`docs/.cdad-state.json` solo en sus campos operativos, `execution.json`, `REQUEST.json`
  + `active_packet`, `cdad-policy.json`, el `cdad-version-check.py` y la proyección de continuidad).
  **No** se reescribe el formato del estado, **no** se separa el historial, **no** hay segunda memoria
  (INV-2/INV-7). El `stage_history` (**304.075 B = 94,8 %** del estado) **NO se emite**: se consulta
  selectivamente ante una duda concreta.
- **Acotada y determinista, con fallo cerrado.** La vista respeta un **límite normativo de 16.384 B**
  (el mismo número ya normativo para el documento de una sesión); al superarlo **falla cerrado**
  (`rc≠0`) **sin emitir proyección parcial**, con diagnóstico que nombra el límite y la bandera
  `--max-bytes N`. El límite **no crece con el historial** y es el mismo para cualquier tamaño de
  estado (la proyección es función de los campos operativos). Misma entrada → mismos bytes; deja el
  estado **byte-idéntico** (INV-1).
- **La selección de entrada es un mapa explícito, no una inferencia.** El campo `entry` emite
  `continuity-reconcile` | `next-unit` | `diagnosis` según condiciones observadas: **un paquete
  `prepared`/`dispatched` se atiende antes que cualquier inferencia de etapa** (caso real: etapa en
  curso + paquete `prepared` ⇒ `continuity-reconcile`, nunca `next-unit`); reposo sin pendiente ⇒
  `next-unit`; configuración incompleta ⇒ `diagnosis`. **No** depende del literal «inicializar» ni
  agrega campo nuevo al estado.
- **Ausencia ≠ incoherencia en el verdicto de versión.** `UNKNOWN`/`NO-PROJECT-AGENTS` son *ausencia*;
  `DRIFT` es *incoherencia*; cualquier `rc≠0` se lee «no verificado coherente», nunca `ok`. El caso
  **«medidor no instalado»** se trata como **ausencia**, no como `DRIFT`; el despliegue es del dueño.
  Límite declarado: la coincidencia de archivos **no** demuestra lo cargado por una sesión abierta.
- **Evidencia mecánica sin enmascarar el `rc`.** El patrón (en `references/orientation.md`) captura el
  retorno **real** del CLI sin tubería que lo sustituya (`PIPESTATUS[0]`, no `$?`); salida acotada con
  evidencia completa por referencia; errores `ERROR: …` accionables. La **asimetría de raíz relativa**
  entre CLIs se **diagnostica en la salida de la vista** (nombra ambos CLIs y el camino de
  recuperación), no solo en prosa.
- **El encargo de tarea trae su contrato aplicable (`packet-contract-v1`, aditivo).** Con
  `--plan-task <ID>` (y el campo opcional `plan_task`), el paquete emite una sección declarada con los
  **comandos de validación de esa tarea iguales a los del bloque canónico `plan-tasks`** del plan
  aprobado (con `@validation_strategy` resuelto) y la regla de **cuándo ampliar**; una tarea ausente
  **falla cerrado nombrando el id**; emite por referencia las postcondiciones/invariantes/decisiones
  aplicables (ids que resuelven a encabezados) con la referencia del contrato (path + `sha256`).
  **Aditivo:** sin `plan_task` el paquete se emite **byte-idéntico**; el conjunto cerrado de campos se
  extiende con una propiedad declarada (una clave desconocida sigue rechazándose). La **provenance**
  de los valores se afirma contra lo parseado del bloque, no contra texto a mano.
- **Política de la suite: declarada una sola vez, consumidores que referencian.** La instrucción del
  paquete declara, en su parte **común** (`packets/common.md`), que la **suite completa no se corre
  salvo que el paquete lo pida** y que **la corre quien cierra**; los assets de rol/subetapa la
  **referencian** (no la copian) y se corrigieron los que afirmaban lo contrario. El **cierre del
  encargo incluye el commit** (el reporte del rol lo declara; no hay gate automático, la verificación
  es la auditoría del orquestador).
- **Resumen del conjunto aditivo + regla del documento multiplexado (`set-summary-v1` /
  `context-meter-r4-v1`).** Para corridas multi-sesión se emite **primero** un resumen en un
  **documento aditivo separado** (sesiones incluidas hasheadas, cobertura, hitos, magnitudes con cubo
  y cobertura, referencias al detalle); el **detalle por sesión NO se emite por defecto** (se pide con
  `--detail`). El registro neutral **por sesión** de 005-002 queda **byte-congelado** sin la bandera
  (INV-5). La regla R4 (total ≤ N × límite por sesión; límite normativo **por documento de sesión**)
  queda declarada **antes** del primer consumo multi-sesión.
- **D11 — la base real nunca se escribe (regla declarada + ausencia verificable).** La no-escritura se
  verifica sobre una **base temporal controlada**; la **concurrencia** se cubre con un **escritor
  activo** durante la lectura; en la **integración real** se comprueba **solo la lectura y los
  resultados** (sin exigir que la base quede inmóvil); **nunca** se intenta escribir en la base real.
- **Capacidades efectivas ligadas a versión/configuración.** `references/capabilities.md` declara cada
  capacidad como observada/documentada/no disponible/desconocida, con el **fallback portable**
  (archivos/enlaces) demostrado; **no** promete el contrato agente↔superficie de OpenChamber (no
  verificado). Sin dashboard/scheduler/fuente de estado nueva.
- **Referencia operativa:** `references/orientation.md`, `references/capabilities.md`,
  `references/project-start.md` §11, `references/context-meter.md` (R4);
  **ADR-025**; contrato normativo en `docs/specs/005-003-orientation-reduction/spec.md` (§2.1–§2.9,
  PD-1..PD-12, INV-1..INV-10).

### Política histórica (2026-09-13 — decisión de Capa 2 de cdad-010)

1. **Bloquear vectores directos y evidentes**, no bypasses hipotéticos: un
   agente con ganas de saltar las vallas siempre encontrará cómo.
2. **La expectativa se documenta** en skills y archivos de procedimiento:
   qué debe hacer el agente, qué no, y para qué.
3. **El agente debe SABER lo que se espera de él**: si no puede cumplir,
   devuelve la tarea explicando por qué; si cumple sin respetar el protocolo
   y sin motivo válido que pueda explicar, **la tarea se considera NO
   cumplida (fallida)** — aunque el artefacto exista.

**Definición operativa de "vector directo y evidente" (2026-09-13, N3 del
re-review de cdad-010):** un vector es directo y evidente si y solo si es
**demostrable con un probe de una sola invocación con output pegado** (Regla
de Oro). No califican: razonamientos sobre lo que el matcher "debería"
hacer, observaciones narradas sin paste, ni construcciones hipotéticas
multi-paso. Motivo: en el propio ciclo cdad-010, dos sesiones concluyeron
veredictos OPUESTOS sobre el mismo matcher ("compuestos pasan por prefijo"
vs "por segmento") — el que tenía probes pegados tenía razón. Cuando un
hallazgo de seguridad no pueda demostrarse con un probe de una invocación,
se registra como candidato de hardening con la premisa explícita a
verificar, nunca como bloqueante por intuición.

### Pares rtk `X*` + `rtk X*` (ADR-009)

Los modelos del workspace envuelven comandos en `rtk` (proxy CLI), así que
las allowlists por comando llevan SIEMPRE el par (`"pytest*"` y
`"rtk pytest*"`), con los subcomandos peligrosos de rtk denegados en todos
los roles. Matriz completa y razones: `docs/adr/ADR-009-politica-rtk-allowlists.md`.

## Convenciones de tests

- **Framework**: bash + grep asserts (`assert_file_has`/`assert_file_not_has`).
- **Estructura**: `tests/*.sh` para invariantes de cdad-003; checks por
  feature en `docs/specs/<id>/VALIDATION.md` (mapeo check↔postcondición).
- Los checks se definen ANTES de editar (RED) y corren desde la raíz del repo.

## Tooling enforcement

- Sin CI aún: gate local = suite bash + checks VALIDATION (deuda registrada).
- Proyectos Odoo gestionados con CDAD: `make lint` (pre-commit-vauxoo,
  pinneado, --no-overwrite, host) + `make test/test-one/test-clean`.

## Anti-patrones del proyecto

- Orquestador escribiendo código/tests inline sin conmutar de modo (AP-10,
  §4). Implementer tocando tests (AP-4). "Verde" sin output (AP-3). Aprobación
  delegada al LLM (indelegable: Memory Bank, specs, priorización de review).

---

Última actualización: 2026-10-12 (005-003)
