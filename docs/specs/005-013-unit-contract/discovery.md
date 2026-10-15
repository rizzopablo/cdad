# Discovery — 005-013-unit-contract (etapa 1)

**Rol:** architect · **Subetapa:** discovery · **Contrato:** `docs/epics/epic-005-real-operation/plan.md`
(aprobado, sha256 `63dda3b8…`) · **Estado:** mapeo técnico y brainstorming. **NO se propone el contrato**
(eso es la subetapa `draft`). **Lectura:** solo lectura; ninguna escritura en el repo. Única escritura:
el archivo de transporte `<tmp>/opencode/discovery-005-013.md`.

Fila 13 del plan (`plan.md:46`), secciones que prevalecen (`plan.md:48-88`, declaradas en `:57-58`),
criterios del epic (`:90-111`), «Operación» (`:119-126`), «Autoridad» (`:128-134`) y «Cambios al plan»
(`:141-257`). Insumos de contexto: `execution.md` (criterio de review 2026-10-12 y «Insumos para la
planificación siguiente», `:83-96`), `skills/cdad-cycle/references/project-execution.md`,
`skills/cdad-cycle/references/re-entry.md`, `skills/cdad-epic/SKILL.md`,
`docs/specs/005-001-idle-and-v7-bootstrap/spec.md`.

## 0. Método y procedencia

- Código citado: `skills/cdad-cycle/scripts/cdad_packet.py` (4441 líneas),
  `skills/cdad-cycle/scripts/cdad_result.py` (1535), `skills/cdad-cycle/scripts/cdad_continuity.py` (1355).
  Verificado que el código de producto del repo es byte-idéntico al instalado: `git diff --name-only
  7212ead..HEAD` devuelve **solo** 8 archivos bajo `docs/` (ninguno de producto), así que el CLI citado
  es el que corre (7212ead).
- Instrucciones del paquete verificadas por hash: `packets/common.md`
  (`37609c56…`), `packets/roles/architect.md` (`268804ca…`),
  `packets/substages/architect-discovery.md` (`1a1d0d19…`) — coinciden con los `instruction_sources` del
  paquete.
- Contrato verificado: `sha256(docs/epics/epic-005-real-operation/plan.md) =
  63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, igual al `contract.sha256` del
  paquete y a `state.active_packet.contract_sha256`.
- Estado consultado de forma dirigida (no se leyó el state completo, ~530 KB): `active_epic`,
  `active_feature`, `current_stage`, `active_packet`, `execution`, `hitl_delegation`, `approver`,
  `version`, `epic_features` y las entradas `epic_history` de `stage=epic-plan`.
- Todo dato no verificado se marca **VERIFY** o **desconocido**. No se inventan interfaces.

## 1. Dónde vive hoy el pin del plan completo y quién lo consume

### 1.1 Las cuatro piezas del pin

| Pieza | Dónde vive | Quién la lee |
|---|---|---|
| Objeto `contract` del request (`kind`,`path`,`sha256`,`commit`) | `REQUEST.json` publicado por `prepare` (`cdad_packet.py:3518-3520`, digest en `:3557-3559`, armado en `:3583`); se rinde en `PACKET.md` (`:914-916`) | `validate_request` (`:824-827`), `render`/`validate-request`/`validate-packet` (`main`, `:4423-4432`), `--resume-packet` (`:1811-1836`), `receive` (`cdad_result.py:513`), evidencia de corrida (`cdad_result.py:1156`, `:1169-1172`) |
| `active_packet.contract_sha256` | `docs/.cdad-state.json` | `_validate_active_packet` (`:469-498`), `validate_request` (`:858`), `--replace-packet` (`:2062-2065`), vista `status` (`:4086-4090`) |
| `epic_history[stage=epic-plan].plan_path` / `plan_sha256` | `docs/.cdad-state.json` | **NADIE**: `grep -rn plan_sha256 skills/ scripts/ agents/ sources/` no devuelve consumidores |
| `_contract_for` (arquitecto → `approved-epic-plan`, `docs/epics/<epic>/plan.md`) | `cdad_packet.py:995-1008` | `prepare` (`:3517`), `--replace-packet` (`:1999`) |

El kind/path esperado por rol se fuerza en `validate_request` (`:814-819`): para `architect`,
`kind == "approved-epic-plan"` **y** `path == "docs/epics/<epic_id>/plan.md"` exactos.

### 1.2 La nota verificada que decide el diagnóstico

- La **aprobación del arquitecto no pinea hash**: `_approved_epic_plan_entry` (`:1346-1360`) exige solo
  una entrada `epic_history` con `stage == "epic-plan"` y `approved_by` no vacío; el comentario D2
  (`:1349-1350`) lo declara: «there is no hash pin (D2, the epic plan is the epic's live mandate, not a
  frozen feature contract)». `_contract_approval_for` (`:1378-1411`) solo verifica la existencia de esa
  entrada para el arquitecto. Confirmado además por el estado: 7 entradas `epic-plan` de epic-005 (6 con
  `plan_sha256`) y ningún consumidor de `plan_sha256`.
- El **request/paquete sí pinea** el sha del plan: `contract.sha256` (`:825-827`) y
  `active_packet.contract_sha256` (`:858`).

**Conclusión (sin ampliar el diagnóstico):**
1. El pin que **bloquea hoy el trabajo en curso** es el **pin del paquete** (`contract.sha256` del
   `REQUEST.json` + `active_packet.contract_sha256`), re-verificado contra los **bytes actuales** del
   archivo por `validate_request` (`:824-827`). Ese mismo `validate_request` es el punto único que usan
   `prepare`, `render`, `validate-request`, `validate-packet`, `--resume-packet` y `receive` (comentario
   explícito en `:828-831`).
2. El pin de la **aprobación** (`epic_history.plan_sha256`, el frontmatter `approved_at` del plan
   `plan.md:6-7`, la sección «Aprobación» `:136-139`) es **histórico/informativo**: no habilita ni
   bloquea nada. La vista `status` **muestra** `active_packet.contract_sha256` como
   `authority.approval.contract_sha256` (`:4086-4090`), pero es display, no control.

Matiz preciso del «bloqueo»: `prepare` de un paquete **nuevo** no falla por el cambio del plan (recomputa
el digest en `:3557-3559`); lo que falla es (a) `prepare` mientras exista un `active_packet` no terminal
(PD-4, `:3506-3510`) y (b) la validación/re-emisión/recepción del paquete **ya publicado** cuando el plan
cambió. Es decir, el trabajo en curso se bloquea en el **paso de validación/recepción**, no en el despacho.

### 1.3 Qué comandos fallan cerrado ante un cambio de bytes del plan

- **Fallan cerrado:** `render`, `validate-request`, `validate-packet` (vía `validate_request:826-827`,
  «contract sha256 does not match exact content»); `prepare --resume-packet` (`:1819-1836`, marcador
  `packet obsolete`, que nombra el registrado y el actual y, si `status == dispatched`, señala
  «reconciliation of the dispatched packet is required»); `receive` (`cdad_result.py:513`);
  `run-python-unittest` / `validate-run-evidence` (`cdad_result.py:1156`, `:1169-1172`).
- **No se ven afectados:** `status` (solo comprueba **existencia** del plan, `_plan_marker`
  `:3996-4006`); `validate-state`; `validate-policy`; `open-unit` (solo lee `epic_features`/state,
  `:3700-3766`); `prepare --record-dispatch` (lee `REQUEST.json`, no los bytes del contrato);
  `prepare` de un paquete nuevo (re-pinea).
- `--replace-packet` es la única salida y **solo** para un paquete `prepared` no despachado
  (`:1958-1967`; spec 005-001 PD-10): un paquete **`dispatched`** no tiene operación de CLI para
  reconciliar su contrato. Precedente citado en el plan (`:185-187`): la edición del 2026-10-08 retiró
  manualmente el paquete `005-001-…-architect-discovery-001`.

## 2. La estructura del plan como FUENTE de una proyección

### 2.1 Cómo se delimita hoy una unidad

- La unidad vive en su **fila de la tabla «Entregas»** (`plan.md:32-46`): columnas Orden, Feature,
  Resultado verificable, Dependencias. La fila 13 es 1 línea / 1485 bytes. La selección por id de feature
  es determinista (comparar la columna Feature).
- Es la forma gruesa de la **ficha de unidad** canónica
  (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md:62-80`) y de las fichas de
  tarea de los planes de feature (`docs/specs/005-011-common-entry/plan.md` §4, `T1..T4`), que el
  validador de `prepare` consume en su forma de máquina (`plan-tasks`, ver §3).

### 2.2 Qué otras partes del plan le aplican

| Sección | Líneas | Bytes | Rol |
|---|---|---|---|
| Fila de la unidad (tabla «Entregas») | 46 | 1485 | objetivo/alcance/aceptación de la unidad |
| «Ajuste de los ciclos pendientes» | 48-88 | 2808 | **prevalece sobre las filas** (declarado en `:57-58`) |
| Criterios de aceptación del epic | 90-111 | 1500 | restricción compartida |
| «Operación» | 119-126 | 457 | restricción compartida |
| «Autoridad» | 128-134 | 367 | restricción compartida |
| «Cambios al plan» | 141-257 | 8413 | **historia** de cada edición y de cada cambio de hash |

### 2.3 Qué es delimitable de forma determinista y qué no

- **Determinista:** la fila de la unidad (por id); las secciones completas por encabezado (los
  extractores por encabezado ya existen: `PLAN_TASK_HEADING`, `_plan_task_ficha`, `cdad_packet.py:3157-3173`).
- **NO determinista (hay que ATRIBUIR, no parsear):** *qué* viñeta de «Ajuste de los ciclos pendientes»
  aplica a una unidad concreta (p. ej. la de 005-002 vs la de 005-013). Por eso la proyección debe
  **incluir la sección entera** (sobre-inclusiva y determinista) y dejar el sentido a la **review**, sin
  heurísticas de listas de palabras.
- **Excluir «Cambios al plan»** del cuerpo de la proyección (es historia): si se incluyera, cualquier
  edición —incluida la propia historia— cambiaría la proyección y volvería a invalidar todo, que es el
  problema a resolver.
- La proyección puede apoyarse en la **forma de ficha** ya existente (§2.1): el plan del epic ya declara,
  por unidad, su resultado verificable y sus dependencias; no hace falta una segunda estructura
  mantenida a mano.

## 3. Piezas por unidad que YA existen (no duplicar)

- **Bloque canónico `plan-tasks` + validador:** el fence se parsea en `_plan_tasks_from_contract`
  (`:2883-2952`), se valida con `_check_plan_tasks` (`:2954-3069`, productor/consumidor, contratos
  compatibles, ciclos, paralelismo) y `_check_plan_validation_plan` (`:3072-3145`, validación por tarea),
  y se **rinde por referencia** al paquete con `--plan-task` / `_plan_task_sections` (`:3150-3260`,
  `PLAN_RELPATH_TEMPLATE = "docs/specs/{feature_id}/plan.md"` en `:3156`). **Es para planes de FEATURE**;
  el plan del epic no tiene ese bloque.
- **Procedencia por fuente:** `_plan_task_sections` rinde `Plan provenance: <path> (sha256 …)` (`:3252`)
  y `Applicable contract … (sha256 …)` (`:3254-3256`); el paquete lleva `instruction_sources` con
  path+sha (`:906-909`).
- **`--plan-version` / `draft-plan`:** un contrato borrador **declarado** es reviewer-only y exige el
  triplete `--contract-kind --contract-path --plan-version` (`:3527-3546`); `plan_version` es obligatorio
  para `draft-plan` y **prohibido** en los kinds aprobados (`:784-792`).
- **Registro durable por paquete:** `.cdad/packets/<id>/.superseded.json` con `reason`,
  `superseded_at`, `contract_sha256_old/new` y la traza `conserved_fields`/`changed_fields`
  (`:2078-2086`, `ASSIGNMENT_UNIVERSE` en `:1846-1849`) — precedente exacto de un registro de impacto por
  cambio de contrato.
- **Regla de fuente única:** el formato del bloque canónico se declara **una sola vez** y los
  consumidores lo referencian, nunca lo copian
  (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md:87-93`); la ficha vive «en el
  plan existente; no crear otro archivo si duplica datos» (`:64`); el mismo criterio en
  `skills/cdad-cycle/references/stage-2-specification.md:119`.

**Evaluación:** la proyección de unidad **no** debe apoyarse en un bloque `plan-tasks` *mantenido a mano*
dentro del plan del epic: eso sería una **segunda declaración** de datos que la tabla ya contiene
(violaría `:64` y `:87-93`). Sí debe apoyarse en: (a) el **objeto `contract`** como portador del pin;
(b) el **patrón de generación por referencia** (`_plan_task_sections`); (c) el **registro durable**
`.superseded.json`; (d) los campos de origen que `epic_history` ya guarda (`plan_path`/`plan_sha256`).
La **pieza nueva** es un **generador determinista de la proyección de unidad** a partir del plan (fila de
la unidad + secciones compartidas nombradas), publicado con sus bytes y con su digest.

**Riesgo verificado que condiciona el diseño:** hoy `_plan_task_sections` **re-resuelve** desde el plan en
cada render (`:3225-3227`, `:3235-3252`) y `_resume_packet` compara `actual != rendered` (`:1839-1840`).
Consecuencia: en un paquete que declara `plan_task`, una edición del plan **rompe el resume** con «does
not match its canonical rendering» (no con `packet obsolete`). Por eso la proyección debe **generarse una
vez, persistirse y pinearse sobre los bytes generados**, no re-generarse en cada validación.

## 4. Consecuencias por TIPO DE CAMBIO (fila 13 (b))

Hoy **no existe** un mecanismo que clasifique el cambio. El comportamiento es uniforme: el pin derivó →
todo falla cerrado igual.

- **Vocabulario de marcadores vigente:** `approval pending` (`:1406-1411`, `:1417-1424`, `:1434-1451`,
  `:1477-1484`); `packet obsolete` (`:1829-1836` para resume, `:1963-1967` para replace);
  `state incoherent` (`:501-531`); PD-4 «complete or fail it before preparing a new packet»
  (`:3506-3510`); `--replace-packet` como salida **manual** (PD-7..PD-11, `:1924-2105`; spec 005-001
  PD-7..PD-11); la reconciliación de la **continuidad** (`cdad_continuity.py reconcile`, `:994-1060`) con
  su vocabulario cerrado en `_classify` (`:965-991`): `expired-authority`, `unknown`, `already-closed`,
  `received`, `dispatched-unknown`, `not-started` — es reconciliación de *efectos*, no de *contrato*.
- **Dónde el state registra hoy una nota de impacto o de motivo:** el campo libre `note` de las entradas
  de `stage_history` (escrito a mano por el orquestador; p. ej. la entrada `specification` de la
  reapertura de 005-003 y las notas de cierre), el `note` de `delegation_history`, y el registro durable
  `.superseded.json` (con `reason` y los dos sha).
- La fila 13 (b) pide distinguir (i) cambio sin efecto, (ii) cambio que **registra el impacto** y exige
  decisión del orquestador, y (iii) retiro de autorización o restricción de aplicación inmediata que
  **impide** las acciones afectadas. Esa distinción **no existe hoy**; el insumo para construirla es
  comparar la proyección previa con la nueva **por parte etiquetada** (fila de la unidad / sección
  compartida / autorización). **VERIFY (diseño, no código):** la etiqueta de «aplicación inmediata» no
  está hoy en el plan; el draft deberá decidir si se declara en la proyección o se atribuye por review.

## 5. Recepción contra el contrato recibido (fila 13 (c))

`receive` (`cdad_result.py:493-589`) liga:

- descriptor (`execution_id`, `packet_id`, `feature_id`) contra la ejecución y el paquete (`:521-526`);
- el `REQUEST.json` (`:512`) y el `PACKET.md` contra su render canónico (`:515-518`);
- el execution context (`:510-513`);
- `active_packet.status == "dispatched"` (`:527-531`);
- validación de alcance (`:534-535`).

Emite un recibo con `semantic_status: "pending"` y `state_transition_requested: "received"`
(`:575-576`), durable e idempotente (`:501-507`, `:581-588`). **El recibo no guarda
`contract_sha256`** (claves en `:550-578`).

**Qué impide hoy recibir un paquete despachado cuyo plan cambió:** `cdad_result.py:513` llama a
`cdad_packet.validate_request`, que en `:824-827` compara `contract.sha256` con el sha de los **bytes
actuales** del archivo del contrato. Si el plan cambió, la recepción falla con «contract sha256 does not
match exact content», aunque el agente haya trabajado contra el contrato que efectivamente recibió.

**Qué habría que cambiar (dirección, sin fijar contrato):** que la validación de un paquete de unidad se
haga contra la **proyección registrada** (los bytes que el paquete recibió y que quedan durables en el
directorio del paquete), no contra el archivo vivo del plan. La recepción **ya** es neutral: no aprueba
(`semantic_status` siempre `pending`), la materialización es CAS con `approval_effect: false` y la
transición del state es **solo** del orquestador (`re-entry.md:54-63`). El contrato recibido es
reconstruible desde el `REQUEST.json` durable + los bytes de la proyección, así que **no** hace falta
tocar el esquema del recibo (mínimo). No se amplía autoridad ni se aprueba al recibir.

## 6. «Aprobación y versión de origen» de la proyección (fila 13 (a), último ítem)

- La aprobación del plan del epic habilita al arquitecto por **existencia** de la entrada `epic_history`
  `epic-plan` con `approved_by`, **sin** pin (D1/D2, `:1346-1360`; `project-execution.md:60-63`).
- `hitl_delegation` (state): `status: active`, `epic_id`, `source`, `scope` (`project-execution.md:75-80`).
  En este epic, `approver` = «Pablo (HITL delegada al orquestador OpenCode…)» y `policy_sha256` =
  `f508ab1e…` (ambos surfaced por `status`, `:4057` y `:4085`).
- **Origen a registrar para la proyección:** id de la unidad + path del plan + sha del plan **al momento
  de generar** + la entrada `epic_history` aprobadora (`approved_by`/`completed_at`) + `policy_sha256`.
  Las entradas `epic_history` `epic-plan` de epic-005 ya llevan `plan_path`, `plan_sha256`, `evidence` y
  `note`: se **reutilizan como origen**, no como pin.
- **«No volver a aprobar por unidad si no cambió nada»** ya es cierto hoy para el arquitecto (no hay pin
  de hash); la proyección debe **preservar** esa propiedad: re-aprobación solo si la proyección cambió.
  **Frontera:** el pin de la spec de los roles de construcción (I2/PD-18, `:1415-1451`) **no se toca**;
  la fila 13 es sobre el plan/unidad y su arquitecto.

## 7. Frontera y fuera de alcance

- **No se anticipa 005-012** (registro de transiciones): la tabla de consecuencias de (b) **no** es la
  operación del CLI que registra una transición. La decisión de *cómo* reconciliar un paquete despachado
  es del orquestador (fila 13 (c)); 005-013 solo debe **registrar el impacto** y hacer que la recepción
  funcione contra el contrato recibido.
- **No** se anticipan las candidatas de `execution.md:89-96` (adopción de versión entre ciclos RD-a;
  estado operativo compacto RD-b): sin unidad ni prioridad.
- **Fuera explícito:** varias unidades a la vez sobre el mismo state (`active_packet` único). Sin CI, sin
  sandbox, sin plataforma de jobs, sin tocar HOME, sin reabrir los contratos de 005-003/005-005/005-007/005-011.

## 8. Recorrido de uso concreto

**Caso real (el que hoy se rompe) — despacho de un architect → alta de una unidad futura independiente →
recepción normal:**

1. El orquestador despacha al arquitecto: `prepare` (rc=0; el `contract.sha256` queda pineado a los bytes
   del plan vigente), `validate-*`, `cdad_continuity begin`, `--record-dispatch` (`prepared → dispatched`).
   Estado actual verificado: `active_packet = 005-013-unit-contract-architect-discovery-001`,
   `status = dispatched`, `contract_sha256 = 63dda3b8…`.
2. Se edita el plan para **agregar una unidad futura independiente** (una fila más). Medición real del
   último cambio equivalente: `git show --stat a205e1c` → **+7 líneas** en `plan.md` y el sha del plan
   completo pasó de `99c69b0f5261…` a `63dda3b83561…`.
3. **Hoy:** `prepare --resume-packet <id>` → rc=2 `packet obsolete` («reconciliation of the dispatched
   packet is required»); `receive` → rc=2 «contract sha256 does not match exact content». La entrega del
   arquitecto **no se puede recibir** aunque su trabajo sea correcto; y no hay operación de CLI para un
   paquete `dispatched` (solo `--replace-packet` para `prepared`). El único camino es retirar/re-pinear a
   mano, como en el precedente `plan.md:185-187`.
4. **Después (objetivo de la fila 13):** el alta de una unidad independiente **no cambia la proyección de
   la unidad activa** → el paquete despachado sigue válido → `receive` rc=0 contra el contrato que el
   agente efectivamente recibió.

**Caso que SÍ debe exigir reconciliación (fila 13 (b) ii/iii):**

1. Cambiar el **alcance o una dependencia relevante** de la unidad activa (su propia fila) → la
   proyección cambia → el CLI **registra el impacto** y el orquestador decide cómo reconciliar.
2. **Retirar una autorización** o cambiar una **restricción de aplicación inmediata** (una de las
   secciones que prevalecen, `plan.md:48-88`) → la proyección cambia → se **impiden** las acciones
   afectadas (no basta con registrar el impacto).
3. Editar «Cambios al plan» (historia) o la fila de **otra** unidad sin dependencias compartidas → la
   proyección **no** cambia → sin efecto sobre el encargo.

## 9. Comparación breve de enfoques

| Enfoque | Problema que resuelve | Fuentes que toca | Límites |
|---|---|---|---|
| **A. Mover el pin al contrato de la unidad** (el arquitecto recibe una proyección generada como su contrato; el sha del plan pasa a procedencia) | Alta de unidades futuras sin invalidar el trabajo en curso; recepción contra el contrato recibido | `_contract_for` (`:995-1008`), kind/path en `validate_request` (`:814-819`), `_validate_active_packet` (`:469-498`), `receive` (`cdad_result.py:513`) | Exige una pieza nueva (generador de la proyección) y decidir el kind/path (**VERIFY**: si basta un path nuevo bajo el kind vigente o hace falta un kind nuevo en `VALID_CONTRACT_KINDS`, `:52`) |
| **B. Mantener el plan como contrato y hacer el pin condicional a la proyección** | Igual, sin cambiar el kind | `validate_request`/`_resume_packet`/`receive` compararían el digest de la proyección | Re-calcular la proyección en cada validación reintroduce el hazard de byte-identidad (`:1839-1840`) salvo que se persista; termina convergiendo a A |
| **C. Sacar la planificación futura a otro documento** (para que el plan no cambie) | No invalida el trabajo | — | Viola fuente única (`planning-contract-draft.md:64`) y agrega mantenimiento documental; contradice «proyección generada» (fila 13 (a)) |
| **D. No tocar el CLI; reconciliar a mano cada vez** | — | — | Es el statu quo; el costo ya está declarado en `execution.md:83-96`; no reduce trabajo operativo |

## 10. Propuesta mínima elegida (dirección; el contrato se fija en el draft)

1. **Generar una proyección de unidad desde el plan** (fuente única): la fila de la unidad (por id) + las
   secciones que prevalecen (`48-88`, `90-111`, `119-126`, `128-134`), **excluyendo** «Cambios al plan».
   Determinista; sin listas de palabras; el sentido lo juzga la review.
2. **Publicar la proyección una vez** (bytes durables junto al paquete/la unidad) y **pinear su digest**.
   El `contract` del arquitecto apunta a la proyección; el sha del plan queda como **procedencia** en el
   origen (reutilizando `epic_history.plan_path/plan_sha256`).
3. **Reutilizar** el objeto `contract`, el patrón de render por referencia (`_plan_task_sections`), el
   registro durable `.superseded.json` y el campo `note` de `stage_history`. **No** crear un bloque
   `plan-tasks` a mano en el plan del epic (segunda declaración).
4. **Clasificar la consecuencia comparando la proyección previa con la nueva por parte**: fila de la
   unidad o dependencia → registra impacto; sección que prevalece / autorización → registra impacto o
   impide según su etiqueta. **VERIFY:** dónde se declara la etiqueta de «aplicación inmediata».
5. **`receive` valida contra la proyección registrada** (el contrato recibido), no contra el archivo vivo
   del plan; sin tocar el esquema del recibo, sin aprobar nada y sin ampliar autoridad.

**Criterio del dueño respetado:** cada pieza **reduce** trabajo (una edición del plan deja de costar un
re-pin/replace/reconciliación), no agrega controles frágiles (nada de tests que decidan el significado de
un párrafo) ni mantenimiento documental (la proyección se **genera**; la regla se **referencia**).

## 11. Plan legible por el humano (borrador de estructura, no el plan de la etapa 2)

- **Objetivo:** que el hash identifique el contrato que **recibió** el agente y que la planificación del
  proyecto deje de bloquearse globalmente por editar el plan.
- **Recorrido:** despacho de un architect → alta de una unidad futura independiente → recepción normal;
  y un cambio relevante que **sí** exige reconciliación.
- **Unidades y orden propuesto** (a confirmar en el draft):
  1. **U1 — proyección de unidad generada + publicación + origen** (base; el arquitecto pasa a recibir la
     proyección como contrato).
  2. **U2 — recepción y resume contra el contrato recibido** (el cambio más pequeño que desbloquea el
     trabajo en curso).
  3. **U3 — tabla de consecuencias por tipo de cambio** (sobre el digest de la proyección, reutilizando el
     registro durable y la nota de impacto).
  4. **U4 — gate de aceptación** (prueba decisiva en proyecto descartable).
  Dependencias: U1 → U2 y U1 → U3; U4 requiere U1+U2+U3. Sin paralelismo (mismo archivo de CLI).
- **Decisiones abiertas para el draft:** kind/path de la proyección (**VERIFY**); dónde se etiqueta
  «aplicación inmediata»; si la proyección vive junto al paquete o por unidad; qué queda del `commit` del
  contrato (hoy `null`).
- **Riesgos:** (a) re-generar la proyección en cada validación reintroduce el hazard de byte-identidad
  (`:1839-1840`); (b) la sobre-inclusión de secciones hace que un cambio irrelevante registre impacto
  (conservador y declarado); (c) el pin de la spec de los roles de construcción **no** debe relajarse
  (I2/PD-18).

## 12. Plan de aceptación proporcional

- **Prueba decisiva (fila 13), con el CLI REAL instalado (7212ead), sobre un PROYECTO DESCARTABLE**
  (nunca este repo, nunca HOME).
- **Entorno descartable — mínimo requerido** (patrón ya existente y probado: `build_project` +
  `prepare` real, `tests/test_004_002_t2_bootstrap.py:96-160` y `tests/test_005_007_t3_open_unit.py:137-274`):
  `docs/cdad-policy.json` de tres campos; `docs/.cdad-state.json` con `epic_history` (`stage: epic-plan`,
  `approved_by`), `hitl_delegation` activa (`epic_id`/`source`/`scope`), `epic_features` (una unidad
  `in-progress` y una `queued`), `execution` v2 y `active_packet`; `docs/epics/<epic>/plan.md` con la fila
  de la unidad y las secciones que prevalecen; el archivo de autoridad referenciado; HOME del subproceso
  en un tempdir vacío.
- **Tramo 1 (unidad independiente):** `prepare` del arquitecto (rc=0) → `--record-dispatch`
  (`prepared→dispatched`) → editar el plan agregando una unidad futura independiente → **`receive` rc=0**
  con `packet_validation`/`identity_validation` passed y `semantic_status: pending`.
- **Tramo 2 (cambio relevante):** cambiar el alcance/una dependencia de la unidad activa o una sección
  que prevalece → el CLI **registra el impacto** (y el orquestador decide); retirar la autorización o
  cambiar una restricción de aplicación inmediata → la acción afectada queda **impedida**.
- **Productor de cada insumo:** el test-writer produce el arnés/fixture descartable y los focales; el
  orquestador produce la edición del plan y corre el CLI real.
- **Actor evaluador:** el orquestador bajo la HITL delegada del epic (`execution.md:8-23`), o el dueño.
- **Evidencia de cierre:** salidas del CLI de ambos tramos (rc y diagnósticos), el `REQUEST.json` y el
  recibo durables, el diff del plan (con su medición de líneas/bytes) y la comparación de digests.
- **Proporcional:** un solo entorno descartable y dos tramos; sin CI; la suite completa la corre una vez
  quien cierra (política de suite completa del paquete).
- **Costo operativo que se reduce:** hoy el alta de una unidad futura obliga a retirar/reemplazar/re-pinear
  el paquete despachado (`--replace-packet` no aplica a `dispatched`); después, es solo una edición del
  plan. Sin compensar con más controles frágiles ni mantenimiento documental.
- **Desconocido declarado:** la operación exacta de reconciliación de un paquete `dispatched` (territorio
  de 005-012); 005-013 no la inventa.

## 13. Medidas disponibles (y lo desconocido)

- **6 cambios de hash del plan** en epic-005: entradas `epic_history` `epic-plan` con `plan_sha256`
  `f3b66be0d7aa…`, `996dd7e0afa8…`, `fbb0770b7fe2…`, `b22bc687e327…`, `99c69b0f5261…`, `63dda3b83561…`
  (la última = vigente = sha actual del plan). Coincide con lo declarado en el encargo.
- **Plan completo:** 257 líneas / 31396 bytes. **Fila 13:** 1 línea / 1485 bytes. **Secciones
  compartidas** (Ajuste 2808 + Criterios 1500 + Operación 457 + Autoridad 367) = **5132 bytes**.
  **Proyección estimada ≈ 6617 bytes** (~21 % del plan), con «Cambios al plan» (8413 bytes) **excluida**.
- **Costo del último cambio equivalente:** `git show --stat a205e1c` → `plan.md` +7 líneas (6 netas),
  sha del plan `99c69b0f5261… → 63dda3b83561…` (medido con `sha256sum` sobre el archivo en cada commit).
- **Verificaciones de código** (grep/sha256/CLI): `plan_sha256` sin consumidores; `7212ead..HEAD` solo
  `docs/`; `status` del repo rc=0 con `entry=continuity-reconcile`.
- **Declarado, no re-medido:** el state pesa ~530 KB y ~486 KB en `stage_history` (`execution.md:93`);
  la vista `status` ~1691 bytes (nota de discovery de 005-011). No se re-midió el tamaño del state
  (consulta dirigida).
- **Desconocido:** cuántas veces el pin bloqueó **efectivamente** una recepción en el epic (el state no lo
  registra de forma agregada; solo se documenta el caso de 005-001, `plan.md:185-187`). Se conserva como
  desconocido.

## 14. Evidencia del rol (read-only)

- **Archivos modificados en el repo:** **ninguno**. Única escritura: `<tmp>/opencode/discovery-005-013.md`
  (archivo de transporte, bytes idénticos a este TEXTO FINAL).
- **Commit:** ninguno (el rol architect es read-only; no commitea).
- **Comandos exactos ejecutados** (todos de lectura o del CLI en modo lectura):
  - `sha256sum docs/epics/epic-005-real-operation/plan.md skills/cdad-cycle/packets/common.md
    skills/cdad-cycle/packets/roles/architect.md skills/cdad-cycle/packets/substages/architect-discovery.md
    docs/cdad-policy.json` → hashes coincidentes con el paquete.
  - `git diff --name-only 7212ead..HEAD` → solo rutas bajo `docs/`.
  - `python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root .` → JSON `compact-view-v1`,
    rc=0, `entry=continuity-reconcile`, `authority.approval.contract_sha256 = 63dda3b8…`.
  - `grep -rn "plan_sha256" skills/ scripts/ agents/ sources/` → sin coincidencias (0 consumidores).
  - `python3 - <<'EOF' … json.load(docs/.cdad-state.json) …` → consulta dirigida de `epic_history`
    (7 entradas `epic-plan` de epic-005, 6 con `plan_sha256`), `active_packet`, `execution`,
    `hitl_delegation`, `epic_features`.
  - `git show --stat a205e1c`, `git show a205e1c^:…/plan.md | sha256sum`,
    `git show a205e1c:…/plan.md | sha256sum` → medición del último cambio de plan.
  - Lecturas `read`/`grep` de `cdad_packet.py`, `cdad_result.py`, `cdad_continuity.py` y de las
    referencias/planes citados.
- **Anonimización:** sin rutas absolutas del dueño ni ids crudos de sesión; se usan `<repo>`, `<home>`,
  `<tmp>`, `<ses-…>` y rutas repo-relativas.
- **No se propuso el contrato** (numeración PD/INV/AC): queda para la subetapa `draft`.
