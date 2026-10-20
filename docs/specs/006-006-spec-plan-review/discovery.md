He terminado el discovery. Aquí está el informe.

---

# Informe de rol — architect, discovery de `006-006-spec-plan-review`

**Paquete:** `006-006-spec-plan-review-architect-discovery-001` · **Contrato:** `approved-epic-plan` → `docs/epics/epic-006-opencode-concurrency/plan.md` (sha `d6da11db…`, verificado en `REQUEST.json` y en `docs/.cdad-state.json:active_packet`).
**Modo:** solo lectura. **Archivos modificados por esta sesión: ninguno.** No hay commit propio (el rol no escribe).
**Fuentes leídas:** `plan.md` §13, `proposal-006-006-spec-plan-review.md`, `execution.md` (§«Evidencia para 006-006», §«Orden: 006-006 antes que 006-004»), el CLI (`cdad_packet.py`, `cdad_result.py`, `cdad_dispatch.py`), los paquetes/subfases/referencias del skill, `sources/roles/*`, los agentes generados, `artifact-policy.json`, los schemas, ADR-013, ADR-013-consumer, la spec de 004-003 (§G1–G5), los tests de 004-003/005-007/006-005 y los paquetes reales de `plan-review` de 006-005.

---

## 0. Resumen ejecutivo

1. La capacidad existe y está instalada: `draft-plan` + `plan-review` son kinds de primera clase (`cdad_packet.py:52-53`, `:64`), con pairing bidireccional (`:909-919`), sin requisito de aprobación (`:1604-1609`), y con el dictamen materializable como `plan-review.md` (`artifact-policy.json:9`; `cdad_result.py:699-700`).
2. **No está en el recorrido principal**: `grep` da **0 ocurrencias** de `plan-review`/`draft-plan` en `agents/`, `sources/`, `skills/cdad-cycle/SKILL.md`, `references/stage-2-specification.md`, `references/re-entry.md` y `references/stage-4-review.md`. El gate 2→3 (`SKILL.md:339-346`) y el exit gate de Stage 2 (`stage-2-specification.md:176-185`) no la nombran.
3. **La barrera mecánica real es más estrecha de lo que se cree**: el CLI no exige *tareas*, exige la **presencia del token ```` ```plan-tasks ````** (`cdad_packet.py:3362-3365`). Medido: `{"tasks": []}` **pasa** las tres validaciones. El problema no es “el plan-tasks obliga a inventar tareas”; es que **el objeto está modelado como un plan**.
4. El objeto revisado **hoy solo puede ser un plan**: `--contract-path` acepta cualquier ruta del proyecto (ADR-013:60-61, deuda O-C), pero cualquier objeto sin bloque `plan-tasks` es rechazado. Verificado empíricamente (§1.7).
5. Las tres razones del rechazo en el proyecto consumidor son **correctas y mecánicas**: (a) el contrato por defecto del reviewer es `approved-feature-spec` → `docs/specs/<feature_id>/spec.md` (`cdad_packet.py:1139`, `:937-938`); (b) un `approved-epic-plan` **no** es admisible para el reviewer (`:920-940`); (c) `plan-tasks` ausente ⇒ `prepare` rc≠0.

---

## 1. Mapa técnico verificado

### 1.1 El contrato del paquete del reviewer (superficie `prepare`)

| Elemento | Ubicación | Estado |
|---|---|---|
| Enum de contract-kinds | `skills/cdad-cycle/scripts/cdad_packet.py:52-53` | `approved-epic-plan`, `approved-unit-contract`, `approved-feature-spec`, `draft-plan` |
| Par rol→subfases | `cdad_packet.py:60-66` (`:64` → `"reviewer": {"review", "plan-review"}`) | `plan-review` ya es subfase de primera clase |
| Objeto `contract` del request | `cdad_packet.py:879-884` (`contract_keys = {kind, path, sha256, commit}` + `plan_version` opcional) | `plan_version` es **la** extensión aditiva existente |
| Guarda de forja | `cdad_packet.py:890-898` | `draft-plan` exige `plan_version` no vacío; un kind aprobado **no** puede declararla |
| Pairing bidireccional | `cdad_packet.py:901-919` | `draft-plan` ⇔ `plan-review`, sólo `reviewer`; ambas escapes se rechazan antes de publicar |
| Par kind/ruta por rol | `cdad_packet.py:920-942` | architect: `approved-epic-plan` \| `approved-unit-contract`; **cualquier otro rol: exactamente `approved-feature-spec` + `docs/specs/<feature_id>/spec.md`** (`:937-938`) |
| Contrato por defecto | `cdad_packet.py:1126-1139` (`:1139`) | el reviewer deriva a la spec aprobada de la feature activa |
| Verificación de digest | `cdad_packet.py:945-950` | `contract.sha256` debe igualar el sha256 del archivo **verificado en ese momento** |
| Sin requisito de aprobación | `cdad_packet.py:1604-1609` (`_contract_approval_for`) y `:1678-1679` | `draft-plan` corta antes: revisar no exige spec aprobada |
| Superficie CLI | `cdad_packet.py:4671-4699` (triple obligatoria `:4678-4682`; `draft-plan` reviewer-only `:4693-4696`; flags `:6409-6413`) | `--contract-kind` + `--contract-path` + `--plan-version` |
| **Puerta `plan-tasks`** | `cdad_packet.py:4710-4721` → `_plan_tasks_from_contract` `:3347-3388` | **solo** si `is_declared_draft` |
| Checks estructurales del plan | `_check_plan_tasks` `:3391-3506`; `_check_plan_validation_plan` `:3509-3584` | productor/consumidor, ciclos, contrato incompatible, paralelismo, plan de validación por tarea |
| `purpose` del input | `cdad_packet.py:4790-4792` | literal fijo **“draft plan for review”** (o “approved contract”) |
| Binding en el state | `cdad_packet.py:4808-4811` | `active_packet.contract_kind` + `contract_sha256` |
| Ruta del plan por feature | `cdad_packet.py:3593` (`PLAN_RELPATH_TEMPLATE`) | `docs/specs/{feature_id}/plan.md` |

**Punto ciego verificado:** `--contract-path` de un `draft-plan` **no** está atado a la feature activa ni a la carpeta `docs/specs/<feature>/`; `_project_path` (`:199-213`) solo garantiza que esté dentro de la raíz del proyecto. ADR-013:60-61 ya lo declara como deuda (O-C). **Es la raíz de la ambigüedad (a).**

### 1.2 El procedimiento `reviewer-plan-review.md`

- Fuente única: `skills/cdad-cycle/packets/substages/reviewer-plan-review.md:1` — una sola línea,currently redactada para **un plan**: *“Review a PLAN DRAFT — its declared intention, its constraints and the plan object — not only the spec.”*
- Se compone como `substages/reviewer-plan-review.md` en el paquete, con `instruction_sources` = `common.md` + `roles/reviewer.md` + el substage, sha-pinned byte a byte (`tests/test_004_003_t2_plan_review.py:141-160`).
- Regla de rol que decide “qué revisar”: `skills/cdad-cycle/packets/roles/reviewer.md:1` — *“assess the object the contract declares: the complete diff against the approved contract for approved contracts, the plan draft for `draft-plan`”*. **Es plan-céntrica**: no contempla un objeto spec.
- Plantilla de invocación (3 flags obligatorias): `skills/cdad-cycle/references/handoff-prompts.md:543-568`.
- Proporcionalidad: dueño canónico único `skills/cdad-cycle/references/stage-4-review.md:5-54` (“Review calibration”), referenciado por el rol (`sources/roles/reviewer.md:40-42`) y nunca copiado.
- Declarado en `skills/cdad-cycle/references/project-execution.md:92-93`: el `draft-plan` “carries no approval requirement”.

### 1.3 Recepción y materialización del kind `plan-review`

- Tabla cerrada rol/subfase→kind: `skills/cdad-cycle/scripts/cdad_result.py:681-700` — `:699-700`: `reviewer` → `{substage}` si es `review` o `plan-review`.
- Tabla cerrada kind→destino: `skills/cdad-cycle/assets/artifact-policy.json:9` → `plan-review` ⇒ `docs/specs/<feature>/`.
- `_allowed_target` (`cdad_result.py:672-678`) + `_is_within` (`:934-937`): **el dictamen solo puede materializarse en la carpeta de la feature del recibo** (= la feature activa de la ejecución). No puede ir a la carpeta de otra feature.
- `semantic_status` siempre `pending` (`:624`, `:880-882`); `approval_effect` siempre `false` (`:737-739`): **materializar nunca aprueba**.
- CAS de materialización: `expected_previous_sha256` (`:753-757`, `:822-852`) — protege **el destino**, **no el objeto revisado**.
- Derivación del kind en la vía de despacho: `skills/cdad-cycle/scripts/cdad_dispatch.py:908-925` → `reviewer/plan-review` ⇒ kind único `plan-review`. El camino de entrega ya cierra.
- **Deuda viva (D-ADP-3, `execution.md:255`)**: por la vía del adaptador el dictamen llegaba como `role-report` y `materialize` lo rechazaba; el orquestador lo copiaba a mano. 006-005 lo corrige con el kind derivado (PD-23) — `tests/test_006_005_u2_opencode_module.py:1378-1392`.

### 1.4 El gate spec→TDD (lo que falta)

- `skills/cdad-cycle/SKILL.md:339-346` — Gate 2→3: spec + 4 secciones + postcondiciones + criterios + marca de aprobación + plan si es complejo. **Ninguna línea sobre revisión independiente.**
- `skills/cdad-cycle/SKILL.md:293-319` — mapa del ciclo: la flecha Stage 2→Stage 3 dice literalmente `(gate: spec.md approved by the user)` (`:299`).
- `skills/cdad-cycle/references/stage-2-specification.md:176-185` — exit gate Stage 2→3: **no** menciona revisión de borrador. El recorrido (`:9-14`, `:42-44`) va brainstorm → spec draft → aprobación.
- El único self-review existente es **del plan** y vive bajo “Planning for complex features” (`stage-2-specification.md:160-164`) — para una feature mediana (spec sin plan) **no hay ni self-review**.
- `skills/cdad-cycle/references/re-entry.md:148-172` — re-entry “Architect — spec draft”: valida el draft y lo pasa directo a aprobación (`:159-161`). **Es el punto exacto donde debería encajar la revisión.**
- Espejo disponible: Gate 4→5 (`SKILL.md:361-366`) exige `review.md` + bloqueantes resueltos o descartados con razón escrita — **el modelo exacto del gate supervisado que pide el plan §13.4**.
- “Cambios de procedimiento, no gates nuevos”: `docs/specs/004-003-planning-procedures/spec.md:82-92` (tabla G1–G5; **G4** = “Subfase de revisión de plan + contract-kind de borrador”, fuente canónica el CLI + `packets/substages/reviewer-plan-review.md`; consumidores a reconciliar: **sólo** `packets/roles/reviewer.md` y la plantilla de `handoff-prompts.md`). Ni `stage-2`, ni `SKILL.md`, ni `re-entry.md` eran consumidores — de ahí el hueco.
- El estado no representa “borrador bajo revisión”: vocabulario de etapas `discovery|specification|tdd|review|merge|idle` (`cdad_packet.py:4685` vía `state-detection.md:24`); sin stage nuevo, la representación es **artefacto + recibo** (como `review.md` en Gate 4→5).

### 1.5 Los agentes generados y las fuentes de rol

- `sources/roles/reviewer.md:16` — `legacy-loads: cdad-cycle only`; `:46-48` — la fila del contrato dice **“stage 4 / diff contra la spec aprobada”**; `:50-53` — anti-bias. **Nada de revisión de borrador.**
- `sources/roles/orchestrator.md:50-66` — el orquestador sólo sabe preparar paquetes con la invocación canónica **sin** las tres flags (`:52-53`); `:94-99` — “noapprove specs / no review the full diff”; `:97-99` — “preparar/delegate role packets, materialize, resolve deviations and replan within the mandate”. **No nombra `plan-review`.**
- `agents/cdad-reviewer.md` (generado): `description` = “stage 4 … review of the diff against the approved spec”; **0 ocurrencias** de `plan-review`/`draft-plan` en todo `agents/`.
- Generación: `Makefile:15-18` (`make agents` → `scripts/cdad-generate.py`); `install.sh:66` incluye `cdad-cycle`; `install.sh:376` — “the cdad-cycle tree travels complete (packets, references and scripts)”, o sea **el substage viaja al producto instalado**.
- `Makefile:20-23` — `make validate` = `tests/validate-consistency.sh` + `tests/validate-odoo-specialization.sh`.

### 1.6 Los tests que fijan el comportamiento actual

| Test | Qué fija |
|---|---|
| `tests/test_004_003_t1_draft_contract.py:119` | `draft-plan` es kind de primera clase; `:181` la forja `approved-*`+`plan_version` se rechaza sin publicar |
| `tests/test_004_003_t1_reviewfix.py:76` | `draft-plan` rechazado para roles ≠ reviewer · `:112` el `purpose` del borrador no es marca de aprobación |
| `tests/test_004_003_t2_plan_review.py:111` | el paquete `plan-review` **lleva el plan, no sólo la spec** (`:129-133`); `:172` no aprueba; `:201` sólo rol reviewer; `:231` encargo suficiente; `:290` **el producto instalado** renderiza el paquete `plan-review` sin el repo fuente |
| `tests/test_004_003_t2_reviewfix.py:70` / `:109` | los dos sentidos del pairing (negativos black-box) |
| `tests/test_004_003_t3_plan_checks.py:281,331,345,358,371` | entrada sin productor, ciclo, contrato incompatible, paralelismo inseguro |
| `tests/test_004_003_t4_validation_fields.py:427` | **PD-8: un plan sin bloque `plan-tasks` es rechazado** (la puerta que bloquea la spec) · `:437` campos por tarea · `:478` code-less con `observable_checks` · `:529` fences malformados fallan fuerte · `:546,607,660` el formato del bloque tiene **una sola casa canónica** (`planning-contract-draft.md` §4.1) |
| `tests/test_005_007_t1_progressive_detail_rule.py:295-307` | el substage consume el marcador `detail` **por referencia** |
| `tests/test_005_007_t2_progressive_plan_validator.py`, `tests/test_005_007_t6_templates.py:249-261`, `tests/test_005_007_reviewfix_blockings.py:156-162` | marcador `detail` (“next”/“planned”), plantillas, bloqueantes del review-fix |
| `tests/test_003_002_t2_reviewfix.py:871-904` | la fila `reviewer/plan-review` con contrato `draft-plan` **se materializa** (R5) |
| `tests/test_006_005_u2_opencode_module.py:1378-1392` | PD-23: la entrega del reviewer en `plan-review` declara kind `plan-review` y `materialize` la acepta |

### 1.7 Mediciones hechas (read-only, sin escrituras)

**(a) La barrera `plan-tasks` medida sobre los documentos reales** (llamada directa a `_plan_tasks_from_contract`/`_check_plan_tasks`/`_check_plan_validation_plan` sobre bytes leídos):

```
FAIL docs/specs/006-005-native-path-parity/spec.md: PolicyError: draft plan is missing the required plan-tasks block … (PD-8)
OK   docs/specs/006-005-native-path-parity/plan.md: 9 tasks; strategy=yes
FAIL docs/epics/epic-006-opencode-concurrency/plan.md: PolicyError: draft plan is missing the required plan-tasks block … (PD-8)
```

**(b) La puerta es de *presencia del token*, no de tareas** — con el bloque presente pero vacío:

```
ACCEPTED  empty tasks list: tasks=[] strategy=None
REJECTED  no tasks key: PolicyError: plan-tasks block must carry a tasks list
ACCEPTED  tasks + strategy: tasks=[] strategy='x'
```

⇒ **Un bloque ```` ```plan-tasks {"tasks": []} ```` vacío hace pasar hoy el objeto spec por la superficie `draft-plan`.** No hace falta inventar tareas; lo que hace falta es que el modelo del objeto admita la spec. Esto es el dato que reencuadra el punto 1 del plan.

**(c) El uso real en 006-005** (`.cdad/packets/*/REQUEST.json`): en los **cuatro** `plan-review` de 006-005 el contrato es siempre `draft-plan` + `docs/specs/006-005-native-path-parity/plan.md` + `plan_version: draft-002…draft-005`; la spec aparece **sólo dentro del texto del `objective`**, nunca como contrato. El commit `82f8806` (“spec y plan draft-002 … **+ plan-tasks derivado**”) y `b9a52a3` (“plan-tasks: U6 sin archivos de código”) documentan que **el plan-tasks se derivó/añadió para que la revisión fuera posible**. El `objective` de `plan-review-001` ya decía “Objeto (los dos borradores, misma entrega del architect): docs/specs/…/spec.md y plan.md” — **la的双 documento viaja en prosa, no en el contrato**.

**(d) Contadores de presencia en el producto** (`plan-review|draft-plan`): `skills/` → 9 archivos · `agents/` → **0** · `sources/` → **0** · `scripts/` → 0 (el código no usa los nombres; usa literales) · `tests/` → 12.

**(e) Discrepancia registrada, no pregunta:** `execution.md:352` (2026-10-19) menciona que el owner autorizó un contrato `draft-spec`; `execution.md:362-364` (2026-10-20, owner) lo resuelve: *“no se abre feature nueva ni se agrega un tipo de contrato: se adelanta 006-006 a 006-004”*. **La mención de `draft-spec` queda derogada**; el plan §13.6 manda (conservar `plan-review`/`draft-plan` con deuda de nombre declarada).

---

## 2. Escenarios de recorrido del usuario real

Cada uno con **paso → herramienta → salida esperada**. “Orq.” = orquestador; “Arch.” = architect; “Rev.” = reviewer (sesión independiente).

### E1 — Spec sin plan (feature mediana)

| # | Paso | Herramienta | Salida esperada |
|---|---|---|---|
| 1 | Arch entrega `docs/specs/<F>/spec.md` (borrador, sin marca de aprobación) | `cdad_packet.py prepare --role architect --substage draft` | `REQUEST.json` con `contract.kind = approved-feature-spec`? **No** — hoy el architect entrega como texto final; el orquestador materializa |
| 2 | Orq. prepara el encargo de revisión con **contrato explícito** | `cdad_packet.py prepare --role reviewer --substage plan-review --contract-kind draft-plan --contract-path docs/specs/<F>/spec.md --plan-version draft-001` | **Hoy: rc=2, `draft plan is missing the required plan-tasks block (PD-8)`.** Tras la feature: rc=0, `contract.kind=draft-plan`, `contract.path=…/spec.md`, `contract.sha256=<sha de los bytes>`, `contract.plan_version=draft-001`, `inputs[0].purpose` = “draft spec for review”, `active_packet.contract_sha256` = ese sha |
| 3 | Rev. revisa en sesión independiente | dispatch del `PACKET.md` renderizado | Dictamen con veredicto-tuple, `## Abstentions`, **sin marca de aprobación** |
| 4 | Orq. materializa el dictamen | `cdad_result.py receive` → `materialize --authorization` | `docs/specs/<F>/plan-review.md`; recibo `semantic_status: pending`; `approval_effect: false` |
| 5 | Orq. transiciona | `cdad_packet.py register-transition` | paquete `completed`; **el state no registra aprobación** |

### E2 — Spec + plan

Igual que E1, con **dos** documentos. El contrato debe fijar **ambos**: el plan (con su `plan-tasks`, checks completos) y la spec (sin plan-tasks, sin checks de plan). Salida esperada: `contract` con la identidad del plan (path+sha+versión) **y** la de la spec (path+sha+versión), de modo que un cambio en cualquiera de los dos se detecte comparando el sha actual con el fijado. El dictamen nombra ambos digests.

### E3 — Borrador que enmienda la spec de OTRA feature (feature B, ciclo activo en A)

| # | Paso | Herramienta | Salida esperada |
|---|---|---|---|
| 1 | Orq. identifica el objeto real | — | El objeto es `docs/specs/<B>/spec.md`, **no** `docs/specs/<A>/spec.md`. **Hoy**: la ruta por defecto es la de A (`cdad_packet.py:1139`) y el reviewer la rechaza — exactamente el motivo (a) |
| 2 | Orq. declara el triple explícito | `prepare … --contract-path docs/specs/<B>/spec.md --plan-version draft-002` | rc=0; el paquete nombra **la carpeta del objeto** (`<B>`), su digest, su versión y su forma; `request.feature_id` = `<A>` (la ejecución) — **la diferencia es visible en el paquete**, no implícita |
| 3 | Rev. | dispatch | El dictamen declara sobre qué documento y qué digest; si el paquete y el documento no coinciden, **abstención o hallazgo**, nunca “revisé el borrador equivocado” |
| 4 | Materialización | `materialize` | El destino permitido sigue siendo `docs/specs/<A>/` (la feature cuyo gate lo consume) — `_allowed_target` (`cdad_result.py:672-678`) no admite otra carpeta. **Cota a declarar**: el veredicto de un borrador de B vive en la carpeta de A |

### E4 — Re-review tras corrección, con identidad y detección de cambio posterior

| # | Paso | Herramienta | Salida esperada |
|---|---|---|---|
| 1 | Orq. prepara la re-review sobre la versión corregida | `prepare … --contract-kind draft-plan --contract-path <mismo path> --plan-version draft-003` | **Nuevo** `contract.sha256` (≠ al de `draft-002`) y **nueva** `plan_version`. La revisión anterior **no** cubre los bytes nuevos — y eso es verificable, no declarativo |
| 2 | Orq. compara | `sha256sum <path>` vs el sha del `REQUEST.json` de la review anterior | Si difiere ⇒ la revisión anterior **no** cubre esos bytes ⇒ corresponde re-review. **Hoy no hay ningún comando que lo haga**: el CAS de `materialize` (`:822-852`) protege el *destino* del dictamen, no el *objeto* revisado |
| 3 | Rev. | re-review **focal** | Dictamen focal: verifica los bloqueantes acordados contra su condición de cierre + las regresiones del arreglo (`stage-4-review.md:28-32`) |

### E5 — El dictamen no aprueba

| # | Paso | Herramienta | Salida esperada |
|---|---|---|---|
| 1 | Rev. emite | texto final | El dictamen **no** contiene marca de aprobación; el substage lo dice literal: *“never mark the reviewed draft approved or authorize implementation”* |
| 2 | Orq. | `receive` | `semantic_status: pending` — *“receiving never approves a gate”* (`re-entry.md:74-77`) |
| 3 | Orq. | `materialize` | `approval_effect: false` obligatorio (`cdad_result.py:737-739`); el dictamen se copia **sin** efecto de aprobación |
| 4 | Authority | aprobación aparte | La aprobación de la spec la da la autoridad vigente (`stage-2-specification.md:46-85`), **nunca** el dictamen. El `plan-review` no habilita construir |

### E6 — (derivado de E4) Un plan coherente entre sí que no cumple la intención

Es el criterio que el plan §13.1 exige: el substage ya lo dice — *“Judge whether the plan reaches the stated intention under its constraints; a well-formed plan that does not is a blocking finding”* — y `execution.md:271` lo reformula como vara: **cumplimiento del contrato (principal) y calidad (secundaria)**, con la intención viajando como **escenarios de recorrido** en el encargo y el reviewer trazando cada escenario por las PD. Evidencia en `execution.md:275`: con los escenarios como vara, la review de 006-005 encontró defectos de recorrido que las reviews centradas en la letra no vieron.

---

## 3. Opciones de diseño para el punto 1 (objeto sin tareas artificiales)

**Restricción del plan (§13):** reutilizar `plan-review`/`draft-plan`; **sin** subfase, agente, etapa ni tipo de artefacto nuevos. Y: “una spec sin plan se revisa sin tareas artificiales: hoy el CLI exige `plan-tasks` … es un cambio de código con aceptación propia”.

**Diagnóstico que reencuadra el problema:** la puerta no exige tareas (§1.7b). El problema es que **el objeto está modelado como un plan** — el kind se llama `draft-plan`, el `purpose` dice “draft plan for review”, el procedimiento dice “Review a PLAN DRAFT” y la regla de rol dice “the plan draft for `draft-plan`”. Un objeto spec no tiene forma legal en ese modelo.

### O1 — La forma la declara el propio objeto (sin flag, sin campo, sin kind)

- Regla: si el objeto lleva el token ```` ```plan-tasks ```` → es un plan → checks completos, **sin cambio**; si no lo lleva → es un spec → los checks estructurales del plan no aplican.
- Superficie nueva: **cero**. El único cambio de comportamiento es la rama `cdad_packet.py:4718-4721`.
- Regresión honesta: un **plan** que olvidó su `plan-tasks` dejaría de ser rechazado en `prepare` → rompe `tests/test_004_003_t4_validation_fields.py:427`. Remedio: el **substage** declara “un plan sin bloque `plan-tasks` es hallazgo BLOQUEANTE” → la garantía se traslada de `prepare` al dictamen (se pierde fail-closed mecánico, se conserva la garantía semántica).
- El paquete deja de mentir: `inputs[0].purpose` pasa a “draft spec for review” / “draft plan for review” según la forma detectada (`cdad_packet.py:4790`).

### O2 — La forma la declara el encargo (campo aditivo en el objeto `contract`) — **recomendada**

- `contract` gana un campo opcional (p. ej. `object_kind: "spec" | "plan"`), con **el mismo patrón aditivo** con que 004-003 T1 añadió `plan_version` (`cdad_packet.py:879-884`, `:890-893`): `contract_keys` admite la clave opcional; `prepare` añade el flag correspondiente; el pairing `draft-plan`⇔`plan-review` **no se toca**.
- No crea kind, subfase, agente, etapa ni tipo de artefacto. `assets/packet-request.schema.json` no exige cambio (`contract` es `{"type":"object"}` sin restricciones). `assets/active-packet.schema.json:16` (enum de `contract_kind`) **no se toca**.
- Cero regresión: con `object_kind: "plan"` los checks siguen fail-closed como hoy; con `object_kind: "spec"` se saltan **sólo** los checks de plan.
- **Identidad doble (plan §13.2):** el mismo mecanismo aditivo admite un segundo documento fijado (`spec_path` + `spec_sha256` + su versión) cuando la revisión cubre spec+plan. Con eso, “un cambio posterior en la spec o en el plan se detecta” es **mecánico**: se compara el sha actual con el fijado, que es exactamente lo que hoy hace `prepare` con el documento principal (`:948-950`).
- Coste: un flag y una rama más en `prepare`; el test-writer debe **reescribir el oráculo** de `tests/test_004_003_t4_validation_fields.py:427` para el caso “plan” (cambio de oráculo, no de producto).

### O3 — La forma la declara la ruta canónica (`docs/specs/<X>/spec.md` / `plan.md`)

- Simple y sin flags, pero **rompe los fixtures compartidos**: `DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"` (`tests/test_004_003_t1_draft_contract.py:47`) se usa en **6** archivos de test (`test_004_003_t2/t3/t4`, `test_005_007_t2/t6`, `test_003_002_t2`) → coordinación con el test-writer sobre fixtures compartidos.
- Crea además una restricción de rutas que hoy no existe (ADR-013 deuda O-C) y que podría chocar con borradores en otra ubicación.

### O4 — Sin cambio de código: bloque `plan-tasks` vacío en el spec — **descartada, pero registrada**

- Verificado: `{"tasks": []}` pasa (§1.7b). Es el rodeo más barato, y es exactamente el rodeo que 006-005 usó (derivando tareas de verdad). Se descarta porque: (i) mete un bloque artificial **dentro de la spec** — lo que el plan prohíbe; (ii) el `purpose` del paquete diría “draft plan for review” para una spec, que es el malEtiquetado que hizo rechazar los paquetes; (iii) el procedimiento seguiría diciendo “Review a PLAN DRAFT”; (iv) deja el modelo mental intacto: el próximo agente repetirá el rodeo. **Sirve como parche de emergencia, con la deuda de nombre declarada.**

### Recomendación

**O2**, con O1 como degradación si el owner quiere el mínimo cambio de superficie.

Criterio (en línea con enmienda 005: “general antes que específico”): O2 es la única que **no introduce una inferencia** (O1 infiere la forma del contenido; O3 la infiere de la ruta) y la única que **reutiliza el precedente ya establecido** (`plan_version` como extensión aditiva de `contract`). No generaliza por gusto: la extensión la necesita la identidad doble, que el owner ya aprobó como precisión de la enmienda 006.

**Paquete de cambios mínimo con O2** (todo dentro del producto, sin artefactos nuevos):

1. `cdad_packet.py`: `contract` acepta `object_kind` (opcional) y, cuando la revisión cubre dos documentos, `spec_path`/`spec_sha256`/`spec_version` (opcionales); `prepare` (**:4678-4699**) acepta el flag de forma; `prepare` (**:4718-4721**) aplica los checks de plan **solo** si la forma es `plan`; `inputs[0].purpose` (**:4790**) refleja la forma.
2. `cdad_packet.py:920-942`: la aserción de kind/ruta del reviewer **no** cambia (el `draft-plan` sigue siendo el kind); lo que se relaja es **qué documento** puede ser el objeto borrador (hoy, cualquiera; mañana, cualquiera, pero con la forma declarada).
3. `packets/substages/reviewer-plan-review.md:1`: **una sola fuente** — el objeto es “intención, restricciones y decisiones + spec + plan si existe + contratos y capacidades”; la forma del objeto la dice el paquete.
4. `packets/roles/reviewer.md:1`: la regla “qué revisar” pasa a “the object the contract declares” **con su forma declarada** (spec o plan), sin ser plan-céntrica.
5. `stage-2-specification.md`: subfase + exit gate; `SKILL.md:339-346`: un criterio en Gate 2→3 (espejo de `:361-366`); `re-entry.md:148-172`: sección de re-entry del dictamen; `handoff-prompts.md:543-568`: la invocación con la forma.
6. `sources/roles/reviewer.md:46-48` (fila del contrato) → `make agents`: el agente generado nombra la revisión de borrador.
7. `artifact-policy.json:9` y `cdad_result.py:699-700`: **sin cambios** (el kind `plan-review` y su destino ya están).

### Cómo se identifica, sin ambigüedad, un borrador que toca otra feature

Tres capas, todas verificables desde el paquete (ninguna depende de que el reviewer adivine):

1. **El contrato nombra el objeto exacto**: `contract.path` = `docs/specs/<B>/spec.md` (no derivable: hoy el default es `docs/specs/<A>/spec.md`, `cdad_packet.py:1139`), `contract.sha256` = sus bytes, `contract.plan_version` = su versión, `contract.object_kind` = `spec`.
2. **El paquete separa “objeto” de “feature activa”**: `request.feature_id` = `<A>` (la ejecución) vs. `contract.path` → `<B>`. La diferencia es legible; el orquestador puede además **diagnosticarla** (no bloquearla): “el borrador declarado pertenece a `<B>`; la ejecución activa es `<A>`”.
3. **La materialización es unilateral**: el dictamen va a `docs/specs/<A>/` (`_allowed_target`, `cdad_result.py:672-678`) — la carpeta del gate que lo consume — y **el dictamen nombra el objeto y su digest**, para que el artefacto no se confunda con un dictamen sobre la spec de A.

**Cota a declarar al owner:** el artefacto del dictamen **no** puede materializarse en la carpeta de otra feature sin tocar la tabla cerrada de destinos. La opción elegida (vive en `<A>/`) no requiere ese cambio; la alternativa (vive en `<B>/`) sí, y ampliaría el alcance de la feature.

---

## 4. Preguntas abiertas (solo el dueño puede decidir)

| # | Pregunta | Por qué es del dueño | Recomendación del architect |
|---|---|---|---|
| **Q1** | **Exención de la revisión: ¿dónde se registra y con qué forma?** El plan §13.5 dice “solo el dueño la exime, de forma explícita y registrada”, pero no declara el soporte. `stage_history` es una lista libre (`skills/cdad-cycle/assets/state-template.json:12`) y ya tiene el precedente de la aprobación delegada (`stage-2-specification.md:80`: `approved_by` + `delegated` + `requested_by`) | Es una decisión de autoridad y de trazabilidad, no de mecánica | Registrar en `stage_history` de la feature, con `stage: "specification"`, `exempted_by`, `delegated`, `requested_by` y `reason` — reutilizando la forma existente, sin tocar el schema del state |
| **Q2** | **Gate 2→3: ¿qué evidencia mínima se exige?** (i) el artefacto `docs/specs/<F>/plan-review.md` presente + sin bloqueantes sin resolver; (ii) sólo el recibo registrado. El plan §13.4 dice “obligación metodológica supervisada, no bloqueo duro nuevo en el CLI”, y §13.4 fija el dictamen “como artefacto (`plan-review.md` en la carpeta de la spec) y como entrega registrada” | Es un criterio de gate: define qué se audita | Espejo del Gate 4→5 (`SKILL.md:361-366`): artefacto + “bloqueantes resueltos o descartados con razón escrita”. Es la lectura más consistente con “supervisado, no enforcement” |
| **Q3** | **Revisión de un borrador de OTRA feature (escenario E3): ¿se permite y dónde vive su dictamen?** El cierre material (`cdad_result.py:672-678`) obliga a que viva en la carpeta de la feature activa | Es una frontera de authority/alcance entre features | Permitirlo; el dictamen vive en la carpeta de la feature cuyo gate lo consume; el paquete y el dictamen nombran el objeto y su digest. (Ampliar la tabla de destinos queda **fuera** de alcance) |
| **Q4** | **Doble identidad: ¿dos documentos fijados en el contrato, o la versión como cadena?** El plan §13.2 (“la revisión fija las versiones de la spec y del plan cuando existen”) es comportamiento; el vehículo es decisión de diseño con coste de coordinación | Con la HITL amplia (execution.md:278-280) esto **lo decide el architect** | Dos documentos fijados en `contract` (mecánico, verificable por digest). La versión como cadena es un modo de fallo silencioso: el digest es el único que se puede comparar con `sha256sum` |
| **Q5** | **¿La revisión es obligatoria también en features triviales?** `stage-2-specification.md:88` admite la variante “Trivial” (un párrafo + un test). El plan §13.5 dice “siempre y con profundidad proporcional; sólo el dueño la exime, de forma explícita y registrada” | Afecta el costo de todo el ciclo | Obligatoria con profundidad proporcional; exención sólo a pedido explícito del dueño y registrada (Q1). No exención por defecto: es justo donde el costo es mínimo |
| **Q6** | **Nombre de la feature y su artefacto**: el id ya está fijo (`006-006-spec-plan-review`) y el artefacto ya está decidido (`plan-review.md` en `docs/specs/<feature>/`, `execution.md:167`). La “deuda de nombre” (`plan-review`/`draft-plan` para una revisión de spec) queda **declarada** | Ya decidido en la enmienda 006 (plan §13.6) | Ninguna pregunta: se declara la deuda y se avanza |

**No pregunto** (ya resuelto y verificado): el nombre `draft-spec` de `execution.md:352` queda **derogado** por `execution.md:362-364` (owner, 2026-10-20): *“no se abre feature nueva ni se agrega un tipo de contrato”*; el kind sigue siendo `draft-plan`. Y W1 (orden/recepción) está resuelto: el orden es **006-005 → 006-006 → 006-004** (`execution.md:362-364`; `docs/progress.md:59-60`; `docs/activeContext.md:172-175`).

---

## 5. Evidencia

**Comandos ejecutados (solo lectura):**

```bash
git status --short && git log --oneline -3 && ls
wc -l docs/epics/epic-006-opencode-concurrency/*.md
grep -n "VALID_CONTRACT_KINDS\|plan-review\|draft-plan\|plan_version\|plan-version\|plan-tasks\|plan_tasks" skills/cdad-cycle/scripts/cdad_packet.py
grep -rn "plan-review\|draft-plan" --include=*.md --include=*.json --include=*.py . | grep -v "^./docs/" | grep -v __pycache__
grep -rn "plan-review\|draft-plan" agents/ | wc -l   # → 0
grep -rn "plan-review\|draft-plan" sources/ | wc -l  # → 0
grep -rn "plan-review\|draft-plan" skills/cdad-cycle/SKILL.md | wc -l   # → 0
grep -n "Gate 2→3\|review.md" skills/cdad-cycle/SKILL.md
git log -S'```plan-tasks' --oneline -- docs/specs/006-005-native-path-parity/plan.md
python3 - <<'PY'   # _plan_tasks_from_contract / _check_plan_tasks / _check_plan_validation_plan
                    # sobre los bytes leídos de 3 documentos del repo
PY
python3 -c "import json; ...docs/.cdad-state.json..."   # active_feature/active_packet/epic_features
git show --stat eca74f4
```

**Salidas destacadas (verbatim):**

```
FAIL docs/specs/006-005-native-path-parity/spec.md: PolicyError: draft plan is missing the required plan-tasks block: the per-task validation plan is part of the plan (PD-8)
OK   docs/specs/006-005-native-path-parity/plan.md: 9 tasks; strategy=yes
FAIL docs/epics/epic-006-opencode-concurrency/plan.md: PolicyError: draft plan is missing the required plan-tasks block: the per-task validation plan is part of the plan (PD-8)

ACCEPTED  empty tasks list: tasks=[] strategy=None
REJECTED  no tasks key: PolicyError: plan-tasks block must carry a tasks list
ACCEPTED  tasks + strategy: tasks=[] strategy='x'

skills 9 · agents 0 · sources 0 · scripts 0 · tests 12   (archivos con plan-review|draft-plan)
```

**Archivos modificados por esta sesión: ninguno.** `git status --short` antes y después muestra el mismo conjunto (` M docs/.cdad-state.json`, `?? docs/planning/`, `?? findings/…`), y el diff de `docs/.cdad-state.json` (1 línea: `active_packet.status: prepared → dispatched`) es **del orquestador**, previo a esta sesión. Los archivos sin trackear tampoco son míos.

**Commit:** ninguno (rol read-only; el artefacto de esta sesión es texto final para que el orquestador lo materialice, ADR-003). Nota de concurrencia: durante la sesión otro actor commiteó `eca74f4` (`docs(epic-006): push tras 006-005`, solo `execution.md`) — **no es mío**; lo verifiqué con `git show`.

**Puntos marcados como VERIFY (no afirmados):** (i) que el cambio de `contract` con campos opcionales sea aceptable para `cdad-generate.py` y para el `install.sh --check` — a verificar en la spec; (ii) que el `receive`/`materialize` acepte una entrega cuyo `contract` lleva campos extra — el `REQUEST.json` se revalida en `receive` (`cdad_result.py:563-566` recomputa el render), lo que hay que comprobar con un RED; (iii) la forma exacta del registro de exención (Q1) depende de Q1/Q2.