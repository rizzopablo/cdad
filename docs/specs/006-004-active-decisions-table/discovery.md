He terminado el discovery. Aquí está el informe.

---

# Informe de rol — architect, discovery de `006-004-active-decisions-table`

**Paquete:** `006-004-active-decisions-table-architect-discovery-001` · **Contrato:** `approved-epic-plan` → `docs/epics/epic-006-opencode-concurrency/plan.md` (sha `d6da11db…`, verificado en `REQUEST.json` y en `docs/.cdad-state.json:active_packet`).
**Modo:** solo lectura. **Archivos modificados por esta sesión: ninguno.** No hay commit propio (el rol no escribe; ADR-003).
**Fuentes leídas:** `plan.md` §10 y §12, `execution.md` (§«Orden: 006-006 antes que 006-004», §«006-005: review», §«006-006: discovery y decisiones», cierre), `skills/cdad-cycle/packets/{common,roles,substages}/*`, `skills/cdad-cycle/scripts/cdad_packet.py` (render/validate/prepare), `cdad_result.py`, `assets/artifact-policy.json`, `assets/memory-bank-templates/*`, `assets/adr-template/ADR.md`, `references/{stage-1,stage-4,stage-5,re-entry,handoff-prompts,bootstrap}.md`, `SKILL.md`, `sources/roles/{architect,reviewer,scribe,orchestrator}.md`, `agents/cdad-reviewer.md`, `docs/adr/ADR-001…033`, `docs/systemPatterns.md`, `Makefile`, `install.sh`, `tests/validate-consistency.sh`, `tests/test_static_block_ceiling.py`, `tests/test_role_packet_render.py`, `tests/test_006_006_u1_draft_object_form.py`, `tests/test_003_002_t2_reviewfix.py`, `tests/test_006_005_u7_scribe_role_report.py`.

---

## 0. Resumen ejecutivo

1. **La sección no existe en ninguna superficie del producto.** `grep -rn "Decisiones vigentes" skills/ sources/ agents/ tests/ install.sh` → **0**. La plantilla del Memory Bank (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:1-50`) tiene 6 secciones H2 y ninguna es la tabla; la instancia viva (`docs/systemPatterns.md`, 885 líneas, 7 H2) tampoco. La tabla es una sección **nueva**, no una reorganización.
2. **El repo tiene 33 ADR (001–033) y ningún índice.** No existe `docs/adr/README.md` en este repo (la plantilla que lo crea sí existe: `assets/memory-bank-templates/adr-README.md`, y `references/bootstrap.md:66-83` la instala en proyectos nuevos). El índice que la plantilla ofrece es **una guía de cómo escribir ADR, no un índice de decisiones** — de ahí el problema que la enmienda 003 enuncia.
3. **El «estado» de los ADR no es derivable mecánicamente.** Medido sobre los 33 archivos: **22 Accepted/aceptado, 8 Proposed, 2 Superseded/Reemplazado (007→033; 008 *parcialmente*→033), 1 Verified (009)**, y **cuatro vocabularios y tres formatos distintos** (`- **Status**:`, `**Status:**`, `* Estado:`, `## Estado` como H2). El template declara un vocabulario de 4 (`assets/adr-template/ADR.md:3`) que el repo **no** respeta. ⇒ El estado de la fila **no puede derivarse de los ADR**: lo declara quien mantiene la tabla.
4. **Ningún ADR declara en forma estructurada a qué roles gobierna.** Los nombres de rol aparecen sólo en prosa (medido sobre los 33: 27 nombran al menos un rol; 6 no nombran ninguno). La columna «roles» de la tabla es **dato nuevo**, no un dato a copiar.
5. **El paquete es el único canal que hoy puede llevar las filas a todos los roles.** El alcance de lectura por defecto (`cdad_packet.py:1238-1248`) es: test-writer → `contract` + `tests`; implementer/reviewer/architect/scribe → `repository-read`. Para el test-writer, `docs/systemPatterns.md` **queda fuera del alcance de lectura** y un `--input docs/systemPatterns.md` sería **rechazado** (`cdad_packet.py:1030-1031`). ⇒ «dejar el archivo y que el rol lo lea» **no** cumple el requisito para todos los roles: las filas tienen que **viajar en el paquete**.
6. **El precedente exacto ya existe y es aditivo.** `request.plan_task` (opcional, `:870`) + `_plan_task_sections` (`:3796-3853`) emiten dos secciones **sólo cuando el campo está declarado**, y el render sin el campo es **byte-idéntico** (oráculo en `tests/test_006_006_u1_draft_object_form.py:432`). Ese es el molde para `## Decisiones vigentes`.
7. **El techo del bloque estático no aprieta.** Techo declarado: `CDAD_STATIC_BLOCK_LIMIT`, default **12000** bytes (`cdad_packet.py:1061-1079`; test `tests/test_static_block_ceiling.py`). Medido: máximo **3031** bytes (`reviewer/plan-review`), mínimo **1309** (`scribe/memory`); **holgura ≥ 8969 bytes** en todos los 14 pares rol/subfase.
8. **Hay una tensión real con «fuente única» que hay que declarar, no resolver de costado.** En la **ruta de paquete** el rol **no carga el skill** (directiva del rol: «Do not load or reload `cdad-cycle`… the packet is the execution contract»), o sea que **un puntero a `<skill-dir>/references/x.md` no es resoluble** por el rol en esa ruta. El texto canónico puede estar en un solo lugar del skill, pero la **obligación operativa** tiene que entrar por la superficie que sí viaja: el **cuerpo del agente generado** (`sources/roles/*.md` → `agents/*.md`) y/o el **bloque estático del paquete** (`packets/roles/*.md`).

---

## 1. Mapa técnico verificado

### 1.1 La plantilla del Memory Bank y dónde vive hoy la sección

| Elemento | Ubicación | Estado verificado |
|---|---|---|
| Plantilla del Memory Bank | `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:1-50` | 6 H2: *Layers and boundaries* (`:5`), *Code conventions* (`:15`), *Framework patterns* (`:29`), *Test conventions* (`:33`), *Tooling enforcement* (`:40`), *Project anti-patterns* (`:44`). **Sin sección de decisiones.** |
| Instancia viva del proyecto | `docs/systemPatterns.md` (885 líneas) | 7 H2: `:5` *Capas y boundaries*, `:23` *Convenciones de código*, `:45` *Patrones del framework*, `:82` *Palanca `write: ask`…*, `:864` *Convenciones de tests*, `:871` *Tooling enforcement*, `:877` *Anti-patrones del proyecto*. Los patrones por feature son **H3 bajo `:45`** (p. ej. `:656` *Forma declarada del objeto…*). **Sin sección de decisiones.** |
| Estructura que crea el bootstrap | `skills/cdad-cycle/references/bootstrap.md:66-83` | `docs/adr/README.md` «(brief guide on how to create ADRs)» + `docs/systemPatterns.md` desde la plantilla. **La plantilla del bootstrap no trae la sección de decisiones.** |
| Guía de ADR (plantilla) | `skills/cdad-cycle/assets/memory-bank-templates/adr-README.md` | Nombra **numeración y formato** (`ADR-NNN-title-in-kebab-case.md`, secuencial) y los **4 estados** (`Proposed`/`Accepted`/`Deprecated`/`Superseded by ADR-NNN`) + «Once **Accepted**, an ADR is not modified». **No es un índice**: no enumera los ADR del proyecto. |
| Convención del Memory Bank | `skills/cdad-cycle/SKILL.md:387-404` | Lista `docs/` (incl. `adr/`) y dice «Templates in `assets/`». **No nombra la tabla de decisiones.** |

**Consecuencia de diseño:** la sección debe existir **en la plantilla** (para proyectos nuevos) **y en la instancia viva** (para este proyecto). La plantilla está en inglés; la instancia viva en español. El título de la sección **no puede ser una dependencia del producto** si la tabla la mantiene el orquestador (no hay parser) — ver §3.

### 1.2 Los ADR del repo: numeración, estados y qué reemplaza a qué

- **33 archivos** `docs/adr/ADR-001-*.md` … `ADR-033-*.md`, numeración correlativa y sin huecos. **No existe `docs/adr/README.md`** en este repo ⇒ hoy el proyecto **no tiene índice de decisiones** (el problema literal de la enmienda 003: «El índice de un proyecto puede incluso afirmar que no hay decisiones»).
- **ADR-034 está reservado** por el plan §12.1 para el principio de general antes que específico; el repo ya lo declara dos veces: `docs/systemPatterns.md:650-654` y `:727-733` («el `ADR-034` está reservado por el plan del epic…»).

**Inventario de estados (medido, los 33):**

| Estado | n | ADR |
|---|---|---|
| Accepted / aceptado | 22 | 001, 002, 003, 004, 005, 006, 010, 011, 013, 014, 015, 017, 018, 019, 020, 021, 022, 023, 024, 031, 032, 033 |
| **Proposed** (no gobiernan) | 8 | 012, 016, 025, 026, 027, 028, 029, 030 |
| **Superseded / reemplazado** | 2 | **007 → ADR-033**; **008 → *parcialmente*→ ADR-033** (el resto sigue vigente) |
| Verified | 1 | 009 (que además dice «pasa a Verified tras los probes…») |

**Formatos de estado reales (4 vocabulario, 3 layouts):** `- **Status**: Accepted` (001, 002, 004-006, 010, 024, 031-033) · `**Status:** **Superseded** → **ADR-033**` (007) · `**Status:** **Verified** (…)` (008, 009) · `Estado: **Decisión metodológica aceptada…**` (011) · `* Estado: **aceptado** / **Aceptado**` (017-023) · `## Estado` + valor en la línea siguiente (012 «Propuesto (2026-10-02)», 013, 014, 015, 016 «Propuesto para aprobación del dueño»).

**Dos consecuencias duras:**
1. La columna «estado (vigente u obsoleto, y cuál lo reemplaza)» **no es derivable** de los archivos: hay que **declararla** en la tabla.
2. El binario «vigente/obsoleto» del plan **no cubre** los 8 *Proposed* (que no gobiernan nada) ni el caso *parcialmente reemplazado* de ADR-008 ⇒ hace falta una regla explícita (ver **Q1** en §5).

**«Qué reemplaza a qué»:** sólo dos relaciones explícitas en el repo: ADR-007 → ADR-033 (completa) y ADR-008 → ADR-033 (parcial, sólo la parte de perfiles/modelos). ADR-001 dice «superseded by ADR-005» en una nota (`:9`) — **una quinta relación no registrada en el campo de estado**. El resto no tiene relación de reemplazo.

**Roles que gobiernan:** no existe campo estructurado. Los roles aparecen en prosa (medido: 27 de 33 nombran al menos un rol; **6 no nombran ninguno**: 002, 012, 016, 018, 023). ⇒ la columna «roles» es **dato nuevo que el orquestador declara al aprobar el ADR**.

### 1.3 Quién mantiene el Memory Bank hoy (stage-5, re-entry, scribe, materialización)

| Pieza | Ubicación | Qué dice (literal) |
|---|---|---|
| El orquestador **no** actualiza el Memory Bank por su cuenta | `references/stage-5-merge.md:5-13` | «You do NOT update the Memory Bank on your own. You coordinate: 1. Verify full CI… 2. Emit handoff to the **scribe**… 3. Validate the drafts at re-entry. 4. Pass the drafts to the **user** for APPROVAL (non-delegable); you commit them after the approval.» |
| Qué entra al paquete del scribe | `references/stage-5-merge.md:36-47` | «Current Memory Bank (`projectbrief`, `activeContext`, `progress`, `systemPatterns`, `adr/`).» — **el `systemPatterns.md` ya viaja al scribe** |
| Re-entry del scribe | `references/stage-5-merge.md:49-51` y `references/re-entry.md:286-303` | «Three drafts present: activeContext entry, progress changes, ADR draft (or "no ADR suggested").» — **tres borradores; el `systemPatterns.md` NO está entre ellos** |
| Decisión sobre el ADR | `references/stage-5-merge.md:69-77` | Alta/media/baja confianza; «could someone in 6 months ask "why did we do X this way"?» |
| Aprobación y commit | `references/stage-5-merge.md:53-68` | Aprobación del usuario **indelegable**; el orquestador commitea `docs/**` con prefijo `docs(memory):` |
| Exit gate de stage 5 | `references/stage-5-merge.md:163-178` | Exige `docs/activeContext.md`, `docs/progress.md` y «If an architectural decision → new ADR in `docs/adr/`». **No exige nada de `docs/systemPatterns.md`** ⇒ hoy nadie está obligado a upkeepar la tabla |
| Anti-patrones | `references/stage-5-merge.md:190-195` | AP-7 «outdated Memory Bank», AP-8 «speculative or missing ADRs», AP-10 «delegating the Memory Bank APPROVAL to the LLM» |
| Procedimiento del scribe | `sources/roles/scribe.md:21-28` | Draft 1 `activeContext.md`, Draft 2 `progress.md`, Draft 3 ADR. **No declara un borrador de `systemPatterns.md`** — aunque el kind existe |
| Fila del contrato del scribe | `sources/roles/scribe.md:31-38` | «Memory Bank update drafts faithful to the evidence»; artefacto: «three Memory Bank drafts» |
| Materialización (el canal que hoy escribe `docs/systemPatterns.md`) | `skills/cdad-cycle/scripts/cdad_result.py:701-712` + `skills/cdad-cycle/assets/artifact-policy.json:13` | kind `scribe-systemPatterns` → destino **`docs/systemPatterns.md`** (archivo, no carpeta). CAS por `expected_previous_sha256` sobre el destino |
| Permiso de escritura del orquestador | `sources/roles/orchestrator.md:106-112` | «materialize the read-only roles' artifacts… and commit them (`git add docs/**` + `git commit`)». **El orquestador puede escribir `docs/**`** ⇒ puede mantener la tabla sin tocar el producto |
| Quién la commitea hoy | `git log -- docs/systemPatterns.md` | siempre con prefijo `docs(memory):` (últimos: `8fd6489` cierre 006-006, `cd31f79` 006-005, `43986e2` 006-003, `e4d17e3` 006-002, `6978709` 006-001) |

**Huecos verificados que la feature tiene que cubrir:**
- **(H1)** El exit gate de stage 5 no exige nada sobre `systemPatterns.md` ⇒ la tabla puede envejecer sin que nadie lo note.
- **(H2)** El procedimiento del scribe declara **tres** borradores; el `systemPatterns.md` no es uno de ellos ⇒ el canal de materialización del scribe puede **no** tocar la tabla (y el kind `scribe-systemPatterns` queda como una capacidad latente).
- **(H3)** **No existe ninguna operación de CLI ni clase de transición para la aprobación de un ADR.** `TRANSITION_CLASSES` = `delivery, advance, gate, closure, late-delivery, disposition` (`cdad_packet.py:5204-5205`); el state no tiene ningún campo de ADR (`keys` del state: `active_epic, active_feature, active_packet, approver, audit_status, current_stage, delegation_history, epic_features, epic_history, epic_stage, execution, hitl_delegation, last_updated, postconditions_status, review_status, stack, stage_history, tdd_substage, version`). ⇒ «agregar la fila al aprobarse un ADR» es, hoy, una **declaración de procedimiento** del orquestador (que ya tiene `docs/**` y el git), no una operación de producto.
- **(H4)** La **matriz de severidad del review ya contempla el ADR**: `references/stage-4-review.md:115-127` → «Boundary violation | Blocking | **Only if an ADR authorizes it**». El reviewer ya tiene el criterio; lo que no tiene es **el ADR a mano** ⇒ el remedy de 006-004 habilita una regla que ya existe.

### 1.4 El reviewer: fuente, substage, agente generado

| Pieza | Ubicación | Contenido verificado |
|---|---|---|
| Fuente canónica del rol | `sources/roles/reviewer.md` | `:13-19` consumidores (opencode, claude-code, orchestrator §2) + `legacy-loads: cdad-cycle only`; `:44-46` puntero al dueño canónico de la calibración; `:49-58` fila del contrato; `:69-80` convención de tests; `:82-92` delta odoo |
| Instrucción de rol en el paquete | `skills/cdad-cycle/packets/roles/reviewer.md:1` | 1 línea, 363 bytes: «Act as reviewer. Work read-only and assess the object the contract declares, with its declared form (spec or plan)…» |
| Substage `review` | `skills/cdad-cycle/packets/substages/reviewer-review.md:1` | 1 línea, **206 bytes**: «Review correctness, readability, architecture, security, performance, and contract compliance. Separate blocking findings, optional improvements, and abstentions…» |
| Substage `plan-review` | `skills/cdad-cycle/packets/substages/reviewer-plan-review.md:1` | 1 línea, **1767 bytes** — ya dice «its declared intention, **its constraints and applicable decisions**, the spec, the plan when one exists…». **«applicable decisions» ya está en el procedimiento y nada las entrega** |
| Agentes generados | `agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer.md`, `agents/claude-code/cdad-reviewer-odoo.md` | **Salidas declaradas**: `Makefile:1-18` (`make staging` → `scripts/cdad-generate.py`; `make agents` → copia) — «never edit them by hand» |
| Generador | `scripts/cdad-generate.py:65` (`REQUIRED_ROLE_SECTIONS`), `:76-77` (marcadores `cdad-section`), `:109-155` (parser, **PD-3: falla ruidoso** ante sección vacía/duplicada/texto fuera de sección) | La fuente de rol es editable; el agente es salida |
| Calibración de la review (dueño canónico) | `references/stage-4-review.md:5-54` | 8 reglas; `:8-10` «This section is the **single canonical owner**… the reviewer role source and any other consumer reference it and never copy it» |
| Qué recibe hoy el reviewer | `references/stage-4-review.md:66-82` | `:77` «Conventions (`AGENTS.md`, `CONTRIBUTING.md`, `docs/systemPatterns.md`)» — **el `systemPatterns.md` ya está en la entrada del reviewer**, y en la ruta de paquete su alcance de lectura es `repository-read` ⇒ puede leer `docs/systemPatterns.md` **y** `docs/adr/` |
| Superficie de materialización del dictamen | `cdad_result.py:699-700` + `artifact-policy.json:8-9` | `review`/`plan-review` → `docs/specs/<feature>/`; `semantic_status` siempre `pending`, `approval_effect` siempre `false` |

### 1.5 Cómo se compone hoy un paquete de rol — y por dónde podrían entrar las filas

**Render** (`skills/cdad-cycle/scripts/cdad_packet.py:1050-1122`), en orden:

| Paso | Ubicación | Hecho verificado |
|---|---|---|
| Fuentes estáticas | `:1053-1055` | exactamente 3: `packets/common.md` + `packets/roles/<role>.md` + `packets/substages/<role>-<substage>.md`, concatenadas con `\n` |
| Techo del bloque estático | `:1061-1079` | `CDAD_STATIC_BLOCK_LIMIT` (env), **default 12000** bytes; exceder ⇒ `PolicyError` con diagnóstico, sin salida mixta |
| Metadatos canónicos | `:1080-1093` | JSON `sort_keys`, con `instruction_sources` = **path + sha256** de cada fuente estática, más `policy` (snapshot + digest) y `path_policy` |
| Secciones fijas | `:1095-1122` | `## Contract` (con las líneas aditivas `form:`/`spec_path`/`spec_sha256`/`spec_version` de 006-006), `## Objective`, `## Inputs`, `## Read scope`, `## Write scope`, `## Invariants`, `## Expected output`, `## Evidence required` |
| **Precedente aditivo** | `:1113` → `_plan_task_sections` (`:3796-3853`) | Si el request **no** declara `plan_task` ⇒ devuelve `[]` ⇒ **render byte-idéntico**. Si lo declara ⇒ emite `## Task validation plan` + `## Applicable contract`, **leyendo el plan del proyecto en el momento del render** |
| `## Inputs` | `:1114-1115` | una línea por input: `- {path}: {purpose}` — **sólo ruta y propósito; el contenido no viaja** |
| Validación del request | `:846-879` | conjunto **cerrado** de campos requeridos + `optional = {"plan_task", "agent"}` (`:870`): cualquier clave desconocida se rechaza |
| Validación de `inputs` | `:1014-1031` | cada input es `{path, purpose}` exacto (`:1027`) y **su path debe estar dentro del alcance de lectura** (`:1030-1031`) |
| Alcances por defecto | `:1238-1248` | test-writer → `[contract, tests]`; implementer → `[repository-read]`; resto → `[repository-read]` |
| `prepare` | `:4778-5054` | arma el request desde flags (`:4983-5013`), `inputs` = contrato + `--input` (`:4999-5007`), `plan_task` opcional (`:5016-5017`); valida (`:5026`) y renderiza (`:5028`) |
| Flags de `prepare` | `:6706-6757` | `--role --substage --objective --input --read-scope --write-scope --invariant --expected-output --evidence --plan-task --contract-kind --contract-path --plan-version --object-kind --spec-path --spec-version` |
| Reemisión | `:6699-6705` | `render` / `validate-request` / `validate-packet` reconstruyen o verifican desde `REQUEST.json` |
| Invocación canónica del orquestador | `references/handoff-prompts.md:3-13` | una llamada escribe `REQUEST.json`, `PACKET.md` y el binding; el stdout se despacha **sin cambios** |

**Por dónde podrían entrar las filas — cuatro candidatas, y por qué dos no alcanzan:**

| Candidata | Mecánica | Por qué sí / por qué no |
|---|---|---|
| **A. Campo opcional del request + sección aditiva del render** | `request.current_decisions` (lista de filas) → sección `## Decisiones vigentes`; `[]`/ausente ⇒ **byte-idéntico** | **Sí.** Es el molde de `plan_task`/006-006. Las filas **viajan**; no depende del alcance de lectura del rol; verificable mecánicamente (que toda fila declarada nombre al rol del paquete) |
| **B. `inputs` + que el rol lea el archivo** | `--input docs/systemPatterns.md` | **No.** (i) el path debe estar en el alcance de lectura (`cdad_packet.py:1030-1031`) ⇒ para el test-writer (`contract`+`tests`) hay que **ampliar el alcance** o falla; (ii) el paquete **no lleva** las filas, sólo una ruta; (iii) el filtrado «las que me nombran» queda en el rol, no en el paquete ⇒ contradice el requisito y la necesidad del usuario |
| **C. Los canales de texto libre que ya existen** | `--objective` / `--invariant` | **技术上 sí, semánticamente no.** Cero código, pero sin sección (la aceptación del plan pide «un test de texto que fija **la sección**»), sin forma de verificar «las filas que nombran a este rol», y sobrecarga el canal de invariantes |
| **D. Que el CLI lea la tabla del proyecto en el render** | el render lee `docs/systemPatterns.md` y filtra por rol (precedente: `_plan_task_sections` lee el plan) | **Viable** y maximally general, pero mete **el formato de un documento de proyecto** dentro del producto (el CLI pasaría a parsear markdown). Contrasta con el patrón actual: el CLI verifica el **digest** del documento del proyecto sin conocer su formato (`cdad_packet.py:971-1002`) |

### 1.6 Los tests que fijan cada superficie

| Superficie | Test / validador | Qué fija |
|---|---|---|
| **Texto del producto (oráculo bash)** | `tests/validate-consistency.sh` (`:26-96` las aserciones: `assert_file_has`, `assert_file_not_has`, `assert_files_identical`, `assert_cmd_ok`, `assert_tree_not_has`; `:138-142` los 4 agentes reviewer; `:146-152` la tabla «How to read the references») | Es **el** lugar natural para «un test de texto que fija la sección y las dos responsabilidades» (aceptación del plan §10) |
| **Techo del bloque estático** | `tests/test_static_block_ceiling.py:1-60` | default 12000; techo bajado ⇒ error explícito sin salida mixta |
| **Composición del paquete** | `tests/test_role_packet_render.py:29-58` (matriz rol/subfase, extracción del bloque estático, delimitadores) | La forma del paquete y el bloque estático |
| **Aditividad del render** | `tests/test_006_006_u1_draft_object_form.py:32-46` y `:432` («the render without the new keys is byte_identical to this revision») | El precedente exacto de 006-004: campo opcional + sección aditiva |
| **`instruction_sources` con digest** | `tests/test_004_003_t2_plan_review.py:141-160` | El sha-pinning byte a byte de las 3 fuentes |
| **Secciones del paquete** | `tests/test_005_003_t6_packet_contract.py:747`; `tests/test_004_003_t1_reviewfix.py:167-169` | Presencia de `## Evidence required` / `## Inputs` (por presencia, no por conjunto exhaustivo ⇒ **una sección nueva no los rompe**) |
| **Materialización del Memory Bank** | `tests/test_003_002_t2_reviewfix.py:723-779` (R5: los 4 kinds del scribe → sus 4 archivos) y `tests/test_006_005_u7_scribe_role_report.py:151, :181` | Que `scribe-systemPatterns` ⇒ `docs/systemPatterns.md` (con CAS) |
| **`docs/systemPatterns.md` como superficie del proyecto** | `tests/test_004_002_t1_policy.py:368-373` (clase `documentation`); `tests/test_005_006_t5_acceptance.py:59, :112` (archivos del Memory Bank en el bootstrap) | Que el archivo sea del proyecto y exista tras el bootstrap |
| **Generación de agentes** | `tests/validate-consistency.sh:138-142` + `Makefile:11-18` | Que los agentes generados contengan lo que la fuente declara (nunca editados a mano) |
| **Instalabilidad** | `install.sh:363-378` | El árbol de `skills/cdad-cycle/` viaja **completo** (packets, references, scripts) ⇒ una reference nueva viaja sola, sin tocar el instalador |

### 1.7 Mediciones hechas (read-only, sin escrituras)

```
### M1 — la sección no existe en ninguna superficie del producto
$ grep -rn "Decisiones vigentes" skills/ sources/ agents/ tests/ install.sh | wc -l
0
### M2 — ADRs del repo
$ ls docs/adr/ | wc -l
33
$ ls docs/adr/README.md
ls: cannot access 'docs/adr/README.md': No such file or directory
### M3 — plantilla del Memory Bank (secciones)
5:## Layers and boundaries
15:## Code conventions
29:## Framework patterns
33:## Test conventions
40:## Tooling enforcement
44:## Project anti-patterns
### M4 — systemPatterns vivo (H2)
7   (7 H2 en 885 líneas)
### M5 — quién toca docs/systemPatterns.md
8fd6489 docs(memory): cierre 006-006 — Memory Bank, closure, evidencia W-1 desplegado
cd31f79 docs(memory): 006-005 Memory Bank y cierre
43986e2 docs(memory): close feature 006-003-… (Memory Bank aprobado por Pablo; ADR-033 reemplaza ADR-007)
e4d17e3 docs(memory): close feature 006-002-delegation-by-layer (…; ADR-032)
6978709 docs(memory): close feature 006-001-… (…; ADR-031)
### M6 — inventario de estados de los 33 ADR (parser sobre el head)
Accepted / aceptado    n=22  001,002,003,004,005,006,010,011,013,014,015,017,018,019,020,021,022,023,024,031,032,033
Proposed               n= 8  012,016,025,026,027,028,029,030
SUPERSEDED / REEMPLAZADO n= 2  007,008
Verified               n= 1  009
total ADR: 33
### M7 — bloque estático por rol/subfase (ceiling 12000)
  reviewer/reviewer-plan-review        3031  headroom=  8969
  implementer/implementer-green        1730  headroom= 10270
  implementer/implementer-review-fix   1714  headroom= 10286
  implementer/implementer-refactor    1641  headroom= 10359
  reviewer/reviewer-review             1470  headroom= 10530
  test-writer/test-writer-audit        1403  headroom= 10597
  architect/architect-discovery        1379  headroom= 10621
  test-writer/test-writer-post-audit   1366  headroom= 10634
  test-writer/test-writer-red          1342  headroom= 10658
  test-writer/test-writer-properties   1334  headroom= 10666
  test-writer/test-writer-e2e          1334  headroom= 10666
  architect/architect-brainstorm       1333  headroom= 10667
  architect/architect-draft            1327  headroom= 10673
  scribe/scribe-memory                 1309  headroom= 10691
  max = 3031  min = 1309
```

---

## 2. Escenarios del usuario real

Cada escenario: **paso → herramienta → salida esperada**. Los pasos de producto marcados *(a construir)* son los que 006-004 debe crear; el resto ya existe y está citado.

### E1 — Aprobar un ADR nuevo y que el siguiente paquete del rol nombrado lo lleve

1. El dueño aprueba el ADR (evento fuera del ciclo) y el orquestador lo commitea en `docs/adr/ADR-NNN-*.md` — **herramienta**: `git` (ya es su alcance: `sources/roles/orchestrator.md:106-112`).
2. *(a construir)* El orquestador **agrega la fila** a la sección «Decisiones vigentes» de `docs/systemPatterns.md` (archivo, estado `vigente`, resumen en una línea, roles que deben consumirla, referencia al archivo del ADR) y la commitea con prefijo `docs(memory):` — **herramienta**: edición + `git` (mismo canal que hoy usa para el Memory Bank).
3. *(a construir)* El orquestador prepara el siguiente paquete del rol nombrado declarando las filas que lo nombran: `cdad_packet.py prepare --project-root <root> --role <rol> --substage <subfase> --objective "…" [--current-decision …] *(flag a decidir; §3)* — **herramienta**: `skills/cdad-cycle/scripts/cdad_packet.py`.
4. El rol lee el paquete y aplica la decisión — **herramienta**: la sesión del rol (el paquete es el contrato).
5. **Salida esperada**: el `PACKET.md` del rol contiene una sección `## Decisiones vigentes` con la fila del ADR (archivo, estado, resumen, rol) y el informe del rol la cita (`file:line` del ADR). Si el rol no está nombrado, esa fila **no** está (E3).

### E2 — Reemplazar un ADR: el viejo aparece obsoleto y **no** se distribuye

1. Se aprueba `ADR-034` que reemplaza a `ADR-0XX`. El orquestador (a) marca la fila del viejo como `obsoleto (reemplazado por ADR-034)` **conservando la fila** (la historia importa) y (b) agrega la fila del nuevo como `vigente`.
2. *(a construir)* Al preparar el paquete, las filas **vigentes** que nombren al rol se declaran; la fila obsoleta **no** se declara entre las que viajan.
3. **Salida esperada**: el paquete del rol contiene la fila de `ADR-034` y **no** contiene la de `ADR-0XX`; la tabla del proyecto sí conserva la fila vieja con su estado y su sucesor ⇒ la historia no se pierde, la distribución se detiene. Si el paquete del rol se arma con la tabla completa, la fila obsoleta debe quedar **marcada** y fuera del conjunto «vigentes que lo nombran» (misma regla, dos posibles representaciones; ver §3 O1).

### E3 — Un rol no nombrado no lo recibe

1. La fila declara `roles: architect, reviewer`. Se prepara un paquete `test-writer`.
2. *(a construir)* La verificación mecánica: **toda fila declarada para un paquete debe nombrar al rol de ese paquete** ⇒ un paquete del test-writer no puede llevar la fila de `ADR-034`; y si la lleva, `prepare` falla nombrando el rol.
3. **Salida esperada**: el paquete del test-writer **no** contiene la fila; y, si el rol no tiene ninguna fila aplicable, el render es **byte-idéntico** al de hoy (INV-4 aditivo: sin sección, no una sección vacía).

### E4 — El reviewer detecta una tabla desalineada con `docs/adr/`

1. Una fila apunta a `docs/adr/ADR-099-lo-que-sea.md` que no existe, o un ADR en vigor no tiene fila.
2. El reviewer (read-only, alcance `repository-read` ⇒ puede leer `docs/systemPatterns.md` **y** `docs/adr/`) compara la tabla con el directorio de ADR.
3. **Salida esperada**: un hallazgo con `file:line` (la fila y el archivo real), `Verdict: BLOCKING` + `Bucket` (regla de observables de `references/verdict-tuple.md`) + consecuencia + **condición de cierre verificable** (regla 2 de la calibración: `references/stage-4-review.md:17-22`). **No es un gate duro** (fuera de alcance: «gates de cita obligatoria»): es un hallazgo, con la severidad que le corresponda por efecto real.

### E5 — Un proyecto sin ADRs

1. Proyecto nuevo: `docs/adr/` vacío (o sin la sección, porque el bootstrap copia la plantilla **sin** la tabla hasta que 006-004 la agregue) y la tabla vacía o ausente.
2. *(a construir)* `prepare` de cualquier rol.
3. **Salida esperada**: **rc=0**; el paquete **no** lleva la sección (sin filas ⇒ sin sección ⇒ render byte-idéntico); ninguna regla nueva bloquea a un proyecto que no adopts ADRs.

### E6 — Una decisión metodológica no está terminada hasta que su regla esté en el skill instalable

1. Se aprueba `ADR-034` (el principio de general antes que específico). La fila dice, además de la regla, **dónde vive**: p. ej. `skills/cdad-cycle/references/<archivo>.md` (§4).
2. La fila marca explícitamente que la decisión **no está terminada** mientras el archivo no exista en el árbol instalado.
3. **Salida esperada**: el paquete del architect y del reviewer **nombra el archivo del skill**; un revisor (o el propio rol) puede verificar que el archivo existe en la instalación (`install.sh:370-378` garantiza que `skills/cdad-cycle/` viaja completo). Si la regla aún no está en el skill, la fila lo dice y la decisión figura como **pendiente de instalación** — no como vigente.

---

## 3. Opciones de diseño para «el paquete de cada rol lleva las filas vigentes que lo nombran»

**Restricciones del plan (§10):** «Fuera de alcance: índices generados, gates de cita obligatoria y cambios en `status`.» Interpretación que propongo y que debe confirmar el dueño (**Q4**): *índices generados* = no se genera `docs/adr/README.md` como índice ni ninguna tabla derivada por herramienta; *gates de cita obligatoria* = el paquete no exige citar el ADR ni el reviewer tiene una puerta que la exija; *cambios en `status`* = no se toca el campo `**Status**` de los ADR ni el `status` de la máquina de estados (la columna «estado» de la tabla es una propiedad de la **fila**, que es el diseño del propio plan).

**Principio aplicado (enmienda 005):** la responsabilidad es **una**: «el rol recibe las decisiones que lo gobiernan». Se compara el costo de **especializar** (5 mecanismos, uno por rol) con el de **generalizar** (un mecanismo agnóstico al rol, con el rol como **dato** de la fila). Generalizar es aquí lo correcto: no hay 5 responsabilidades sino 1 con 5 Yelp.

### O1 — **General (recomendada):** un campo opcional en el request + una sección aditiva del render

- **Mecánica**: `request.current_decisions` (lista de filas: `file`, `state`, `summary`, `roles`, `reference`) → el render emite `## Decisiones vigentes` **sólo** si hay filas; `prepare` acepta un flag para declararlas; `validate_request` admite el campo como opcional (junto a `plan_task`/`agent`, `:870`) y **verifica mecánicamente** que toda fila declarada nombre al rol del paquete; la forma de la fila se valida (campos exactos, `file` existente, `roles` dentro del vocabulario de roles).
- **Costo**: 1 campo opcional + 1 flag + 1 sección + 1 verificación (mecánica) + ~1 test de texto + ~1 test de comportamiento. **Cero** cambios en `artifact-policy.json`, en la tabla de kinds, en el state, en el instalador.
- **A favor**: las filas **viajan** (requisito del plan y de la necesidad del usuario); no depende del alcance de lectura del rol (el caso test-writer); render byte-idéntico cuando no hay filas (INV-4, precedente 006-006); verificable.
- **En contra**: el **contenido** de las filas lo declara el orquestador ⇒ trabajo de LLM por paquete y sin garantía mecánica de que no falte una fila (la garantía es «la fila que se declaró nombra a este rol», no «toda fila vigente fue declarada»).

### O2 — **General:** que el CLI lea la tabla del proyecto en el render y filtre por rol

- **Mecánica**: el render lee `docs/systemPatterns.md` (o el archivo que la tabla ocupe), parsea la sección y filtra las filas cuyo `roles` incluye al rol del paquete. Precedente: `_plan_task_sections` ya lee el plan del proyecto en el render (`:3818-3819`).
- **Costo**: un parser del formato de la tabla **dentro del producto** + una dependencia del render respecto del archivo del proyecto + el fallo honesto cuando el archivo no existe (proyecto sin ADRs: sin sección).
- **A favor**: **garantía máxima**: nadie puede olvidar declarar una fila; el filtrado es determinista; el orquestador deja de ser el que selecciona.
- **En contra**: el producto pasa a conocer el formato de un documento de proyecto — rompe el patrón vigente (el CLI verifica el **digest** del documento sin conocer su formato, `:971-1002`); acopla el byte del paquete al estado de la tabla (cada cambio de la tabla cambia el paquete, sin que la tabla entre en la identidad del paquete); y **mezcla** el «vehículo» con el «mantenimiento»: el plan dice que el orquestador mantiene la tabla.

### O3 — **General:** las filas viajan en los canales de texto que ya existen (`--objective` / `--invariant`)

- **Costo**: **cero código**.
- **En contra**: no hay sección (la aceptación del plan pide un test que fije «la sección»); no hay forma de verificar «las filas que nombran a este rol»; el canal de invariantes se sobrecarga semánticamente; el orquestador selecciona a mano en cada paquete. **Queda como degradación**, no como diseño.

### O4 — **Específica:** la tabla como `--input` y que el rol la lea

- **Costo**: casi cero código.
- **En contra**: el path del input debe estar en el alcance de lectura (`:1030-1031`) ⇒ para el test-writer hay que **ampliar el alcance** (o falla); el paquete **no lleva** las filas; el filtrado «las que me nombran» pasa al rol. **Descartada** por no cumplir el requisito.

### Recomendación

**O1**, con **O2** como refuerzo opcional y **O3** como degradación.

El razonamiento, en línea con la enmienda 005:
- **General antes que específico**: un solo mecanismo, agnóstico al rol; el rol es un **dato** de la fila. O1 es la única que **no introduce una inferencia** (O2 no infiere, pero sí acopla el producto a un formato de proyecto; O4 infiere del alcance; O3 no estructura nada) y la única que **reutiliza el precedente establecido** (`plan_task`/`agent` como extensiones aditivas del request, con render byte-idéntico cuando el campo falta — `tests/test_006_006_u1_draft_object_form.py:432`).
- **El producto conoce la forma; el proyecto conoce el contenido.** La tabla es un documento del proyecto; el producto sólo valida la **forma** de cada fila y su coherencia con el rol del paquete. Así el reviewer's check y el del paquete comparten la misma verdad sin que ningún componente parseé markdown de proyecto.
- **Reparto de responsabilidades con las fronteras ya dibujadas**: el **orquestador** mantiene la tabla (ya tiene `docs/**` y el git; `sources/roles/orchestrator.md:106-112`) y **declara** las filas al preparar; el **CLI** verifica mecánicamente que toda fila declarada nombre al rol del paquete (fail-closed, nombrando la fila y el rol); el **reviewer** compara la tabla con `docs/adr/` y reporta el desalineo como hallazgo, no como puerta.
- **Costo delta O1 vs O2**: O1 cuesta una verificación mecánica y delega la completitud al orquestador; O2 compra completitud al precio de acoplar el producto a un formato. Recomiendo **O1** y, si el dueño quiere la completitud garantizada, **O2 como modo opcional y declarado** (no por defecto) — con la deuda de nombre declarada, como se hizo con `plan-review`/`draft-plan` (plan §13.6).

---

## 4. ADR-034: fuente única, referencias y tamaños

### 4.1 Dónde va la fuente única del principio

**Propuesta:** un archivo nuevo de referencia en el skill instalable —
`skills/cdad-cycle/references/design-principles.md` (§ «Principio de general antes que específico») — con **el texto del principio** (el bloque del plan §12) **y su límite** («no aumenta las justificaciones que los agentes deben producir») **en el mismo lugar**. El árbol `skills/cdad-cycle/` viaja completo al entorno instalado (`install.sh:370-378`), así que **no hace falta tocar el instalador**.

Se elige una *reference* y no `SKILL.md` porque: (a) el patrón del repo es exactamente ese — «dueño canónico único» en `references/` y puntero desde el rol (`sources/roles/reviewer.md:44-46`: «calibration owned by `references/stage-4-review.md`… not duplicated here»; y `references/stage-4-review.md:8-10`: «the reviewer role source and any other consumer reference it and never copy it»); (b) `SKILL.md` es el documento **siempre cargado** por el orquestador — meter ahí una regla de diseño para dos roles carga a todos.

**Y el ADR-034** (que lo redacta el architect y aprueba el dueño) apunta a ese archivo como la regla que lo materializa; la fila de la tabla lo referencia igual ⇒ el mecanismo de §10.1 (punto 4: «Una decisión que cambia la metodología de CDAD no está terminada hasta que su regla está en el skill o el agente instalable; la fila guarda la referencia») queda servido por la misma fila.

### 4.2 Cómo la referencian architect y reviewer **sin re-enunciarla**

Tres superficies, y sólo las que llegan al rol:

| Superficie | Archivo | Qué lleva | Por qué |
|---|---|---|---|
| **Cuerpo del agente** (se carga en **ambas** rutas: es el system prompt del rol) | `sources/roles/architect.md` (sección `directive` o `capacity`) y `sources/roles/reviewer.md` (sección `directive`) | **La obligación del rol** en una línea + **el puntero** al dueño canónico | Es el patrón vigente (`sources/roles/reviewer.md:44-46`). `make agents` la propaga a los 4 agentes reviewer y los 2 architect (`Makefile:11-18`) |
| **Bloque estático del paquete** (ruta de paquete) | `skills/cdad-cycle/packets/roles/architect.md`, `packets/roles/reviewer.md` | La **obligación mínima** + el puntero | En la ruta de paquete **no se carga el skill** ⇒ un puntero a `<skill-dir>/references/…` **no es resoluble** por el rol. El bloque estático sí viaja (y su digest viaja en `instruction_sources`) |
| **Tabla de referencias del skill** | `skills/cdad-cycle/SKILL.md:454-471` («How to read the references») | Una fila que dice cuándo cargar el archivo | Es la tabla que el validador ya mira (`tests/validate-consistency.sh:146-152`) ⇒ el puntero queda **verificable** |

**La regla de una sola casa, aplicada sin re-enunciar:**
- El **texto** del principio (el bloque del plan §12) + su **límite**: **una sola vez**, en el archivo de referencia.
- La **obligación del rol** (architect: «considera alternativas generales y específicas en las decisiones relevantes y explica el criterio elegido»; reviewer: «evalúa consecuencias reales: duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento; la falta de una abstracción, por sí sola, no es un defecto») — es **duty**, no principle: se declara en la fuente del rol (una línea cada una) y **no** es una copia del principio.
- La **referencia** al archivo canónico, en las tres superficies de arriba.

**Deuda que hay que declarar (no esconder):** en la **ruta de paquete** el rol no puede abrir el archivo de referencia si su alcance de lectura no lo cubre (`repository-read` cubre el proyecto, no el árbol instalado). Consecuencia honesta: el rol recibe la **obligación operativa** completa y la **fuente canónica** como dirección a seguir cuando pueda; la lectura íntegra del principio depende de que el rol alcance el skill — igual que hoy ocurre con el puntero a `references/stage-4-review.md` (mismo patrón, misma limitación ya aceptada en el producto). No es un defecto nuevo: es la consecuencia de un patrón vigente.

### 4.3 Tamaño del bloque estático por rol y techos

- **Techo declarado**: `CDAD_STATIC_BLOCK_LIMIT`, default **12000** bytes, adjustable por entorno (`cdad_packet.py:1061-1079`); oráculo: `tests/test_static_block_ceiling.py`; efecto: exceder ⇒ `PolicyError` con diagnóstico y **sin salida mixta** (no se publica un paquete truncado).
- **Medición de los 14 pares rol/subfase** (M7, arriba): máximo **3031** (`reviewer/plan-review`), mínimo **1309** (`scribe/memory`), **holgura mínima 8969 bytes**.
- **Presupuesto de la feature**: la referencia canónica del principio **no va** al bloque estático (va al archivo de referencia). Al bloque estático van: (a) un puntero en `packets/roles/architect.md` (hoy 224 bytes) y en `packets/roles/reviewer.md` (363 bytes) — **+~150-300 bytes cada uno** ⇒ el peor caso (reviewer/plan-review) pasa a ≈**3300 bytes**, muy por debajo del techo; (b) nada en `common.md` (901 bytes), porque el principio no es de todos los roles (el test-writer no lo necesita y cargar la tabla de decisiones a todos los roles sería el error de «especializar al revés»).
- **La tabla en el paquete** (las filas) **no** va por el bloque estático: va por la sección aditiva del render, que no tiene techo propio (el techo es sólo del bloque estático). **Presupuesto a vigilar**: si un rol acumulara 20 filas de ~200 bytes, son ~4 KB por paquete ⇒ conviene un tope declarado por paquete (nº máximo de filas) para que la tabla no crezca sin control. **Es una decisión de diseño que propongo** (tope de filas por paquete, fail-closed con diagnóstico), no un hecho medido.

---

## 5. Preguntas abiertas (solo el dueño puede decidir)

| # | Pregunta | Por qué es del dueño | Recomendación del architect |
|---|---|---|---|
| **Q1** | **¿Qué entra en la tabla: sólo las decisiones en vigor?** El binario del plan («vigente u obsoleto») no cubre 8 ADR **Proposed** (012, 016, 025-030 — que no gobiernan nada), ni el caso **parcialmente** reemplazado de ADR-008, ni el ADR-009 «Verified» | Es el alcance de la tabla: define qué se distribuye y qué el reviewer compara | Filas **sólo** para las decisiones en vigor (Accepted/Verified) + las reemplazadas marcadas `obsoleto (reemplazado por ADR-NNN)`. Los **Proposed no son filas** (no gobiernan) ⇒ el reviewer's check es «toda decisión en vigor tiene fila», no «toda decisión tiene fila». **No** re-clasificar el `**Status**` de los ADR (fuera de alcance) |
| **Q2** | **¿Quién decide qué roles gobiernan cada decisión?** Ningún ADR lo declara en forma estructurada (27 de 33 nombran roles sólo en prosa; 6 no nombran ninguno) | Es un criterio de gobernanza del proyecto, no de mecánica | Quien aprueba el ADR declara los roles **en el momento de la aprobación** (la fila se crea ahí) ⇒ no hay un paso de re-clasificación de los 33 ADR. El reviewer **no** juzga si la asignación de roles es la correcta: verifica que los roles nombrados existan (vocabulario cerrado) ⇒ como máximo un hallazgo **opcional** |
| **Q3** | **¿Esta feature siembra la tabla de este repo?** El plan dice «una fila por ADR» (33) y que ADR-034 es la **primera fila**; la aceptación sólo menciona «plantilla y referencias actualizadas» | Define el tamaño del trabajo y si la tabla arranca poblada o vacía | Sembrar **con la primera fila (ADR-034)** + el resto de las decisiones **en vigor** que el orquestador pueda justificar con evidencia (no las 33 de un tirón: 8 son Proposed). Declarar en el informe de la feature cuántas filas quedan fuera y por qué |
| **Q4** | **¿A qué `status` se refiere «cambios en `status`» (fuera de alcance)?** | Cambia el alcance materialmente | Que se refiera al campo `**Status**` de los ADR **y** al `status` de la máquina de estados: la feature **no** normaliza el vocabulario de estado de los ADR (ni agrega campos ni estados), y el «estado» de la tabla es una propiedad de la **fila**, que es el diseño del propio plan. Confirmar, porque la lectura alternativa («no cambiar el `status` del state») es la misma en la práctica y la del ADR es la que tiene consecuencias |
| **Q5** | **¿Nombre y ubicación de la sección en la plantilla?** La plantilla está en inglés y la instancia viva en español; el plan la nombra «Decisiones vigentes» | Es una convención visible del proyecto, no una mecánica | Que el **título no sea una dependencia del producto** (la tabla la mantiene el orquestador; el CLI no la parsea) ⇒ título libre. Recomendación: la plantilla (inglesa) usa `## Current decisions`; este repo usa `## Decisiones vigentes` (como nombra el plan) y la ubica como **primer H2**, después de la intro (es la parte corta y siempre relevante; el resto es profundidad) |
| **Q6** | **¿La tabla se mantiene sólo al aprobar un ADR, o también en el cierre de cada feature?** El exit gate de stage 5 no menciona hoy `docs/systemPatterns.md` (`references/stage-5-merge.md:163-178`) y el procedimiento del scribe declara **tres** borradores, ninguno de ellos el `systemPatterns.md` (`sources/roles/scribe.md:21-28`), aunque el kind de materialización existe (`artifact-policy.json:13`) | Es el reparto entre dos superficies (producto vs proyecto) y decide si el gate de stage 5 cambia | La feature **no** cambia el exit gate de stage 5 (eso es alcance de otra feature); en cambio, el **orquestador** mantiene la tabla en el evento «ADR aprobado» — que es un evento de **aprobación**, no de cierre — y el `systemPatterns.md` sigue entrando al paquete del scribe como hoy (`stage-5-merge.md:45`), por si el scribe lo actualiza. **Declarar** que la tabla tiene dos writers (orquestador en la aprobación; scribe opcionalmente en el cierre) y que el orquestador es el que resuelve el conflicto por CAS (`cdad_result.py` materializa con `expected_previous_sha256`) |

**No pregunto** (ya resuelto y verificado): el **orden** de la feature (006-005 → 006-006 → 006-004, `execution.md:362-364`); que **ADR-034 está reservado** (plan §12.1 + `docs/systemPatterns.md:650-654`, `:727-733`); que la sección **no existe** hoy en ninguna superficie (medido, 0 ocurrencias); que el **techo** del bloque estático es 12000 y no aprieta (medido, holgura ≥ 8969); que el **test de texto** que pide la aceptación vive en `tests/validate-consistency.sh` (el validador bash del repo) — y que un test de comportamiento del render va en pytest, como los de 006-006.

---

## 6. Verificaciones pendientes (VERIFY) y deudas que registrar

- **VERIFY (no verificado, no inventado):** cualquier **API o flag nuevo** que la feature use (`--current-decision`, `request.current_decisions`, `## Decisiones vigentes`, el nombre del archivo de referencia del principio) **no existe hoy** — son propuestas de diseño de este informe, no superficies verificadas. No las uso como hechos en ningún punto.
- **Deuda a declarar en la spec de la feature:**
  1. **D-1 — el bloque estático no tiene dueño de las filas.** La sección del render es aditiva; la *población* depende de que el orquestador declare las filas ⇒ completitud no garantizada mecánicamente (y por eso la alternativa O2 queda sobre la mesa).
  2. **D-2 — el puntero a la referencia del principio no es resoluble en la ruta de paquete** (el rol no carga el skill). Misma limitation que el puntero vigente a `references/stage-4-review.md`.
  3. **D-3 — el estado de los ADR no es uniforme** (4 vocabularios, 3 layouts, 8 Proposed, 1 parcialmente reemplazado) ⇒ la tabla **no** puede derivarse de los archivos y la comparación del reviewer es contra el conjunto que la propia tabla declara, no contra una re-derivación.
  4. **D-4 — no hay operación de CLI ni clase de transición para la aprobación de un ADR** ⇒ «agregar la fila al aprobarse un ADR» es procedimiento del orquestador, no estado verificable por el producto.
  5. **D-5 — el exit gate de stage 5 y el procedimiento del scribe no mencionan `docs/systemPatterns.md`** ⇒ la tabla tiene un solo writer declarado (el orquestador) y el kind `scribe-systemPatterns` queda como capacidad latente.
  6. **D-6 — el paquete puede crecer sin tope** si la tabla crece ⇒ hace falta un tope declarado de filas por paquete (decisión de diseño propuesta en §4.3).

---

## 7. Evidencia

**Archivos modificados por esta sesión: ninguno.** (Rol read-only; `write_scope: []` en el paquete.) `git status --short` al cierre:

```
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

> Las tres entradas no versionadas y la modificación del state **preexistían** a esta sesión (las dejó la preparación del paquete: commit `1880824 docs(state): 006-004 discovery preparado`); esta sesión no los tocó.

**Comandos ejecutados (solo lectura):**

```bash
# contrato y estado
git status --short && git log --oneline -3 && git branch --show-current
python3 -c "import json; s=json.load(open('docs/.cdad-state.json')); …"   # active_feature, active_packet, epic_features
ls docs/epics/epic-006-opencode-concurrency/ && wc -l docs/epics/epic-006-opencode-concurrency/*.md
sed -n '270,352p' docs/epics/epic-006-opencode-concurrency/plan.md
sed -n '238,277p;355,397p' docs/epics/epic-006-opencode-concurrency/execution.md

# superficie del Memory Bank
grep -n "^## " skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md
grep -n "^## " docs/systemPatterns.md && wc -l docs/systemPatterns.md
cat skills/cdad-cycle/assets/memory-bank-templates/adr-README.md
cat skills/cdad-cycle/assets/adr-template/ADR.md
ls docs/adr/ | wc -l ; ls docs/adr/README.md

# inventario de estados de los 33 ADR (parser sobre el head de cada archivo)
python3 - <<'PY'   # 22 Accepted / 8 Proposed / 2 Superseded / 1 Verified
PY
for f in docs/adr/ADR-*.md; do … head -20 | grep -i -E 'Status|Estado' … ; done

# paquete
grep -n "def render_packet\|def prepare\|def validate_request\|def _plan_task_sections\|def _default_scopes\|ROLE_SUBSTAGES\|TRANSITION_CLASSES" skills/cdad-cycle/scripts/cdad_packet.py
sed -n '1046,1122p;1238,1248p;3796,3853p;4778,5054p;6690,6760p' skills/cdad-cycle/scripts/cdad_packet.py
grep -rn "scribe-systemPatterns" skills/cdad-cycle/assets/artifact-policy.json skills/cdad-cycle/scripts/cdad_result.py
grep -n "## \|Legacy path\|Do not load" sources/roles/{architect,reviewer,scribe,orchestrator}.md

# bloque estático y techos
wc -c skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/*.md skills/cdad-cycle/packets/substages/*.md
python3 - <<'PY'   # suma por par rol/subfase vs. techo 12000
PY
grep -rn "CDAD_STATIC_BLOCK_LIMIT" skills/ tests/ build/

# superficie de la sección
grep -rn "Decisiones vigentes" skills/ sources/ agents/ tests/ install.sh | wc -l    # → 0

# tests
grep -rn "instruction_sources" tests/*.py
sed -n '1,60p' tests/test_static_block_ceiling.py
sed -n '26,96p' tests/validate-consistency.sh
sed -n '1,46p;432,440p' tests/test_006_006_u1_draft_object_form.py
git log --oneline -6 -- docs/systemPatterns.md
```

**Salidas destacadas (verbatim):**

```
### M1 — la sección no existe en ninguna superficie del producto
0
### M2 — ADRs del repo
33
ls: cannot access 'docs/adr/README.md': No such file or directory
### M6 — inventario de estados de los 33 ADR
Accepted / aceptado      n=22  001,002,003,004,005,006,010,011,013,014,015,017,018,019,020,021,022,023,024,031,032,033
Proposed                 n= 8  012,016,025,026,027,028,029,030
SUPERSEDED / REEMPLAZADO n= 2  007,008
Verified                 n= 1  009
total ADR: 33
### M7 — bloque estático por rol/subfase (ceiling 12000)
  reviewer/reviewer-plan-review        3031  headroom=  8969
  architect/architect-discovery        1379  headroom= 10621
  scribe/scribe-memory                 1309  headroom= 10691
  max = 3031  min = 1309
```

**Commit:** **ninguno** — el rol architect es read-only y no escribe (ADR-003); el artefacto de esta sesión es este texto final, que el orquestador materializa en `docs/specs/006-004-active-decisions-table/discovery.md` y registra como entrega.