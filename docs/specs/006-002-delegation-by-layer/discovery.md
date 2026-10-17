I'll start by verifying the contract hash and reading the epic plan, then inventory the delegation surface.
Contract hash matches. Now let me read the execution record and map the delegation surface.
# Discovery — `006-002-delegation-by-layer`

**Rol:** architect · **Subetapa:** 1 (Discovery) · **Contrato:** `docs/epics/epic-006-opencode-concurrency/plan.md` §8 (enmienda 001) + §9 (enmienda 002) · **Estado del state:** `active_feature=006-002-delegation-by-layer`, `current_stage=discovery`, sin spec ni plan de feature (`docs/specs/006-002-delegation-by-layer/` no existe).

Verificación del contrato: `sha256(plan.md)=b6a59502…f2e63` (coincide con el packet). Trabajo **read-only**: árbol limpio antes y después; no se editó, commiteó ni instaló nada.

---

## 0. Método y límites de esta etapa

Leí el plan (§8, §9), `execution.md` (incidente, insumo del consumidor, hallazgos de 006-001) y todo el texto instalable que decide delegación, más el generador, el instalador y los tests acoplados. Las citas son `archivo:línea` relativas al repo. Lo que no pude verificar quedó como **VERIFY** explícito (§4). No propongo spec definitiva ni la apruebo; entrego mapeo y decisiones recomendadas.

---

## 1. Inventario: texto instalable que hoy decide delegación o nombra runtime/modelos

Leyenda de capa objetivo: **SKILL** = metodología general y única · **AGENTE** = comportamiento por runtime · **SCRIPT** = SO, independiente del runtime · **ADAPTADOR** = orquestar agentes de **otro** runtime o de un runtime sin delegación propia · **CONFIG** = 006-003 (instalador/config), fuera de esta feature.

### 1.1 `skills/cdad-cycle/SKILL.md` (598 líneas)

| # | Líneas | Qué decide/nombra hoy | Capa correcta | Acción |
|---|---|---|---|---|
| 1 | 42-46 | Preámbulo “regardless of the harness (native sub-agents, permission globs, **task/delegate routing**)” | SKILL, con nombres fuera | Quitar nombres de herramientas; dejar “delegación nativa del runtime, si existe” |
| 2 | 67-75 | Tabla §2, columna **Model family** con modelos concretos: `deepseek-v4-pro`, `glm-5.2`, `deepseek-v4-flash`, `qwen3.7-plus` | CONFIG | Eliminar la columna de modelos; ver decisión (f) |
| 3 | 77 | Párrafo de perfiles con modelos concretos y flags `install.sh --economical|--optimus|--premium|--basic` | CONFIG | Quitar de la skill; el principio “modelo configurado” reemplaza el mapa |
| 4 | 79-82 | Invariantes anti-sesgo (reviewer de otra familia, test-writer no ve implementación, auditoría por sesión distinta) | **SKILL** | Conservar (es la invariante de rol) |
| 5 | 128-131 | `stack` → variantes `cdad-<role>-<stack>` | SKILL | Conservar (genérico) |
| 6 | 134-141 | Delegación externa ≠ recursión; no amplía autoridad; el worker no escribe el state | **SKILL** | Conservar y ampliar con la regla de dueño del ciclo de vida |
| 7 | 143-150 | SPAWN GUARD nombrando `sessions_spawn` | SKILL con nombre de tool | Generalizar: “la herramienta de spawn del runtime; nunca reintentar el rechazo” |
| 8 | 152-162 | Regla de decisión: OpenCode `task`/`delegate` (canal muerto), Claude Code `Agent` + PreToolUse hooks; punteros a las dos referencias | **AGENTE** | SKILL solo conserva el **orden** (nativo → nuevo chat → inline) sin nombrar tools |
| 9 | 243 | Recomendación modo B: “`task`/`delegate` es preferido” | AGENTE | Delegar al agente del runtime |
| 10 | 263-275 | Paso 4: “dispatch those bytes through **Task**”, “`task`/`delegate`” | AGENTE | Reemplazar por “el mecanismo nativo que declara el agente orquestador” |
| 11 | 462-466 | Tabla de referencias expone `opencode-delegation.md` (Task) y `claude-code-delegation.md` (Agent); `progress-guards.md` con `opencode run` | AGENTE / ADAPTADOR | Retirar las dos filas de runtime; la de `progress-guards` queda solo bajo la regla de adaptadores |
| 12 | 499-504 | “Multi-environment compatibility” (a1 OpenCode `task`/`delegate`, a2 Claude Code `Agent`, (b) handoff, (c) Zed) | SKILL (orden) + AGENTE (mecanismo) | Dejar el orden en abstracto; el mecanismo va al agente |
| 13 | 288 | “rotate at a natural task boundary” (ya existe) | SKILL | Conservar y **citar** desde la disciplina de contexto (e) |

### 1.2 `skills/cdad-cycle/references/` (24 archivos)

| # | Archivo:líneas | Qué decide/nombra hoy | Capa correcta | Acción |
|---|---|---|---|---|
| 14 | `opencode-delegation.md:1-194` | Todo el mecanismo OpenCode: `task` vs `delegate` (78-122), clasificación por permisos del plugin (80-97), `write: ask` como palanca (96-97, 117-122), PWD (56-63), carga `mode: subagent` (37-54), mapeo rol→`subagent_type` (18-26), puntero a la tabla única de modelos (28-35), fallback 429 (124-132), reload/version/provenance (148-194) | **AGENTE (OpenCode)** | Mover el núcleo al agente OpenCode; el detalle histórico/verificación a `docs/` (no instalable) |
| 15 | `claude-code-delegation.md:1-122` | Mecanismo CC: `Agent` (7-15), mapeo con **modelos concretos** `sonnet|haiku|opus` (19-26), hooks PreToolUse y guard v2 (41-92), re-delegación (93-103), fallback sin Agent (105-111), verificación ADR-008 (113-122) | **AGENTE (Claude Code)** | Igual: núcleo al agente CC; detalle a docs |
| 16 | `cli-delegation.md:1-334` | Contrato del **adaptador externo** (`cdad_delegate.py`, modos `server|service|standalone`, señal durable, `receive`) — correcto como documento de adaptador; **pero** 267-276 pone la regla “dentro de OpenCode se delega con `task`” dentro de la skill | ADAPTADOR (1-266, 278-334) + **AGENTE** (267-276) | Conservar como contrato del adaptador; mover 267-276 al agente del runtime |
| 17 | `sub-agent-strategies.md:11-55, 97-105, 131-166` | Estrategia por entorno (OpenCode, CC, Zed), “different model per sub-agent” (40), alias de modelo CC (51), tabla de recomendación (97-105), cheat-sheet de permisos (131-142), regla de decisión con variantes (163-166) | AGENTE + SKILL (solo 69-95, fallback universal) | Partir: genérico queda; por-runtime va al agente |
| 18 | `handoff-prompts.md:36-49, 86-91, 515` | “Invocation with native sub-agents in OpenCode … via `task` con `subagent_type`” (36-40), “OpenCode @name, Claude Code Task” (91), **modelo concreto de ejemplo** `mofgw/qwen3.7-plus` (515) | AGENTE (36-49, 86-91) + CONFIG (515) | Quitar nombres de tool y modelo; dejar plantillas metodológicas |
| 19 | `context-meter.md:156-198` | Contrato del **lector**: `reader.dispatch_tools` reconoce `subagent` y `task`; `cdad_delegate.py` como despacho material (171-198) | SCRIPT/medición (parametrizado por runtime) | **No es una instrucción de delegación**: declararlo contrato de medición; si se toca, parametrizar el set por runtime |
| 20 | `progress-guards.md:27, 38` | “dispatch roles as external processes (e.g. `opencode run`)”, comportamiento con `background: true` | ADAPTADOR | Dejar solo bajo la regla “otro runtime / sin delegación nativa” |
| 21 | `project-execution.md:160-183` | Mecanismos por runtime de agentes derivados y barreras de path (OpenCode W-2/W-3, guard CC) | AGENTE (adyacente) | Fuera de 006-002; no es delegación |
| 22 | `runtime-adoption.md:15-53` | Adopción por runtime (`--runtime opencode|claude-code|codex`, `.opencode/agents`, `.claude/agents`) | AGENTE (adyacente) | Fuera de 006-002 |
| 23 | `orientation.md:125` | “leg claude-code” del chequeo de versión | AGENTE (dato de versión) | Aceptable; no es delegación |
| 24 | `re-entry.md:14-68` | Protocolo de materialización y **recibo** (`receive`, staged-file en `.cdad/inbox`, `validate-receipt`, `materialize`, transición) — **independiente del transporte**; no nombra tools de runtime | **SKILL** | Conservar; agregar el enlace de equivalencia de transporte (decisión d) |

### 1.3 `skills/cdad-epic/`

| # | Ubicación | Hallazgo | Capa | Acción |
|---|---|---|---|---|
| 25 | `SKILL.md:215-228` | “Why there is no `cdad-epic-*` sub-agent”: menciona runtimes como hecho (“the same agent in both runtimes”) pero **no** fija tools ni modelos | SKILL | Conservar; sin cambios |
| 26 | `SKILL.md:68, 287`; `references/feature-handoff.md:26-31, 113` | Delegación al `cdad-cycle` / sub-agentes en genérico | SKILL | Conservar |

### 1.4 Fuentes, generador, agentes e instalador

| # | Ubicación | Hallazgo | Capa | Acción |
|---|---|---|---|---|
| 27 | `sources/roles/orchestrator.md:74-79, 97-102` | Orden de delegación y guard de spawn en la fuente del rol (compartida) | **SKILL/AGENTE (fuente)** | Conservar el principio; el mecanismo por runtime no va acá |
| 28 | `sources/roles/orchestrator.md:165-173` | Anti-sesgo + “Model: per profile from `scripts/cdad-models.sh`” (meta-fuente) | SKILL | Alinear a “modelo configurado”; sin nombres |
| 29 | `sources/roles/orchestrator.md:177-189` | Bash supervisor: nombra `mode: all`/`permission: allow` de OpenCode y `Edit/Write/Task` de CC | AGENTE | Aceptable como política declarada; idealmente referenciar el adaptador |
| 30 | `sources/agents/adapters/opencode.md:14, 52-57` | `mode: subagent`, `write: ask`, `task`/`delegate` | **AGENTE (correcto)** | Es el lugar correcto; se le suma la sección de delegación |
| 31 | `sources/agents/adapters/claude-code.md:13-33, 74-79` | `tools:` con `Agent`, `model:` por perfil, provenance de `basic`, hooks | **AGENTE (correcto)** | Correcto; se le suma la sección de delegación |
| 32 | `scripts/cdad-generate.py:812-828` | El orden de delegación y el guard de spawn están **hardcodeados en Python** y emitidos en ambos runtimes | AGENTE (fuente) | Mover a una sección `delegation` por adaptador y componerla en `compose_orchestrator_agent` (ver a) |
| 33 | `scripts/cdad-generate.py:201, 578-613` | `model_for` y `models_note` resuelven modelos por runtime×perfil | CONFIG | 006-003 |
| 34 | `agents/cdad-orchestrator.md:172-179, 263-266` y `agents/claude-code/cdad-orchestrator.md:5, 178-185, 269-272` | Salidas generadas (regla neutral + tool-loading del adaptador; CC con `model: opus`) | AGENTE | Se regeneran con `make agents` |
| 35 | `install.sh:1036-1045` | **El mismo árbol de skills se instala en las tres bases** (`~/.config/opencode/skills`, `~/.agents/skills`, `~/.claude/skills`) | Restricción de diseño | **No existe hoy** un mecanismo de “referencia por runtime instalada solo con ese runtime” |
| 36 | `install.sh:47-52, 126-141, 329-360` | Los **agentes** sí son por runtime; los perfiles/modelos son del instalador | AGENTE / CONFIG | Los agentes son la vía natural; perfiles → 006-003 |
| 37 | `scripts/cdad-models.sh:1-174` | Mapa único de modelos (perfiles) | CONFIG | 006-003, no 006-002 |

### 1.5 Tests acoplados al texto que se mueve (impacto, no texto instalable)

| Test | Qué fija hoy |
|---|---|
| `tests/test_005_004_t1_dispatch_tool_name.py:62-64` | Rutas de `claude-code-delegation.md` y `opencode-delegation.md` |
| `tests/test_005_004_t4_cc_guard_decisions.py:95` | `claude-code-delegation.md` como “consumidor” de PD-4/PD-9/PD-8 (aserciones de contenido, p. ej. 500-615) |
| `tests/test_005_005_t3_provenance.py:61` | `opencode-delegation.md` documenta reload/provenance |
| `tests/test_005_009_t3_spawn_reconciliation.py:69, 231-264, 491-495` | “conservación” de la prohibición de re-delegación en `claude-code-delegation.md` y `SKILL.md` |
| `tests/test_005_010_t3_references.py:67-74, 88-114` | Contenido de `cli-delegation.md` y `opencode-delegation.md`; prohíbe modelos concretos en ambas |
| `tests/validate-consistency.sh:126-135, 227-232, 263-269` | La tabla “How to read the references” **debe** incluir `claude-code-delegation.md`; asserts sobre ese archivo; `--basic` y el caveat en SKILL.md y en ambos orquestadores |

Conclusión del inventario: el texto instalable está **duplicado por capas**: el mismo mecanismo aparece en la skill (§4 + 2 referencias + `handoff-prompts` + `sub-agent-strategies` + `cli-delegation` 267-276 + `progress-guards`) y en los agentes (regla neutral + tool-loading). Eso es exactamente lo que produjo el incidente: un orquestador que leyó la skill como si mandara usar los scripts.

---

## 2. Decisiones recomendadas

### (a) Dónde vive la regla de delegación de cada runtime y cómo se genera sin duplicar

**Hecho decisivo:** hoy no se puede instalar una referencia distinta por runtime sin cambiar el instalador, porque `install.sh:1036-1045` copia el **mismo** árbol de skills a las tres bases. La opción “referencia por runtime en la skill” queda descartada por evidencia, no por preferencia.

**Recomendación: opción A1 — la regla vive en el agente orquestador de cada runtime, generada desde una sección nueva `delegation` del adaptador fuente.**

- `sources/agents/adapters/opencode.md` suma `<!-- cdad-section:delegation -->` con: herramienta nativa `task`, `subagent_type: cdad-<role>`, mapeo rol→subagente, paso del paquete byte-idéntico, recibo, prohibición del adaptador dentro del runtime, declaración de familia por perfil, y las 4 reglas de contexto.
- `sources/agents/adapters/claude-code.md` suma la misma sección con `Agent` y sus diferencias (hooks ya declarados en `frontmatter`).
- `scripts/cdad-generate.py` deja de hardcodear el orden (812-828) y emite `sections["delegation"]` en `compose_orchestrator_agent`. `parse_source` ya admite secciones extra (`REQUIRED_ADAPTER_SECTIONS = ("frontmatter","permissions","tool-loading")`, `scripts/cdad-generate.py:64,107-153`), así que el cambio es aditivo y determinista.
- Las dos referencias de runtime se **retiran de la skill**: el núcleo pasa al agente; el detalle histórico/verificación (reload, `delegate` muerto, 429, provenance) se mueve a `docs/` como evidencia, no como texto instalable. `cli-delegation.md` se queda como contrato del adaptador, sin su regla 267-276.
- Costo: hay que actualizar los 6 tests acoplados de §1.5 (o repuntar su `CONSUMER` al nuevo dueño). Es trabajo real y debe estar en el plan de la feature.

**Alternativa A2** (si el dueño quiere que el detalle largo siga consultable en runtime): emitir un archivo de referencia *de capa runtime* junto a los agentes (`<root>/.config/opencode/…`, `<root>/.claude/…`) e instalarlo con `install.sh`. Es más fiel a “referencia por runtime”, pero agrega maquinaria de instalador y manifiesto; no la recomiendo para esta feature porque el orquestador necesita la **regla**, no la historia del canal `delegate`.

**Por qué no dejar todo en la skill con la regla neutralizada:** las referencias son intrínsecamente runtime-específicas; neutralizarlas las vuelve inútiles, y mantenerlas en la skill reproduce la ambigüedad del incidente.

### (b) Qué queda en `cdad-cycle` §4

Contenido recomendado (sin nombres de tools ni de runtimes):

1. **Principio:** cada rol se ejecuta en una sesión aislada; el orquestador decide **cómo** según lo que declare el agente de su runtime.
2. **Orden:** delegación nativa del runtime (si existe) → handoff a chat nuevo → inline declarado como último recurso con el costo de aislamiento dicho.
3. **Regla de adaptadores (criterio del dueño del ciclo de vida):** si el runtime es dueño del spawn, la espera, la recolección y la limpieza, el orquestador solo valida el resultado y **no** usa el adaptador; el adaptador existe para orquestar agentes de **otro** runtime o de un runtime **sin** delegación propia. Prohibido re-despachar dentro del mismo runtime por el adaptador.
4. **Invariantes de rol:** reviewer de familia distinta (garantizada por configuración cuando el perfil fija modelos; **declarada** cuando no — ver c); el test-writer nunca ve implementación; el worker no escribe `docs/.cdad-state.json`; la delegación no amplía autoridad ni alcance; una sesión separada **no** es sandbox.
5. **Spawn guard:** prohibido que un subagente spawnee sub-subagentes; el rechazo no se reintenta en bucle; se devuelve control con handoff.
6. **Recibo:** todo transporte termina en el mismo `receive` (enlace a `re-entry.md`, ver d).
7. **Paquete y re-entrada independientes del transporte** (explícito, plan §9).

**Sale de §4:** `task`, `delegate`, `Agent`, `sessions_spawn`, `subagent_type`, `opencode run`, PreToolUse hooks, y los punteros a las dos referencias por runtime.

### (c) Familia distinta del reviewer con perfil `basic`, sin fijar modelos

**Hecho:** con `basic`, los agentes no llevan `model:` (`sources/agents/adapters/claude-code.md:15-33`; `scripts/cdad-models.sh:34-39` devuelve vacío) y, en OpenCode, el modelo se resuelve por configuración de agente, no por llamada (`opencode-delegation.md:28-35`). Por eso `task` no puede garantizar familia, y el consumidor resolvió el problema usando el adaptador (causa medida en `execution.md:112-118`).

**Recomendación — declaración en tres partes, idéntica en cada orquestador:**

1. **Por perfil:** si el perfil/config fija modelos, la familia distinta se cumple por configuración; si el perfil es `basic`, **no está garantizada por el instalador** y el orquestador **no elige ni inventa un modelo**.
2. **Registro:** el intento registra `runtime`, `model_configured`, `model_reported`, `session` con `null`/`unknown` cuando no se observó (campos ya existentes: `project-execution.md:138-139`; `cli-delegation.md:107-108`), y el gate de review escribe “invariante no garantizado” en lugar de omitirlo (plan §9.4).
3. **Salida legítima:** si el dueño necesita la garantía ya, la vía es el **handoff a chat nuevo** donde **el usuario** elige el modelo; nunca el adaptador, nunca un modelo fijado por el orquestador.
4. **006-003** aporta el script que compara modelos efectivos y el diagnóstico de misma familia; 006-002 **no** lo implementa.

Con esto, un orquestador OpenCode `basic` tiene una respuesta única: despacha el reviewer por `task`; si no puede demostrar la familia, lo declara y no cambia de transporte.

### (d) Recibo con delegación nativa (`task`/`Agent`)

**Hecho:** `receive` solo acepta partes escenificadas (`source.kind == "staged-file"` en `.cdad/inbox`, `skills/cdad-cycle/scripts/cdad_result.py:238-240, 255-277`), y el protocolo de escenificación ya está escrito y se usó en todo 006-001 (`re-entry.md:14-68`, en especial 25-45). El adaptador hace lo mismo por su cuenta (`cli-delegation.md:105-106`).

**Recomendación:** declarar la **equivalencia de transporte** en `re-entry.md` (nueva subsección, ~8 líneas) y enlazarla desde §4 y desde la sección `delegation` de cada agente:

- nativo (`task`/`Agent`) → el rol devuelve **FINAL TEXT** en la misma sesión del orquestador;
- el orquestador escribe los bytes exactos en `.cdad/inbox` + `RESULT.json` (sin retipear, resumir ni regenerar) y corre `receive`;
- `validate-receipt` → `materialize` → `register-transition` (sin cambios);
- el recibo sigue `semantic_status: pending`: recibir no aprueba gate.

No hace falta CLI nueva ni tocar el adaptador. Es un enlace que hoy falta (plan §9: “el recibo en la delegación nativa, enlazado a `re-entry.md`”).

### (e) Disciplina de contexto del orquestador

**Dónde se escribe:**

- `sources/roles/orchestrator.md` (directiva/limites): las 4 reglas, en 4 líneas —
  1. orientarse **primero** con `cdad_packet.py status` (vista compacta, límite de bytes, falla cerrada: `orientation.md:14-38`), sin volcados de state/ledger/skill;
  2. rotar la sesión en **bordes de tarea** (`SKILL.md:288`, `continuity.md`), no a mitad de unidad;
  3. **no reparar por su cuenta**: si un rol devuelve algo roto o incompleto, se re-despacha al rol con el defecto nombrado; el orquestador no escribe scripts de reparación;
  4. **nunca `/tmp`** como canal ni workspace: usar `.cdad/inbox` para el recibo y el workspace declarado para temporales (consistente con `handoff-prompts.md:627`, “never /tmp/”).
- `skills/cdad-cycle/references/orientation.md` §1: es la dueña de la regla “vista primero, expansión condicional”; ahí se cita la rotación y el “no volcado”.
- `SKILL.md` §4/§Orchestrator flow: una frase que remita a (1)-(4), sin duplicar.

**Cómo se verifica:**

- Test de texto sobre `build/staging/agents/{opencode,claude-code}/cdad-orchestrator.md` (perfil `basic`) que exige los 4 conceptos y prohíbe `/tmp` en texto instalable;
- **límite honesto:** el test prueba que la regla existe, no que se cumple. La única evidencia de comportamiento es el transcript de la corrida real de (3), y es una muestra, no una garantía.

### (f) Tabla de modelos de `cdad-cycle` §2 bajo “modelos por configuración”

**Recomendación (sin invadir 006-003):**

- Eliminar de `SKILL.md` la columna “Model family” con identificadores concretos (líneas 67-75) y el párrafo de perfiles (línea 77).
- Reemplazar por una sola frase: *“El modelo de cada rol es el configurado en el runtime; esta skill no nombra modelos. La familia distinta del reviewer es una invariante: garantizada por configuración cuando el perfil fija modelos; verificada por configuración (006-003) y declarada cuando no.”*
- Quitar el ejemplo de modelo concreto de `handoff-prompts.md:515`.
- **No tocar:** `install.sh`, `scripts/cdad-models.sh`, ADR-007, el mapa de perfiles ni `model_for`/`models_note` (son de 006-003). La fuente del orquestador ya se declara simbólica (`sources/roles/orchestrator.md:170-173`); 006-003 vaciará las celdas.
- Tests: `tests/validate-consistency.sh:263-269` (F001) afirma hoy que SKILL.md y ambos orquestadores mencionan `--basic` y caveatean la invariante; al quitar el párrafo de perfiles hay que **reformular** ese assert, no borrarlo.

---

## 3. Criterios de aceptación verificables

| ID | Postcondición | Cómo se verifica |
|---|---|---|
| **AC-006-002-1** | Ningún texto **instalable de skill** nombra una herramienta de despacho de un runtime ni un modelo concreto en contexto de delegación | Test de texto (patrón de `test_005_010_t3_references.py:88-114`): prohibir `` `task` ``, `` `delegate` ``, `` `Agent` ``, `subagent_type`, `opencode run`, `sessions_spawn` y el regex de modelos en `skills/cdad-cycle/**` y `skills/cdad-epic/**`. **Ojo:** `context-meter.md` declara `task` como *dato de medición*; el test debe excluirlo explícitamente por ser contrato de lector, no instrucción |
| **AC-006-002-2** | Cada agente orquestador declara su mecanismo nativo, el mapeo rol→subagente y el paso del paquete byte-idéntico | Test sobre `build/staging/agents/<runtime>/cdad-orchestrator.md` con perfil `basic`: OpenCode exige `task` + `subagent_type`; CC exige `Agent` + `subagent_type`; ninguno exige el adaptador |
| **AC-006-002-3** | §4 de `cdad-cycle` conserva principio, orden, regla de adaptadores, invariantes de rol y spawn guard, sin nombres de runtime | Test de conceptos + test de ausencia (mismo patrón que AC-1) |
| **AC-006-002-4** | Un orquestador OpenCode `basic` resuelve el despacho del reviewer sin ambigüedad: despacha por `task`; no usa el adaptador; declara la familia no garantizada y registra el intento | Test de texto: la sección `delegation` del agente contiene (i) `task` como mecanismo, (ii) la prohibición del adaptador intra-runtime, (iii) la frase de perfil `basic` + “no garantizado” + registro. **Más la corrida real acotada de abajo** |
| **AC-006-002-5** | El recibo de la delegación nativa está enlazado: FINAL TEXT → `.cdad/inbox` → `receive` → `validate-receipt` → `materialize` → transición | Test de texto que exige el enlace desde §4 y desde la sección `delegation` hacia “Orchestrator materialization protocol” de `re-entry.md`; test unitario existente de `receive` sigue verde |
| **AC-006-002-6** | Las 4 reglas de contexto están en ambos orquestadores generados y no hay instrucción de `/tmp` en texto instalable | Test de texto sobre staging `basic` + grep de ausencia |
| **AC-006-002-7** | `make staging PROFILE=basic && make agents` es determinista/idempotente y `make validate` pasa con los tests de referencias actualizados | `make agents` dos veces + `diff`; `make validate`; suite focal de los 6 módulos de §1.5 |
| **AC-006-002-8** | Ningún cambio de esta feature toca instalador, `cdad-models.sh`, config de delegación ni el adaptador | `git diff --name-only` acotado a `skills/**`, `sources/**`, `agents/**`, `tests/**`, `docs/**` |

### Cómo probar AC-4 (el criterio del plan)

**Prueba 1 — texto (barata, determinista):** generar staging `basic` y afirmar sobre `agents/opencode/cdad-orchestrator.md`: (a) la herramienta de despacho nombrada es `task` con `subagent_type: cdad-<role>`; (b) una rama explícita para `basic` que dice “familia no garantizada por el instalador; el orquestador no fija modelo; se registra”; (c) prohibición explícita de `cdad_delegate.py`/`opencode run` para un despacho intra-runtime; (d) enlace al recibo.

**Prueba 2 — corrida real acotada (evidencia de comportamiento, no prueba):**
1. `make staging PROFILE=basic` + `install.sh` con raíz redirigida a un proyecto **descartable** (patrón de `tests/test_005_008_t3_acceptance.py:167-217`).
2. Preparar un paquete de reviewer con `cdad_packet.py prepare` sobre una feature descartable.
3. Dar al orquestador OpenCode una comisión de una línea (“despachá el reviewer de este paquete”) y **una sola** tarea.
4. Evidencia exigida del transcript: una llamada `task` con `subagent_type: cdad-reviewer`; **cero** invocaciones de `cdad_delegate.py`/`opencode run`; el texto final del reviewer escenificado en `.cdad/inbox` y `receive` con recibo `pending`.
5. Límite declarado: si el proveedor no responde (precedente `execution.md:168-170`), la corrida se declara bloqueada por ambiente y no se sustituye por un test de texto presentado como comportamiento.

---

## 4. Riesgos, fuera de alcance y desconocidos

**Riesgos**

1. **Acoplamiento de tests (alto):** mover/retirar las dos referencias rompe 6 módulos y 2 bloques de `validate-consistency.sh` (§1.5). Debe ser una unidad propia con sus tests actualizados en el mismo diff; si no, el “make validate pasa” del plan es inalcanzable.
2. **El consumidor no cambia solo (alto):** su handoff prescribe el adaptador y su config por familia (`execution.md:112-118`). Hasta que su dueño actualice el handoff, el incidente puede repetirse aunque CDAD quede correcto. Queda fuera de alcance por decisión del plan (§8), pero **debe declararse en el cierre**.
3. **Pérdida de detalle al retirar las referencias (medio):** reload/version/provenance son evidencia útil; se preservan en `docs/`, no se borran.
4. **Agentes instalados que no se actualizan (medio):** el instalador preserva conflictos (`execution.md:101-104`); un `cdad-orchestrator.md` editado por el dueño no recibe la regla. Declarar el paso de reinstalación.
5. **Tamaño del agente (medio):** componer todo el detalle runtime en el orquestador sube el costo de contexto; por eso la recomendación es núcleo compacto en el agente y detalle en `docs/`.
6. **Falso positivo del test de ausencia (bajo-medio):** “task” aparece en prosa legítima (“atomic task”); el oráculo debe apuntar a formas de herramienta (`subagent_type`, code-span, `Agent tool`), no a la palabra suelta.
7. **`basic` no puede garantizar la familia:** es el resultado honesto, no un defecto a esconder; si el dueño exige la garantía, la vía es configuración (006-003) o selección del usuario en un chat nuevo.

**Fuera de alcance (declarado)**

- Handoff y configuración del **consumidor** (lo actualiza su dueño).
- **006-003:** instalador siempre `basic`, plantilla de config de delegación, credencial del servidor, script de comparación de familias.
- **006-004:** tabla de decisiones vigentes.
- Runtimes nuevos y el adaptador de Claude Code (no existe; 005-004 lo dejó como incremento).
- Comportamiento del adaptador OpenCode (006-001 cerrada) y `cdad-models.sh`.

**Desconocidos / VERIFY**

- **VERIFY-1:** si OpenCode 2.0.27 acepta un parámetro `model` por llamada en `task`. La evidencia del repo dice que el modelo es por configuración de agente (`opencode-delegation.md:28-35`) y el incidente asume que `task` no garantiza familia; **no afirmar** lo contrario. Verificación: inspeccionar el esquema de la herramienta en una instalación aislada y registrar la observación.
- **VERIFY-2:** si `delegate` sigue siendo canal muerto en 2.0.27 (evidencia de un deploy anterior, `opencode-delegation.md:99-105`). La regla no debe depender de eso: el mecanismo nativo es `task`.
- **VERIFY-3:** si Claude Code aplica `model` por llamada bajo `basic` como *selección del usuario/config* y no como decisión del orquestador. Está observado (`docs/specs/005-004-claude-code-roles/t5-acceptance.md:17`; `adapters/claude-code.md:24-33`), pero la lectura “paso el valor configurado, no lo invento” es una decisión de política a confirmar en el brainstorm.
- **VERIFY-4:** impacto exacto en los 6 tests acoplados: hay que leer cada aserción al escribir el plan (no lo resolví en discovery; solo identifiqué los módulos y líneas).

---

## 5. Evidencia de esta ejecución

**Archivos modificados:** ninguno. **Commit:** ninguno (`HEAD = f2592c8`); `git status --porcelain` vacío antes y después.

**Comandos (solo lectura) y salida acotada:**

```
sha256sum docs/epics/epic-006-opencode-concurrency/plan.md docs/cdad-policy.json
→ b6a59502ff18b6a2826e7cf672b790630d988a597cd6b24213442922ee4f2e63  docs/epics/…/plan.md
→ f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711  docs/cdad-policy.json

git rev-parse HEAD → f2592c8…
git status --porcelain → (vacío)

ls skills/cdad-cycle/references/ → 24 archivos (incl. opencode-delegation.md, claude-code-delegation.md, cli-delegation.md, sub-agent-strategies.md, re-entry.md, context-meter.md)
find sources -type f → 7 fuentes de rol + 2 adaptadores
find agents/claude-code -type f → 11 agentes

grep -n 'task|delegate|Agent|standalone|model' skills/cdad-cycle/SKILL.md
→ 67-77 (tabla + perfiles), 152-162 (task/Agent), 243, 275, 462-466, 499-504
grep -n 'deepseek-v4|glm-5|qwen3|minimax|sonnet|haiku|opus' skills/cdad-cycle sources/roles
→ SKILL.md:69-77; claude-code-delegation.md:21-26; sub-agent-strategies.md:51; handoff-prompts.md:515

sed -n '1036,1045p' install.sh
→ install_skills(): el MISMO árbol se copia a OPENCODE_SKILLS_DIR, AGENTS_SKILLS_DIR y CLAUDE_CODE_SKILLS_DIR

grep -n 'REQUIRED_ADAPTER_SECTIONS|def compose_orchestrator_agent' scripts/cdad-generate.py
→ 64 REQUIRED_ADAPTER_SECTIONS = ("frontmatter","permissions","tool-loading")
→ 749-869 compose_orchestrator_agent (812-828: orden de delegación hardcodeado)

python3 skills/cdad-result.py receive --help → requiere --descriptor
grep -n 'staged-file|inbox' …/cdad_result.py → 238-240 (kind debe ser staged-file), 69/255-277 (.cdad/inbox)

python3 -c "state…" → active_epic=epic-006-opencode-concurrency, active_feature=006-002-delegation-by-layer, current_stage=discovery
ls docs/specs/006-002-delegation-by-layer → No such file (no existe spec: no la declaro)
```

**Nota de anonimización:** el informe usa rutas relativas al repo; no incluye rutas del dueño, endpoints, ids de sesión ni nombres de otros proyectos. No leí `tests/.sensitive-patterns.local` ni toqué `~/.claude`, `~/.config` ni servicios.

---

### Resumen para el orquestador

El hallazgo central es que **la skill contiene hoy el mecanismo de cada runtime en cinco lugares distintos** (SKILL §4, dos referencias, `handoff-prompts`, `sub-agent-strategies`, `cli-delegation` 267-276) mientras los agentes solo tienen una regla neutral. La corrección de capas no requiere scripts nuevos: requiere (i) una sección `delegation` por adaptador fuente compuesta en el orquestador, (ii) retirar las dos referencias de runtime de la skill, (iii) dejar en §4 el principio, la regla de adaptadores por dueño del ciclo de vida y las invariantes de rol, (iv) enlazar el recibo nativo a `re-entry.md`, y (v) aceptar que `basic` **declara** la familia no garantizada en vez de resolverla con un modelo o con el adaptador. El costo principal es el acoplamiento de 6 tests y `validate-consistency.sh`, y el riesgo residual es que el consumidor siga prescribiendo el adaptador hasta que su dueño actualice su handoff.
