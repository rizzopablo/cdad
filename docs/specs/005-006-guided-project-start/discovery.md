# Discovery — 005-006-guided-project-start

Subetapa: **discovery** (etapa 1). Rol: architect. Read-only sobre el producto.
Contrato: `docs/epics/epic-005-real-operation/plan.md` (sha256 `4b403b0e…d6c71`, verificado con `sha256sum`).
Insumos: `plan.md` fila 3 (`:35`) y `docs/epics/epic-005-real-operation/evidence/005-006-attempt-1.md`.
Complemento leído: `findings/session-guided-start-friction-2026-10-10.md`.
Raíz del repo de desarrollo: `<repo>` (el directorio contenedor
`<repo-parent>` es otro repo que solo guarda un gitlink; ver
`.cdad/local/handoff-005-005.local.md:3`).

Este documento **mapea** la superficie real. No propone el contrato (eso es la subetapa `draft`).

---

## 0. Definición del resultado exigido (texto del contrato)

`plan.md:35` (fila 3): una instrucción breve («usá CDAD para inicializar este proyecto y comenzar
su análisis preliminar») debe bastar para llegar a una **primera delegación útil**. El orquestador
debe: (a) reconocer o inicializar el proyecto conservando lo existente (documentación, planes,
convenciones propias como nombres de épicas y features); (b) descubrir requisitos y restricciones
(stack, organización, privacidad, entorno de pruebas, límites operativos, autoridad) y registrarlos
en su lugar canónico creando solo lo que falte; (c) distinguir lo inferible de lo que decide el
usuario y preguntar solo esto último; (d) preparar encargos completos. El contrato obliga en las dos
direcciones (insumos, capacidades y salida legítima ante bloqueo). **Límite explícito** (`plan.md:35`,
cierre): *no traslada el prompt largo a una plantilla*.

---

## 1. Recorrido de arranque de punta a punta (reposo → primera delegación)

### 1.1 Qué lee hoy un orquestador, en orden, desde reposo

Entidad de entrada: **agente `cdad-orchestrator`**. Su cuerpo desplegado está en
`agents/cdad-orchestrator.md` (fuente canónica `sources/roles/orchestrator.md`; derivado de proyecto
`.opencode/agents/cdad-orchestrator.md`).

1. **Intake del agente** — `sources/roles/orchestrator.md:19-43` (idéntico en
   `agents/cdad-orchestrator.md:11-37`):
   - Camino preparado: si existe `.cdad/execution.json` para la feature activa, se usa el renderer
     `scripts/cdad_packet.py prepare` / `render` (`:19-36`).
   - **Camino legacy, SECOND** (`:37-40`): *«Without a prepared execution/request, load the
     `cdad-cycle` skill with the skill tool»*.
   - `legacy-loads: cdad-cycle only` (`:46-48`).
2. **Skill de ciclo** — `skills/cdad-cycle/SKILL.md` (588 líneas). Regla absoluta
   (`:11-35`); modos de invocación A/B (`:210-238`); flujo del orquestador, pasos 1-6
   (`:240-281`); tabla "cómo leer las referencias" (`:439-461`); gates (`:322-372`);
   Memory Bank (`:376-395`); formato del state (`:397-435`); coordinación con `cdad-epic` (`:500-512`).
3. **Detección de estado** — `skills/cdad-cycle/references/state-detection.md` (115 líneas):
   algoritmo de 5 pasos (`:5-88`), inferencia sin state (`:44-60`), detección de Memory Bank (`:98-107`).
4. **Ejecución por proyecto v2** — `skills/cdad-cycle/references/project-execution.md` (236 líneas):
   política (`:7-49`), autoridad I2 (`:51-83`), primera preparación/bootstrap (`:84-97`), resume
   (`:99-108`), registro de despacho (`:109-119`), reconciliación de política (`:121-139`),
   mecanismos por runtime (`:141-163`), reemplazo (`:164-236`).
5. **Continuidad** — `skills/cdad-cycle/references/continuity.md` (143 líneas): tabla
   applies/does-not-apply (`:12-20`), flujo mínimo (`:27-45`), clases `contract`/`living` (`:61-115`).
6. **Bootstrap** — `skills/cdad-cycle/references/bootstrap.md` (129 líneas): cuando no hay Memory
   Bank ni `docs/specs/` (`:1-3`), pasos 1-5 (`:13-114`).
7. **Epic** (si `active_epic` no es nulo) — `skills/cdad-epic/SKILL.md` (289 líneas) + sus
   referencias: `state-detection.md`, `epic-discovery.md`, `epic-planning.md`, `feature-handoff.md`.
8. **Adaptadores** — `sources/agents/adapters/opencode.md` y `claude-code.md` (carga de skills por
   el tool `skill`/`Skill`, `opencode.md:52-57`, `claude-code.md:45-50`).

### 1.2 Dónde vive —o falta— el procedimiento de arranque corto (fricción 6)

**Verificado (ausencia):** las referencias de `cdad-cycle` son
`anti-patterns, bootstrap, claude-code-delegation, continuity, handoff-prompts, opencode-delegation,
progress-guards, project-execution, receiving-feedback, re-entry, runtime-adoption, stage-1..5,
stage-debugging, state-detection, sub-agent-strategies, verdict-tuple`; las de `cdad-epic`:
`anti-patterns, epic-closure, epic-discovery, epic-integration, epic-planning, feature-handoff,
state-detection`. **No existe ningún archivo de "arranque/reconocimiento/startup"** y la tabla de
carga (`SKILL.md:443-460`) no tiene fila para iniciar desde reposo. El arranque hay que **deducirlo**
combinando: intake del agente + `state-detection.md` + `project-execution.md` + `continuity.md` +
`bootstrap.md` + el skill de epic. Ese es el costo que describe
`findings/session-guided-start-friction-2026-10-10.md:51-55` (fricción 4 del finding: «carga tardía y
voluminosa del procedimiento») y `evidence/005-006-attempt-1.md:30-31` (fricción 6: leyó
`project-execution.md` y `continuity.md` para deducir el arranque).

**Tres "inicializaciones" distintas conviven y no están desambiguadas en un lugar corto:**
| Sentido de "inicializar" | Dónde vive | Qué crea |
|---|---|---|
| Memory Bank del proyecto | `bootstrap.md:66-102` | `docs/{projectbrief,systemPatterns,activeContext,progress}.md`, `adr/`, `specs/`, `.cdad-state.json` |
| Bootstrap de ejecución v2 | `project-execution.md:84-97`; `cdad_packet.py:1571` (`_bootstrap_v2_execution`), `:1650-1659` | `.cdad/executions/<id>/execution.json`, binding `state.execution`, `.cdad/packets/<id>/` |
| Adopción/activación por runtime | `runtime-adoption.md:9-39` (`scripts/cdad-activate.py`) | `.opencode/opencode.jsonc`, `.cdad/activation.json`, enlaces de skills |

---

## 2. Reconocimiento e inicialización del proyecto

### 2.1 Qué distingue «parcialmente inicializado» de «nuevo» y de «configuración incompleta»

**Primitivas verificadas (todas deterministas y ya existentes):**

- Con `.cdad-state.json` presente → es **fuente de verdad** (`state-detection.md:9-32`), con
  sanity-check contra los archivos reales (`:84-88`).
- Sin state → **inferencia por archivos** (`state-detection.md:44-60`): sin
  `projectbrief.md`+`activeContext.md` → **bootstrap**; Memory Bank pero sin `docs/specs/` →
  discovery; spec sin marca de aprobación → specification; etc. Estos son exactamente los tres
  estados a distinguir (nuevo / parcial / incompleto).
- **Memory Bank "inicializado"** = los 4 documentos existen con contenido real
  (`state-detection.md:98-107`); si falta cualquiera → bootstrap.
- **Configuración incompleta / incoherente** (lado ejecución): `prepare` falla cerrado sin publicar
  nada: sin política → error (`project-execution.md:60-61`, PD-1); sin autoridad o con pin
  ausente/derivado → diagnóstco `approval pending` rc=2 (`:72-73`); sin state → error
  (`cdad_packet.py:1770` `_load_json(... "project state")`).
- **Acoplamiento con el plan (crítico):** `prepare` exige que `state.epic_features` contenga la
  feature de la ejecución **exactamente una vez** y no cerrada, y que `active_feature` coincida
  (`cdad_packet.py:549-554`, `:1459-1509`). Un cambio de plan que agregue features **sin**
  sincronizar `epic_features` rompe el arranque (raíz de la fricción 5, §4.4).

### 2.2 Documentos/registros canónicos (verificados en este repo)

| Registro | Estado aquí | Fuente del contrato |
|---|---|---|
| `docs/.cdad-state.json` | presente (171 KB); `active_epic=epic-005-real-operation`, `epic_stage=features-loop`, `active_feature=005-006-guided-project-start`, `current_stage=discovery`, `execution={id: exec-005-006-…}`, `hitl_delegation.status=active`, `active_packet=005-006-…-architect-discovery-001` | `assets/state-template.json` (claves: `version, stack, active_epic, epic_stage, active_feature, current_stage, tdd_substage, audit_status, postconditions_status, epic_features, stage_history, epic_history, approver, last_updated, execution, active_packet, hitl_delegation`) |
| `docs/cdad-policy.json` | presente (461 B) | `project-execution.md:7-49`; `execution-004-001.json` (path_policy) |
| `.cdad/activation.json` | **ausente** (verificado); `.cdad/` es git-ignorado (`.gitignore:11`) | `runtime-adoption.md:37-39` |
| Memory Bank | `docs/{projectbrief,systemPatterns,activeContext,progress}.md` presentes | `state-detection.md:98-107` |
| plan del epic | `docs/epics/epic-005-real-operation/plan.md` (tracked) | `state-detection.md:34-42`; `cdad-epic/SKILL.md` |
| convención de nombres | features = `<epic-num>-<feat-num>-<slug>` o slug compuesto; la pertenencia vive en `epic_features`, no hace falta codificarla en el id | `cdad-epic/SKILL.md:151`, `:187-194` |
| registro local de instalación | `.cdad/local/handoff-005-005.local.md` (§005-006, `:17-20`), fuera de git | `runtime-adoption.md`; `.gitignore:11` |

### 2.3 Qué "crea bootstrap hoy sin pisar lo existente"

- **Memory Bank:** `bootstrap.md:19` pide confirmación antes de crear; `:66-102` copia plantillas y
  deja `<TODO>`; anti-patrones `:121-125` (no crea specs ni ADRs vacíos).
- **Ejecución v2:** `project-execution.md:92-97` — si ya existe contexto previo (v1 o v2 activa)
  exige `--new-execution`; no adopta hacia atrás; v1 falla con diagnóstico y no reescribe (PD-10,
  `project-execution.md:100-105`).
- **Adopción/activación:** determinista y no-clobber con propiedad — reemplaza solo lo que emitió el
  generador y registró en `.cdad/activation.json`; un destino ajeno divergente es conflicto rc≠0,
  todo o nada (`runtime-adoption.md:55-79`).
- **Agentes derivados:** `prepare` conserva archivos ajenos y rechaza sobrescribir derivados
  modificados sin resolución explícita (PD-8, `004-002/spec.md:82`).

---

## 3. Registro de requisitos y restricciones (dónde va cada uno)

| Requisito | Lugar canónico | Inferible vs decide el usuario |
|---|---|---|
| **stack** | `state.stack` | **autodetectado** por convención `*-architect` (candidato único → escribe sin preguntar; ambiguo → pregunta si hay usuario, si no deja `null` y lo anota en `activeContext.md`). Fuente: `bootstrap.md:37-64`; activación en `SKILL.md:125-132` |
| **privacidad** | `docs/cdad-policy.json` → `path_policy.private_paths` | edición reservada; es la «barrera deliberadamente obvia» (`project-execution.md:21-38`) |
| **entorno de pruebas** | metodología define la evidencia; **el proyecto declara los comandos**; `test_roots` en la política | regla única en `systemPatterns.md:241-246` (INV-6) + `execution.json.test_roots`; en Odoo vía `skills/odoo-make-env/` |
| **límites operativos** | `policy.temporary_roots`; ADR-011 (autoridad/capacidades/límites proporcionales) | `project-execution.md:7-17`; ADR-011 (`sources/roles/architect.md` cdad-shared:limits-core) |
| **autoridad** | `state.hitl_delegation` + `approver`; decisión del dueño en `docs/epics/<epic>/execution.md` | **decide el usuario** (no delegable); `plan.md:68-79`, `execution.md`; enforcement en `project-execution.md:74-82` |
| **organización / convenciones** | Memory Bank `projectbrief.md`/`systemPatterns.md`; convención de nombres de epic (`cdad-epic/SKILL.md:151`) | bootstrap pregunta nombre/propósito/framework/CI/aprobador (`bootstrap.md:23-35`) |

**Regla "inferible vs decide" ya enunciada:** `bootstrap.md:23-35` (*«No hagas un cuestionario
largo. Tres o cuatro preguntas concretas»*), `:37-64` (stack automático), `:59-61` (ambigüedad → si
hay usuario pregunta; si no, registra la duda). En `stage-1-discovery.md:45-73` el orquestador guía
el discovery preguntando lo mínimo y delega el mapeo al architect.

---

## 4. Fricciones 1, 2, 4 y 5 (texto exacto que las causa / las resolvería)

### 4.1 Fricción 1 — no cargó las skills por iniciativa propia

- **Causa ubicada:** `sources/roles/orchestrator.md:37-40` (idéntico `agents/cdad-orchestrator.md:31-34`):
  la skill `cdad-cycle` solo se nombra como **camino legacy, SECOND**, condicionado a *«Without a
  prepared execution/request»*. En un arranque desde reposo esa condición es ambigua: no hay
  ejecución preparada, pero el agente no tiene una instrucción de "cargala ya".
- **Agravante:** `legacy-loads: cdad-cycle only` (`:46-48`) y el disparador vive solo en la
  `description` del SKILL (`SKILL.md:3`, *«Use ALWAYS when the user mentions CDAD…»*), que no es
  una orden operativa del agente. El texto que **resolvería** es el intake del agente
  (`orchestrator.md:19-43`): una entrada de arranque que ordene cargar la metodología primero.
- **Evidencia:** `evidence/005-006-attempt-1.md:16-19`; `findings/…-2026-10-10.md:51-55`.

### 4.2 Fricción 2 — usó el CLI/rutas del repo, no la versión instalada

- **Causa ubicada (rutas relativas al proyecto en el cableado):**
  - `sources/roles/orchestrator.md:80-82` → `skills/cdad-cycle/references/continuity.md`,
    `scripts/cdad_continuity.py`.
  - `sources/roles/orchestrator.md:97-98` → `skills/cdad-cycle/references/re-entry.md`,
    `scripts/cdad_result.py`.
  - `SKILL.md:260-261` → `scripts/cdad_packet.py render`.
  - `continuity.md:31-44` → `python3 skills/cdad-cycle/scripts/cdad_continuity.py begin …`.
  - `SKILL.md:451-452` (tabla de referencias) → `scripts/cdad_continuity.py`, `references/…`.
- **Contraste con el producto instalado:** `install.sh:47-52` define
  `$INSTALL_ROOT/.config/opencode/{agents,skills}`, `.agents/skills`, `.claude/skills`;
  `install.sh:397-409` describe el layout de instalación; `README.md:5-10` fija el entrypoint
  `$CDAD_INSTALL_ROOT/skills/cdad-cycle/scripts/cdad_packet.py`; `runtime-adoption.md:37-39` registra
  la raíz adoptada. En **cualquier otro proyecto** `scripts/…` y `skills/cdad-cycle/…` (relativos al
  proyecto consumidor) **no existen** → contradice "operar con la versión instalada" y no es portable.
- **Matiz de resolución:** `project-execution.md:47-49` advierte que `--input`/`--decision-ref`
  resuelven contra el **cwd**, no contra `--project-root` — relevante para no confundir "ruta del
  CLI" con "ruta del proyecto".
- **Evidencia:** `evidence/005-006-attempt-1.md:20-23`.

### 4.3 Fricción 4 — `resume` en reposo sin ejecución activa

- **Causa ubicada (texto que prescribe `resume` sin matizar):**
  - `SKILL.md:244` (paso 1 del flujo): *«When you start a new session, rebuild the carried context
    first with `resume`»*.
  - `sources/roles/orchestrator.md:86` (idéntico `agents/cdad-orchestrator.md:80`): *«`resume` —
    read-only; the first step of every new session that resumes work»*.
  - `continuity.md:19` (tabla): `resume` aplica a *«Any new session that must rebuild goal…»* y
    *«Without a checkpoint it renders an empty `no-checkpoint` projection (rc 0)»*.
  - `SKILL.md:280` y `:452` refuerzan `resume`/`reconcile`.
- **Qué falta:** la distinción «continuar la feature siguiente» vs «reanudar una ejecución cerrada»
  no está expresada en el arranque (lo señala `findings/…-2026-10-10.md:37-43` y
  `evidence/005-006-attempt-1.md:26-27`). `resume` no aporta en reposo porque no hay checkpoint.
- **Evidencia:** `evidence/005-006-attempt-1.md:26-27`.

### 4.4 Fricción 5 — cambio de plan no reflejado en `epic_features`

- **Causa ubicada (el procedimiento no dice quién/cuándo sincroniza):**
  - `skills/cdad-epic/references/epic-planning.md:130-143` («If the plan needs to be updated during
    the feature loop»): manda **actualizar `plan.md`**, registrar el cambio con fecha/motivo y
    commitear; re-aprobación solo si cambia alcance/criterios. **No menciona `epic_features`.**
  - El único punto que puebla `epic_features` es el gate E2→features (`epic-planning.md:120-122`).
  - `feature-handoff.md:89-98` cubre "una feature falla y devuelve trabajo", pausando la feature en
    curso, pero **no** el alta de features nuevas en `epic_features`.
- **Efecto verificado en código:** `prepare` exige la entrada en `epic_features` y su estado
  (`cdad_packet.py:549-554`, `:1459-1509`). Es decir, el defecto no es cosmético: sin sincronizar,
  el arranque de la feature nueva falla cerrado. Nota: en este repo el state **ya** refleja
  005-006/005-007 (sync hecha a mano el 2026-10-10), pero el procedimiento sigue sin asignar el
  responsable.
- **Evidencia:** `evidence/005-006-attempt-1.md:28-29`; `findings/…-2026-10-10.md:66-70`.

---

## 5. Contrato bidireccional del arranque

### 5.1 Qué da hoy el arnés al rol (insumos / capacidades)

- **Insumos:** el intake define los dos caminos y los insumos (`orchestrator.md:19-43`); el paquete
  preparado lleva `inputs`, `read_scope`, `write_scope`, `invariants`, `expected_output`,
  `evidence_required` (`project-execution.md:164-232`); la regla de state-passing exige contexto
  completo y unidad atómica (`orchestrator.md:69-75`; `SKILL.md:192-201`).
- **Capacidades:** tabla de contrato por rol (`orchestrator.md:117-121`); resolución de stack para
  elegir variante `cdad-<role>-<stack>` (`orchestrator.md:168-180`); sección bash del orquestador
  (`orchestrator.md:134-147`).
- **Salida legítima ante bloqueo (parcial):** «no fallback silencioso» ante paquete inválido
  (`orchestrator.md:41-43`); «no equivalent retries / detours; reportar el bloqueo con evidencia»
  (agent `cdad-orchestrator.md:197-218`, written-scope rule); resource de límites en
  `sources/roles/architect.md` (cdad-shared:limits-core).
- **Vacío verificado:** **no hay** un camino definido para el arranque desde reposo cuando **no hay**
  ejecución preparada y el proyecto **no está reconocido** (nuevo / parcial): el intake solo cubre
  "preparado" vs "legacy cargar cdad-cycle". Ese es el hueco de contrato bidireccional que la feature
  debe cerrar.

### 5.2 Salida legítima ante bloqueo — referencias existentes

- Mensajes de bloqueo que distinguen aprobación pendiente / paquete obsoleto / estado incoherente:
  `plan.md:33` (fila 005-001, punto d) y `project-execution.md:72-73`.
- `SKILL.md:31-34`: si el usuario pide trabajo de rol, o se conmuta de modo explícito o se recuerda
  con cortesía — no se hace el trabajo inline.

---

## 6. Aceptación

### 6.1 Distinción del proyecto existente parcialmente inicializado

- El proyecto de aceptación se identifica en el **registro local de la instalación**, no en este
  repo: `.cdad/local/handoff-005-005.local.md:17-20` (§005-006) nombra el proyecto elegido por el
  dueño y su raíz. `.cdad/` está git-ignorado (`.gitignore:11`), por lo que ese nombre **no** aparece
  en archivos versionados — consistente con `plan.md:139-142` (se reemplazó el nombre interno por la
  referencia al registro local).
- Esto materializa el requisito `plan.md:35`: *«un proyecto existente parcialmente inicializado,
  elegido por el dueño (identificado en el registro local de la instalación, no en este repo)»*.

### 6.2 Comprobaciones pequeñas de "proyecto nuevo" y "configuración incompleta" verificables sin
depender de nombres/carpetas/entorno

Primitivas deterministas ya existentes y **agnósticas del proyecto** (verificables con fixtures
temporales):

| Comprobación | Primitiva verificada | Test existente |
|---|---|---|
| Proyecto nuevo (sin Memory Bank) → bootstrap | `state-detection.md:44-60`, `:98-107`; `bootstrap.md:66-102` | (a nivel flujo; no hay test directo del bootstrap de Memory Bank) |
| Sin política → error, sin publicar | `project-execution.md:60-61` (PD-1) | `tests/test_004_002_t1_policy.py` |
| Sin autoridad / pin ausente → `approval pending` rc=2 | `project-execution.md:72-73` | `tests/test_005_001_t1_role_approval.py` |
| State en reposo legítimo aceptado / incoherente rechazado | `plan.md:33` (VALIDATE-IDLE) | `tests/test_005_001_t3_idle.py` |
| Bootstrap v2 crea identidad sin contexto manual | `cdad_packet.py:1571`, `:1650-1659`; PD-3 | `tests/test_004_002_t2_bootstrap.py` |

Estas comprobaciones no dependen de nombres, carpetas ni entorno del proyecto de aceptación.

---

## 7. Frontera con 005-003

- `plan.md:35` (fila 005-006) cierra con: *«Frontera con 005-003: 005-006 resuelve el arranque;
  005-003, la orientación al retomar; comparten el mismo procedimiento de reconocimiento del
  proyecto.»*
- `plan.md:37` (fila 005-003 `orientation-reduction`): reduce las lecturas previas al `resume` (base
  18 en la sonda 2); se acepta solo con sonda nueva medida por la herramienta de 005-002.
- `findings/…-2026-10-10.md:100-105` distribuye: **005-006** = arranque, reconocimiento y encargos
  suficientes; **005-003** = lectura compacta y selección del camino de continuidad.
- El **procedimiento de reconocimiento** compartido es `state-detection.md` (cada skill tiene su
  copia: `skills/cdad-cycle/references/state-detection.md` y
  `skills/cdad-epic/references/state-detection.md`) — punto de posible unificación/deduplicación a
  resolver en `draft` (VERIFY: cuál es dueño canónico).

---

## 8. Límite explícito del plan

`plan.md:35`, cierre: **«No traslada el prompt largo a una plantilla.»** Es un invariante de la
solución: la fricción 6 no se resuelve moviendo el prompt largo a una plantilla; el arranque debe
resolverse en un procedimiento corto y directo.

---

## 9. Recorridos concretos de uso (petición inicial → primera entrega)

**R1 — Proyecto nuevo, desde reposo.** «usá CDAD para inicializar este proyecto y comenzar su
análisis preliminar» → hoy: el agente no tiene orden de cargar la skill (fricción 1) → si la carga,
`state-detection.md` infiere **bootstrap** (sin `projectbrief`/`activeContext`) → `bootstrap.md`
crea el Memory Bank (pregunta 3-4 cosas) → sin ejecución preparada, el primer encargo debe pasar por
`prepared execution path` (requiere `state.execution`, política y autoridad). **Punto de fricción:**
el bootstrap y el bootstrap de ejecución v2 son procedimientos separados y ninguno encadena al otro
hacia la primera delegación.

**R2 — Proyecto existente parcialmente inicializado, epic activo (caso del intento 1).** Instrucción
breve → reconocer repo anidado (contenedor vs raíz) → detectar `active_epic`/`active_feature` →
**sincronizar `epic_features` con el plan aprobado** (fricción 5; sin esto `prepare` falla) →
evitar `resume` en reposo (fricción 4) → preparar el primer encargo con el **CLI instalado**
(fricción 2). Objetivo: primera delegación útil (p. ej. discovery del architect).

**R3 — Configuración incompleta.** State presente, `docs/cdad-policy.json` ausente →
`prepare` falla cerrado (PD-1); o autoridad sin pin → `approval pending` rc=2. El arranque debe
**decir qué falta y cómo seguir**, no inventar ni cambiar de versión en silencio.

---

## 10. Puntos de extensión (dónde tocaría la solución, sin proponerla)

- **Intake del agente orquestador** — `sources/roles/orchestrator.md:19-48` (fuente canónica;
  regenera `agents/cdad-orchestrator.md` y `.opencode/agents/…` vía `scripts/cdad-generate.py`, ver
  header `sources/roles/orchestrator.md:1-16`).
- **Skill de ciclo** — `skills/cdad-cycle/SKILL.md:240-281` (flujo), `:439-461` (tabla de
  referencias), `:500-512` (coordinación con epic).
- **Referencias de `cdad-cycle`** — un procedimiento corto de arranque/reconocimiento encajaría en
  `references/` (hay un hueco explícito: no existe tal archivo).
- **Skill y referencias de `cdad-epic`** — `epic-planning.md:130-143` (sincronización de
  `epic_features`), `feature-handoff.md` (camino de continuación).
- **CLI/política** — `docs/cdad-policy.json`, `state.execution`, procedencia en `runtime-adoption.md`.
- **Adaptadores** — `sources/agents/adapters/{opencode,claude-code}.md` (carga de skills,
  `external_directory`).
- **Path policy del repo (para tests)** — `path_policy` del paquete: `test_roots: ["tests"]`,
  `documentation_roots: ["docs"]`, `documentation_files: ["README.md"]`,
  `implementation_roots: ["agents","skills","scripts","sources","build"]`,
  `implementation_files: ["install.sh"]` (del payload del packet).

---

## 11. Convenciones aplicables (verificadas)

- **Estado:** un único escritor (`docs/.cdad-state.json`); el CLI de continuidad nunca lo escribe
  (`continuity.md:141-143`).
- **Evidencia de tests:** dueño canónico único en `stage-3-tdd.md` §«Test evidence policy»; el
  proyecto declara los comandos (`systemPatterns.md:241-246`, INV-6).
- **Autorización por rol:** architect se habilita con la aprobación del plan del epic; otros roles
  exigen `stage_history.specification` con pin `contract_path`+`contract_sha256`
  (`systemPatterns.md:190-200`; `project-execution.md:56-73`).
- **Nomenclatura de feature:** `<epic-num>-<feat-num>-<slug>` (o slug compuesto); pertenencia en
  `epic_features` (`cdad-epic/SKILL.md:151`, `:187-194`).
- **Paths personales/instalación:** al registro local git-ignorado `.cdad/local/`
  (`005-005/spec.md` §7 D7; `.gitignore:11`).
- **Aprobaciones no delegables del orquestador:** spec, prioridad de review, Memory Bank, plan del
  epic (`SKILL.md:480`; `plan.md:68-79`).

---

## 12. Riesgos y elementos abiertos a VERIFY

1. **VERIFY — dueño canónico del procedimiento de reconocimiento compartido** entre
   `cdad-cycle/references/state-detection.md` y `cdad-epic/references/state-detection.md`
   (frontera 005-003). No hay hoy una única definición declarada para ambos.
2. **VERIFY — `resume` rc=0 sin checkpoint:** `continuity.md:19` lo afirma; no se ejecutó aquí
   (no re-ejecuté el CLI; evidencia de la sesión original). Confirmar contra la versión instalada.
3. **VERIFY — camino de invocación del CLI instalado:** README fija `$CDAD_INSTALL_ROOT/…` pero el
   cableado escribe rutas relativas al proyecto (`orchestrator.md:80-98`). Cuál es el mecanismo
   esperado (variable `CDAD_*`, activación, o descubrimiento) es una decisión abierta.
4. **VERIFY — `README.md` no documenta el arranque guiado:** la sección "Per-deploy configuration"
   (`README.md:227-254`) cubre `external_directory` de `opencode.jsonc`, pero no el recorrido de
   arranque; `README.md` es un único `documentation_file` de la política.
5. **VERIFY — `.cdad/activation.json`** ausente en este repo; para el proyecto de aceptación no se
   puede afirmar si usa activación, variable global o instalación global: depende de su entorno
   (fuera de este repo).
6. **VERIFY — sincronización de `epic_features`:** no existe texto de procedimiento que asigne
   responsable; el enforcement existe en código (`cdad_packet.py:549-554`, `:1459-1509`). Confirmar
   si la solución debe nombrarlo en `cdad-epic` o en el arranque.
7. **Riesgo — no re-introducir la condición ambigua:** el límite de `plan.md:35` (no mover el prompt
   largo a una plantilla) exige que cualquier arreglo del arranque sea un procedimiento operativo
   corto, no un documento de plantilla.
8. **Riesgo — doble bootstrap:** Memory Bank bootstrap y ejecución v2 bootstrap comparten la palabra
   "bootstrap" pero son procedimientos distintos; confundirlos reproduce el ruido del intento 1.

---

## 13. Evidencia de ejecución (comandos, sin modificar el repo)

- `sha256sum docs/epics/epic-005-real-operation/plan.md` → `4b403b0e…d6c71` (coincide con el contrato).
- `git log --oneline -3` (raíz `<repo>`) → `f8aac63 docs(epic-005):
  evidencia del primer intento de arranque…`.
- `ls`/`find` de `skills/*/references`, `sources/`, `agents/`, `.cdad/`, `docs/` (estructura).
- `python3 -c "import json; json.load(open('docs/.cdad-state.json'))"` (claves y campos epic/execution).
- `rg` sobre `sources/roles/orchestrator.md`, `skills/cdad-cycle/SKILL.md`,
  `skills/cdad-epic/references/epic-planning.md`, `skills/cdad-cycle/scripts/cdad_packet.py`
  (líneas citadas).
- `git check-ignore -v .cdad/local/handoff-005-005.local.md` → `.gitignore:11:.cdad/`.
