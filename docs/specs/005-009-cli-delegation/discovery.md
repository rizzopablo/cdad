# Discovery — 005-009-cli-delegation (etapa 1, mapeo técnico y brainstorming)

Rol: architect (subetapa discovery). Read-only. No se editó el repo.
Contrato: `docs/epics/epic-005-real-operation/plan.md` — sha256 verificado
`f3b66be0d7aafc4f2a7ef7bd4e14dc7c8ecbefb1fa8615df123d41ee6deaefef` (coincide con el packet).
Fecha: 2026-10-10.

> Nota de ubicación del repo: el árbol real vive en `<repo-root>/`
> (raíz del proyecto CDAD). Todas las rutas de este reporte son relativas a esa raíz.
> El packet declara las rutas relativas a esa misma raíz; `docs/epics/...` existe ahí.
> No hay cambio de producto: solo lectura.

Este reporte NO propone el contrato (eso es la subetapa draft). Mapea la superficie,
señala puntos de extensión, riesgos y VERIFY abiertos.

---

## 1. Resumen ejecutivo

- El mecanismo de despacho/recepción **ya existe en gran parte** y es reutilizable:
  `prepare` (paquetes canónicos), el registro I8 (`--record-dispatch`), el ledger
  `.cdad/executions/<id>/dispatches/`, los recibos (`cdad_result.py receive`) y la
  reconciliación (`cdad_continuity.py reconcile`/`resume`). El state del ciclo tiene un
  único escritor (el orquestador).
- **No existe un dispatcher/adaptador previo como script en el producto.** La evidencia
  muestra que el despacho real se hizo a mano con `opencode run --auto` (documentado en
  `docs/specs/004-002-.../dispatch-ledger.md` y en la evidencia de 2026-09-29). Esa
  ausencia es lo que 005-009 debe cubrir con un adaptador por destino.
- El **modo de carga del rol** en OpenCode es el punto más delicado: los roles se generan
  con `mode: subagent` y el orquestador con `mode: all`. Hay evidencia local de que
  `opencode run --agent <rol mode:subagent>` **cuelga en silencio** (entry debe ser
  `mode:all`/primary). El adaptador debe verificar el modo soportado y evitar el fallback
  silencioso a un agente genérico.
- El **proyecto y la versión** ya son verificables: manifiesto derivado
  `.opencode/agents/.cdad-derived.json` (`source_dir` + `source_version`) y
  `cdad-version-check.py` (COHERENT/DRIFT/NO-PROJECT-AGENTS/UNKNOWN). Falta la
  comprobación de la **configuración efectiva** de una sesión (agente/modelo/proyecto
  realmente cargados), que hoy solo se infiere del ledger de observaciones.
- La **prohibición de spawn** vive en `skills/cdad-cycle/SKILL.md:136-143` (SPAWN GUARD),
  `sources/roles/orchestrator.md:74-76` y `references/claude-code-delegation.md:63-69`;
  hay que reconciliarla (conservar donde el runtime no la soporte, distinguirla de la
  delegación externa autorizada).

---

## 2. Superficie existente reutilizable (entidades verificadas archivo:línea)

### 2.1 `prepare` — paquetes canónicos
- `skills/cdad-cycle/scripts/cdad_packet.py:3290` — `def prepare(args, project_root)`.
- Parser y superficie de opciones: `cdad_packet.py:3452-3510`:
  - `prepare` con `--project-root`, `--execution-context`, `--role`, `--substage`,
    `--objective`, `--input`, `--read-scope`, `--write-scope`, `--invariant`,
    `--expected-output`, `--evidence` (`:3470-3500`).
  - Comandos de render/validación: `render`, `validate-request`, `validate-packet`
    (`:3463-3469`).
  - Modos de paquete: `--new-execution` (`:3476`), `--resume-packet` (`:3478`),
    `--replace-packet` (`:3480`), `--propose-policy` (`:3484`), `--reconcile-policy`
    (`:3486`), `--record-dispatch` (`:3490`).
- El paquete canónico se publica en `.cdad/packets/<packet_id>/` con `REQUEST.json` +
  `PACKET.md` (verificado: `.cdad/packets/005-009-cli-delegation-architect-discovery-001/`).
- `REQUEST.json` (verificado) declara: `schema_version`, `packet_id`, `execution_id`,
  `feature_id`, `role`, `substage`, `objective`, `contract{kind,path,sha256,commit}`,
  `inputs[]`, `read_scope[]`, `write_scope[]`, `invariants[]`, `expected_output`,
  `evidence_required[]`.
- El packet que un rol recibe es el `PACKET.md` (render): primera línea
  `---cdad-packet-json` + bloque JSON canónico + cuerpo `# CDAD task`. Es exactamente
  el texto que un adaptador debe transportar al worker sin reescribir reglas
  (contrato mínimo, criterio 1: "no reescribe las reglas del paquete en una plantilla
  paralela").

### 2.2 Registro de despacho I8 (`--record-dispatch`)
- `cdad_packet.py:2209-2212` — `OBSERVATION_KEYS = {runtime, model_configured,
  model_reported, session, started_at, provenance}` (esquema cerrado).
- `cdad_packet.py:2213` — `OBSERVATION_TEXT_FIELDS`.
- `cdad_packet.py:2248-2284` — `_load_observation_document` valida el esquema cerrado;
  rechaza claves desconocidas (identidad forjada o resultados de recepción).
- `cdad_packet.py:2339` — `def _record_dispatch(args, project_root)`. Docstring
  (`:2340-2351`): toma `execution_id`, `packet_id`, `role`, `substage` **del paquete
  publicado** (nunca del documento de observación); guarda el intento en
  `.cdad/executions/<execution-id>/dispatches/<attempt-id>.json`.
- `cdad_packet.py:2379-2386` — forma del registro: `{execution_id, packet_id, role,
  substage, runtime, model_configured, model_reported, session, started_at, provenance}`.
- `cdad_packet.py:2388-2389` — ruta del intento.
- `cdad_packet.py:2400-2408` — transición `prepared → dispatched` (nunca a
  completed/failed; results/gates/postconditions no se tocan).
- `cdad_packet.py:2294-2334` — `_publish_dispatch_atomic`: el registro y el state se
  publican en UNA transacción.
- Ejemplo real verificado: `.cdad/executions/exec-004-002-project-execution-bootstrap-001/dispatches/review-009-a1.json`
  (contiene `runtime`, `model_configured`, `model_reported`, `session`, `started_at`,
  `provenance` con la fuente de cada campo).
- **Implicación para el adaptador:** I8 ya captura "identidad de intento/sesión" y
  "configuración efectiva observada, o desconocida explícitamente" (provenance mapea
  campo→fuente). El adaptador debe alimentar este registro; NO crear otro ledger.

### 2.3 Ledger de ejecución
- Directorio: `.cdad/executions/<execution-id>/dispatches/` (`cdad_packet.py:2215`
  `DISPATCHES_DIRNAME = "dispatches"`; `cdad_continuity.py:237` `_dispatch_dir`).
- Ejecuciones existentes (verificado): `.cdad/executions/exec-005-009-cli-delegation-001/`
  (con `execution.json`, `continuity/head.json`, `continuity/bodies/…`) y varias otras.
- El ledger humano por feature vive en `docs/specs/<id>/dispatch-ledger.md`
  (p.ej. `docs/specs/004-002-project-execution-bootstrap/dispatch-ledger.md`), con filas
  que registran runtime/modelo/sesión/resultado por paquete. **Evidencia del despacho
  real previo** (ver §3).

### 2.4 Recibos — `cdad_result.py receive`
- `cdad_result.py:493` — `def receive(args, project_root)`.
- `cdad_result.py:526-530` — exige que el paquete activo esté `dispatched` (la recepción
  requiere la observación I8, o un recibo durable previo).
- `cdad_result.py:549-577` — forma del recibo: `{schema_version, execution_id,
  packet_id, feature_id, role, substage, source, parts[], bundle_sha256,
  packet_validation:"passed", identity_validation:"passed", scope_validation,
  run_evidence_status:"not-provided", semantic_status:"pending",
  state_transition_requested:"received", received_at}`.
- `cdad_result.py:396-431` — verificación del recibo durable (`_verify_durable`,
  `_load_durable_receipt`); idempotencia (`:501-507`, `:580-588`).
- `cdad_result.py:594` — `validate_receipt` re-verifica un recibo durable.
- **Implicación:** la "entrega final durable" ya tiene destino canónico
  (`.cdad/results/<execution-id>/<packet-id>/{parts,bundle.json,receipt.json}`) y el
  recibo declara `semantic_status:"pending"` — es decir, **el recibo NO aprueba el gate**;
  el re-entry lo hace el responsable del ciclo. Esto ya implementa "rc=0 no aprueba un
  gate".

### 2.5 Reconciliación y resume — `cdad_continuity.py`
- `cdad_continuity.py:915` — `_has_dispatch` (lee `.cdad/executions/<id>/dispatches/*.json`).
- `cdad_continuity.py:929` — `_receipt_signal` → `absent|unreadable|readable`; un recibo
  ilegible NO es señal fiable (`:931-955`).
- `cdad_continuity.py:965` — `_classify(authority_state, receipt_state, dispatch, closed)`
  → `expired-authority|unknown|already-closed|received|dispatched-unknown|not-started`.
- `cdad_continuity.py:994` — `_run_reconcile` (read-only, determinista); envelope con
  `classification`, `signals`, `unknowns`, `reasons`.
- `cdad_continuity.py:1229` — `_run_resume` (proyección de contexto para una sesión nueva).
- Parser: `cdad_continuity.py:1297-1334` (`reconcile`, `resume`, `trigger`).
- `references/continuity.md:15-46` — tabla applies/does-not-apply y flujo mínimo del
  orquestador (begin → reconcile → resume → trigger).
- **Implicación:** "tras una interrupción se reconcilian los efectos antes de repetir" ya
  está implementado (`reconcile` no repite efecto; `_classify` distingue
  `dispatched-unknown` de fallo).

### 2.6 Patrón de ejecución externa acotada — `cdad_result.py run-python-unittest`
- `cdad_result.py:1316` — `def run_python_unittest(args, project_root)`: lee un
  `RUN.json` (run_request), ejecuta `run_request["argv"]` con `subprocess.run`
  (`:1323`), toma snapshots before/after (`:1320`, `:1332`) y emite evidencia
  (`:1333-1353`).
- `cdad_result.py:1367` — `validate_run_evidence` recalcula snapshots y clasifica
  (`valid-current|stale|unknown|invalid`).
- `cdad_result.py:95` — `RUN_REQUEST_KEYS`; `:1141` — `_load_run_binding`.
- Parser: `cdad_result.py:1476-1492`.
- **Implicación:** este es un **precedente de "ejecutar un argv externo con evidencia
  durable y reconciliación"**, pero está **especializado a `python3 -m unittest`**
  (el parser extrae conteos unittest: `_parse_unittest_counts`, `:1306`). No es un
  runner genérico de delegación; sirve como patrón/estructura, no como adaptador listo.
  VERIFY-5.

### 2.7 State del ciclo (único escritor)
- `docs/.cdad-state.json` (verificado): `active_epic`, `epic_stage`, `active_feature:
  "005-009-cli-delegation"`, `current_stage:"discovery"`, `epic_features[]`,
  `epic_history[]`, `stage_history[]`.
- El orquestador es el escritor único: `references/continuity.md:9-11` ("every write to
  `docs/.cdad-state.json` stay with the orchestrator (single writer)") y
  `references/opencode-delegation.md:123-127`.
- `agents/cdad-orchestrator.md:146` (fila de roles) — el orquestador escribe
  `docs/**` + state; los roles no.
- **Implicación:** el worker NUNCA escribe el state (criterio (g): "una delegación no
  amplía autoridad ni permite al worker escribir el state").

---

## 3. Dispatcher/adaptador previo: ausencia registrada (con evidencia de búsqueda)

Búsqueda acotada (no global):
- `ls scripts/` → `cdad-activate.py`, `cdad-bash-allowlist.sh`, `cdad_continuity.py`,
  `cdad-generate.py`, `cdad_guard.py`, `cdad-models.sh`, `cdad_packet.py`,
  `cdad_result.py`, `claude-code-path-guard.sh`, `validate-subagents.sh`. Los cuatro
  `cdad_*.py` de `scripts/` son **wrappers** de 330 bytes que hacen `runpy` del script
  canónico en `skills/cdad-cycle/scripts/` (verificado leyendo `scripts/cdad_packet.py`,
  `scripts/cdad_result.py`, `scripts/cdad_continuity.py`, `scripts/cdad_guard.py`).
  **Ninguno es un dispatcher de delegación.**
- `rg -il "dispatcher" scripts/ skills/ sources/` → **sin coincidencias** en el producto.
- `rg -l "opencode run|opencode --|--auto|--print"` → coincidencias solo en docs/
  (evidencia/ledger), no en scripts de producto.
- `find . -iname "*dispatch*"` → solo directorios de ledger (`dispatches/`) y documentos
  `dispatch-ledger.md`; **ningún script**.
- `rg -il "dispatcher|script previo" findings/` → solo
  `findings/external-orchestration-readiness-2026-10-10.md`, que explícitamente declara
  que **no comprobó** el script previo (ver §11, hecho 7).

Conclusión: **el dispatcher previo NO está disponible como artefacto en este repo.**
El despacho real se ejecutó manualmente con `opencode run --auto`, con evidencia en:
- `docs/specs/004-002-project-execution-bootstrap/dispatch-ledger.md:14-15,84-101`
  (filas "OpenCode 2.0.16 (`opencode run --auto`)", con sesiones `ses_…`).
- `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:29,32,39`.

Esto es consistente con la T1 propuesta (inventario y contrato: "Si no está disponible,
registrar esa ausencia"). **No es una búsqueda interminable**: la ausencia queda
documentada con referencias locales concretas.

---

## 4. Cómo se carga un rol CDAD en OpenCode: modos, documentado vs probado, fallback

### 4.1 Dónde se declara
- Fuente canónica del adaptador OpenCode: `sources/agents/adapters/opencode.md`.
  - `:11` — layout: `~/.config/opencode/agents/cdad-<role>[-odoo].md`.
  - `:14` — `mode: subagent` para los roles; **orquestador: `mode: all` +
    `permission: allow`**.
  - `:15-18` — `model:` emitido desde `scripts/cdad-models.sh`; el instalador lo
    reescribe según el perfil.
  - `:19-23` — `steps: 300` (techo de bucle, no presupuesto); el orquestador no lo lleva.
- Agentes generados (verificado):
  - `agents/cdad-architect.md:3` → `mode: subagent`.
  - `agents/cdad-orchestrator.md:3` → `mode: all`.
- Generador: `scripts/cdad-generate.py` (fuente determinista; `sources/agents/adapters/opencode.md:3`).
- Publicación por proyecto: `prepare` publica `.opencode/agents/` + manifiesto
  (`.opencode/agents/.cdad-derived.json`) — `references/runtime-adoption.md:41-53`.

### 4.2 Modos: agente principal vs `mode: subagent` (documentado vs probado)
- Documentado: los roles son `mode: subagent`; solo el orquestador es `mode: all`
  (`sources/agents/adapters/opencode.md:14`).
- **Probado (evidencia local):**
  - `docs/specs/opencode-read-map-and-steps-2026-09-29/spec.yaml:53` —
    "`opencode run --agent <mode: subagent role>` hangs silently: entry must be a
    mode:all/primary agent (orchestrator) that delegates".
  - `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:32` — dos
    binarios coexisten; `--agent <mode: subagent role>` **cuelga en silencio**.
  - `docs/specs/004-002-project-execution-bootstrap/dispatch-ledger.md:97` — un review se
    cortó por transporte en una cadena de `opencode run` anidadas; "una entrada simple no
    cubre el subárbol en OpenCode".
- Documentado (task vs delegate, plugin classification): `references/opencode-delegation.md:51-95`.
  - `:69-70` — con el lever `write: ask` (cdad-010), los 10 sub-agentes son *task-ables*;
    todo el ruteo CDAD en OpenCode va por `task`.
  - `:72-78` — `delegate` es canal muerto en este deploy (no pasa modelo; timeout 0 mensajes).
- Documentado (recarga): `references/opencode-delegation.md:149-167` — un proceso NUEVO
  re-lee los agentes; un agente de proyecto en `.opencode/agents/` **reemplaza** al global
  del mismo nombre. Verificado en aislamiento (`opencode debug agent`) para proceso nuevo;
  **NO verificado** `opencode reload` sobre un server ya iniciado (1.18.32 no expone
  `reload`; server headless 401).

### 4.3 Riesgo de fallback silencioso a un agente genérico
- Evidencia de que existen agentes **no-Cdad** en el mismo namespace de OpenCode:
  el directorio global instalado contiene 20 agentes `.md`: los 11 CDAD (5 roles ×
  base/odoo + orquestador) **más** `bootstrapper`, `coder`, `general`, `ofap`, `ofap-plan`,
  `probe`, `researcher`, `reviewer`, `scribe` (observación local de este VPS).
- Riesgo: si el adaptador no verifica el modo de carga y el agente efectivamente
  seleccionado, una entrada `mode: subagent` puede colgar en silencio o degradar a un
  agente genérico (p.ej. `general`/`coder`), que no aplica el contrato CDAD del rol.
- El contrato mínimo lo prohíbe explícitamente (`priority-perl-cli-plan-2026-10-10.md:147`):
  "no asumir que `mode: subagent` sirve como agente principal de un CLI, ni permitir
  fallback silencioso a un agente genérico".
- Perfil de modelos observado en el global: `~/.config/opencode/agents/.cdad-models-profile`
  = `basic` (sin modelo fijo; los agentes heredan el default del runtime). Relevante para
  "selección de modelo": en `basic` no hay modelo por rol garantizado (ADR-007).

---

## 5. Selección de proyecto y versión; comprobación de la configuración EFECTIVA

### 5.1 Proyecto explícito e independiente del directorio del coordinador
- El proyecto se fija con `--project-root` en los CLIs (`cdad_packet.py`, `cdad_result.py`,
  `cdad_continuity.py`; p.ej. `cdad_result.py:1462,1469,1473,1479`).
- El contrato mínimo lo exige (`priority-perl-cli-plan-2026-10-10.md:144-145`):
  "El proyecto es explícito e independiente del directorio del coordinador".
- VERIFY: hoy no hay un artefacto único que fije "el proyecto" para un adaptador; cada
  comando recibe `--project-root`. El adaptador debe resolverlo y no depender del cwd.

### 5.2 Agentes derivados y manifiesto `.cdad-derived.json`
- Manifiesto verificado: `.opencode/agents/.cdad-derived.json`:
  - `:48` — `policy_sha256` (= `f508ab1e…`, coincide con la política del packet).
  - `:50` — `source_dir`: `…/.config/opencode/agents` (origen de los derivados).
  - `:51` — `source_version`: `35062b0cf1842c5fc4a09bd68c18084f78e7c8f5`.
  - `:2-46` — `agents{<name>:{derived_sha256, source_sha256}}`.
- Origen resuelto por `prepare` (005-005 PD-12): `references/runtime-adoption.md:41-53`
  — (1) `CDAD_OPENCODE_AGENTS_DIR`; (2) `.cdad/activation.json` →
  `<adopted_root>/.config/opencode/agents`; (3) global `$HOME/.config/opencode/agents`.
  Si el origen difiere del registro o del `source_dir` previo, `prepare` emite diagnóstico
  en stderr (nunca cambia de versión en silencio, INV-7).
- Derivados: `cdad_packet.py:86-92` (`DERIVED_MANIFEST_NAME = ".cdad-derived.json"`,
  `DERIVED_STAGE_DIRNAME = "derived"`); `:2448` `_derived_role`; `:2485`
  `_derived_source_dir`; `:2535-2544` `_previous_derived_source`; `:2621` `_derived_maps`;
  `:2806` `_build_derived_payloads`; `:2756` `_reject_hand_modified_derived` (un derivado
  editado a mano hace fallar `prepare`).

### 5.3 Comprobación de versión
- `skills/cdad-cycle/scripts/cdad-version-check.py`:
  - `:47` — `DERIVED_MANIFEST_REL = .opencode/agents/.cdad-derived.json`.
  - `:110-122` — `_project_version` lee `source_version` + `source_dir`.
  - `:24-29` — veredictos: `COHERENT`(0) / `DRIFT`(1) / `NO-PROJECT-AGENTS`(4) /
    `UNKNOWN`(3); cualquier no-cero = versión NO verificada coherente.
  - `:74-107` — resolución del installation root por `source_dir` y por el skill tree.
- VERIFY: en el checkout de desarrollo no hay `version.txt` (verificado: ausente en la
  raíz del repo) → el CLI reporta `UNKNOWN` en dev, no toma la versión de la instalación
  global. Es intencional (F2 del script).

### 5.4 Comprobación de la configuración EFECTIVA (no solo archivos presentes)
- Lo que YA existe: el registro I8 captura `runtime`, `model_configured`, `model_reported`,
  `session`, `started_at` con `provenance` (fuente de cada campo) —
  `cdad_packet.py:2209-2213,2379-2386`; ejemplo real
  `…/exec-004-002-…/dispatches/review-009-a1.json` (provenance: "orchestrator dispatch
  command (-m)" para `model_configured`; "opencode.db session_v2.model" para
  `model_reported`; "opencode.db session_v2.id" para `session`).
- Lo que NO existe como producto: un lector del runtime que confirme en vivo
  agente/modelo/proyecto realmente cargados en una sesión del worker. El precedente de
  lectura de sesiones de OpenCode es 005-002 (pausada) y el `opencode-session-scan.py`
  de la evidencia de 2026-09-29 (prototipo, no producto) —
  `docs/epics/epic-003-context-efficiency/friction-intake-004-001.md:10-14`.
- El finding lo pide explícitamente:
  `findings/external-orchestration-readiness-2026-10-10.md:137-139,205-206` —
  "comprobar configuración efectiva, advertencias y operaciones reales", "Evidencia de
  los agentes/configuración cargados, no solo de archivos presentes".
- VERIFY-2 (abierto): ¿cómo comprueba el adaptador el agente/modelo/proyecto efectivos
  sin depender de un lector de sesión que no es producto? Opciones a evaluar en draft:
  (a) alimentar `model_reported`/`session` desde el runtime si expone un identificador;
  (b) declarar `unknown` honestamente cuando no haya fuente fiable.

---

## 6. Capacidades que debe declarar un adaptador (requeridas vs opcionales)

Fuente del contrato: `findings/external-orchestration-readiness-2026-10-10.md:100-107` y
`priority-perl-cli-plan-2026-10-10.md:139-163`.

Requeridas (contrato mínimo):
1. **Sesión nueva de rol** (aislamiento de contexto): el worker no ve la conversación del
   coordinador; recibe solo el paquete y sus insumos.
2. **Carga de política del proyecto**: `docs/cdad-policy.json` versionada; el rol opera con
   sus mapas de permisos (`cdad_packet.py:_derived_maps`).
3. **Selección de modelo**: configurable por ejecución/rol; registrar configurado y
   observado, o `unknown`. NO fijar un proveedor en CDAD (ADR-007 / `scripts/cdad-models.sh`).
4. **Salida final capturable**: el texto final del rol debe poder persistirse durablemente
   (`cdad_result.py receive` → `.cdad/results/.../receipt.json`).
5. **Identificación de sesión/intento**: alimenta I8 (`--record-dispatch`) y el recibo.
6. **Espera soportada**: sin callback probado, usar una espera fiable o comprobaciones
   espaciadas; nunca prometer notificación inexistente
   (`findings/external-orchestration-readiness-2026-10-10.md:213-217`).
7. **Recuperación/reconciliación**: tras interrupción, reconciliar antes de repetir
   (`cdad_continuity.py reconcile`).

Opcionales (no bloquean el primer recorrido):
- **Cancelación**: `findings:104` — sin callback puede usarse espera; cancelación real solo
  si está soportada y probada.
- **Callback / background / notificación automática**: solo si ya son fiables
  (`priority-perl-cli-plan-2026-10-10.md:154-156`).
- Distinguir **documentado vs probado**: una capacidad opcional ausente no bloquea otros
  recorridos legítimos (`findings:100-107`).

Separación de hechos (obligatoria):
- Éxito del proceso ≠ entrega del rol ≠ aprobación del gate.
  `findings:60-63,210-212`: "«completado» no equivale a «gate aprobado»".
- `rc=0` sin resultado final suficiente NO cierra la tarea.
- Timeout NO prueba ausencia de cambios.
- Un fallo de transporte NO prueba que el worker no escribió nada.

---

## 7. Prohibición heredada de spawn desde subagentes (texto exacto + reconciliación)

Dónde vive el texto exacto:
- `skills/cdad-cycle/SKILL.md:136-143` — **SPAWN GUARD (anti-loop)**:
  "If you are running as a SUBAGENT (runtime=subagent …) **`sessions_spawn` is FORBIDDEN
  — you cannot spawn sub-subagents.** It is a runtime design limitation (anti-recursion).
  NEVER try it … retrying 2000+ times in a loop … (incident Aug 05 2026 — cdad-architect
  FEAT-003 <project>, 2153 attempts, orchestrator cycle stalled 2h). If you need to
  delegate from a subagent → return control to the orchestrator with a handoff packet
  (rule 2) and let IT decide the spawn."
- `sources/roles/orchestrator.md:74-76` — "Anti-recursion: running as a subagent, spawning
  sub-subagents is prohibited by the runtime — never retry a rejected spawn in a loop;
  return control with a handoff packet and let the orchestrator decide the spawn."
- Generado: `agents/cdad-orchestrator.md:163` (misma regla) y `:156-161` (orden de
  delegación: sub-agente → new-chat handoff → inline).
- `references/claude-code-delegation.md:63-69` — "CDAD explicitly forbids a sub-agent from
  delegating to another sub-agent (SPAWN GUARD, SKILL.md §4, incident of Aug 5, 2026)" +
  depth limit de Claude Code.

Cómo reconciliarla (per `priority-perl-cli-plan-2026-10-10.md:179-182` y
`findings:80-84,306-308`):
- **Conservar** la prohibición donde el runtime no soporte el spawn (sub-subagentes
  nativos): sigue siendo válida (anti-recursion del runtime).
- **Distinguirla** de la delegación externa autorizada: el nuevo recorrido es
  coordinador→worker (una sesión de rol en OTRO CLI), no recursión de subagentes dentro
  del mismo runtime.
- Primer aterrizaje: coordinador→worker, devolución al coordinador, **sin delegación
  recursiva automática**. Si más adelante se permiten cadenas: registrar
  padre/responsable y acotar profundidad/coste/tiempo según mandato.
- Una delegación **no amplía autoridad** ni permite al worker escribir el state.

---

## 8. Primer adaptador OpenCode: recorrido concreto (Claude → OpenCode)

Entrada del recorrido común (`findings:36-44`):
`agente autorizado → encargo canónico → adaptador del CLI destino → sesión de rol →
resultado durable → re-entry del responsable`.

Recorrido concreto mapeado con el mecanismo existente:

1. **Encargo canónico (coordinador Claude).** `prepare` produce el paquete:
   `python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root <root> --role <role>
   --substage <substage> --objective "…" [--input …]` (`cdad_packet.py:3470-3500`).
   Salida: `PACKET.md` (render) + `REQUEST.json` en `.cdad/packets/<id>/`.
2. **Registrar el despacho (I8) antes/junto con el envío.** `prepare --record-dispatch
   <packet_id> --attempt-id <id> --input <observaciones.json>` (`cdad_packet.py:2349-2389`)
   con el documento de observación de claves cerradas
   (`OBSERVATION_KEYS`, `cdad_packet.py:2209`). Transición `prepared → dispatched`.
3. **Invoke del worker OpenCode.** El texto a transportar es el `PACKET.md` íntegro.
   El adaptador lanza la sesión de rol en el CLI destino. Evidencia local del mecanismo
   real usado: `opencode run --auto` (con `--standalone` para servidor privado)
   (`docs/specs/004-002-.../dispatch-ledger.md:14-15,84-101`;
   `docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:29`).
   Punto crítico: `--agent <rol mode:subagent>` **cuelga en silencio** → la entry debe ser
   un agente `mode:all`/primary (el orquestador) que delegue
   (`spec.yaml:53`; `results.md:32`). El adaptador debe verificar el modo soportado y NO
   caer a un agente genérico.
4. **Espera fiable.** No esperar al cliente `opencode run` (puede volver antes de que el
   rol termine); esperar sobre la base de sesiones / señales durables
   (`results.md:39`; `friction-intake-004-001.md:41-48`).
5. **Entrega durable.** El worker entrega su texto final; se persiste con
   `cdad_result.py receive --project-root <root> --execution-context <exec.json>
   --packet <PACKET.md> --request <REQUEST.json> --descriptor <result.json>`
   (`cdad_result.py:1460-1466`, `:493`). Requiere el paquete `dispatched` (`:526-530`).
   Emite recibo con `semantic_status:"pending"` (no aprueba gate).
6. **Re-entry del responsable.** El orquestador (escritor único del state) reconcilia y
   decide el gate: `cdad_continuity.py reconcile --project-root <root> --execution-context
   <exec.json> --packet <packet_id> --json` (`cdad_continuity.py:1312-1317`, `:994`) y,
   si corresponde, `resume` (`:1319-1324`, `:1229`).
7. **Interrupción/recuperación.** `reconcile` clasifica (`already-closed|received|
   dispatched-unknown|not-started|unknown|expired-authority`) sin repetir efecto
   (`cdad_continuity.py:965-991`).

Dirección inversa (OpenCode → otro CLI) y otros destinos: incrementos siguientes; el
diseño debe admitirlos, no implementarlos todos
(`priority-perl-cli-plan-2026-10-10.md:134-137,176-177`).

---

## 9. Puntos de extensión

- **Nuevo adaptador por destino** (el "un adaptador por destino"): NO existe hoy. El
  lugar natural es `skills/cdad-cycle/scripts/` (junto a los CLIs canónicos), con wrapper
  en `scripts/` si se quiere invocación desde el repo
  (patrón de wrappers: `scripts/cdad_packet.py` etc.). VERIFY-1.
- **Alimentar I8** con `runtime`, `model_configured`, `model_reported`, `session`,
  `started_at`, `provenance` (`cdad_packet.py:2209`). Sin campos nuevos si alcanza el
  esquema cerrado.
- **Persistir la entrega** por `cdad_result.py receive` (sin crear otro formato).
- **Reconciliar** por `cdad_continuity.py reconcile`/`resume`.
- **Configuración portable** (contrato mínimo, criterio 6): selección de modelo, binarios,
  logs, servidores y tiempos en el nivel correcto. Los valores concretos de este VPS NO
  deben ir a producto ni a contratos públicos
  (`priority-perl-cli-plan-2026-10-10.md:157-159`; `findings:221-235`).
- **Patrón de evidencia de ejecución externa**: reutilizar el diseño de
  `run-python-unittest` (`cdad_result.py:1316-1353`) para snapshots before/after y
  reconciliación, sin copiar su especialización a unittest.
- **Manifest/versión**: apoyarse en `.cdad-derived.json` + `cdad-version-check.py`.

---

## 10. Riesgos

- **R-1 (alto) Modo de carga silencioso.** `mode: subagent` como entry cuelga en silencio
  (`spec.yaml:53`; `results.md:32`). Un adaptador que no verifique el modo soportado puede
  quedar colgado sin resultado y sin error. Mitigación a especificar: verificar el modo,
  fallar cerrado, nunca caer a genérico.
- **R-2 (alto) Fallback silencioso a agente genérico.** Existen agentes no-Cdad en el
  namespace (`general`, `coder`, `reviewer`, `scribe`, …). Si el rol no se carga, el
  worker podría correr sin el contrato CDAD. Debe detectarse y reportarse.
- **R-3 (alto) Esperar al cliente, no a la sesión.** `opencode run` puede volver antes de
  que el rol termine (`results.md:39`; `friction-intake:41-48`). La "entrega" no debe
  declararse por el rc del cliente.
- **R-4 (medio) Configuración efectiva no comprobada.** Solo hay archivos/manifiesto; falta
  confirmar agente/modelo/proyecto realmente cargados (VERIFY-2). El perfil `basic` observado
  implica que el modelo por rol no está garantizado por el instalador (ADR-007).
- **R-5 (medio) Doble binario de OpenCode.** Coexisten binarios con bases de sesión
  distintas (1.18.32 legacy vs 2.x); uno cuelga en silencio con `--agent subagent`
  (`results.md:32`). El adaptador debe fijar/registrar el binario y su versión sin
  hardcodear rutas de este VPS.
- **R-6 (medio) Prohibición de spawn mal reconciliada.** Si se elimina sin más, se
  reintroduce recursión no soportada; si se mantiene como veto universal, contradice el
  recorrido legítimo (`findings:80-84`).
- **R-7 (medio) `/tmp` como canal.** Prohibido entre procesos (regla del proyecto,
  `findings:158-160`); usar rutas estables del workspace / workspace declarado.
- **R-8 (bajo) Deriva de versión.** Manifiesto derivado local puede quedar por detrás de la
  instalación global (DRIFT); la comprobación debe hacerse, no editar hashes a mano
  (`priority-perl-cli-plan-2026-10-10.md:19-22`).

---

## 11. Límites honestos (a preservar en el contrato)

- Un **proceso separado NO es un sandbox**: no impide nuevas lecturas ni acceso al
  repositorio (`findings:112-113`; `agents/cdad-orchestrator.md:211-213`).
- Cambiar de **CLI NO garantiza otra familia de modelo** ni aislamiento de información
  (`findings:31-34`).
- **`rc=0` no aprueba un gate**; el recibo queda `semantic_status:"pending"`
  (`cdad_result.py:574`).
- **Timeout no prueba ausencia de cambios**: antes de repetir, reconciliar
  (`findings:60-63`; `cdad_continuity.py:965-991`).
- Un fallo de transporte no prueba que el worker no escribió nada
  (`findings:62-63,298-299`).
- **Sin valores de este VPS** en producto o contratos públicos
  (`priority-perl-cli-plan-2026-10-10.md:157-159`).
- `grep`/`shell`/sesión separada no se presentan como sandbox
  (`priority-perl-cli-plan-2026-10-10.md:104-106`).

---

## 12. VERIFY abiertos

- **VERIFY-1 — Ubicación y forma del adaptador.** ¿Dónde vive el adaptador OpenCode
  (nuevo script en `skills/cdad-cycle/scripts/` + wrapper en `scripts/`, u otra ubicación)?
  ¿Es un CLI con subcomandos o un módulo? A decidir en draft con evidencia de
  `install.sh` (qué se instala y a dónde) — no verificado en esta subetapa.
- **VERIFY-2 — Configuración efectiva.** ¿Cómo comprueba el adaptador agente/modelo/
  proyecto efectivamente cargados sin un lector de sesión de producto? Opciones: leer un
  identificador del runtime si existe; declarar `unknown` honestamente. (005-002, pausada,
  sería el lector; su discovery NO se repite.)
- **VERIFY-3 — Modo de carga soportado.** Confirmar, contra la versión de OpenCode vigente
  en el momento del draft, cuál es el camino soportado para una entry no-interactiva
  (`mode:all` + delegación vs `--agent` de rol), y cómo el adaptador verifica el modo. La
  evidencia local es de 1.18.32/2.0.16 y 2026-09-29; puede haber cambiado.
- **VERIFY-4 — Espera soportada.** Confirmar el mecanismo de espera fiable (base de
  sesiones / señal durable) y su recuperación, sin callback inventado. La evidencia dice
  "esperar sobre la base de sesiones, no sobre el cliente" (`results.md:39`); falta
  especificar la superficie concreta.
- **VERIFY-5 — Reutilización de `run-python-unittest`.** ¿El adaptador reutiliza el patrón
  snapshots/evidencia o el runner acotado? El runner es específico de unittest; el patrón
  (argv + snapshots + reconcile) parece reutilizable, pero no es un runner genérico.
- **VERIFY-6 — `install.sh` y publicación.** Cómo se instala/publica un adaptador nuevo y
  si toca el manifiesto/derivados. No verificado en esta subetapa (fuera del objetivo del
  discovery).
- **VERIFY-7 — Segundo destino / dirección inversa.** Cuál sería el segundo CLI verificado
  y su coste/capacidades; explícitamente posterior (`priority-perl-cli-plan:196-197`).
- **VERIFY-8 — Aceptación conjunta (R2).** El recorrido real Claude → OpenCode → recepción
  CDAD debe aportar la aceptación R2 pendiente de 005-006 y la de interoperabilidad; el
  adaptador debe construirse sobre una versión estable (la sucesora de 005-008 para la
  aceptación conjunta).

---

## 13. Evidencia de la sesión (comandos y resultados)

- `sha256sum docs/epics/epic-005-real-operation/plan.md`
  → `f3b66be0d7aafc4f2a7ef7bd4e14dc7c8ecbefb1fa8615df123d41ee6deaefef` (coincide).
- `git rev-parse HEAD` → `3054b21ad294f49e795b1a4f4ed77ee406e2e8ff`.
- `git status --short` → ` M docs/.cdad-state.json`; `?? docs/specs/005-003-orientation-reduction/`
  (estado previo, no tocado por esta sesión).
- Lecturas: plan del epic, `priority-perl-cli-plan-2026-10-10.md`,
  `findings/external-orchestration-readiness-2026-10-10.md`, `handoff-005-009.md`.
- `rg`/`ls` acotados (ver §3) para el dispatcher previo: sin coincidencias en producto.
- Observaciones locales (NO van a producto): `command -v opencode` → no en PATH;
  `~/.opencode/bin/opencode` presente (210 MB) + `opencode2` (wrapper de 1 línea);
  `~/.config/opencode/agents/*.md` = 20; `.cdad-models-profile` = `basic`;
  sin `version.txt` en el checkout.

Archivos modificados por esta sesión: **ninguno en el repo**. Único archivo escrito:
`/tmp/opencode/discovery-005-009.md` (temporal declarado, fuera del repo).
