# 006-006-spec-plan-review — SPEC (etapa 2, borrador draft-001)

Estado: **BORRADOR — SIN APROBAR**. Esta entrega no lleva marca de aprobación y no la lleva nunca por el dictamen de la revisión de borrador (INV-1). La aprobación es un acto separado de la autoridad vigente (`skills/cdad-cycle/references/stage-2-specification.md`:46-85).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §13 (enmienda 006) — sha256 `d6da11db…9809`, verificado contra el paquete `exec-006-006-spec-plan-review-001` y recalculado en disco.
Decisiones de entrada (orquestador, HITL delegada, mantenidas el 2026-10-20): `docs/epics/epic-006-opencode-concurrency/execution.md`:379-388.
Insumo: `docs/specs/006-006-spec-plan-review/discovery.md` (etapa 1, mismo autor).
Base medida: HEAD `7f39e24`. Todas las citas de código son de ese HEAD y nombran además el símbolo (los números de línea pueden correrse).
Anonimización: rutas relativas al repositorio; sin rutas del host, endpoints, ids de sesión ni credenciales. El proyecto consumidor se nombra «el proyecto consumidor»; **no se nombra**.

## 0. Intención y decisiones de entrada

**Intención.** Que la revisión independiente de un borrador **de especificación** —la spec y el plan cuando existe— sea una capacidad **de primera clase del recorrido**, con la misma disciplina que ya tiene la revisión de un plan, y no un rodeo. Hoy la capacidad existe (`plan-review` + `draft-plan`) pero **no está en el recorrido principal** y **sólo admite planes**: `grep` da **0** ocurrencias de `plan-review`/`draft-plan` en `agents/`, `sources/` y `skills/cdad-cycle/SKILL.md`; el gate 2→3 (`SKILL.md`:339-346) y el exit gate de Stage 2 (`stage-2-specification.md`:176-185) no la nombran; y el CLI **exige el bloque `plan-tasks`** a cualquier borrador declarado (`cdad_packet.py`:4718-4721 → `_plan_tasks_from_contract`:3347-3388). Medido: `{"tasks": []}` **pasa** las tres validaciones ⇒ la puerta no exige tareas, exige la *forma de plan*. El problema real es que **el objeto está modelado como un plan**, no que el plan-tasks obligue a inventar tareas.

**Las tres razones del rechazo en el proyecto consumidor son correctas y mecánicas** (no son un error del uso): (a) el contrato por defecto del reviewer es `approved-feature-spec` → `docs/specs/<feature_id>/spec.md` (`cdad_packet.py`:1126-1140); (b) un `approved-epic-plan` **no** es admisible para el reviewer (`cdad_packet.py`:920-942, la aserción de kind/ruta por rol); (c) `draft-plan` sin `plan-tasks` ⇒ `prepare` rc≠0.

**Decisiones adoptadas (cierran Q1-Q6 y O2 del discovery; ninguna es una decisión de diseño abierta):**

| Decisión | Contenido | Dónde se aplica |
|---|---|---|
| O2 (forma declarada) | `contract.object_kind` (`spec`\|`plan`) como extensión **aditiva** del contrato — el mismo patrón con que 004-003 T1 añadió `plan_version` (`cdad_packet.py`:879-883) | §2.1 |
| Q4 (identidad doble) | Cuando la revisión cubre spec y plan, el contrato **fija los dos documentos por digest** | §2.3 |
| Q3 (otra feature) | Se permite revisar el borrador de otra feature; el dictamen vive en la carpeta de la feature activa y nombra el objeto y su digest; **la tabla de destinos no se amplía** | §2.4 |
| Q2 (gate 2→3) | Artefacto `plan-review.md` presente, con cada bloqueante resuelto o descartado con razón escrita. **Obligación supervisada, sin bloqueo duro en el CLI** | §2.6 |
| Q5 (proporción) | La revisión es **siempre** obligatoria, con profundidad proporcional; no hay exención por defecto | §2.6, D-5 |
| Q1 (exención) | Sólo el owner la exime, explícita y registrada en `stage_history` (`exempted_by`, `delegated`, `requested_by`, `reason`) | §2.7 |
| Q6 (nombre) | La deuda de nombre (`plan-review`/`draft-plan` para una revisión de spec) queda **declarada** | §10 |

**Lo que el discovery dejó medido y esta spec recoge:** (i) el kind `draft-plan` **no** exige aprobación (`cdad_packet.py`:1604-1609; `references/project-execution.md`:92-93) ⇒ revisar un borrador no-approved no es circular; (ii) el pairing `draft-plan` ⇄ `plan-review` es bidireccional y sólo del reviewer (`cdad_packet.py`:909-919) ⇒ **no se crea subfase, agente, stage ni kind nuevos**; (iii) el dictamen se materializa con el kind `plan-review` → `docs/specs/<feature>/` (`assets/artifact-policy.json`:9; `cdad_result.py`:681-706) y **nunca** con efecto de aprobación (`cdad_result.py`:737-739); (iv) el CAS de `materialize` protege **el destino**, **no el objeto revisado** (`cdad_result.py`:822-852) ⇒ la detección de deriva es comparar digests fijados, no el CAS.

## 1. Descripción funcional

La feature hace tres cosas, en este orden:

1. **Un borrador de especificación tiene forma legal en la superficie de revisión.** Hoy el kind `draft-plan` modela un plan: el nombre, el `purpose` del input (`cdad_packet.py`:4790-4792: «draft plan for review»), el procedimiento («Review a PLAN DRAFT», `packets/substages/reviewer-plan-review.md`:1) y la regla de rol («the plan draft for `draft-plan`», `packets/roles/reviewer.md`:1) son plan-céntricos, y el CLI exige el bloque `plan-tasks` a cualquier borrador. La feature **declara la forma del objeto en el encargo** (extensión aditiva del `contract`), y **los checks estructurales del plan se aplican sólo al documento cuya forma es `plan`**. Una spec sin plan se revisa **sin tareas artificiales**: no se mete un bloque `plan-tasks` vacío dentro de la spec (§2.1, §2.2).
2. **La revisión entra en el recorrido principal y en el gate.** El procedimiento canónico dice **qué se revisa** (una sola fuente: `packets/substages/reviewer-plan-review.md`, generalizado al *objeto de especificación*); `stage-2-specification.md` la declara como subfase de la etapa 2 y su exit gate la nombra; `SKILL.md` gana un criterio en el gate 2→3 (espejo del gate 4→5, `SKILL.md`:361-366); `re-entry.md` gana la re-entry del dictamen; `handoff-prompts.md` gana la invocación con la forma. El rol reviewer y los agentes generados nombran la revisión de borrador (§2.5, §2.8).
3. **La identidad y la trazabilidad del objeto revisado quedan fijadas.** El contrato fija por digest el documento principal y, cuando la revisión cubre spec y plan, **los dos**; el paquete los lleva como `inputs`; el dictamen nombra el objeto y su digest; una corrección produce digest nuevo ⇒ la revisión anterior no cubre los bytes nuevos ⇒ toca re-review focal (§2.3, §2.4).

**Lo que NO hace:** no crea kind, subfase, agente, stage, tipo de artefacto ni verbo nuevos; no amplía la tabla cerrada de destinos; no renombra `draft-plan`/`plan-review`/`plan_version`; no convierte el gate 2→3 en un bloqueo duro del CLI; no toca la revisión final del resultado (etapa 4), que se mantiene en sesión nueva.

## 2. Contrato

### 2.1 La forma del objeto se declara en el contrato (`object_kind`)

El objeto `contract` del request es un conjunto cerrado de claves (`cdad_packet.py`:879-883: `contract_keys = {"kind","path","sha256","commit"}`, más `plan_version` cuando está presente). La feature lo **extiende de forma aditiva**, con el mismo patrón de `plan_version`:

| Clave | Presencia | Significado |
|---|---|---|
| `kind` | siempre | `draft-plan` (kind **conservado**; deuda de nombre, §10) |
| `path` | siempre | **documento principal** del objeto revisado |
| `sha256` | siempre | digest de los bytes del documento principal, **verificado** contra el archivo (`cdad_packet.py`:945-950) |
| `commit` | siempre | `null` (sin hash pin de commit en este kind) |
| `plan_version` | siempre en `draft-plan` | versión del **borrador revisado** (la del documento principal; **deuda de nombre** cuando el principal es una spec, §10) |
| **`object_kind`** | **opcional** | **forma del documento principal**: `spec` \| `plan`. **Ausente ⇒ `plan`** (comportamiento vigente, fail-closed; §2.2) |
| `spec_path` | opcional | **documento acompañante** (la spec), cuando la revisión cubre spec **y** plan |
| `spec_sha256` | opcional | digest de los bytes de la spec acompañante, **verificado** contra el archivo |
| `spec_version` | opcional | versión de la spec acompañante |

**Reglas (todas mecánicas, todas observables):**

- **R-1 (conjunto cerrado, aditivo).** `set(contract)` debe ser exactamente `contract_keys` ∪ {las claves opcionales presentes}; **cualquier clave desconocida se rechaza** (igual que hoy). `assets/packet-request.schema.json`:15 declara `contract` como `{"type":"object"}` ⇒ **no cambia el schema**.
- **R-2 (forja).** `object_kind`, `spec_path`, `spec_sha256` y `spec_version` **sólo** son admisibles sobre un kind `draft-plan`. Un kind `approved-*` que las declare se rechaza **antes de publicar nada** (el mismo patrón y el mismo sitio que la forja de `plan_version`, `cdad_packet.py`:890-898).
- **R-3 (valor cerrado).** `object_kind` fuera de `{spec, plan}` ⇒ rc≠0 nombrando el valor y la forma admitida.
- **R-4 (por omisión = `plan`).** Sin `object_kind`, el objeto se trata como plan: los checks del plan se aplican y la puerta `plan-tasks` sigue vigente. **Es la dirección fail-closed**: olvidar la bandera produce el rechazo vigente, nunca una aceptación silenciosa.
- **R-5 (banderas de `prepare`).** `prepare` admite `--object-kind {spec,plan}`, `--spec-path` y `--spec-version`. El digest del documento acompañante **lo calcula `prepare` de los bytes del archivo** (como el del principal), no se afirma desde fuera: un digest afirmado que no coincide con los bytes se rechaza nombrando la divergencia.
- **R-6 (todo o nada).** `spec_path`, `spec_sha256` y `spec_version` aparecen **juntos o ninguno**. `spec_path` sin `spec_version` (o al revés) ⇒ rc≠0 nombrando la clave que falta. El documento acompañante **debe existir** en el proyecto: si falta ⇒ rc≠0 nombrando la ruta.
- **R-7 (el acompañante es la spec).** El documento acompañante es **siempre** la spec, y sólo existe cuando el principal es el plan (R-8). No hay un acompañante de otra forma: la forma se declara por **la clave que la transporta**, nunca por inferencia del contenido ni de la ruta.
- **R-8 (principal = plan cuando hay plan).** Cuando la revisión cubre spec y plan, el **principal es el plan** y la spec es el acompañante. Cuando la revisión cubre sólo la spec, el principal es la spec y no hay acompañante. El principal es, por tanto, **el documento más estructurado disponible**, y el `plan-tasks` sigue siendo exigible cuando existe un plan.
- **R-9 (el paquete nombra la forma).** `inputs` lleva **una entrada por documento fijado**, en orden fijo (principal primero, acompañante después), con su `purpose`: `«draft spec for review»` para la spec, `«draft plan for review»` para el plan. La sección `## Contract` del render nombra la forma (`- form: spec` \| `- form: plan`) y, si hay acompañante, su ruta, digest y versión. **Sin las claves nuevas, el render es byte-idéntico al de hoy** (el bloque `## Contract` y `## Inputs` sólo crecen cuando el contrato declara algo nuevo) — el patrón aditivo ya establecido (006-005 PD-7).
- **R-10 (compatibilidad).** Un paquete publicado antes de la feature (contrato sin `object_kind`) sigue siendo válido, recibible y materializable; sus bytes de render no cambian.

**Superficie afectada, medida:** `cdad_packet.py` — `contract_keys` (:879-883), guarda de forja (:890-898), validación del contrato (:920-950), `prepare` (:4671-4699), checks del plan (:4718-4721), construcción de `inputs` (:4790-4792), render (:998-1059, metadata :1028, `## Contract` :1045-1047, `## Inputs` :1051-1052), tabla de banderas (:2011, :6409-6413).

### 2.2 Los checks del plan se aplican sólo al documento cuya forma es `plan`

Hoy la rama es binaria: `if is_declared_draft:` ⇒ `_plan_tasks_from_contract` + `_check_plan_tasks` + `_check_plan_validation_plan` sobre los bytes del contrato (`cdad_packet.py`:4718-4721). Con la forma declarada, la rama pasa a ser **condicional a la forma del documento principal**:

| Forma del principal | ¿Checks del plan? | Efecto observable |
|---|---|---|
| `plan` (o ausente ⇒ `plan`) | **sí** | igual que hoy: sin bloque `plan-tasks` ⇒ rechazo; bloque malformado ⇒ rechazo; checks estructurales y por tarea aplicados |
| `spec` | **no** | una spec sin `plan-tasks` se acepta; **no** se inventan tareas ni se mete un bloque artificial en la spec |
| `plan` + spec acompañante | **sí, sólo sobre el principal** | la spec acompañante **nunca** se juzga por las reglas del plan |

**Consecuencia deorcamiento:** el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 («un plan sin el bloque `plan-tasks` es rechazado») **se conserva sin cambio de oráculo**, porque la forma por omisión es `plan` (R-4). Este es el punto que la opción O2 del discovery anticipaba como coste («reescribir el oráculo»); con el valor por omisión **ese coste no se paga** (plan §4, A-1).

**Ayuda al diagnóstico (declarada):** cuando la puerta `plan-tasks` rechaza y la forma **no** fue declarada, el diagnóstico nombra la bandera que la declara (`--object-kind spec`). No cambia la Fail-Closed: el rechazo sigue siendo el mismo y sigue sin publicar nada; sólo el mensaje señala la salida legítima. El oráculo vigente del test sólo exige que el stderr nombre el token `plan-tasks` (`assert_rejected_without_publication`:399-423), de modo que la ayuda es compatible con él.

### 2.3 Identidad doble: los dos documentos fijados por digest

Cuando la revisión cubre spec y plan, el contrato lleva **las dos identidades**: `path`/`sha256`/`plan_version` (plan) y `spec_path`/`spec_sha256`/`spec_version` (spec). Los dos digests se **verifican contra los bytes** en `prepare` (`cdad_packet.py`:945-950 para el principal; el mismo control para el acompañante). Consecuencias:

- **Un cambio posterior en cualquiera de los dos documentos se detecta mecánicamente**: se compara el digest actual del archivo con el digest fijado en el `REQUEST.json` del paquete de revisión (con `sha256sum`, el mismo instrumento que usa el propio CLI). No hay comando nuevo: la comparación la hace el orquestador, y el paquete conserva el registro.
- **La revisión anterior no cubre los bytes nuevos**: un digest distinto ⇒ toca re-review **focal** (regla 4 de la calibración, `references/stage-4-review.md`:28-32), no una ronda nueva completa.
- **El dictamen declara el objeto y su digest**: obligación de procedimiento (§2.5) y **mecánicamente recuperable** por la cadena recibo → paquete → `REQUEST.json` → digests fijados. **No** se añade una comprobación nueva en `materialize` (D-9): el CAS de `materialize` protege el destino, y atar el texto libre de la parte a un digestVOLVERÍA frágil (un error tipográfico del revisor convertiría la recepción en un fallo tardío) sin ganancia real, porque la trazabilidad ya es recuperable.

### 2.4 Revisar el borrador de otra feature (y por qué el dictamen vive en la carpeta de la feature activa)

El contrato de un borrador puede apuntar a **cualquier** documento del proyecto (`_project_path` sólo garantiza que esté dentro de la raíz; la restricción a `docs/specs/<feature>/` **no existe** — deuda ADR-013 O-C, declarada y **fuera de alcance**). Por eso es admisible, y necesario, revisar el borrador de **otra** feature.

Tres capas, todas verificables desde el paquete (ninguna depende de que el revisor adivine):

1. **El contrato nombra el objeto exacto**: `contract.path` (no derivable: el default es `docs/specs/<active>/spec.md`, `cdad_packet.py`:1126-1140), `contract.sha256`, `contract.plan_version` y `contract.object_kind`.
2. **El paquete separa «objeto» de «feature activa»**: `request.feature_id` = la feature de la ejecución vs. `contract.path` ⇒ la diferencia es legible en el propio paquete.
3. **La materialización es unilateral**: el dictamen va a `docs/specs/<feature activa>/` (`_allowed_target`, `cdad_result.py`:672-678) y **nombra el objeto y su digest**, para que el artefacto no se confunda con un dictamen sobre la spec de la feature activa. **Ampliar la tabla de destinos queda fuera de alcance** (decisión Q3).

### 2.5 Qué se revisa (una sola fuente) y quién lo dice

**Dueño único del «qué se revisa»:** `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` — se generaliza del *plan* al **objeto de especificación**: intención declarada, restricciones y decisiones aplicables, **spec**, **plan cuando existe**, contratos y capacidades necesarias para ejecutar y obtener evidencia. La forma del objeto la dice el paquete, no el procedimiento.

**La regla de rol deja de ser plan-céntrica:** `skills/cdad-cycle/packets/roles/reviewer.md`:1 pasa de «the plan draft for `draft-plan`» a «el objeto que el contrato declara, **con su forma declarada** (spec o plan)». Es un consumidor: **no copia** la regla.

**Se conservan, verbatim, dos obligaciones del procedimiento actual** (regresión de 005-007 PD-12, `tests/test_005_007_t1_progressive_detail_rule.py`:295-307): (a) la **separación** entre validación estructural y juicio semántico; (b) el consumo del marcador `detail` **por referencia** a su regla canónica (`stage-2-specification.md`, sección «Progressive detail») — el substage **no** la re-enuncia.

**La vara del juicio (§13.1 y `execution.md`:271):** un plan o una spec **coherentes entre sí pero que no alcanzan la intención** es un **hallazgo bloqueante**. El encargo lleva la intención **como escenarios de recorrido** (§3.1) y el revisor traza cada escenario por las PD: «si todas pasan, ¿el especialista puede hacer su trabajo?».

### 2.6 El recorrido principal y el gate 2→3

- **Subfase de la etapa 2** (`stage-2-specification.md`): tras el borrador y **antes** de la aprobación, se prepara y despacha el paquete `reviewer`/`plan-review` sobre el borrador; el dictamen se recibe y se materializa; sus bloqueantes van al architect o se descartan con razón escrita por la autoridad que aprueba; si la corrección cambia el diseño, hay **re-review focal**; recién entonces se aprueba.
- **Criterio en el gate 2→3** (`SKILL.md`:339-346), **espejo del gate 4→5** (`SKILL.md`:361-366): el artefacto `docs/specs/<feature>/plan-review.md` está presente y cada bloqueante está resuelto o descartado con razón escrita. **Es una obligación metodológica supervisada, no un bloqueo duro nuevo en el CLI** (§13.4): el CLI no verifica la existencia del dictamen, y el §2.3 de esta spec **no** añade esa verificación.
- **Re-entry** (`references/re-entry.md`:148-172): la re-entry del architect («spec draft») y la nueva re-entry del revisor de borrador (qué hacer con el dictamen: corregir, re-review focal, exención).
- **Invocación** (`references/handoff-prompts.md`:543-568): la plantilla del revisor declara la forma (`--object-kind spec` cuando el objeto es una spec) y la identidad doble (`--spec-path`, `--spec-version`).
- **Proporción** (Q5): la revisión ocurre **siempre**, con profundidad proporcional (calibración vigente, `references/stage-4-review.md`:5-54). **No hay exención por defecto.**
- **El dictamen no es insumo del test-writer** y **no habilita construir** (§13.6): los roles de construcción siguen exigiendo el pin de aprobación en `stage_history` (`cdad_packet.py`:1586-1620); el dictamen no lo suple ni lo anticipa.

### 2.7 La exención: del owner, explícita y registrada

Decisión Q1: sólo el owner exime la revisión, de forma explícita y registrada. La **forma del registro** es una entrada de `stage_history` de la feature, con los cuatro campos **estructurados** que nombra la decisión:

```json
{ "feature": "<F>", "stage": "specification", "transition": "gate",
  "approved_by": "<la autoridad que aprueba la spec>",
  "exempted_by": "<el owner que exime la revisión>",
  "delegated": true, "requested_by": "<quién pidió la exención>",
  "reason": "<por qué>", "approval_effect": false }
```

**Vehículo:** el verbo existente `register-transition`, clase `gate`, con **tres banderas opcionales nuevas** (`--exempted-by`, `--exemption-reason`, `--requested-by`) y un interruptor (`--delegated`), admisibles **sólo** con `--transition gate`. La entrada resultante conserva sus campos actuales (`approved_by`, el pin del contrato, `transition_key`, …) y **suma** los tres campos nuevos. `delegated` y `requested_by` son, además, los campos que el **precedente de la aprobación delegada** ya usa en el estado (`stage-2-specification.md`:80) y que hoy **ningún verbo del producto puede producir** — el flags cierra ese hueco, y lo hace en el mismo sitio.

**Por qué la exención va en la entrada de aprobación y no en una entrada libre:** (a) la exención **es** una forma de pasar el gate 2→3, así que pertenece al acto que lo abre; (b) atada a la aprobación, **no puede flotar** nivivir en un `stage` que habilite construcción por su cuenta; (c) la entrada de aprobación conserva su pin de contrato y su `approved_by` — la exención **no** cambia lo que la aprobación autoriza, sólo **declara cómo** se pasó el criterio de revisión.

**Nada de esto habilita construir:** la exención no altera el pin de aprobación, no crea un kind nuevo y no modifica la comprobación de la etapa de construcción.

### 2.8 El rol y los agentes

`sources/roles/reviewer.md` (fuente editable; los agentes son **salidas declaradas** de `scripts/cdad-generate.py`, `Makefile`:15-18) pasan a declarar: la etapa 2 además de la 4; el artefacto `plan-review.md` (además de `review.md`); y la revisión de **borrador** (no aprobado) como parte del rol. La fila de la tabla de contrato (`sources/roles/reviewer.md`:48) y el texto generado (`agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer*.md`) quedan alineados; `make agents` es **determinista** (dos corridas, mismos bytes) y `make validate` sigue verde.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **La forma del objeto se declara en el encargo.** El contrato acepta `object_kind` con valores `spec` \| `plan`; el valor viaja al `REQUEST.json` y a la metadata del paquete; un valor fuera del conjunto cerrado ⇒ rc≠0 **nombrando el valor**; una clave cualquiera no declarada ⇒ rc≠0 (el conjunto sigue cerrado); un kind `approved-*` que declare `object_kind` ⇒ **rechazo antes de publicar** (forja). | `REQUEST.json` del paquete en los tres casos; rc≠0 en cada negativo; `out-dir` sin entradas y state byte-idéntico en cada rechazo (el mismo control que `assert_rejected_without_publication`, `tests/test_004_003_t4_validation_fields.py`:399-423) |
| **PD-2** | **Por omisión, la forma es `plan` y el comportamiento vigente no cambia.** Sin `object_kind`: el objeto se trata como plan; los checks del plan se aplican; un borrador sin bloque `plan-tasks` **sigue rechazándose** con el diagnóstico vigente; un paquete con bloque malformado **sigue rechazándose**; el render de un paquete sin las claves nuevas es **byte-idéntico** al de hoy. | el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 **sin cambio de oráculo** (control negativo explícito en el RED); comparación byte a byte del render de un paquete con y sin las claves nuevas; el test de bloque malformado (`tests/test_004_003_t4_validation_fields.py`:529) verde sin cambios |
| **PD-3** | **Una spec se revisa sin tareas artificiales.** Con `object_kind: spec`, un borrador de spec **sin** bloque `plan-tasks` es aceptado y publica paquete; con `object_kind: plan` (o ausente) el mismo archivo es rechazado; la spec **no** contiene ni se le inyecta bloque `plan-tasks`; los checks de plan **nunca** se aplican a un documento de forma `spec`. | `prepare` rc=0 con la spec; rc≠0 con los mismos bytes declarados como `plan`; el `REQUEST.json` de la spec **no** contiene el token `plan-tasks`; inspección: la rama de checks se decide por la forma declarada |
| **PD-4** | **La identidad doble fija los dos documentos por digest.** Con `--spec-path`/`--spec-version`: el contrato lleva `spec_path`, `spec_sha256` (calculado de los bytes) y `spec_version`; el digest **coincide** con `sha256sum` del archivo; un archivo acompañante **inexistente** ⇒ rc≠0 nombrando la ruta; `spec_path` sin `spec_version` (o al revés) ⇒ rc≠0 nombrando la clave ausente; el acompañante exige principal de forma `plan`; un kind `approved-*` que declare el acompañante ⇒ rechazo por forja. | los tres campos del `REQUEST.json`; `sha256sum` del acompañante comparado con el campo; los tres negativos con rc≠0 y sin publicación |
| **PD-5** | **El paquete lleva los documentos fijados y su forma.** `inputs` lleva una entrada por documento (principal primero), con `purpose` `«draft spec for review»` / `«draft plan for review»`; la sección `## Contract` del render nombra la forma y, si hay acompañante, su ruta, digest y versión; **sin** las claves nuevas el render es byte-idéntico; la metadata del paquete lleva el contrato completo. | el `REQUEST.json` (`inputs`) y el `PACKET.md` renderizado (sección `## Contract`); comparación byte a byte del render antes/después |
| **PD-6** | **El dictamen nombra el objeto y su digest, y vive en la carpeta de la feature activa.** Con un borrador de **otra** feature: `prepare` rc=0 con `--contract-path` de esa feature; el paquete muestra `feature_id` (la ejecución) ≠ la carpeta del `contract.path`; el dictamen se materializa **sólo** en `docs/specs/<feature activa>/` con el kind `plan-review`; un target en la carpeta de **otra** feature ⇒ rc≠0 (la tabla de destinos no se amplía); el procedimiento exige que el dictamen nombre el objeto y su digest. | `REQUEST.json` (los dos identificadores, comparables); `materialize` rc=0 con sha idéntico hacia `docs/specs/<feature activa>/plan-review.md`; `materialize` rc≠0 hacia `docs/specs/<otra>/`; texto del substage (deriva) |
| **PD-7** | **El dictamen no equivale a aprobación.** El texto del dictamen **no** contiene marca de aprobación; el recibo queda `semantic_status: pending`; la autorización de materialización exige `approval_effect: false` (`cdad_result.py`:737-739); el estado **no** registra aprobación al recibir ni al materializar; la aprobación de la spec es un acto **posterior y separado** (el pin de `stage_history`). | el texto de la entrega (grep de la marca de aprobación); los campos del recibo; el estado antes/después; la entrada de `stage_history` que habilita construcción es la de aprobación, con su pin |
| **PD-8** | **Un cambio posterior en el objeto se detecta.** Tras la revisión, cambiar el documento principal (o el acompañante) cambia su digest; el digest fijado en el `REQUEST.json` de la revisión **no** coincide con `sha256sum` del archivo ⇒ la revisión anterior no cubre esos bytes ⇒ toca re-review focal; con bytes sin cambiar, el digest fijado coincide y no hay re-review. | comparación `sha256sum` contra el `contract.sha256` / `contract.spec_sha256` del `REQUEST.json`, antes y después de la edición; los dos casos |
| **PD-9** | **La exención es del owner, explícita y registrada.** `register-transition --transition gate` con `--exempted-by` + `--exemption-reason` (+ `--requested-by`, `--delegated`) escribe una entrada de `stage_history` con `exempted_by`, `reason`, `requested_by` y `delegated`; **sin** esas banderas la entrada **no** lleva esos campos; las banderas son **inadmisibles** fuera de la clase `gate`; la entrada de exención **no** habilita construcción por sí sola (el pin de aprobación sigue siendo el que manda). | el `stage_history` del estado tras cada invocación; el rechazo de las banderas fuera de la clase; el rol de construcción sigue bloqueado sin la aprobación con su pin |
| **PD-10** | **El gate 2→3 y el exit gate de la etapa 2 declaran la evidencia de la revisión.** `SKILL.md` (gate 2→3) y `stage-2-specification.md` (exit gate) nombran el artefacto `plan-review.md` y la condición de bloqueantes; `re-entry.md` tiene la re-entry del dictamen; `handoff-prompts.md` declara la invocación con la forma. **Ninguna de estasSuperficies es un bloqueo del CLI.** | deriva textual sobre las tres superficies (el patrón de deriva del proposal §6) + comprobación negativa: `prepare` **no** verifica la existencia del dictamen (ningún camino nuevo de rechazo) |
| **PD-11** | **El rol y los agentes generados nombran la revisión de borrador.** `sources/roles/reviewer.md` declara la etapa 2, el artefacto `plan-review.md` y la revisión de borrador; los cuatro agentes generados lo contienen tras `make agents`; `make staging` es determinista (dos corridas, mismos bytes); `make validate` verde. | el texto de la fuente y el de los cuatro agentes generados; comparación byte a byte de dos corridas de `make staging`; salida de `make validate` |
| **PD-12** | **El procedimiento conserva sus obligaciones y su frugalidad de fuente.** El substage sigue separando validación estructural de juicio semántico, sigue exigiendo el juicio sobre la intención (un plan/spec coherente que no la alcanza es bloqueante), sigue **sin** re-enunciar la regla de detalle progresivo (la referencia por referencia) y sigue **sin** aprobar; el bloque estático del paquete del reviewer sigue por debajo del techo declarado. | los tests de 005-007 (`tests/test_005_007_t1_progressive_detail_rule.py`:295-307) verdes sin cambio; tamaño del bloque estático (`common.md` + `roles/reviewer.md` + `substages/reviewer-plan-review.md`) con la medición y el techo (`cdad_packet.py`:1015-1027) |
| **PD-13** | **El recorrido de aceptación (U6) en un proyecto descartable.** En un proyecto **descartable** (nunca el proyecto activo, nunca el HOME): (a) un borrador de **spec sin plan** se revisa, se recibe y su dictamen se materializa en `docs/specs/<F>/`; (b) un borrador de **spec + plan** se revisa con los dos digests fijados; (c) un borrador de **otra** feature se revisa y su dictamen aterriza en la carpeta de la feature activa nombrando el objeto; (d) tras corregir el borrador, el digest cambia y la re-review focal queda requerida; (e) **ninguno** de los tresreviews deja estado de aprobación. Se declaran versión y configuración observadas y **no se generaliza**. | los tres paquetes, sus `REQUEST.json` (digests), los tres recibos (`pending`), los tres dictámenes materializados con su carpeta destino, el estado resultante (sin aprobación) y la comparación de digests del caso (d) |
| **PD-14** | **La revisión no habilita construir y no es insumo del test-writer.** Con el dictamen recibido y materializado, `prepare` para el rol test-writer **sigue rechazando** sin la entrada de aprobación con su pin; el dictamen no aparece entre las entradas del paquete del test-writer; la revisión del **resultado** (etapa 4) no se toca. | el rechazo de `prepare` (test-writer) con el diagnóstico de `approval pending`; el `inputs` del paquete del test-writer; la superficie de la etapa 4 sin cambios (grep) |
| **PD-15** | **Los guardas vigentes de pairing y de rol siguen verdes.** `draft-plan` con otra subfase ⇒ rechazo; `plan-review` sobre un kind aprobado ⇒ rechazo; `draft-plan` para un rol ≠ reviewer ⇒ rechazo; un kind `approved-*` que declare las claves nuevas ⇒ rechazo (forja). Los cuatro casos son los de `cdad_packet.py`:909-919, :920-942 y :4693-4696, ampliados por PD-1/PD-4. | los tests vigentes de 004-003 T1/T2 (`tests/test_004_003_t1_draft_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_004_003_t2_reviewfix.py`) verdes sin cambio de oráculo + los casos nuevos de forja |

### 3.1 Escenarios de recorrido (E1..E6) — la vara

Cada escenario es la **intención** de la feature expresada como recorrido comprobable: si todas las PD de su fila pasan, el escenario tiene que funcionar **de verdad**. Un escenario no cubierto es un hueco: se cubre o se declara.

| Escenario | Qué tiene que funcionar (recorrido) | PD que lo garantizan | Hueco declarado |
|---|---|---|---|
| **E1** | **Una feature mediana (spec sin plan) puede ser revisada.** El architect entrega el borrador de la spec; el orquestador prepara el encargo de revisión con la **forma declarada** (`--object-kind spec`); el reviewer revisa en **sesión independiente**; el dictamen se recibe y se materializa como `docs/specs/<F>/plan-review.md`; el state **no** registra aprobación; la aprobación viene aparte. | PD-1, PD-3, PD-5, PD-7, PD-10, PD-12, PD-13, PD-14, PD-15 | **Ninguno** para el recorrido mecánico. **Declarado**: la revisión es *supervisada* — el CLI no verifica que el dictamen exista ni que sus bloqueantes estén resueltos; esa comprobación es del gate y de la autoridad (Q2, §13.4). |
| **E2** | **Una feature compleja (spec + plan) se revisa como un objeto único, con las dos identidades fijadas.** El contrato fija el plan **y** la spec por digest; el paquete lleva los dos documentos; los checks del plan se aplican **al plan** y no a la spec; el dictamen nombra **ambos** digests; una corrección en cualquiera de los dos invalida la cobertura de la revisión anterior. | PD-1, PD-2, PD-3, PD-4, PD-5, PD-8, PD-13, PD-15 | **Ninguno**. La **identidad doble** (Q4) es por digest, no por cadena de versiones: la versión de cada documento viaja **junto a** su digest, y el digest es lo comparable con `sha256sum`. |
| **E3** | **Un borrador que enmienda la spec de OTRA feature se puede revisar** — la necesidad que vino del proyecto consumidor, donde no se pudo pedir la review de un borrador de spec y el reviewer rechazó dos paquetes con razón (contrato por defecto = spec aprobada; el plan de la épica no es admisible para el reviewer; `draft-plan` exige `plan-tasks`). En la ejecución de la feature **A**, el objeto es `docs/specs/<B>/spec.md`: el paquete nombra el objeto exacto con su digest y **deja visible** que la feature activa es A y el objeto es de B; el dictamen aterriza en `docs/specs/<A>/` (la carpeta del gate que lo consume) **nombrando el objeto y su digest**; nada se materializa en la carpeta de B. | PD-1, PD-4, PD-5, PD-6, PD-7, PD-13 | **Ninguno** mecánico. **Cota declarada (Q3)**: el dictamen **no** puede vivir en la carpeta de la otra feature sin tocar la tabla cerrada de destinos — **fuera de alcance** de esta feature (y declarado como deuda, §8). |
| **E4** | **La re-review tras la corrección es focal y verificable.** El architect corrige → versión nueva → digest nuevo; la revisión anterior **no** cubre los bytes nuevos (comprobable, no declarativo); la re-review verifica **los bloqueantes acordados contra su condición de cierre** y las regresiones del arreglo (calibración, regla 4), sin abrir una caza de variantes nueva. | PD-8, PD-10, PD-12, PD-13 | **Ninguno** mecánico. **Declarado**: la re-review es **focal por la calibración**, no por una regla absoluta (§13.2: «no hay regla absoluta»); el caso de una corrección puramente mecánica puede no requerir re-review separada (calibración, regla 6). |
| **E5** | **El dictamen no aprueba ni habilita construir.** El dictamen no lleva marca de aprobación; el recibo queda `pending`; `materialize` exige `approval_effect: false`; el estado no registra aprobación; el test-writer sigue bloqueado sin el pin de aprobación de la spec. | PD-7, PD-14, PD-15 | **Ninguno**. |
| **E6** | **Un plan (o una spec) coherente entre sí pero que NO alcanza la intención es rechazado.** El revisor lo declara **bloqueante**; el architect lo corrige o la autoridad lo descarta con razón escrita; el gate 2→3 no se pasa con el bloqueante abierto. | PD-10, PD-12, PD-13 | **Declarado**: el «no alcanza la intención» es un **juicio semántico** del revisor; el producto no lo puede verificar. Lo que el producto garantiza es la **vara**: la intención viaja **como escenarios de recorrido** (§3.1) y el revisor traza cada escenario por las PD. La evidencia de que la vara funciona es el recorrido real (PD-13). |

## 4. Invariantes (INV-n)

- **INV-1.** La revisión de borrador **no aprueba nada**: nunca una marca de aprobación en el dictamen, nunca `semantic_status` distinto de `pending`, nunca `approval_effect: true`, nunca una entrada de estado que habilite construcción por su cuenta.
- **INV-2.** **El objeto revisado siempre está fijado por digest.** Una revisión sin digest fijado no es una revisión: el paquete lo lleva, el dictamen lo nombra y la cadena recibo → paquete → `REQUEST.json` lo hace recuperable.
- **INV-3.** **La forma se declara; nunca se infiere.** Ni por el contenido del documento (token `plan-tasks`), ni por su ruta (`spec.md`/`plan.md`), ni por el nombre del kind. La forma viaja en el encargo.
- **INV-4.** **Sin kind, subfase, agente, stage, tipo de artefacto ni verbo nuevos.** Se reutilizan `draft-plan`, `plan-review`, el rol reviewer, la etapa 2 y el kind `plan-review` → `docs/specs/<feature>/`. Los nombres se conservan **con la deuda declarada** (§10).
- **INV-5.** **Las reglas del plan no juzgan a una spec.** Los checks estructurales y por tarea se aplican exclusivamente al documento cuya forma es `plan`; una spec nunca se rechaza por no traer un bloque `plan-tasks`.
- **INV-6.** **Falla cerrado por omisión.** Sin `object_kind`declared, el objeto se trata como plan: el comportamiento vigente se conserva y el olvido de la bandera produce un rechazo, nunca una aceptación silenciosa.
- **INV-7.** **La exención es del owner, explícita y registrada, y no amplía la autoridad.** La exención se registra en la entrada que abre el gate, con `exempted_by`, `delegated`, `requested_by` y `reason`; no cambia el pin de la aprobación, no habilita construcción y no se concede por defecto (Q5).
- **INV-8.** **El dictamen no es insumo del test-writer.** No entra en el paquete del test-writer, no lo habilita y no altera el aislamiento de ese rol.
- **INV-9.** **Una sola fuente por regla.** «Qué se revisa» vive en un único archivo (`packets/substages/reviewer-plan-review.md`); el rol, la plantilla y la re-entry lo **referencian**. La calibración sigueHaving un único dueño (`references/stage-4-review.md`).
- **INV-10.** **El cambio es aditivo y no reescribe lo vigente.** Sin las claves nuevas, el render es byte-idéntico, los paquetes publicados antes siguen siendo recibibles y los oráculos vigentes se conservan (PD-2, PD-15).
- **INV-11.** **El paquete no miente sobre lo que lleva.** El `purpose` de cada input describe la forma real del documento; la sección `## Contract` nombra la forma y la identidad acompañante.

## 5. Decisiones (D-n)

- **D-1 — La forma la declara el encargo (`contract.object_kind`), no el objeto.** Adoptada por el orquestador (O2). *Rechazadas:* (a) **inferencia por el contenido** (O1: si el documento lleva el token `plan-tasks`, es un plan) — infiere y además **relaja** la puerta de un plan mal formado, rompiendo el oráculo vigente de PD-8; (b) **inferencia por la ruta** (O3: `docs/specs/<X>/spec.md` es spec, `plan.md` es plan) — infiere, impone una restricción de rutas que hoy no existe (deuda ADR-013 O-C) y **rompe los fixtures compartidos** (11 archivos de test usan `DRAFT_PLAN_RELPATH`); (c) **bloque `plan-tasks` vacío dentro de la spec** (O4: hoy pasa) — mete un bloque artificial en el spec, deja el `purpose` mintiendo («draft plan for review» para una spec), mantiene el procedimiento plan-céntrico y deja el modelo mental intacto: el próximo agente repetirá el rodeo. Es el rodeo que 006-005 ya usó (commits `82f8806`, `b9a52a3`) y por eso queda **declarado como parche de emergencia**, no como diseño.
- **D-2 — El valor por omisión de la forma es `plan`.** Consecuencia: **el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 se conserva sin cambio** y los **11 archivos de test** que comparten el fixture `DRAFT_PLAN_RELPATH` (`tests/test_004_003_t1_draft_contract.py`:47) **no se tocan** — no hay coordinación de fixtures compartidos con el test-writer. Es la dirección fail-closed: el olvido de la bandera **rechaza**, no acepta.
- **D-3 — La identidad doble viaja como dos documentos fijados, no como una cadena de versiones.** El principal es el plan cuando existe; la spec es el acompañante, fijada por `spec_path`/`spec_sha256`/`spec_version`. *Rechazada:* la versión como cadena de caracteres — el digest es lo único comparable con `sha256sum`; una cadena puede coincidir mientras los bytes no.
- **D-4 — Los checks del plan se aplican al documento cuya forma es `plan`.** Regla única, sin excepciones ni listas de excepciones.
- **D-5 — La revisión es obligatoria y proporcional; la exención es del owner, explícita y registrada.** Q5 y Q1. La profundidad la fija la calibración vigente; no se exige familia ni modelo (A-5 vigente).
- **D-6 — La exención se registra en la entrada que abre el gate**, con tres banderas opcionales nuevas sobre la clase `gate` ya existente. *Rechazadas:* (a) una entrada libre en `stage_history` — flotaría sin relación con el gate y no la verifica nadie; (b) una clase de transición nueva — amplía superficie en la maquinaria de 005-012 para un caso periférico; (c) la exención como texto dentro del `note` — la información deja de ser estructurada y por tanto no es verificable; (d) la exención como `approved_by` — confunde «quién exime» con «quién aprueba», que la decisión Q1 mantiene separados.
- **D-7 — «Qué se revisa» tiene un dueño único y el resto lo referencia.** El substage se generaliza al objeto de especificación; `packets/roles/reviewer.md`, `sources/roles/reviewer.md`, `handoff-prompts.md` y `re-entry.md` lo referencian. *Rechazada:* una segunda regla para el caso «spec sola» — dos dueños derivan.
- **D-8 — La tabla de destinos no se amplía.** El dictamen de un borrador de otra feature vive en la carpeta de la feature activa y nombra el objeto. *Rechazada:* materializar en la carpeta del objeto — tocaría la tabla cerrada (`cdad_result.py`:672-678) y ampliaría el alcance de la feature (Q3).
- **D-9 — «El dictamen nombra el digest» es obligación de procedimiento, no un enforcement nuevo en `materialize`.** Razón: el CAS de `materialize` protege el destino, no el objeto; la trazabilidad del objeto es **ya recuperable** por la cadena recibo → paquete → `REQUEST.json`; y atar el texto libre de la parte a un digest volvería frágil la recepción (un error tipográfico del revisor = fallo tardío) sin ganancia real. *Rechazada:* la comprobación en `materialize` —.exigiría A-1 sobre dos tests de materialización (`tests/test_003_002_t2_reviewfix.py`:871-904 y `tests/test_006_005_u2_opencode_module.py`:1378-1392) a cambio de una garantía que la trazabilidad ya da.
- **D-10 — El gate 2→3 es supervisado.** Criterio en el gate y en el exit gate; el CLI no lo bloquea. *Rechazada:* un bloqueo duro en el CLI — el §13.4 lo excluye explícitamente.
- **D-11 — Se conservan los nombres.** `draft-plan`, `plan-review`, `plan_version` y el artefacto `plan-review.md`. La deuda está declarada (§10) y no se renombra en esta feature.

## 6. Desconocidos (V-n) y su resolución

- **V-1 — ¿El producto instalado (copia por archivo) renderiza el paquete con la forma declarada?** El árbol `skills/cdad-cycle/` viaja completo al instalarse (`install.sh`:376) y el substage viaja con él; lo **no medido** es el render del CLI instalado con `--object-kind`. *Resolución:* RED de la **installed product** (el patrón de `tests/test_004_003_t2_plan_review.py`:290, que ya renderiza `plan-review` desde el producto instalado sin el repo fuente), con comparación byte a byte contra el render del repo.
- **V-2 — ¿`cdad-generate.py` sigue siendo determinista con la fuente del rol cambiada?** *Resolución:* dos corridas de `make staging` con comparación byte a byte de los cuatro agentes del reviewer; si no fuera determinista, es un defecto de 004-001 ya cubierto por sus propios tests.
- **V-3 — ¿`receive` revalida el request con el conjunto de claves ampliado?** `cdad_result.py`:561 llama a `validate_request`, que es **la misma función** que `prepare` usa ⇒ el conjunto cerrado ampliado aplica en ambos lados. *Resolución:* RED que **recibe** un paquete cuyo contrato lleva `object_kind` (hoy sería rechazado por el conjunto cerrado); el RED lo demuestra, no lo supone.
- **V-4 — ¿La entrada de exención interfiere con la regla de «una sola aprobación `specification` vigente» (PD-14)?** La regla exige `stage == "specification"` **y** un pin de contrato; la exención viaja **en la misma entrada** que la aprobación, no en una entrada nueva ⇒ no hay una segunda aprobación que compita. *Resolución:* RED que registra la aprobación con exención y verifica que el cierre (PD-8(b)) la reconoce como vigente, y que una segunda aprobación sin `--supersedes` **sigue** rechazándose.
- **V-5 — ¿El techo del bloque estático admite el substage generalizado?** Medido: el bloque del reviewer/plan-review ocupa **2728 bytes** con un techo declarado de **12000** (`cdad_packet.py`:1015-1027) ⇒ holgura de 9272. *Resolución:* la medición se repite en el RED de U2 y se registra; si el substage广义 la superara, el RED falla (y la respuesta es **no** subir el techo).

## 7. Medición de la aceptación

- Se mide lo **observado**: rc de cada comando, digests fijados y observados, carpetas destino de los dictámenes, campos de los recibos, el estado antes/después, el tamaño del bloque estático y los bytes de los dos `make staging`. **«Desconocido» no es cero** y **no se generaliza** el resultado de un recorrido.
- **No** se fijan reducciones porcentuales, tiempos ni tamaños como meta.
- La evidencia de que la **vara** (E1-E6) funciona es el recorrido real (PD-13), no una simulación: un recorrido que no atrapa ningún defecto es **buen resultado** y se declara igual (epic §13, «recepción real»).
- La **suite completa** la corre **una vez**, quien cierre (política declarada en el paquete); las unidades citan su propia evidencia focal y las regresiones de su ficha.

## 8. Fuera de alcance

1. **Ampliar la tabla cerrada de destinos** para que el dictamen de un borrador de otra feature viva en la carpeta de esa feature (D-8; Q3 lo excluye).
2. **Renombrar** `draft-plan` / `plan-review` / `plan_version` (D-11; deuda de nombre, §10). El nombre `draft-spec` que se mencionó en `execution.md`:352 **queda derogado** por `execution.md`:362-364.
3. **Un comando de comparación de digests** o de detección automática de deriva: la comparación la hace el orquestador con `sha256sum` y el `REQUEST.json` (D-9, PD-8).
4. **El bloqueo duro del gate 2→3 en el CLI** (D-10; §13.4).
5. **La revisión formal del resultado** (etapa 4) y la calibración: no se tocan.
6. **La deuda ADR-013 O-C** (restringir el `contract.path` a `docs/specs/<feature>/`): declarada, no se cierra aquí.
7. **El transporte, la delegación, la política de Bash** y las features 006-003/006-004/006-005: no se tocan.
8. **La autorización y el modelo**: la revisión no exige familia ni modelo (A-5 vigente) y no habilita construir.

## 9. Riesgos residuales

- **El olvido de `--object-kind` se manifiesta como un error poco informativo** (la puerta `plan-tasks`). *Mitigación:* la ayuda de diagnóstico que nombra la bandera (PD-3) sin relajar el rechazo. *Riesgo residual:* mínimo y en la dirección segura.
- **La deuda de nombre proyecta una imagen falsa** (una «plan-review» de una spec). *Mitigación:* deuda declarada (§10) y el `purpose`/la forma correctos en el paquete. *Riesgo residual:* aceptado por decisión del owner (Q6).
- **El gate supervisado puede ser saltado** por un orquestador que no siga el procedimiento (el CLI no verifica la existencia del dictamen). *Riesgo residual:* **declarado y aceptado** por §13.4; la mitigación es la disciplina del gate, no el enforcement.
- **La exención puede volverse costumbre** (es más barata que revisar). *Mitigación:* Q5 la prohíbe **por defecto** y la exige del owner, explícita y registrada; la entrada queda en `stage_history`, visible.
- **La re-review focal depende del juicio del revisor** sobre si la corrección cambió el diseño. *Riesgo residual:* la calibración (reglas 4 y 6) lo gobierna; no hay regla absoluta (§13.2) y así queda declarado.

## 10. Límites y deuda declarada

- **Deuda de nombre (decidida, Q6).** El kind `draft-plan`, la subfase `plan-review`, el artefacto `plan-review.md` y el campo `plan_version` **se conservan** aunque la revisión sea de una spec. Consecuencias aceptadas: `plan_version` transporta la versión del documento principal (que puede ser una spec); el `purpose` del input sí distingue la forma («draft spec for review» / «draft plan for review»); el nombre del kind y de la subfase siguen diciendo «plan». **Condición de cierre:** cuando exista una revisión del nombre, el cambio debe tocar el enum cerrado de kinds (`cdad_packet.py`:52-53), los enums de schema (`assets/packet-request.schema.json`, `assets/result-receipt.schema.json`, `assets/active-packet.schema.json`), la plantilla y los oráculos de 004-003 — es un trabajo **acotado pero de coordinación**, y esta feature no lo hace.
- **Deuda de la puerta `plan-tasks`.** El nombre del token y del bloque sigue diciendo «plan-tasks» aunque el objeto pueda ser una spec. Se conserva por el mismo motivo.
- **Deuda ADR-013 O-C.** El `contract.path` de un borrador puede ser cualquier ruta del proyecto: no hay restricción a `docs/specs/<feature>/`. Declarada en el discovery; **fuera de alcance** (§8.6).
- **Deuda de laAmbientación.** El veredicto de un borrador de otra feature no puede vivir en la carpeta de esa feature (D-8, Q3).
- **Deuda de la exención en el CLI.** `delegated` y `requested_by` **sí** quedan producibles por el verbo (D-6); lo que queda fuera es la *verificación* de que la exención sea del owner y no de un tercero — la **autoridad** la verifica `register-transition` por su cuenta (`_gate_authority`), y el nombre del owner viaja como texto declarado, no como identidad criptográfica. Declarado: la exención es un acto de autoridad registrado, no una firma.

## 11. Trazabilidad con el contrato de la épica

| Aceptación (epic §13) | PD |
|---|---|
| el reviewer recibe y revisa borradores sin aprobación ficticia, incluida una spec sin plan | PD-1, PD-3, PD-5, PD-7, PD-13 |
| puede rechazar una spec y un plan coherentes entre sí que no cumplen la intención | PD-10, PD-12, PD-13 (E6) |
| el dictamen no equivale a aprobación | PD-7, PD-14 |
| un cambio en la spec o en el plan después de la revisión se detecta | PD-8, PD-4 |
| la conducta está en los artefactos instalados | PD-1..PD-6, PD-10, PD-11 (V-1) |
| `make validate` y la suite pasan | PD-11, PD-12 + plan §5 |

