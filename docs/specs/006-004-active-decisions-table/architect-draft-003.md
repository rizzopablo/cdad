All corrections are applied, verified, and the plan-tasks block still validates against the product's own validators. Here is **REVISION 3**.

**Rol:** architect (etapa 2, substage `draft`) · **Modo:** read-only (`write_scope: []`) · **Paquete:** `006-004-active-decisions-table-architect-draft-003` · **Dictamen aplicado:** `plan-review-002.md` (1 BLOCKING · 1 OPTIONAL)

---

===BEGIN spec.md===
# 006-004-active-decisions-table — SPEC (etapa 2, borrador draft-003)

Estado: **BORRADOR — SIN APROBAR**. Esta entrega no lleva marca de aprobación y no la lleva nunca por el dictamen de la revisión de borrador (INV-6). La aprobación es un acto separado de la autoridad vigente (`skills/cdad-cycle/references/stage-2-specification.md`:88-120).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §10 (enmienda 003) y §12 (enmienda 005) — sha256 `d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809`, **verificado en disco** y coincidente con el del paquete `exec-006-004-active-decisions-table-001`.
Decisiones de entrada (orquestador, HITL delegada, 2026-10-20): `docs/epics/epic-006-opencode-concurrency/execution.md`:399-415 — diseño **O1**, **Q1**..**Q6**, tope de filas fail-closed, y ADR-034 como fuente única del principio.
Decisiones de entrada de **esta revisión** (orquestador, 2026-10-20): la **regla general del CAS por digest base** (DEC-13), dictada como regla **general antes que específica** y no como parche de esta tabla; y la **separación de las comprobaciones de siembra** en una unidad con gate posterior a la materialización (DEC-14).
Insumo: `docs/specs/006-004-active-decisions-table/discovery.md` (etapa 1, mismo autor).
Dictamen aplicado: `docs/specs/006-004-active-decisions-table/plan-review-001.md` (2 BLOCKING · 2 OPTIONAL) — sus cuatro hallazgos están corregidos (§0.1) — y `docs/specs/006-004-active-decisions-table/plan-review-002.md` (1 BLOCKING · 1 OPTIONAL), corregidos en esta revisión (§0.2).
Base medida: HEAD `a9cc7ab`. **El discovery se escribió antes de que 006-006 fuera construido**; por eso esta spec **re-verifica** las superficies que aquel documento cita: el bloque estático, el conjunto de campos del request y las funciones del render se miden **hoy** (mediciones M1..M9 abajo), no se copian.
Anonimización: rutas relativas al repositorio; sin rutas del host, endpoints, ids de sesión ni credenciales; el proyecto consumidor no se nombra.
**Numeración (declarada):** `DEC-n` numera las **decisiones** de esta spec; `D-1..D-6` numera la **deuda declarada** (§10), con la numeración heredada del discovery de esta feature para no colisionar con las decisiones.

## 0.1 Revisión 2 — qué cambió respecto de draft-001

| Hallazgo | Corrección | Dónde |
|---|---|---|
| **B-1** — U4 exigía documentos que sólo produce U5 | Las comprobaciones se separan **por superficie**: **U4** = plantilla + procedimiento (gate que no necesita ningún documento ajeno); **U5** = materialización (gate = materialización + aprobación registrada); **U7** (nueva) = verificación de la **tabla viva** y del **ADR-034**, con gate **posterior** a la materialización de U5. El bloque de `tests/validate-consistency.sh` que mira la tabla viva pasa de U4 a U7. | §3 (PD-11), §5 (DEC-14), §12; plan §1, §2, §3 (U4, U5, U7) |
| **B-2** — el CAS con el digest actual no detecta una propuesta obsoleta | El CAS usa el **digest base** (el de la versión **sobre la que se preparó** la propuesta), **nunca** el actual; ante conflicto, la vía es **re-despachar** al rol con un **paquete nuevo** sobre la base nueva; **nunca** fusionar a mano ni **actualizar el digest esperado** para forzar el paso; el orquestador —que mantiene la tabla— escribe sus propias filas **directamente en `docs/`** con su commit. U6 demuestra la cadena completa e identifica los bytes aplicados. | §0 (M9), §2.5, §3 (PD-9, E7), §5 (DEC-13), §6 (V-6), §9, §10 (L-7); plan §3 (U4, U6) |
| **O-1** — PD-11 exigía a la vez fila vigente y ADR pendiente | Se **distinguen dos fases**: el ADR-034 **entregado** es un borrador `Proposed`; su **aprobación** es un acto posterior y separado, cuya evidencia se registra; el documento **materializado** lleva el estado **aprobado**. La comprobación final **reconoce la aprobación separada** y no exige que el ADR siga pendiente. | §3 (PD-11), §5 (DEC-14), §12; plan §3 (U5, U7) |
| **O-2** — el ADR entregado re-enunciaba el principio que declara no copiar | El ADR-034 **referencia** la casa canónica (`skills/cdad-cycle/references/design-principles.md`) y el contrato aprobado (`docs/epics/epic-006-opencode-concurrency/plan.md` §12) y **no reproduce** ni el texto del principio ni el de su límite. | ADR-034 (entrega separada) |

Lo demás de `draft-001` **se conserva** (contrato de la fila, render, tabla, siembra, invariantes, límites, riesgos).

## 0.2 Revisión 3 — qué cambió respecto de draft-002

| Hallazgo | Corrección | Dónde |
|---|---|---|
| **B-3** — U7 fijaba el inventario inicial (25 vigentes, 1 obsoleta, 8 `Proposed` excluidos) en el validador permanente | El inventario sembrado queda como **evidencia puntual de aceptación** (U5/U7) y **no** como aserción. `tests/validate-consistency.sh` lleva **sólo invariantes duraderas** que admiten aprobaciones y reemplazos nuevos: cada fila apunta a un archivo **existente** (dirección **fila → archivo**, no al revés); toda fila `obsoleto` nombra un reemplazo **existente**; todo `roles` ∈ vocabulario cerrado; la fila de **ADR-034** existe; la nota declara que **el estado lo declara quien mantiene la tabla**. El **cierre verificable** es un caso descartable: **agregar un ADR aprobado** y **reemplazar** una decisión **pasan** el comprobador; una fila con archivo inexistente **falla**. | §3 (PD-11), §4 (INV-15), §5 (DEC-15), §9, §12; plan §1.2, §2, §3 (U5, U7), §4, §6 |
| **O-3** — el cierre conservaba la circularidad como obligación vigente | La frase de `plan.md`:194 se sustituye por el **orden corregido**: U4 pasa su gate **sin** la siembra; la siembra (U5) depende de U3 y U4; la verificación (U7) corre **después** de la siembra ⇒ `U1 → U2 → U3 → U4 → U5 → U7 → U6`. | plan §5 |

Lo demás de `draft-002` **se conserva** (contrato de la fila, render, tabla, invariantes, límites, riesgos, y el resto del plan y del ADR-034).

## 0. Intención y necesidad del usuario real

- **Actor**: quien dirige el ciclo en un proyecto (el dueño, o el orquestador bajo HITL delegada) y, en el otro extremo, el **rol delegado** que recibe el encargo (architect, reviewer, implementer, test-writer, scribe).
- **Lo que quiere, en sus palabras**: «que la decisión que aprobamos gobierne el trabajo siguiente, sin que nadie tenga que abrir `docs/adr/` para adivinar qué sigue vigente».
- **Punto de partida legítimo**: el proyecto tiene `docs/adr/` con sus decisiones y `docs/systemPatterns.md` con sus convenciones. Hoy esa segunda superficie **no dice qué decisiones están en vigor**, y el paquete de un rol **no dice nada de ellas**.
- **Primer resultado útil**: cuando el orquestador aprueba un ADR y prepara el siguiente paquete, ese paquete **lleva** la decisión vigente que gobierna a ese rol —con el archivo donde está, su estado, un resumen de una línea y el lugar donde vive su regla—; y el proyecto muestra, en un solo lugar, qué decisiones están en vigor, cuáles ya no y por qué.

**La necesidad está medida, no supuesta** (discovery §0, reverificado hoy):

- **M1** — `grep -rn "Decisiones vigentes\|Current decisions" skills/ sources/ agents/ tests/ install.sh` → **0**. La sección es **nueva**, no una reorganización.
- **M2** — `ls docs/adr/ADR-*.md | wc -l` → **33**, y **no existe `docs/adr/README.md`** en este repo: hoy el proyecto **no tiene índice de decisiones** (el problema literal de la enmienda 003).
- **M3** — El **paquete es el único canal que puede llevar las filas a todos los roles**: el alcance de lectura por defecto del test-writer es `contract` + `tests` (`cdad_packet.py`:1238-1248) ⇒ `docs/systemPatterns.md` **queda fuera de su alcance** y un `--input docs/systemPatterns.md` sería **rechazado** (`cdad_packet.py`:1030-1031). «Dejar el archivo y que el rol lo lea» **no** cumple el requisito para todos los roles: las filas tienen que **viajar en el paquete**.
- **M4** — El **estado de un ADR **no es derivable**: 33 archivos con **cuatro vocabularios y tres formatos** de estado distintos, 8 *Proposed* (6 con `Proposed` y 2 con `Propuesto`), 2 reemplazados (uno **parcialmente**) y 1 *Verified* ⇒ la columna «estado» **la declara quien mantiene la tabla**, no se re-deriva.
- **M5** — El **precedente exacto ya existe y es aditivo**: `request.plan_task` (opcional, `cdad_packet.py`:870) + `_plan_task_sections` (`:3796`) emiten dos secciones **sólo cuando el campo está declarado**, y el render sin el campo es **byte-idéntico** (`tests/test_006_06_u1_draft_object_form.py`:432). Ese es el molde de `## Current decisions`.
- **M6** — El techo del bloque estático **no aprieta**: `CDAD_STATIC_BLOCK_LIMIT`, default **12000** bytes (`cdad_packet.py`:1063-1079); medido hoy, máximo **3031** (`reviewer/plan-review`), mínimo **1309** (`scribe/memory`) ⇒ **holgura mínima 8969 bytes** en los 14 pares rol/subfase.
- **M7** — **No hay operación de CLI ni clase de transición para la aprobación de un ADR**: `TRANSITION_CLASSES` = `delivery, advance, gate, closure, late-delivery, disposition` (`cdad_packet.py`:5204-5205) y el state no tiene ningún campo de ADR ⇒ «agregar la fila al aprobarse un ADR» es, hoy, una **declaración de procedimiento** del orquestador (que ya tiene `docs/**` y el git), no una operación de producto.
- **M8** — La **tensión real con «fuente única»**: en la **ruta de paquete** el rol **no carga el skill** (directiva del rol: «Do not load or reload `cdad-cycle`… the packet is the execution contract») ⇒ un puntero a `<skill-dir>/references/x.md` **no es resoluble** por el rol en esa ruta. La **obligación operativa** tiene que entrar por la superficie que sí viaja: el **cuerpo del agente generado** (`sources/roles/*.md` → `agents/*.md`) y/o el **bloque estático del paquete** (`packets/roles/*.md`).
- **M9 — El CAS protege el destino, no la base.** Medido en el código, no inferido: `_apply_copy` (`skills/cdad-cycle/scripts/cdad_result.py`:822-855) compara el digest **actual** del destino con `expected_previous_sha256` y **rechaza** si difieren («conflict: target … current digest does not match expected_previous_sha256 (CAS): refusing to overwrite», `:847-848`; con digest nulo, «(create-only)», `:844`). **No** sabe ni comprueba **sobre qué versión redactó el rol la propuesta**: `expected_previous_sha256` viaja en la **autorización** (`skills/cdad-cycle/assets/materialize.schema.json`:31-35; validación en `cdad_result.py`:748-757), que redacta el orquestador. ⇒ una autorización hecha con el digest **actual** **pasa** y pisa el cambio ajeno. La detección de una propuesta obsoleta es, por tanto, **disciplina de procedimiento**, no verificación del producto (DEC-13, L-7).

## 1. Descripción funcional

La feature hace cuatro cosas, en este orden:

1. **Una decisión vigente puede viajar en el encargo.** Un campo **opcional** del request (`current_decisions`) transporta las filas de las decisiones que gobiernan al rol del paquete; el render emite una sección aditiva `## Current decisions` **sólo** si hay filas. Sin el campo, el render es **byte-idéntico** (patrón aditivo ya establecido por `plan_task`/`agent`). (§2.1, §2.3)
2. **La forma de la fila la valida el producto; el contenido, el proyecto.** El CLI comprueba mecánicamente la **forma** de cada fila declarada (conjunto cerrado de claves, archivo existente, estado de vocabulario cerrado, roles de vocabulario cerrado) y que **nombre al rol del paquete**; y falla cerrado con un tope declarado. El proyecto —no el producto— decide **qué** filas existen y **qué** dice cada una. (§2.2)
3. **La tabla del proyecto tiene un dueño y dos responsabilidades.** La sección «Decisiones vigentes» del `docs/systemPatterns.md` del proyecto (y de su plantilla) es el índice: una fila por decisión, con su archivo, su estado, un resumen de una línea, los roles que deben consumirla y la referencia. **El orquestador la mantiene** (al aprobarse un ADR) y **el reviewer la revisa** (contra `docs/adr/` y contra el cambio). (§2.5)
4. **El principio de general antes que específico tiene una casa y llega al rol que lo debe aplicar.** `ADR-034` registra el principio y su límite; el texto vive en **un único archivo del skill instalable**; el **architect** tiene la obligación de considerar alternativas generales y específicas y explicar el criterio, y el **reviewer** la de evaluar consecuencias reales —con el límite explícito: **la falta de una abstracción no es, por sí sola, un defecto**. (§2.6)

**Lo que NO hace:** no crea kind, subfase, agente, stage, tipo de artefacto ni verbo nuevos; no parsea el documento del proyecto (el producto conoce la **forma** de una fila, no el formato de un markdown de proyecto); no amplía la tabla cerrada de destinos (`assets/artifact-policy.json`); no normaliza el vocabulario de estado de los ADR ni toca el `status` de la máquina de estados; no cambia el exit gate de stage 5; no genera índices; no exige citar un ADR (no hay gate de cita obligatoria).

## 2. Contrato

### 2.1 El campo opcional y su forma

El request tiene un conjunto **cerrado** de campos (`cdad_packet.py`:860-873). La feature lo **extiende de forma aditiva**, con el mismo patrón de `plan_task` (`:870`) y `agent`:

| Clave | Presencia | Significado |
|---|---|---|
| `current_decisions` | **opcional** | lista de **filas** de decisiones vigentes que gobiernan al rol del paquete. Ausente o lista vacía ⇒ el paquete no lleva la sección |

- **R-1 (conjunto cerrado, aditivo).** `set(request)` debe ser exactamente `required ∪ {las opcionales presentes}`; **cualquier clave desconocida se rechaza** (igual que hoy). El conjunto no se relaja: se **agrega** una propiedad declarada.
- **R-2 (forma de la fila: conjunto cerrado).** Cada fila es un objeto cuyo conjunto de claves es **exactamente**:
  - `file` — string no vacío, ruta **relativa al proyecto** (POSIX);
  - `state` — string, valor de un vocabulario **cerrado**: `vigente` | `obsoleto`;
  - `summary` — string no vacío, **una línea** (sin `\n`);
  - `roles` — lista **no vacía** de strings;
  - `reference` — string no vacío;
  - `superseded_by` — string no vacío, **opcional y condicional**: **exigido** si `state == "obsoleto"` y **prohibido** si `state == "vigente"`.
  Cualquier otra clave ⇒ rechazo nombrando la clave. (La forma es la de una fila de la tabla del proyecto: la **misma** forma sirve para el documento y para el request, y por eso el orquestador puede construir el request desde la tabla sin traducción.)
- **R-3 (el archivo existe).** `file` debe existir en el proyecto y ser un archivo regular. Si no ⇒ rc≠0 nombrando la ruta. **`reference` NO se verifica**: puede apuntar al árbol instalado del skill, que el CLI no resuelve (§10, L-4).
- **R-4 (vocabulario de consumidores cerrado).** Los valores de `roles` se toman de un conjunto **cerrado**: los cinco roles delegados (`architect`, `test-writer`, `implementer`, `reviewer`, `scribe`) más `orchestrator` (que es un rol del producto —`sources/roles/orchestrator.md`, `agents/cdad-orchestrator.md`— pero **no** un rol despachado por paquete). Un valor fuera ⇒ rc≠0 nombrando el valor y el vocabulario.
- **R-5 (la fila nombra al rol del paquete).** **Toda** fila declarada para un paquete debe nombrar **al rol de ese paquete** en su `roles`. Si no ⇒ rc≠0 nombrando la fila y el rol del paquete. Es **fail-closed**: una fila que no concierne al rol **no viaja**, ni siquiera por descuido.
- **R-6 (sólo lo vigente viaja).** Una fila con `state == "obsoleto"` **no es admisible en un paquete** ⇒ rc≠0 nombrando la fila y su `superseded_by`. Las filas obsoletas **conservan su sitio en la tabla del proyecto** (la historia importa) y **no se distribuyen**. La distinción es del **producto**, no de la disciplina: «la fila vieja está en la tabla, la nueva gobierna» es una regla verificable, no una intención.
- **R-7 (tope de filas, fail-closed).** Un paquete admite **como máximo 32 filas** de decisiones. Más ⇒ rc≠0 nombrando el número declarado y el tope. (Valor y justificación: §2.4.)
- **R-8 (la invocación).** `prepare` admite `--current-decision <JSON>` **repetible**: cada valor es un objeto JSON que el CLI parsea y valida según R-2..R-7, y las filas quedan en `request.current_decisions` **en el orden declarado**. Un valor que no sea JSON, o un JSON que no sea objeto ⇒ rc≠0 nombrando la bandera y el índice de la ocurrencia.
- **R-9 (la sección del render es aditiva).** El render emite `## Current decisions` **sólo** cuando `current_decisions` está presente y **no vacío**. Sin el campo (o con la lista vacía) el render es **byte-idéntico** al del producto sin esta feature **dentro de una misma revisión** (§10, L-1: la garantía es intra-revisión, por el mismo motivo que 006-006 R-10).
- **R-10 (la forma de la sección).** La sección va **inmediatamente después de `## Contract`** y **antes** del bloque de plan-task, con una entrada por fila, en el orden declarado:

      ## Current decisions

      - Decision: docs/adr/ADR-034-principio-general-antes-especifico.md
        - state: vigente
        - summary: <la línea de una>
        - roles: architect, reviewer
        - reference: skills/cdad-cycle/references/design-principles.md

- **R-11 (el `summary` es una línea).** Un `summary` con salto de línea ⇒ rc≠0 nombrando la fila. Una fila es una línea: la legibilidad del paquete depende de ello.
- **R-12 (la fila no aprueba nada).** Las filas no tienen efecto de aprobación: el recibo queda `semantic_status: pending` y `approval_effect: false`, como hoy (`cdad_result.py`:624, `:737-739`, `:880-882`). Una decisión **vigente** no es una **aprobación**: son hechos distintos (ADR-014).
- **R-13 (el esquema del request).** `skills/cdad-cycle/assets/packet-request.schema.json` gana la propiedad opcional `current_decisions` (el documento queda veraz). La brecha preexistente —`agent` no figura en el schema— **no** se corrige aquí: es deuda declarada (§10, D-6).

### 2.2 El reparto: qué sabe el producto y qué sabe el proyecto

| | Producto (CLI) | Proyecto (tabla, orquestador) |
|---|---|---|
| Qué filas existen | — | **lo declara** el orquestador, al aprobar el ADR |
| La forma de cada fila | **la valida** (R-2..R-4) | la respeta |
| A qué rol pertenece cada fila | **lo comprueba** (R-5) | lo declara |
| Qué dice la decisión | — | el `summary` y el `reference` |
| Si la decisión sigue vigente | — | el `state` (no es derivable de los ADR: M4) |
| Que lo vigente viaje y lo obsoleto no | **lo exige** (R-6) | — |
| Que el paquete no crezca sin control | **lo acota** (R-7) | — |

Ésta es la frontera que hace la feature general sin hacerla ambigua: **una** responsabilidad («el rol recibe las decisiones que lo gobiernan»), **un** mecanismo, agnóstico al rol —el rol es un **dato** de la fila—, y **cero** parsing de documentos de proyecto.

### 2.3 La sección del render

`render_packet` (`cdad_packet.py`:1050-1121) compone, hoy: metadatos canónicos → bloque estático → `## Objective` → `## Contract` → [bloque de plan-task] → `## Inputs` → `## Read scope` → `## Write scope` → `## Invariants` → `## Expected output` → `## Evidence required`. La sección nueva se inserta **entre `## Contract` y el bloque de plan-task** (R-10). Con `current_decisions` ausente, **no hay ninguna diferencia de bytes** en el render (R-9).

**Lo que se toca y lo que no:** se **agrega** una rama; no se modifica la composición de ninguna sección existente, ni la metadata, ni el bloque estático, ni los alcances por defecto (`cdad_packet.py`:1238-1248). El paquete del test-writer **sigue** sin poder leer `docs/`: las filas llegan **dentro** del paquete, no por el alcance.

### 2.4 El tope de filas (32) y su justificación

- **Medido**: la tabla sembrada de este repo tendrá **25 filas vigentes** (24 decisiones en vigor existentes + `ADR-034`) y **1 obsoleta** (que no viaja). El **mayor** número de filas que un paquete podría llevar hoy es, por tanto, **25**.
- **Medido**: el paquete más cargado hoy lleva **8 filas** (el del architect: ADR-002, 003, 004, 009, 011, 013, 032, 034).
- **Elegido: 32.** Es la **potencia de dos inmediatamente superior** al conjunto vigente máximo posible (25) ⇒ **no ata hoy**, deja margen para que la tabla crezca, y **acota** la declaración sin límite (33 filas ⇒ rechazo nombrado, no un paquete que crece sin control). Un tope más bajo ataría de rutina; uno más alto no acotaría nada.
- El tope es **fail-closed y con salida**: el diagnóstico nombra el número declarado, el tope y la acción siguiente (revisar la tabla y declarar sólo lo que gobierna al rol).
- **El 25 es una fotografía, no una propiedad.** Aprobar un ADR nuevo o reemplazar una decisión **cambia** el conjunto ⇒ el tope **no** se deriva del inventario ni se re-deriva de él en ningún momento: el **32** es un **número declarado** (DEC-6), no un tope que se mueva solo, y el validador **no** fija el inventario (DEC-15, INV-15).

### 2.5 La tabla del proyecto: plantilla, upkeep y las dos responsabilidades

- **La sección y su título.** La plantilla del Memory Bank (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`) gana la sección **`## Current decisions`** (plantilla en inglés) como **primer H2** después de la introducción; en este repo la instancia viva (`docs/systemPatterns.md`) usa **`## Decisiones vigentes`** en el mismo lugar. El **título no es una dependencia del producto** (Q5): el CLI no parsea el documento ⇒ el título es libre; la **forma de la fila** sí es la del producto.
- **El bootstrap no se toca**: `references/bootstrap.md`:66-83 copia la plantilla ⇒ un proyecto nuevo nace con la sección (vacía) y con `docs/adr/README.md` (la guía de cómo escribir ADR, que **no** es un índice — M2).
- **Responsabilidad 1 — el orquestador mantiene la tabla.** En `references/stage-5-merge.md` §5.4 (la decisión sobre el ADR), el orquestador **agrega la fila** al aprobarse un ADR y **marca la fila del reemplazado como `obsoleto`** conservándola, con su `superseded_by`. El **exit gate de stage 5 no cambia** (Q6): no se agrega ninguna casilla nueva al gate (`references/stage-5-merge.md`:163-178).
- **Responsabilidad 2 — el reviewer revisa la tabla.** El **dueño canónico de la comprobación** es `references/stage-4-review.md` (la referencia canónica del reviewer), que gana una sección corta con las dos comprobaciones: (a) **alineación** — cada fila apunta a un archivo que existe en `docs/adr/`, y el contraste entre el conjunto de filas y el directorio; (b) **respeto** — el cambio respeta las decisiones vigentes **de su rol** (las filas que el paquete le lleva). La **regla de rol** (`sources/roles/reviewer.md` + `packets/roles/reviewer.md`) la **referencia** y no la copia, con el mismo patrón que la calibración (`sources/roles/reviewer.md`:44-46).
- **La re-entry (Q6) — la regla general del CAS por digest base (DEC-13).** La tabla tiene **dos escritores** —el orquestador en la aprobación del ADR, y el scribe opcionalmente en el cierre (el `systemPatterns.md` ya entra al paquete del scribe, `references/stage-5-merge.md`:36-47)— y la reconciliación se declara así:
  1. **El CAS se hace contra el digest BASE**, es decir **contra la versión del destino sobre la que se preparó la propuesta** (la que el rol leyó), **nunca** contra el digest actual del destino. Medido: el producto compara el destino con `expected_previous_sha256` y no sabe nada de la base (M9) ⇒ usar el digest actual **no** detecta una propuesta obsoleta y **pisa** el cambio ajeno (DEC-13).
  2. **El orquestador escribe sus propias filas directamente en `docs/`**, con su commit (`docs(memory):`): no pasa por el CAS del scribe y no comparte su base.
  3. **Ante un conflicto** (el destino cambió desde la base ⇒ «conflict: … (CAS): refusing to overwrite», `cdad_result.py`:847-848), la vía es **re-despachar** al rol con un **paquete nuevo** sobre la **base nueva**, para que la propuesta se rehaga sobre lo que ahora existe. **No** se fusiona a mano y **no** se actualiza el digest esperado para forzar el paso: «subir el digest» haría pasar el CAS **borrando** el cambio del otro escritor (M9).
  4. **El documento reconciled** es el de la propuesta re-despachada: conserva **la fila del orquestador** (porque la base nueva ya la traía) **y los cambios del rol**. La evidencia identifica **los bytes aplicados**.
- **Dónde vive la regla.** La regla del punto 1 y la del punto 3 son **generales** (afectan a **toda** materialización con CAS, no sólo a esta tabla) ⇒ viven en el **paso 3 (MATERIALIZE) del protocolo de materialización** de `references/re-entry.md`, que es su superficie canónica; el **caso particular de la tabla** (los dos escritores, el orquestador escribiendo directo) vive en la **sección `### Scribe`** de la misma referencia. La regla **general antes que específica** (§2.6) es también la que exige no dejar la regla general escondida en un caso particular.

### 2.6 El principio de general antes que específico: una casa, dos obligaciones, un límite

- **La casa (una sola).** `skills/cdad-cycle/references/design-principles.md` —un archivo **nuevo** del skill instalable— lleva la sección «General before specific» con **el texto del principio** y **su límite** («the principle improves design judgement; it does not increase the justifications that agents must produce»). Se elige una *reference* y no `SKILL.md` porque ése es el patrón del repo —«dueño canónico único» en `references/` y puntero desde el rol (`references/stage-4-review.md`:8-10)— y porque `SKILL.md` se carga siempre: meter ahí una regla de diseño para dos roles carga a todos. El árbol `skills/cdad-cycle/` viaja completo al entorno instalado (`install.sh`:370-378) ⇒ **no hace falta tocar el instalador**.
- **La fuente única, verificada.** El texto normativo del principio aparece en **un solo archivo** del árbol instalable (`skills/`, `sources/`, `agents/`). Los consumidores lo **referencian**; el deber del rol es **duty**, no principio, y por eso vive en la fuente del rol (una línea) y no es una copia.
- **Obligación del architect** (una línea, en `sources/roles/architect.md` y en `packets/roles/architect.md`): en las decisiones relevantes, **considera las alternativas generales y específicas y explica el criterio elegido**; el principio y su límite viven en el archivo citado y **no se re-enuncian aquí**.
- **Criterio del reviewer** (una línea, en `sources/roles/reviewer.md` y en `packets/roles/reviewer.md`, con el procedimiento en `references/stage-4-review.md`): evalúa **consecuencias reales** —duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento— y **la falta de una abstracción, por sí sola, no es un defecto**.
- **Por qué el bloque estático también lleva la obligación (D-2 del discovery).** En la **ruta de paquete** el rol **no carga el skill** ⇒ un puntero a `<skill-dir>/references/…` no es resoluble por el rol. El bloque estático **sí viaja** (y su digest viaja en `instruction_sources`), de modo que la **obligación operativa** llega completa por esa vía. La lectura íntegra del principio depende de que el rol alcance el skill: es la **misma limitación** que ya acepta el puntero vigente a `references/stage-4-review.md`, no un defecto nuevo (§10, D-2).
- **El ADR-034** apunta al archivo del skill como la regla que materializa, y **no re-enuncia** el texto del principio ni el de su límite (O-2): los referencia. La fila de la tabla lo referencia igual ⇒ el mecanismo de §10.4 del plan («una decisión que cambia la metodología no está terminada hasta que su regla está en el skill instalable; la fila guarda la referencia») queda servido por la **misma** fila.
- **La regla general que esta spec acaba de aplicar a sí misma.** DEC-13 (el CAS por digest base) se dictó **general** y no como parche de esta tabla: es la forma que la decisión del orquestador exige («general antes que específico»), y por eso vive en el protocolo general de materialización (§2.5), no en el caso de la tabla.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **La forma de la fila se valida y falla cerrado.** Una fila con `file`, `state`, `summary`, `roles` y `reference` válidos es aceptada; una clave **desconocida** ⇒ rc≠0 nombrando la clave; `state` fuera de `{vigente, obsoleto}` ⇒ rc≠0 nombrando el valor y el vocabulario; `superseded_by` **ausente** con `state: obsoleto` ⇒ rc≠0; `superseded_by` **presente** con `state: vigente` ⇒ rc≠0; `file` inexistente ⇒ rc≠0 nombrando la ruta; `roles` vacío ⇒ rc≠0; un nombre de rol fuera del vocabulario ⇒ rc≠0 nombrando el valor; `summary` con salto de línea ⇒ rc≠0. | el `REQUEST.json` del paquete en el caso bueno; rc≠0 y **sin publicación** (`out-dir` sin entradas, state byte-idéntico) en cada negativo, con el mismo control que `assert_rejected_without_publication` (`tests/test_004_003_t4_validation_fields.py`:399-423) |
| **PD-2** | **La fila nombra al rol del paquete.** Una fila que nombra el rol del paquete es admitida; una fila que **no** lo nombra ⇒ rc≠0 **nombrando la fila y el rol del paquete**; una fila que nombra a otro rol delegado (pero no al del paquete) ⇒ rc≠0 por la misma regla. | los rc de `prepare` y el texto del diagnóstico; el `REQUEST.json` del caso bueno |
| **PD-3** | **Sólo lo vigente viaja.** Una fila `obsoleto` **no** es admisible en un paquete ⇒ rc≠0 nombrando la fila y su `superseded_by`; la fila obsoleta **conserva su sitio** en la tabla del proyecto (no se borra). | rc≠0 del `prepare` con la fila obsoleta; el texto de la tabla del proyecto tras el rechazo (la fila sigue) |
| **PD-4** | **El tope de filas falla cerrado.** 32 filas admitidas; 33 ⇒ rc≠0 nombrando el número declarado y el tope; el estado queda byte-idéntico y no se publica nada. | los dos rc; el conteo de filas del `REQUEST.json`; el `out-dir` vacío en el rechazo |
| **PD-5** | **La sección del render es aditiva y byte-idéntica sin filas.** Sin `current_decisions` (o con la lista vacía) el render es **byte-idéntico** al del producto sin la feature **en la misma revisión**; con filas, el render emite `## Current decisions` **después de `## Contract`**, con una entrada por fila, en el orden declarado, con `file`, `state`, `summary`, `roles` y `reference`. | comparación byte a byte del render con y sin el campo, **en la misma revisión** (el `PACKET.md` entero **no** se congela: las fuentes de instrucción y sus digests cambian legítimamente entre revisiones — L-1); el texto de la sección en el caso con filas |
| **PD-6** | **Las filas viajan en el encargo, no en un archivo que el rol debe abrir.** El `REQUEST.json` lleva `current_decisions` con las filas en el orden declarado; el paquete del rol las lleva en la sección; el paquete de un rol **sin** filas aplicables no lleva la sección (byte-idéntico); el test-writer **sigue** sin poder leer `docs/` (su alcance no cambia) y **sí** recibe las filas que lo gobiernan. | el `REQUEST.json`; el `PACKET.md`; los `read_scope` del paquete del test-writer (sin cambios) |
| **PD-7** | **La plantilla trae la sección y un proyecto sin ADR no queda bloqueado.** La plantilla del Memory Bank contiene `## Current decisions`; el bootstrap la instala (copia literal de la plantilla); un proyecto **sin** ADR prepara cualquier rol con rc=0 y **sin** sección; la sección vacía **no** es una fila. | `grep` sobre `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`; el `prepare` rc=0 de un proyecto sin `docs/adr/`; el render sin sección |
| **PD-8** | **Las dos responsabilidades están escritas donde se aplican.** `references/stage-5-merge.md` dice que el orquestador **agrega la fila** al aprobarse un ADR y **marca la anterior como obsoleta**; el **exit gate de stage 5 no cambia** (no hay casilla nueva). `references/stage-4-review.md` dice que el reviewer **compara la tabla con `docs/adr/`** y que **el cambio respeta las decisiones vigentes de su rol**; la fuente del rol y su bloque estático **referencian** esa regla y no la copian. | derivación textual sobre las tres superficies (el patrón de derivación del proposal de 006-006) + el control negativo: el **exit gate** de `references/stage-5-merge.md` tiene el **mismo** número de casillas que antes |
| **PD-9** | **El CAS se hace contra el digest base y la reconciliación es un re-despacho, no una fusión.** (a) La autorización de materialización declara el digest **base** (la versión del destino sobre la que el rol preparó la propuesta), **nunca** el digest actual del destino. (b) Si el destino cambió desde esa base ⇒ la materialización se **rechaza por CAS**, nombrando el conflicto («refusing to overwrite»), y **no** sobrescribe. (c) La vía de salida es **re-despachar** al rol con un **paquete nuevo** sobre la **base nueva**: **no** se fusiona a mano y **no** se actualiza el digest esperado para forzar el paso. (d) El documento final conserva **la fila del orquestador** (que la base nueva ya traía) **y los cambios del rol**. (e) La evidencia identifica **los bytes aplicados**. | el texto de `references/re-entry.md` (derivación, paso 3 MATERIALIZE y sección Scribe) + el recorrido real de U6 (E7) con los rc, el texto del conflicto y la comparación del documento final contra la base nueva |
| **PD-10** | **La fuente única, las dos obligaciones y el límite.** `skills/cdad-cycle/references/design-principles.md` existe y lleva el principio **y** su límite; el texto normativo del principio aparece en **un único archivo** del árbol instalable (`skills/`, `sources/`, `agents/`); la fuente del architect y la del reviewer **nombran** la obligación y **apuntan** al archivo canónico, y **no** copian el texto del principio; el criterio del reviewer nombra las cuatro consecuencias reales y el límite («la falta de una abstracción, por sí sola, no es un defecto»); `SKILL.md` §«How to read the references» tiene una fila para el archivo nuevo; el ADR-034 **no** re-enuncia el texto del principio ni el de su límite. | el test de texto de `tests/validate-consistency.sh` (bloque nuevo): unicidad por `grep -rl` sobre el árbol instalable; presencia de las obligaciones; **control negativo** de copia; el límite presente en las dos superficies del reviewer; y, sobre el ADR materializado, la ausencia de reproducción del texto del principio |
| **PD-11** | **La siembra de este repo (Q3), en dos capas: lo duradero se valida; el inventario se acredita.** **(a) Validador permanente — invariantes duraderas** (sólo propiedades que admiten **aprobaciones y reemplazos nuevos**): la sección `## Decisiones vigentes` existe como **primer H2** de `docs/systemPatterns.md`; **cada** fila apunta a un archivo que **existe** (dirección **fila → archivo**, no al revés: el validador **no** exige que todo ADR tenga fila, porque el estado de un ADR no es derivable — M4, D-3); **toda** fila `obsoleto` nombra un reemplazo, y ese reemplazo **existe**; **todo** `roles` de **toda** fila pertenece al vocabulario cerrado (los cinco roles delegados más `orchestrator`); la fila de **ADR-034** existe, `vigente`, con los roles `architect` y `reviewer` y con la referencia al archivo canónico; la nota declara que **el estado lo declara quien mantiene la tabla** (D-3); el **ADR-034 materializado** existe, **no** está `Proposed` (la comprobación **reconoce** la aprobación separada: O-1), apunta a la fuente única y **no** re-enuncia el texto del principio (INV-1, O-2). El bloque **no contiene ningún conteo**: ni el número de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas. **(b) Evidencia puntual de la siembra** (en la aceptación de **U5** y **U7**, **no** en el validador): el inventario sembrado —**25 vigentes**, **1 obsoleta** (`ADR-007`), **8 `Proposed` excluidos**— se **acredita una vez** con la evidencia de la unidad y **no** se convierte en aserción permanente. **(c) Cierre del comprobador**, en un caso descartable: **agregar un ADR aprobado** (una fila `vigente` más) ⇒ **pasa**; **reemplazar** una decisión (marcar su fila `obsoleto` con su reemplazo) ⇒ **pasa**; una fila que apunta a un archivo **inexistente** ⇒ **falla**. | el bloque de texto de `tests/validate-consistency.sh` **de la unidad de verificación de la siembra** (presencia de la sección; bucle que comprueba que **cada** fila apunta a un archivo existente; toda fila `obsoleto` con su reemplazo existente; vocabulario cerrado de `roles`; fila de ADR-034; nota del estado) **más** los tres casos del cierre sobre copias descartables **más** la evidencia de U5/U7 con el inventario medido |
| **PD-12** | **El recorrido de aceptación (U6) en un proyecto descartable.** (a) un ADR aprobado produce una fila y el siguiente paquete del rol nombrado **la lleva**; (b) un ADR reemplazado deja la fila vieja **obsoleta** en la tabla y **fuera** del paquete; (c) un rol no nombrado **no** recibe la fila y su paquete es byte-idéntico al de hoy; (d) un proyecto sin ADR funciona sin cambios; (e) el reviewer **detecta** una tabla desalineada (una fila que apunta a un archivo inexistente) como **hallazgo** con `file:line`, veredicto y condición de cierre —no como puerta—; (f) la regla del principio **existe en el árbol instalado** y el paquete del architect y del reviewer la nombran; (g) la **cadena del CAS** de PD-9 se ejecuta completa y su evidencia identifica los bytes aplicados. | los paquetes y sus `REQUEST.json`; los rc; el texto del hallazgo del reviewer; la comparación byte a byte del caso (c); la existencia del archivo de referencia en la instalación; la evidencia de la cadena del CAS |
| **PD-13** | **Las guardas vigentes siguen verdes.** El paquete sin el campo nuevo no cambia (byte-idéntico, intra-revisión); el bloque estático de los 14 pares rol/subfase queda **por debajo** del techo declarado de 12000 bytes tras las adiciones; `make validate` verde; `make staging` es **determinista** (dos corridas, mismos bytes) y los agentes generados contienen las obligaciones; el CLI instalado (el producto instalado) renderiza la sección igual que el del repo. | `tests/test_static_block_ceiling.py` + la **medición** del bloque estático en el RED; salida de `make validate`; comparación byte a byte de dos `make staging`; el patrón de producto instalado de `tests/test_004_003_t2_plan_review.py`:290 |

### 3.1 Escenarios de recorrido (E1..E7) — la vara

Cada escenario es la **intención** de la feature expresada como recorrido comprobable: si todas las PD de su fila pasan, el escenario tiene que funcionar **de verdad**. Un escenario no cubierto es un hueco: se cubre o se declara.

| Escenario | Qué tiene que funcionar (recorrido) | PD que lo garantizan | Hueco declarado |
|---|---|---|---|
| **E1** | **Se aprueba un ADR y el siguiente paquete del rol nombrado lo lleva.** El dueño aprueba el ADR y el orquestador lo commitea en `docs/adr/ADR-NNN-*.md`; el orquestador **agrega la fila** a la sección «Decisiones vigentes» de `docs/systemPatterns.md` (archivo, `state: vigente`, resumen de una línea, roles que deben consumirla, referencia) y la commitea con prefijo `docs(memory):`; al preparar el paquete de ese rol, **declara** la fila; el rol la recibe **dentro** del paquete y la cita. Si el rol no está nombrado, esa fila **no** está. | PD-1, PD-2, PD-5, PD-6, PD-8, PD-11 | **Ninguno** para el recorrido mecánico. **Declarado**: la **completitud** (que el orquestador declare *todas* las filas del rol) **no** está garantizada mecánicamente: la garantía del producto es «toda fila declarada nombra a este rol», no «toda fila vigente fue declarada» (D-1). |
| **E2** | **Una decisión se reemplaza: la vieja queda obsoleta en la tabla y no se distribuye.** Se aprueba `ADR-034` que reemplaza a `ADR-0XX`: el orquestador **marca la fila vieja** como `obsoleto (reemplazado por ADR-034)` **conservándola** y **agrega** la nueva como `vigente`; al preparar el paquete, la fila **vigente** viaja y la **obsoleta no** (y, si se intentara declararla, el producto **rechaza** nombrando su sucesor). | PD-3, PD-5, PD-8, PD-12 | **Ninguno** mecánico. **Cota declarada**: la fila vieja sobrevive **sólo** en la tabla del proyecto; el paquete no la lleva ni la marca. |
| **E3** | **Un rol no nombrado no lo recibe.** La fila declara `roles: architect, reviewer`; al preparar un paquete de `test-writer`, la fila **no** viaja; y si el orquestador la declara de todos modos, `prepare` **falla** nombrando la fila y el rol. Un rol sin ninguna fila aplicable ⇒ paquete **byte-idéntico** al de hoy. | PD-2, PD-5, PD-6, PD-12 | **Ninguno**. La diferencia entre «no declarada» y «declarada para otro rol» es **ruidosa y recuperable** en los dos casos. |
| **E4** | **El reviewer detecta una tabla desalineada con `docs/adr/`.** Una fila apunta a `docs/adr/ADR-099-lo-que-sea.md` (que no existe) o el directorio y la tabla no coinciden; el reviewer (read-only, alcance `repository-read` ⇒ puede leer `docs/systemPatterns.md` **y** `docs/adr/`) lo detecta y lo reporta con `file:line`, `Verdict: BLOCKING` + `Bucket` (regla de observables de `references/verdict-tuple.md`), consecuencia y **condición de cierre verificable** (regla 2 de la calibración). | PD-8, PD-12 | **Declarado**: **no es un gate duro** (fuera de alcance: «gates de cita obligatoria») ⇒ es un hallazgo, con la severidad que le corresponda por efecto real. Y **no re-deriva** el estado de los ADR (D-3): contrasta el conjunto que la tabla declara. |
| **E5** | **Un proyecto sin ADR no queda bloqueado.** Proyecto nuevo: `docs/adr/` vacío y la sección recién instalada, vacía; `prepare` de cualquier rol ⇒ **rc=0**, **sin** sección, render **byte-idéntico**; ninguna regla nueva bloquea a un proyecto que no adopte ADR. | PD-7, PD-9, PD-12 | **Ninguno**. La sección vacía **no** es una fila: la lista vacía no emite sección. |
| **E6** | **Una decisión metodológica no está terminada hasta que su regla está en el skill instalable.** Se aprueba `ADR-034`; su fila dice **dónde vive** la regla (`skills/cdad-cycle/references/design-principles.md`); el paquete del architect y del reviewer **nombran** ese archivo; un revisor puede verificar que el archivo **existe** en el árbol instalado (`install.sh`:370-378 garantiza que `skills/cdad-cycle/` viaja completo). | PD-10, PD-11, PD-12 | **Ninguno** mecánico. **Declarado**: el CLI **no** verifica el `reference` (puede apuntar al árbol instalado, que el CLI no resuelve) ⇒ la comprobación es del **reviewer** (E4/E6), no del producto (L-4). |
| **E7** | **El CAS reconcilia la tabla sin pisar a nadie.** D0 = la versión de `docs/systemPatterns.md` sobre la que el scribe preparó su propuesta; el scribe entrega la propuesta P(base D0); el orquestador **escribe su fila directamente en `docs/`** y commitea ⇒ D1; la materialización de P con la **base D0** se **rechaza** nombrando el conflicto; el orquestador **re-despacha** al scribe con un **paquete nuevo** sobre la **base D1**; el scribe entrega P2(base D1) y la materialización **pasa**; el documento final conserva **la fila nueva** (que venía en D1) **y los cambios del scribe**; la evidencia identifica **los bytes aplicados** (el diff del documento final contra D1) y **no** hay fusión manual ni digest esperado retocado. | PD-9, PD-11, PD-12 | **Ninguno** mecánico. **Declarado**: la base la conoce el orquestador porque la registra al preparar el paquete del rol (el digest del destino en ese momento); el producto no la verifica (L-7). Y **el orquestador no pasa por el CAS** para sus propias filas: las escribe en `docs/` con su commit. |

## 4. Invariantes (INV-n)

- **INV-1 — Una decisión, una casa.** El texto normativo del principio de general antes que específico vive en **un único archivo** del árbol instalable; los demás lo **referencian** y no lo re-enuncian.
- **INV-2 — El cambio es aditivo.** Sin `current_decisions`, el render es **byte-idéntico** **dentro de una misma revisión** del producto (PD-5, PD-13) y los oráculos vigentes se conservan. **Entre revisiones no se promete compatibilidad**: un paquete publicado antes de un cambio de las fuentes de instrucción no es recibible después (mismo mecanismo y mismo precedente que 006-006 R-10/PD-16; §10, L-1).
- **INV-3 — Fallar cerrado es la dirección por omisión.** Una fila mal formada, una fila que no nombra al rol, una fila obsoleta en un paquete, un estado desconocido, un rol desconocido, un archivo inexistente y el exceso de filas **se rechazan**, con un diagnóstico que nombra la fila, el valor o la ruta. Ninguno de esos casos produce un paquete publicado «a medias».
- **INV-4 — El producto conoce la forma; el proyecto conoce el contenido.** El CLI valida la **forma** de una fila y su coherencia con el rol; **no** parsea el documento del proyecto, **no** deriva el estado de un ADR de su texto, **no** re-deriva qué decisiones están en vigor.
- **INV-5 — Lo que no se distribuye, no se distribuye.** Una decisión reemplazada conserva su fila en la tabla (la historia) y **no viaja** en ningún paquete (R-6). La distinción es del producto, no de la disciplina.
- **INV-6 — El dictamen no aprueba.** La revisión de este borrador (o de cualquier otro) no aprueba nada: ni la spec, ni el plan, ni el ADR-034, ni las filas que la tabla declara. La aprobación de cada uno de esos actos es **posterior y separada** (`references/stage-2-specification.md`:88-120; ADR-004, ADR-014).
- **INV-7 — La fila no es una aprobación.** Las filas viajan con `semantic_status: pending` y `approval_effect: false`; una decisión vigente no habilita construir ni sustituye el pin de aprobación (ADR-014, ADR-019).
- **INV-8 — El aislamiento del test-writer se conserva.** El test-writer **no** gana acceso a `docs/`: las decisiones le llegan **dentro** del paquete, no por el alcance. El alcance por defecto no cambia (`cdad_packet.py`:1238-1248).
- **INV-9 — Una regla, un dueño.** «Qué se revisa» tiene un dueño canónico (`references/stage-4-review.md` para el reviewer; `packets/substages/reviewer-*.md` para el procedimiento de la subfase); el rol, la re-entry y la plantilla **lo referencian**. La calibración sigue teniendo un único dueño (`references/stage-4-review.md`:8-10).
- **INV-10 — Nada se pierde en silencio.** Una fila que el orquestador no declara no viaja (y eso es una **decisión** suya, no un olvido del producto); una fila malformada no viaja **en silencio**: el rechazo la nombra; la tabla del proyecto conserva la historia de las decisiones reemplazadas.
- **INV-11 — El paquete no miente sobre lo que lleva.** La sección nombra el archivo, el estado, el resumen, los roles y la referencia de cada fila; una fila que no gobierna al rol **no aparece**.
- **INV-12 — La regla de rol no se duplica.** La fuente del rol y su bloque estático **declaran la obligación** y **apuntan** al dueño canónico; el texto del principio **no** se copia en ninguna otra superficie del árbol instalable, y el ADR-034 lo **referencia** sin re-enunciarlo.
- **INV-13 — El CAS es contra la base, y reconciliar es re-despachar.** Toda materialización con CAS declara el digest **base** (la versión sobre la que se preparó la propuesta), **nunca** el digest actual; un conflicto **no** se resuelve actualizando el digest esperado ni fusionando a mano, sino **re-despachando** al rol sobre la base nueva; el resultado conserva lo escrito por los dos. La regla es **general** (toda materialización con CAS) y vive en el protocolo general (`references/re-entry.md`, paso 3), no en el caso particular de la tabla.
- **INV-14 — Borrador, aprobación y materialización son tres actos distintos.** El ADR-034 entregado es un **borrador** (`Proposed`); su **aprobación** es un acto posterior y separado, con evidencia registrada; sólo después se materializa, y el documento materializado lleva el estado **aprobado**. Ninguna comprobación exige que el ADR **siga** pendiente, y ninguna fila `vigente` precede a la aprobación.
- **INV-15 — El inventario de la siembra no es una restricción permanente.** El validador permanente comprueba **propiedades** de la tabla (cada fila apunta a un archivo existente; toda fila `obsoleto` nombra un reemplazo existente; los roles son del vocabulario cerrado; la fila de ADR-034 existe), **nunca** el **número** de filas ni el inventario de excluidas ⇒ **aprobar un ADR nuevo o reemplazar una decisión no obliga a tocar los tests** (PD-11). Los conteos de la siembra son **evidencia puntual de aceptación** (U5/U7), no un oráculo permanente (DEC-15).

## 5. Decisiones (DEC-n)

- **DEC-1 — Diseño O1: un campo opcional del request + una sección aditiva del render.** *Adoptada por el orquestador (O1).* *Rechazadas:* (a) **O2** — que el CLI lea la tabla del proyecto y filtre por rol: metería el **formato de un documento de proyecto** dentro del producto (el CLI hoy verifica el **digest** del documento sin conocer su formato, `cdad_packet.py`:971-1002) y ataría el byte del paquete al estado de la tabla; (b) **O3** — texto libre en `--objective`/`--invariant`: sin sección, sin verificación de «la fila nombra a este rol», y sobrecarga semántica del canal de invariantes; (c) **O4** — la tabla como `--input`: el path debe estar en el alcance de lectura (`cdad_packet.py`:1030-1031) ⇒ para el test-writer habría que **ampliar** el alcance (o falla), y el paquete no lleva las filas.
- **DEC-2 — La fila tiene una forma cerrada de seis claves, con `superseded_by` condicional.** *Razón:* una forma única sirve **a la vez** al documento del proyecto y al request ⇒ el orquestador construye el request desde la tabla sin traducción, y el producto valida una **forma** que el proyecto ya respeta. *Rechazada:* la forma de **cinco** claves con el reemplazo dentro del `state` (texto libre): el vínculo «quién reemplaza a quién» dejaría de ser verificable.
- **DEC-3 — El estado de la fila es `vigente` | `obsoleto`, y el binario del plan se respeta.** Una fila con `state: obsoleto` **no** es admisible en un paquete (R-6) ⇒ el producto conserva la regla del plan («el paquete lleva las filas **vigentes** que lo nombran») y la hace verificable. *Rechazada:* un tercer estado (`parcialmente reemplazado`): ampliaría el vocabulario de estado que el plan fija, y el caso real (ADR-008) se resuelve en la fila con `state: vigente` y el resumen que nombra la parte reemplazada (DEC-4). *Consecuencia declarada:* el vínculo con el reemplazante **no viaja** en el paquete (no puede: la fila obsoleta no viaja) ⇒ se conoce por la tabla del proyecto.
- **DEC-4 — ADR-008 es una fila `vigente`, no `obsoleto`.** Medido: `docs/adr/ADR-008-…md`:3-9 declara `**Status:** **Verified** … **parcialmente reemplazado por ADR-033** … el resto sigue vigente`. Declarar la fila `obsoleto` **afirmaría** un reemplazo total que nadie ha declarado; declarar `vigente` **sin más** ocultaría la parte reemplazada. ⇒ `state: vigente` y el `summary` nombra el alcance residual y el reemplazo parcial. El ADR-033 lo confirma por su cuenta («su retiro formal es una decisión aparte»).
- **DEC-5 — El vocabulario de consumidores de una fila incluye `orchestrator`.** El orquestador es un rol del producto (`sources/roles/orchestrator.md`, `agents/cdad-orchestrator.md`) pero **no** es un rol despachado por paquete. Medido: **7** de los 33 ADR (002, 004, 012, 016, 018, 021, 023) no nombran **ninguno** de los cinco roles delegados; de ellos, **5** están en vigor (002, 004, 018, 021, 023) y gobiernan **exactamente** la conducta del orquestador (dónde se desarrolla y se instala, quién aprueba, quién declara la clase de una referencia, el arranque desde reposo, la interfaz de delegación). Sin `orchestrator` en el vocabulario, esas cinco decisiones **no** podrían tener fila ⇒ el índice perdería precisamente las decisiones más服务器as del ciclo. *Consecuencia declarada:* una fila que nombra sólo `orchestrator` **no viaja** en ningún paquete (no existe un paquete de orquestador); el orquestador la consume leyendo la tabla, que él mismo mantiene. *Rechazada:* un vocabulario de **cinco** ⇒ la tabla quedaría incompleta por construcción.
- **DEC-6 — El tope es 32 filas por paquete, fail-closed.** Justificación medida en §2.4. *Rechazados:* un tope **atado al número de filas de la tabla** (sería un tope que se mueve solo, y por tanto ningún tope); un tope **por bytes** (la sección no tiene techo propio y el byte de la fila depende del texto libre del `summary` ⇒ un tope de bytes no es determinista sin normalizar el texto); **sin tope** (el paquete crece sin control: D-6).
- **DEC-7 — El `reference` no lo verifica el CLI.** Puede apuntar al árbol instalado del skill, que el CLI no resuelve ⇒ el producto no puede comprobarlo sin conocer la instalación. *Consecuencia:* la comprobación es del **reviewer** (E4/E6), que sí puede leer el proyecto y la instalación. *Rechazada:* verificar el `reference` contra el proyecto: daría una garantía **falsa** (el archivo puede estar en el árbol instalado, no en el proyecto).
- **DEC-8 — La fila viaja como `--current-decision` (JSON, repetible), no como archivo.** *Razón:* un solo mecanismo, sin un segundo artefacto que pueda divergir de la tabla, sin ambigüedad de parseo (el `summary` es texto libre: un separador textual lo rompería) y con la fila **en el request** (JSON) desde el primer momento. *Rechazada:* un `--current-decisions <archivo.json>`: crea un segundo lugar donde vive el contenido de las decisiones, y obliga a decidir quién lo escribe y con qué garantía de frescura.
- **DEC-9 — El principio se materializa en un archivo **nuevo** del skill, no en `SKILL.md` ni en el `stage-2`.** *Razón:* el patrón del repo (un dueño canónico en `references/`, los consumidores lo referencian) y el hecho de que `SKILL.md` se carga siempre (una regla de diseño para dos roles cargaría a todos). *Rechazada:* `SKILL.md` (carga universal) y `references/stage-4-review.md` (es el dueño de la **calibración** del reviewer, no del principio de diseño: mezclar dos dueños crea dos fuentes).
- **DEC-10 — El deber del reviewer vive en `references/stage-4-review.md`, con puntero desde la fuente del rol y su bloque estático.** *Razón:* el mismo patrón que la calibración (`sources/roles/reviewer.md`:44-46 → `references/stage-4-review.md`:8-10). *Rechazada:* enunciar el procedimiento completo en el bloque de rol (duplicaría la regla en dos superficies y lo haría divergir) y en el substage de la subfase (el deber es **del rol**, no de una subfase: aplica a la revisión del resultado y a la del borrador).
- **DEC-11 — La tabla se mantiene en el evento «ADR aprobado», no en el cierre de cada feature.** (Q6, del orquestador.) El exit gate de stage 5 **no** cambia. *Razón:* el evento que crea una decisión es su aprobación; el cierre de una feature puede no tener decisión nueva, y atar ahí la tabla la deja envejecer sin evento que la mueva. *Consecuencia:* el upkeep es **procedimiento**, no producto (D-4) ⇒ por eso la fila se declara al preparar el paquete, y la completitud no está garantizada mecánicamente (D-1).
- **DEC-12 — La revisión del borrador de esta spec sigue el procedimiento vigente de 006-006.** 006-006 ya está construida (el gate 2→3 con la revisión de borrador es la superficie vigente): esta spec y este plan se revisan con `draft-plan` + `plan-review` (la revisión del **borrador**, sobre un borrador no aprobado, que es exactamente lo que 006-006 habilitó), y la aprobación es de la autoridad vigente. *Razón:* la feature 006-004 **no** reimplementa la revisión; la usa.
- **DEC-13 — El CAS se hace contra el digest BASE de la propuesta; ante conflicto, la vía es re-despachar, nunca fusionar ni retocar el digest.** *(Decisión del orquestador, 2026-10-20; general antes que específica.)* **Medido** (M9): `_apply_copy` (`cdad_result.py`:822-855) compara el destino con `expected_previous_sha256` y **no** sabe sobre qué versión redactó el rol la propuesta ⇒ una autorización con el digest **actual** pasa y **pisa** el cambio ajeno. **Decisión:** (a) el digest declarado es **siempre** el **base** —la versión del destino sobre la que el rol preparó la propuesta; (b) un conflicto se resuelve **re-despachando** al rol con un paquete nuevo sobre la base nueva; (c) **no** se fusiona a mano ni se **actualiza el digest esperado** para forzar el paso (eso borraría el cambio del otro escritor); (d) el orquestador, que mantiene la tabla, **escribe sus filas directamente en `docs/`** con su commit; (e) la evidencia identifica los bytes aplicados. **Dónde vive:** por ser **general** (afecta a toda materialización con CAS), en el **paso 3 (MATERIALIZE)** del protocolo de materialización de `references/re-entry.md`; el caso de la tabla, en su sección `### Scribe`. *Rechazadas:* (i) **materializar contra el digest actual** (draft-001): no detecta la propuesta obsoleta y pisa al otro escritor — es el defecto B-2; (ii) **fusionar a mano** la fila del orquestador con la propuesta del scribe: mezcla dos ediciones en un artefacto que nadie redactó y rompe la trazabilidad del receipt; (iii) **subir el digest esperado** sin rehacer la propuesta: hace pasar el CAS **descartando** el cambio ajeno — es el peor de los tres, porque el conflicto deja de ser visible.
- **DEC-14 — Las comprobaciones se separan por superficie: plantilla/procedimiento (U4) y siembra verificada (U7), con la materialización (U5) en el medio.** *(Dictamen `plan-review-001.md`, B-1.)* **Razón:** el gate de una unidad no puede depender de documentos que produce una unidad **pendiente** (U4 exigía la tabla viva y el ADR-034, que produce U5: en el GREEN de U4 esos documentos no existían). **Decisión:** U4 verifica **sólo** plantilla y procedimiento; U5 **materializa** los dos documentos del proyecto y su gate es la materialización **más la aprobación registrada**; **U7 (nueva)** verifica la tabla viva y el ADR-034, con gate **posterior** a U5. *Consecuencia declarada:* el bloque de `tests/validate-consistency.sh` que mira la tabla viva **nace en U7**, no en U4 ⇒ `make validate` es verde en U4 **sin** la tabla, y vuelve a ser verde en U7 **con** ella. *Rechazada:* dejar la comprobación en U4 «con la tabla ya sembrada» (es el defecto B-1: una unidad que sólo puede pasar si otra pendiente ya entregó su producto); y la alternativa de que U5 verificara su propia siembra ⇒ el gate quedaría atado a un artefacto que la misma unidad produce, sin una comprobación independiente (y el dictamen pide una unidad **posterior**, no la misma).
- **DEC-15 — El validador permanente lleva invariantes duraderas; el inventario sembrado es evidencia puntual.** *(Dictamen `plan-review-002.md`, B-3.)* **Razón:** el inventario inicial (25 vigentes, 1 obsoleta, 8 `Proposed` excluidos) sirve para **acreditar la siembra**, pero **no** es una propiedad estable del proyecto: el siguiente ADR aprobado exige una fila más y el validador rechazaría una tabla **correctamente** mantenida; aprobar un `Proposed` o reemplazar una decisión rompen igual las cantidades fijadas ⇒ el procedimiento normal que esta feature introduce obligaría a **modificar sus tests históricos** después de cada cambio legítimo del inventario. **Decisión:** (a) el bloque de `tests/validate-consistency.sh` que mira la tabla viva comprueba **sólo** invariantes duraderas —cada fila apunta a un archivo existente; toda fila `obsoleto` nombra un reemplazo existente; todo `roles` está en el vocabulario cerrado; la fila de ADR-034 existe; la nota declara que el estado lo declara quien mantiene la tabla—; (b) el inventario sembrado **se acredita una vez**, en la aceptación de U5 y U7, y **no** se convierte en aserción; (c) el **cierre** del comprobador es un **caso descartable**: agregar un ADR aprobado y reemplazar una decisión **pasan**, y una fila con archivo inexistente **falla**. *Rechazada:* (i) **fijar el inventario en el validador** (`draft-002`): convierte una fotografía en una restricción permanente y penaliza el upkeep normal; (ii) **no comprobar nada de la tabla**: perdería el control negativo de la desalineación (E4) y el deber del reviewer quedarían sin oráculo; (iii) **re-derivar el estado de cada ADR desde su texto** para que el validador supiera qué filas *deberían* existir: contradice D-3 (el estado **no** es derivable: cuatro vocabularios y tres formatos) y rechazaría una tabla correctamente declarada.

## 6. Desconocidos (V-n) y su resolución

- **V-1 — ¿El CLI instalado renderiza la sección con la misma forma?** Lo **no medido** es el render del producto **instalado** con `--current-decision` (el árbol instalado viaja completo, `install.sh`:376, pero el CLI instalado es otro proceso). *Resolución:* el RED de U1/U2 renderiza **desde el producto instalado** y compara byte a byte con el render del repo (el patrón de `tests/test_004_003_t2_plan_review.py`:290).
- **V-2 — ¿`make staging` sigue siendo determinista con las fuentes de rol cambiadas?** *Resolución:* dos corridas de `make staging` con comparación byte a byte de los agentes de architect y de reviewer; si no lo fuera, es un defecto de 004-001 ya cubierto por sus propios tests (`tests/test_cdad_generate.py`).
- **V-3 — ¿`receive` revalida el request con el conjunto ampliado?** `cdad_result.py`:561 llama a `validate_request`, que es **la misma función** que usa `prepare` ⇒ el conjunto cerrado ampliado aplica en ambos lados. *Resolución:* el RED **recibe** un paquete cuyo request lleva `current_decisions` (hoy sería rechazado) y otro con una fila malformada (hoy también): el RED lo demuestra, no lo supone.
- **V-4 — ¿El bloque estático sigue bajo el techo tras las adiciones?** Medido hoy: máximo **3031** bytes (`reviewer/plan-review`) con techo **12000** ⇒ holgura **8969**. Las adiciones previstas (dos líneas de deber en `packets/roles/architect.md` y `packets/roles/reviewer.md`, ~150-300 bytes cada una) llevan el peor caso a ≈**3400** bytes. *Resolución:* la **medición** se repite en el RED de U3/U4 y se registra; si superara el techo, el RED falla (y la respuesta **no** es subir el techo).
- **V-5 — ¿La política de compatibilidad entre revisiones se comporta como queda declarada?** Lo **no medido** es la corrida de dos fases con el CLI real (publicar con las fuentes anteriores → cambiar las fuentes → recibir después). *Resolución:* el caso de PD-16(c) de 006-006, reproducido aquí (esta feature **también** cambia dos de las tres fuentes de instrucción: `packets/roles/architect.md` y `packets/roles/reviewer.md`), se ejecuta en U6 y su salida real se pega en la evidencia.
- **V-6 — ¿Cómo se comporta la cadena del CAS sobre `docs/systemPatterns.md` con dos escritores?** Medido en el código: la materialización con `expected_previous_sha256` que no coincide con el destino ⇒ `ResultError` «conflict: … current digest does not match expected_previous_sha256 (CAS): refusing to overwrite» (`cdad_result.py`:847-848); y con `expected_previous_sha256` nulo sobre un destino divergente ⇒ «(create-only)» (`:844`). Lo **no medido** es la **corrida real** con los dos escritores y con la **base** como digest declarado. *Resolución:* el caso de PD-9/E7 se ejecuta en U6 con la cadena completa —D0 → propuesta(base D0) → D1 (escritura directa del orquestador) → materialización con la **base D0** y su rechazo nombrado → re-despacho con paquete nuevo sobre **D1** → propuesta(base D1) → materialización exitosa → documento final que conserva la fila nueva y los cambios del scribe— y **los bytes aplicados** quedan identificados en la evidencia; si el comportamiento real difiere de lo declarado, **se corrige la declaración** (no al revés).

## 7. Medición de la aceptación

- Se mide lo **observado**: el rc de cada comando, el contenido del `REQUEST.json`, el texto de la sección renderizada, la comparación byte a byte de los renders, la **medición** del bloque estático, la salida de `make validate`, los bytes de las dos `make staging` y el texto de las derivaciones.
- La cadena del CAS se mide **por sus bytes**: el digest base de cada propuesta, el digest del destino en cada momento, el texto del rechazo, el diff del documento final contra la base nueva y la identificación de los bytes aplicados.
- **«Desconocido» no es cero** y no se generaliza el resultado de un recorrido. La evidencia de que la **vara** (E1..E7) funciona es el **recorrido real** (PD-12), no una simulación: un recorrido que no atrapa ningún defecto es **buen resultado** y se declara igual.
- La **suite completa** la corre **una vez**, quien cierra (política declarada en el paquete); las unidades citan su propia evidencia focal y las regresiones de su ficha.
- **No** se fijan reducciones porcentuales, tiempos ni tamaños como meta. El tope de 32 (§2.4) **no** es una meta de rendimiento: es un límite de seguridad declarado.

## 8. Fuera de alcance

1. **Índices generados** (una `docs/adr/README.md` índice o cualquier tabla derivada por herramienta) — excluido por el plan §10.
2. **Gates de cita obligatoria** (que el paquete exija citar el ADR, o que el reviewer tenga una puerta que la exija) — excluido por el plan §10. E4 es un **hallazgo**, no una puerta.
3. **Cambios en `status`**: ni el campo `**Status**` de los ADR (no se normaliza el vocabulario: M4) ni el `status` de la máquina de estados. El «estado» de la tabla es una propiedad de la **fila**, que es el diseño del propio plan (Q4). *La excepción declarada:* el ADR-034 que esta feature **crea** lleva su estado de borrador y, tras su aprobación, el estado aprobado — es el ADR **nuevo** de la feature, no una normalización de los 33 existentes.
4. **El exit gate de stage 5** — no se le agrega ninguna casilla (Q6).
5. **Un kind, subfase, agente, stage, tipo de artefacto o verbo nuevos**: se reutilizan `prepare`, el campo opcional del request, el kind `scribe-systemPatterns` y el materializador existente (`assets/artifact-policy.json`:13).
6. **Que el CLI lea o parsee el documento del proyecto** (O2, DEC-1).
7. **Una operación de CLI o una clase de transición para la aprobación de un ADR** (D-4): el upkeep de la tabla es procedimiento del orquestador, no estado verificable por el producto.
8. **La revisión formal del resultado** (etapa 4) y su calibración: se tocan **sólo** para añadirles el deber del reviewer; su texto vigente no se altera.
9. **El CLI instalado en el HOME del dueño**: el despliegue es del owner (`docs/epics/…/plan.md` §6); esta feature prepara el candidato y su receta, no despliega.
10. **Migrar, reescribir o normalizar** los 33 ADR existentes: no se toca ninguno de ellos (salvo **crear** `ADR-034`).
11. **Retirar formalmente ADR-001 y ADR-005**: su contenido operativo (el mapa de modelos por agente) ya no tiene efecto desde ADR-033, pero **su retiro formal es una decisión del dueño** (ADR-033 §Notas). La tabla los refleja **en vigor** con un `summary` que lo dice, en vez de afirmar un reemplazo que nadie ha declarado.
12. **Cambiar el producto de CAS** (que pasara a verificar la base): DEC-13 es **procedimiento declarado**; el producto sigue protegiendo el destino, no la base (L-7).

## 9. Riesgos residuales

- **La completitud de la tabla no está garantizada mecánicamente** (D-1): el producto garantiza «la fila declarada nombra a este rol», no «toda fila vigente fue declarada». *Mitigación:* el procedimiento de upkeep (DEC-11) + el deber del reviewer (PD-8), que compara la tabla con `docs/adr/`. *Riesgo residual:* **declarado** — un orquestador distraído puede preparar un paquete sin la fila que le corresponde; el reviewer lo ve, pero no lo bloquea.
- **El puntero al archivo del principio no es resoluble en la ruta de paquete** (D-2): el rol no carga el skill. *Mitigación:* la **obligación** viaja en el bloque estático y en el cuerpo del agente; el **principio íntegro** queda como dirección a seguir cuando el rol alcance el skill. *Riesgo residual:* el mismo del patrón vigente (puntero a `references/stage-4-review.md`), **declarado**.
- **Una fila puede quedar desactualizada** si el orquestador aprueba un ADR y no actualiza la tabla. *Mitigación:* el upkeep es un evento con nombre (aprobación de un ADR) y el reviewer lo contrasta. *Riesgo residual:* **declarado**; el exit gate de stage 5 **no** lo cubre (Q6) ⇒ es deuda (D-5).
- **El validador permanente no comprueba la completitud del inventario**: por construcción (INV-15) no sabe cuántas filas hay ni si cada ADR tiene fila ⇒ un ADR aprobado **sin** fila no lo detecta el validador. *Mitigación:* el upkeep es un evento con nombre (aprobación de un ADR, DEC-11) y el **reviewer** contrasta la tabla con `docs/adr/` (E4, PD-8). *Riesgo residual:* **declarado** — la alternativa (fijar el inventario) queda rechazada por DEC-15 porque rompe el procedimiento normal de la feature.
- **El estado de la fila es una declaración, no un hecho derivado** (D-3): 4 vocabularios, 3 formatos, 8 *Proposed*, 1 reemplazo parcial. *Mitigación:* la tabla **declara**; el reviewer contrasta contra el conjunto declarado, no contra una re-derivación. *Riesgo residual:* **declarado** — una tabla mal declarada es posible y la revisión la expone, no la impide.
- **Un paquete en vuelo se invalida al cambiar las fuentes de instrucción** — y esta feature cambia dos (`packets/roles/architect.md`, `packets/roles/reviewer.md`). *Mitigación:* la política declarada (L-1), con su caso en U6. *Riesgo residual:* **declarado y aceptado** (mismo precedente que 006-006 D-12).
- **El estado «obsoleto» de una fila no viaja** ⇒ el rol que recibe el paquete **no ve** que la decisión fue reemplazada (sólo ve la nueva). *Mitigación:* la fila nueva nombra su `reference`; la historia queda en la tabla del proyecto. *Riesgo residual:* **declarado y aceptado** — es exactamente lo que el plan pide («la fila vieja se conserva, la distribución se detiene»).
- **La fila puede crecer sin que nadie lo note** si el orquestador declara filas irrelevantes. *Mitigación:* R-5 (la fila debe nombrar al rol) + el tope (R-7). *Riesgo residual:* **declarado** — el tope acota el volumen, no la pertinencia.
- **Dos escritores de la tabla** (orquestador y scribe): el orquestador escribe la fila; el scribe puede proponer un `systemPatterns.md` completo. *Mitigación:* CAS **contra la base** + reconciliación por **re-despacho** (DEC-13, PD-9). *Riesgo residual:* **declarado** — el conflicto es ruidoso (no hay sobrescritura silenciosa) y la reconciliación cuesta un **ciclo extra** de despacho; el coste es visible, no oculto.
- **La base la conoce el orquestador, no el producto**: si el orquestador registrara mal la base, el CAS compararía contra un digest que no es la base ⇒ o falla limpio (conflicto) o pasa sobre una versión que no era la base. *Mitigación:* la base es el digest del destino **en el momento de preparar el paquete del rol**, un valor que el orquestador puede leer y anotar; la evidencia de U6 muestra la cadena con los digests. *Riesgo residual:* **declarado** (L-7).

## 10. Límites y deuda declarada

- **L-1 — Deuda de compatibilidad entre revisiones (heredada del precedente de 006-006).** Un paquete publicado antes de un cambio de las fuentes de instrucción **no** es recibible después (los digests de las fuentes son parte de la identidad del paquete: `cdad_packet.py`:1080-1094 compone y publica sus digests; la recepción re-renderiza y compara, `cdad_result.py`:563-566). **No** se corrige el renderer. La política declarada (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo) y su caso demonstrativo están en U6. Deuda **declarada**, no defecto: es inherente al contrato de paquete, y esta feature lo **toca** (dos de las tres fuentes) ⇒ lo declara.
- **L-2 — Deuda del puntero no resoluble en la ruta de paquete** (D-2): la lectura íntegra del principio depende de que el rol alcance el skill. Patrón vigente, limitación ya aceptada.
- **L-3 — Deuda de la completitud de la tabla** (D-1): el upkeep es procedimiento; la garantía del producto es de **forma**, no de completitud. La alternativa O2 (CLI que lee la tabla) queda sobre la mesa con su coste declarado (acoplar el producto a un formato de documento).
- **L-4 — Deuda de la verificación del `reference`** (DEC-7): el CLI no lo comprueba; la comprobación es del reviewer. El `file` sí se comprueba (existe en el proyecto).
- **L-5 — Deuda del exit gate de stage 5** (D-5): el gate no menciona `docs/systemPatterns.md` ⇒ la tabla tiene **un** escritor declarado (el orquestador) y el kind `scribe-systemPatterns` queda como capacidad latente; el procedimiento de la re-entry del scribe declara la reconciliación, pero el **gate** no la exige.
- **L-6 — Deuda del esquema del request** (D-6): `assets/packet-request.schema.json` declara `additionalProperties: false` y **no** incluye `agent` (añadido por 006-005) ⇒ el esquema ya no describe el request vigente. Esta feature **agrega** su propiedad (`current_decisions`) para no agravar la brecha; **no** corrige la de `agent` (fuera de alcance). El esquema no se valida en runtime (medido: ningún test lo valida) ⇒ la brecha es documental, no funcional.
- **L-7 — El producto no verifica la base del CAS; la disciplina es del procedimiento.** Medido (M9): el materializador compara el destino con `expected_previous_sha256` y **no** sabe sobre qué versión se redactó la propuesta ⇒ la regla de DEC-13 vive en `references/re-entry.md` (paso 3 MATERIALIZE) y la cumple el orquestador. *Lo que **no** se promete:* que el producto detecte por sí solo una propuesta con base obsoleta; lo detecta **el CAS** (rechazo nombrado) cuando la base declarada no es el destino actual, y lo que **no** detecta es el caso peor —base declarada = destino actual, propuesta redactada sobre otra base— que por eso la regla obliga a declarar la base **real**. *Cerrar esta deuda* (que el producto transporte la base y la verifique) sería un cambio de la **autorización** y del materializador: **fuera de alcance** de esta feature y declarado como tal.
- **D-1 a D-6 (numeración del discovery, conservada):** (D-1) el bloque estático no tiene dueño de las filas ⇒ completitud no garantizada mecánicamente; (D-2) el puntero a la referencia del principio no es resoluble en la ruta de paquete; (D-3) el estado de los ADR no es uniforme ⇒ la tabla no puede derivarse de los archivos; (D-4) no hay operación de CLI ni clase de transición para la aprobación de un ADR ⇒ el upkeep es procedimiento; (D-5) el exit gate de stage 5 y el procedimiento del scribe no mencionan `docs/systemPatterns.md`; (D-6) el paquete puede crecer sin tope ⇒ esta feature lo acota con un tope declarado y fail-closed (DEC-6).

## 11. Trazabilidad con el contrato de la épica

| Aceptación (plan §10, enmienda 003) | PD |
|---|---|
| 1. La plantilla del Memory Bank suma la sección «Decisiones vigentes»: una fila por ADR con archivo, estado (vigente u obsoleto, y cuál lo reemplaza), resumen en una línea y roles que deben consumirlo | PD-7, PD-11 |
| 2. El orquestador la mantiene: agrega la fila al aprobarse un ADR y marca el reemplazado como obsoleto. El paquete de cada rol lleva las filas vigentes que lo nombran | PD-2, PD-3, PD-5, PD-6, PD-8, PD-9 |
| 3. El reviewer revisa que la tabla coincida con los ADR del repo y que el cambio respete las decisiones vigentes de su rol | PD-8, PD-12 (E4) |
| 4. Una decisión que cambia la metodología de CDAD no está terminada hasta que su regla está en el skill o el agente instalable; la fila guarda la referencia | PD-10, PD-11 |
| Aceptación: plantilla y referencias actualizadas (stage-5, re-entry, reviewer); un test de texto que fija la sección y las dos responsabilidades; `make validate` y la suite pasan | PD-7, PD-8, PD-9, PD-10, PD-13 |

| Aceptación (plan §12, enmienda 005) | PD |
|---|---|
| 1. ADR-034 registra el principio y su límite; lo redacta el architect y lo aprueba el dueño | PD-11 (el ADR entregado, borrador `Proposed`) + la aprobación, acto separado (INV-6, INV-14) |
| 2. Fuente única instalable: el principio vive en un solo lugar del skill; los roles lo referencian | PD-10, INV-1, INV-12 |
| 3. Architect: considera alternativas generales y específicas en las decisiones relevantes y explica el criterio elegido | PD-10 |
| 4. Reviewer: evalúa consecuencias reales (duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento); la falta de una abstracción, por sí sola, no es un defecto | PD-8, PD-10 |
| Vehículo: se construye junto con 006-004, que lo distribuye como primera fila de «Decisiones vigentes» | PD-11 (ADR-034 es fila de la tabla sembrada) |
| Aceptación: ADR-034 aprobado; un test de texto fija la fuente única, la obligación del architect, el criterio del reviewer y el límite; `make validate` y la suite pasan | PD-10, PD-13 |

**Inventario (no es un ítem de aceptación del contrato):** los conteos de la siembra (25 vigentes · 1 obsoleta · 8 `Proposed` excluidos) **no** son un ítem de aceptación de la épica **ni** una aserción del validador: son **evidencia puntual** de U5/U7 (DEC-15, INV-15).

**Garantía propia de la feature** (no es un ítem de aceptación de la épica): la fila viaja **en** el paquete —no por el alcance de lectura— y **falla cerrado** cuando su forma, su rol, su estado o su cantidad no son admisibles ⇒ PD-1..PD-6, PD-13. Y la reconciliación de la tabla **no pisa** al otro escritor, porque el CAS es contra la base y la reconciliación es un re-despacho ⇒ PD-9, E7, DEC-13.

## 12. La siembra de este repo (Q3)

**Qué se siembra.** `docs/systemPatterns.md` gana la sección `## Decisiones vigentes` como **primer H2** (después de la introducción), con una tabla de una fila por decisión.

**La regla de siembra (declarada, con su evidencia).** Se siembra una fila por decisión **en vigor** (Accepted/Verified) y una por cada decisión **reemplazada** (marcada `obsoleto` con su reemplazo). **Los 8 ADR *Proposed* no son filas** (Q1: no gobiernan). Los roles de cada fila se declaran **al aprobarse el ADR** (Q2) y, en esta siembra, se derivan del **texto operativo** de cada ADR: los roles cuyo trabajo la decisión constrain hoy. Una decisión cuya regla es el propio ADR lleva la **referencia** = el propio ADR; una decisión cuya regla vive en el skill lleva la **referencia** = el archivo del skill.

**Filas sembradas (25 vigentes + 1 obsoleta = 26) — la fotografía de la siembra:** *este inventario **acredita** la siembra y **no** es una restricción permanente: el validador no lleva ningún conteo (INV-15, DEC-15).*

| Decisión | Archivo | Estado | Roles que deben consumirla | Referencia |
|---|---|---|---|---|
| ADR-001 | `docs/adr/ADR-001-modelos-por-etapa.md` | vigente | orchestrator | el propio ADR |
| ADR-002 | `docs/adr/ADR-002-arquitectura-repo-fuente-e-install-sh.md` | vigente | architect, orchestrator | el propio ADR |
| ADR-003 | `docs/adr/ADR-003-orquestador-materializa-artefactos.md` | vigente | architect, reviewer, scribe, orchestrator | el propio ADR |
| ADR-004 | `docs/adr/ADR-004-usuario-aprueba-no-solo-humano.md` | vigente | architect, orchestrator | el propio ADR |
| ADR-005 | `docs/adr/ADR-005-modelos-via-mofgw.md` | vigente | orchestrator | el propio ADR |
| ADR-006 | `docs/adr/ADR-006-git-ejecutado-por-agentes-aprobacion-del-usuario.md` | vigente | test-writer, implementer, orchestrator | el propio ADR |
| ADR-007 | `docs/adr/ADR-007-perfiles-de-modelos.md` | **obsoleto (reemplazado por ADR-033)** | orchestrator | el propio ADR |
| ADR-008 | `docs/adr/ADR-008-claude-code-como-segundo-runtime.md` | vigente | orchestrator | el propio ADR |
| ADR-009 | `docs/adr/ADR-009-politica-rtk-allowlists.md` | vigente | architect, test-writer, implementer, reviewer, scribe | el propio ADR |
| ADR-010 | `docs/adr/ADR-010-modelo-unico-mvp-epic-003.md` | vigente | orchestrator | el propio ADR |
| ADR-011 | `docs/adr/ADR-011-autonomia-supervisada-limites-proporcionales.md` | vigente | architect, test-writer, implementer, reviewer, scribe, orchestrator | el propio ADR |
| ADR-013 | `docs/adr/ADR-013-contrato-plan-borrador-revision-sin-aprobacion.md` | vigente | architect, reviewer, orchestrator | el propio ADR |
| ADR-014 | `docs/adr/ADR-014-recepcion-materializacion-aprobacion-separadas.md` | vigente | orchestrator | el propio ADR |
| ADR-015 | `docs/adr/ADR-015-guard-progreso-analizador-readonly-juicio-orquestador.md` | vigente | orchestrator | el propio ADR |
| ADR-017 | `docs/adr/ADR-017-activacion-por-proyecto-raiz-aislada.md` | vigente | orchestrator | el propio ADR |
| ADR-018 | `docs/adr/ADR-018-clases-de-referencia-declaradas-por-el-escritor.md` | vigente | orchestrator | el propio ADR |
| ADR-019 | `docs/adr/ADR-019-aprobacion-por-rol-nombra-el-contrato-reemplazo-conserva-el-encargo.md` | vigente | test-writer, implementer, orchestrator | el propio ADR |
| ADR-020 | `docs/adr/ADR-020-politica-unica-de-evidencia-y-procedencia-declarada.md` | vigente | test-writer, implementer, reviewer, orchestrator | el propio ADR |
| ADR-021 | `docs/adr/ADR-021-arranque-guiado-procedimiento-corto-por-referencia.md` | vigente | orchestrator | el propio ADR |
| ADR-022 | `docs/adr/ADR-022-mapas-de-permisos-derivados-coherentes-con-el-clasificador.md` | vigente | test-writer, implementer, orchestrator | el propio ADR |
| ADR-023 | `docs/adr/ADR-023-delegacion-externa-interfaz-comun-adaptador-por-destino.md` | vigente | orchestrator | el propio ADR |
| ADR-024 | `docs/adr/ADR-024-medicion-contexto-instrumento-opcional-readonly-no-gate.md` | vigente | orchestrator | el propio ADR |
| ADR-031 | `docs/adr/ADR-031-seleccion-explicita-de-modo-y-servicio-no-gestionado.md` | vigente | orchestrator | el propio ADR |
| ADR-032 | `docs/adr/ADR-032-delegacion-por-capa-agente-del-runtime-dueno-del-mecanismo.md` | vigente | architect, orchestrator | el propio ADR |
| ADR-033 | `docs/adr/ADR-033-modelos-por-configuracion-sin-perfiles.md` | vigente | orchestrator | el propio ADR |
| **ADR-034** | `docs/adr/ADR-034-principio-general-antes-especifico.md` | vigente | architect, reviewer | `skills/cdad-cycle/references/design-principles.md` |

**Asignaciones no obvias y su evidencia** (para que la siembra sea auditable):
- **ADR-003** → los tres roles read-only + el orquestador: su texto operativo es que el orquestador **materializa** los artefactos de los roles read-only, que por eso entregan **texto final** y no escriben.
- **ADR-006** → test-writer, implementer y orquestador: su texto nombra literalmente «roles write-capable (test-writer, implementer)» y «el orquestador commitea `docs/**`».
- **ADR-009** → los cinco roles: su texto asigna `rtk read*/grep*/find*/diff*` a los roles lectores (architect, reviewer, scribe) y los **deniega** a los write-capable (test-writer, implementer) ⇒ la decisión gobierna a los cinco.
- **ADR-011** → los cinco + el orquestador: fija el marco operativo de **todo** agente («el agente elige herramientas… dentro de ese marco») y la responsabilidad del orquestador.
- **ADR-020** → test-writer, implementer, reviewer y orquestador: es la **política única de evidencia** (consumida por los paquetes de GREEN/refactor/review-fix) y su cierre con suite completa, que corre el orquestador.
- **ADR-001 y ADR-005** → `orchestrator`, con un `summary` que **declara** que su mapa de modelos por agente **no tiene efecto operativo** desde ADR-033 y que **su retiro formal es una decisión pendiente del dueño** (ADR-033 §Notas). No se declaran `obsoleto` porque **nadie ha declarado** ese reemplazo.
- **ADR-008** → `vigente` con un `summary` que nombra el alcance residual (hooks, guard de rutas, agentes `claude-code`, instalación, validación) y el reemplazo **parcial** de la parte de perfiles y modelos (DEC-4).
- **ADR-010** → `orchestrator`, con un `summary` que declara su alcance acotado (excepción de modelo único para el MVP del epic-003) y su regla de vencimiento.
- **ADR-002, 004, 014, 015, 017, 018, 021, 022, 023, 024, 031, 032, 033** → su texto operativo no gobierna el trabajo de un rol delegado sino la conducta del orquestador (dónde se desarrolla y se instala, quién aprueba, la clase de una referencia, el arranque, la interfaz de delegación, el guard, la política de permisos, la política de evidencia, el modo de ejecución, la capa de delegación, la fuente de modelos) ⇒ `orchestrator`; **ADR-019** gobierna además el pin de aprobación de los roles de construcción (test-writer, implementer) ⇒ los tres.

**Qué queda fuera de la tabla, y por qué (declarado, como pide Q3):**
1. **Los 8 ADR *Proposed*** (012, 016, 025, 026, 027, 028, 029, 030): no gobiernan trabajo alguno hasta su aprobación (Q1). Se listan en la nota de la tabla para que el conjunto sea auditable. **Esta lista es una fotografía de la siembra**: cuando uno de ellos se apruebe, pasa a ser fila y la lista se actualiza — y **el validador no se toca** (DEC-15).
2. **Nada más**: las 24 decisiones en vigor tienen fila (24 + ADR-034 = 25 vigentes) y la única reemplazada tiene su fila obsoleta.

**La nota de la tabla.** La sección incluye, bajo la tabla, una nota breve que declara: (a) la lista de ADR excluidos y el motivo; (b) que el **estado de una fila lo declara quien mantiene la tabla** y no se re-deriva de los ADR (D-3); (c) que la **referencia** es el lugar donde vive la regla que la decisión implanta. Sin esa nota, el conjunto parecería completo por casualidad.

**Verificación de la siembra (PD-11) — y dónde vive, en dos capas.** (1) **Invariantes duraderas** ⇒ en el bloque de texto de `tests/validate-consistency.sh` de la **unidad de verificación de la siembra (U7 del plan)**, cuyo gate corre **después** de la materialización de U5 y de la aprobación del ADR-034 — y **no** en U4, cuya comprobación es sólo de plantilla y procedimiento (DEC-14, B-1). Ese bloque comprueba **propiedades**, no **cifras**: la sección, la existencia del archivo de cada fila, la existencia del reemplazo de cada fila `obsoleto`, el vocabulario cerrado de `roles`, la fila de ADR-034, la nota del estado, y el ADR-034 materializado (aprobado, apuntando a la fuente única, sin re-enunciar el principio). (2) **Evidencia puntual** ⇒ el **inventario** sembrado (25 vigentes · 1 obsoleta · 8 `Proposed` excluidos) se acredita **una vez**, en la evidencia de aceptación de U5 y U7, y **no** entra en el validador: un ADR aprobado nuevo o un reemplazo **no obligan a tocar** `tests/validate-consistency.sh` (DEC-15, INV-15). La **aprobación del ADR-034** es un acto **posterior y separado** de su redacción: el documento que el architect entrega es un **borrador `Proposed`**, y el que se materializa en `docs/adr/` lleva el estado **aprobado** con la evidencia de esa aprobación registrada (INV-14). La comprobación **reconoce** esa aprobación y **no** exige que el ADR siga pendiente.

Status: **BORRADOR — SIN APROBAR** (draft-003). La aprobación es un acto separado de la autoridad vigente.
===END spec.md===

===BEGIN plan.md===
# 006-004-active-decisions-table — PLAN (etapa 2, borrador draft-003)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (superficie vigente de 006-006: `draft-plan` + `plan-review` sobre un borrador no aprobado; DEC-12 de la spec).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §10 y §12 (sha256 `d6da11db…9809`, verificado en disco). Spec: la de esta carpeta (misma entrega). Decisiones de entrada: `docs/epics/epic-006-opencode-concurrency/execution.md`:399-415.
Decisiones de entrada de esta revisión (orquestador, 2026-10-20): la **regla general del CAS por digest base** (spec DEC-13) y la **separación de las comprobaciones de siembra** (spec DEC-14), que introduce **U7**.
Dictamen aplicado: `docs/specs/006-004-active-decisions-table/plan-review-001.md` (2 BLOCKING · 2 OPTIONAL) — los cuatro hallazgos están corregidos (§7) — y `docs/specs/006-004-active-decisions-table/plan-review-002.md` (1 BLOCKING · 1 OPTIONAL), corregidos en esta revisión (§8).
Insumo: `docs/specs/006-004-active-decisions-table/discovery.md`. Base medida: HEAD `a9cc7ab`.
Medición de partida: el bloque estático máximo ocupa **3031** bytes (`reviewer/plan-review`) con techo declarado de **12000** (`cdad_packet.py`:1063-1079) ⇒ holgura **8969**; el mínimo, **1309** (`scribe/memory`). El tope de filas por paquete es **32** (spec §2.4) y el conjunto vigente sembrado es de **25** filas.

## 1. Orden y dependencias

`U1 (el encargo: la fila, su forma y el tope) → U2 (la sección aditiva del render) → U3 (el principio: una casa y las dos obligaciones) → U4 (la tabla y su upkeep: plantilla y procedimiento) → U5 (la siembra: materialización de los documentos del proyecto) → U7 (la verificación de la siembra) → U6 (el recorrido de aceptación)`.

- **U1 → U2**: la sección del render **consume** el campo que U1 define y valida; sin U1 no hay qué renderizar.
- **U2 → U3 → U4**: U3 fija **el texto de rol** (la casa del principio y el deber del reviewer); U4 fija **el documento del proyecto** (la sección de la plantilla, el upkeep de stage-5 y la reconciliación de la re-entry) y **consume** el texto de U3 (el deber del reviewer que U3 escribe es el mismo que U4 nombra en el recorrido). U3 precede a U4 porque U4 **reutiliza** el deber declarado en U3, no lo re-declara.
- **U5** depende de U3 y U4: siembra la tabla (que nombra ADR-034) y materializa el ADR-034 (que apunta a la casa del principio). **Precondición de U5**: la **aprobación** del ADR-034 por la autoridad vigente — la fila de una decisión que aún no está aprobada no puede ser `vigente`. **El gate de U5 es la materialización misma más la aprobación registrada**: U5 **no** se gatea con el bloque de texto que mira la tabla viva (ese bloque es de U7).
- **U7** depende de U5: verifica la **tabla viva** y el **ADR-034 materializado**. Su gate corre **después** de la materialización ⇒ **no exige ningún documento de una unidad pendiente** (DEC-14, B-1).
- **U6** depende de todo (U1–U5 y U7): es el recorrido real.
- **Ninguna unidad es `parallel` con otra**: U1 y U2 tocan el mismo archivo (`skills/cdad-cycle/scripts/cdad_packet.py`), y U3 y U4 se tocan (`sources/roles/reviewer.md`, `packets/roles/reviewer.md`); el paralelismo inseguro lo rechaza el CLI (`cdad_packet.py`:3503-3523, «unsafe parallelism»).
- Ninguna unidad empieza sin su RED declarado y sin la revisión de spec/plan hecha.

### 1.1 Por qué U4 ya no puede gatear la tabla viva (B-1)

En `draft-001`, U4 incorporaba a `tests/validate-consistency.sh` comprobaciones sobre la **tabla viva** y sobre la **existencia del ADR-034**, y exigía `make validate` verde. Pero **ambos documentos los produce U5**, que depende de U4: al llegar al GREEN de U4 sus productores siguen pendientes, y el implementer no puede escribirlos (su alcance es el producto) ni el orquestador puede ejecutar U5 respetando la dependencia declarada. El remedio es **separar por superficie** y conservar los responsables:

| Superficie | Dueño | Unidad | Gate |
|---|---|---|---|
| Plantilla del Memory Bank y referencias del skill (upkeep de stage-5, reconciliación de la re-entry) | implementer (texto del producto) | **U4** | texto verde + regresiones + `make validate` — **sin** la tabla viva ni el ADR-034 |
| Documentos del proyecto (`docs/systemPatterns.md`, `docs/adr/ADR-034-…md`) | orquestador (ADR-003) | **U5** | materialización + **aprobación** del ADR-034 registrada |
| Verificación de la tabla viva y del ADR-034 materializado | verificador (orquestador), sobre la producción de U5 | **U7** (nueva) | bloque de texto verde **después** de U5 + control negativo del comprobador |

Cada unidad pasa su gate **sin documentos de unidades pendientes**: U4 no mira lo que U5 producirá; U5 no exige su propio bloque de verificación; U7 sí lo exige, y U5 ya está cerrada cuando U7 corre.

### 1.2 Qué NO es una invariante: el inventario de la siembra (B-3)

El inventario inicial de la tabla es una **fotografía**, no una propiedad del proyecto: aprobar un ADR nuevo **añade** una fila y reemplazar una decisión **cambia** el estado de una fila. Fijarlo en el validador permanente obligaría a **modificar los tests** después de cada cambio legítimo del inventario — justo el procedimiento normal que esta feature introduce (dictamen B-3). Por eso la verificación se parte en **dos capas**:

| Capa | Qué lleva | Dónde vive | ¿Admite cambios de inventario? |
|---|---|---|---|
| **Invariantes duraderas** | cada fila apunta a un archivo **existente** (dirección **fila → archivo**); toda fila `obsoleto` nombra un reemplazo **existente**; todo `roles` ∈ vocabulario cerrado (los cinco roles delegados + `orchestrator`); la fila de **ADR-034** existe; la nota declara que **el estado lo declara quien mantiene la tabla**; el ADR-034 materializado no está `Proposed`, apunta a la fuente única y no re-enuncia el principio | `tests/validate-consistency.sh` — bloque de **U7** | **Sí**: aprobar un ADR o reemplazar una decisión **no** obliga a tocar el validador |
| **Evidencia puntual de la siembra** | el inventario sembrado: **25** filas vigentes, **1** obsoleta, **8** `Proposed` excluidos | evidencia de aceptación de **U5** y **U7** | n/a: se **reemplaza**, no se **comprueba** |

**Regla.** El validador permanente **no lleva conteos**: ni el número de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas. El **cierre** del comprobador se demuestra en un **caso descartable**: **agregar un ADR aprobado** y **reemplazar** una decisión **pasan** el comprobador; una fila que apunta a un archivo **inexistente** **falla**.

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | **El encargo: la fila declarada, su forma y el tope.** `request.current_decisions` (opcional, aditivo), la validación de la forma de la fila (conjunto cerrado, `file` existente, `state` de vocabulario cerrado, `summary` de una línea, `roles` de vocabulario cerrado, `superseded_by` condicional), la regla «la fila nombra al rol del paquete», la regla «sólo lo vigente viaja», el **tope de 32** fail-closed, la bandera `--current-decision` y la propiedad del esquema | — | PD-1, PD-2, PD-3, PD-4, PD-6 | RED + focales GREEN + regresiones de contrato/packets (A-1) + `make validate` |
| **U2** | **La sección aditiva del render:** `## Current decisions` se emite **sólo** con filas, después de `## Contract`, con una entrada por fila en el orden declarado; sin filas el render es **byte-idéntico** (intra-revisión). La invocación de `prepare` con la bandera, declarada en la plantilla de handoff | U1 | PD-5, PD-6, PD-13 | RED + focales GREEN + regresiones de render (A-1) + `make validate` |
| **U3** | **El principio: una casa y las dos obligaciones.** `references/design-principles.md` (nuevo) con el principio y su límite; la fila en la tabla de referencias de `SKILL.md`; la **obligación del architect** y el **criterio del reviewer** (con el límite «la falta de abstracción no es defecto») en la fuente de cada rol y en su bloque estático; el **deber del reviewer sobre la tabla** con su procedimiento en `references/stage-4-review.md`; el test de texto | U2 | PD-8, PD-10, PD-13 | RED de texto + regresiones de generación/paquetes (A-1) + `make staging` determinista + `make validate` |
| **U4** | **La tabla y su upkeep, sólo en plantilla y procedimiento:** la sección en la plantilla del Memory Bank; el **upkeep del orquestador** en `references/stage-5-merge.md` (sin tocar el exit gate); la **regla general del CAS por digest base** y la reconciliación por re-despacho en `references/re-entry.md`; el test de texto de esas superficies | U3 | PD-7, PD-8, PD-9, PD-13 | RED de texto + regresiones de la skill (A-1) + `make validate` — **sin** la tabla viva ni el ADR-034 |
| **U5** | **La siembra de este repo** (no es unidad de código): `docs/systemPatterns.md` con la sección `## Decisiones vigentes` y sus 26 filas, y `docs/adr/ADR-034-principio-general-antes-especifico.md` con el estado **aprobado**. El **inventario** sembrado (25/1/8) es la **evidencia puntual** de esta unidad, **no** una aserción permanente (§1.2). **Documentos del proyecto: los materializa el orquestador** (ADR-003; `sources/roles/orchestrator.md`:106-112) | U3, U4 | PD-11 | materialización por el orquestador + **aprobación** del ADR-034 registrada (sin el bloque de texto de la siembra: eso es de U7) |
| **U7** | **La verificación de la siembra** (no es unidad de código): el bloque de texto de `tests/validate-consistency.sh` que comprueba la **tabla viva** y el **ADR-034 materializado** con **invariantes duraderas** —**nunca** con el número de filas (§1.2)— y su **control negativo**: el caso descartable que **admite** una aprobación y un reemplazo nuevos y **falla** con una fila que apunta a un archivo inexistente | U5 | PD-11 | bloque de texto verde **después** de la materialización de U5 + control negativo del comprobador |
| **U6** | **El recorrido de aceptación** (no es unidad de código): E1..E7 sobre un proyecto **descartable**, incluida la **cadena del CAS** | U1–U5, U7 | PD-12, PD-9, PD-13 | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1 — El encargo: la fila declarada, su forma y el tope

- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_packet.py`, **cuatro** zonas:
    1. el **conjunto cerrado del request** (`optional = {"plan_task", "agent"}`, `:870`) extendido **de forma aditiva** con `current_decisions` — la clausura **no** se relaja: cualquier otra clave desconocida sigue rechazándose;
    2. la **validación de la forma de la fila** y las reglas de admisión (conjunto cerrado de claves; `file` existe en el proyecto; `state` ∈ {`vigente`,`obsoleto`}; `summary` de una línea; `roles` no vacío y dentro del vocabulario cerrado de seis —los cinco roles delegados más `orchestrator`—; `superseded_by` exigido si `state == "obsoleto"` y prohibido si `state == "vigente"`); la regla «**toda fila declarada nombra el rol del paquete**»; la regla «**una fila `obsoleto` no es admisible en un paquete**»; el **tope de 32** fail-closed;
    3. `prepare` (`:4778`): la bandera **repetible** `--current-decision` (`:6730` y vicinity, junto a `--input`/`--invariant`), el parseo JSON de cada valor y la construcción de `request["current_decisions"]` **en el orden declarado** (junto a `:5016`, donde se declara `plan_task`);
    4. `skills/cdad-cycle/assets/packet-request.schema.json`: la propiedad opcional `current_decisions` (el esquema queda veraz; la brecha preexistente de `agent` **no** se corrige — spec L-6).
- **RED:** `tests/test_006_004_u1_decisions_field.py` (nuevo) —
  - **PD-1**: la forma buena es aceptada; clave desconocida ⇒ rc≠0 nombrando la clave; `state` fuera del vocabulario ⇒ rc≠0 nombrando el valor; `superseded_by` ausente con `obsoleto` ⇒ rc≠0; `superseded_by` presente con `vigente` ⇒ rc≠0; `file` inexistente ⇒ rc≠0 nombrando la ruta; `roles` vacío ⇒ rc≠0; rol fuera del vocabulario ⇒ rc≠0; `summary` con salto de línea ⇒ rc≠0. En cada negativo: **sin publicación** (out-dir vacío, state byte-idéntico — el control de `tests/test_004_003_t4_validation_fields.py`:399-423).
  - **PD-2**: la fila que nombra el rol ⇒ admitida; la que no lo nombra ⇒ rc≠0 **nombrando la fila y el rol**; la que nombra a otro rol delegado ⇒ rc≠0 por la misma regla.
  - **PD-3**: la fila `obsoleto` ⇒ rc≠0 nombrando la fila y su `superseded_by`.
  - **PD-4**: 32 filas ⇒ admitidas; 33 ⇒ rc≠0 nombrando el número y el tope, sin publicar.
  - **PD-6**: el `REQUEST.json` lleva `current_decisions` con las filas **en el orden declarado**; una fila declarada para el rol equivocado **no** llega al paquete del rol correcto.
  - **V-1**: el **producto instalado** renderiza el paquete con las filas, byte a byte igual que el del repo (el patrón de `tests/test_004_003_t2_plan_review.py`:290).
  - **V-3**: `receive` revalida el request con el conjunto ampliado: el RED **recibe** un paquete con filas (hoy sería rechazado) y otro con una fila malformada (hoy también) ⇒ el RED lo demuestra, no lo supone.
  - Fixture: proyecto descartable con el patrón de `PrepareProject` (`tests/test_004_003_t2_plan_review.py`), con **fixtures propios** (no el compartido `DRAFT_PLAN_RELPATH`).
- **Regresiones:** `tests/test_packet_prepare.py`, `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_004_003_t1_draft_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_004_003_t2_plan_review.py`, `tests/test_004_003_t4_validation_fields.py`, `tests/test_005_012_t1_register_transition_base.py`, `tests/test_static_block_ceiling.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED declarado y fallando por la razón correcta; GREEN focal; las regresiones listadas verdes **sin cambio de oráculo**; `make validate`.

### U2 — La sección aditiva del render

- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_packet.py`: el **render** (`:1050-1121`) emite `## Current decisions` **entre `## Contract` y el bloque de plan-task** (`:1108-1113`) **sólo** si `current_decisions` está presente y no vacío; con el campo ausente o la lista vacía, **no hay ninguna diferencia de bytes**. La sección lleva, por fila y en el orden declarado, `- Decision: <file>` y las líneas `state`, `summary`, `roles`, `reference`.
  - `skills/cdad-cycle/references/handoff-prompts.md`: la invocación de `prepare` **con la bandera** `--current-decision` (en la sección «Prepared packet contract» y en la plantilla del reviewer), **sin re-enunciar** la regla de la fila (que vive en el paquete y en la spec).
- **RED:** `tests/test_006_004_u2_decisions_section.py` (nuevo) —
  - **PD-5**: con filas ⇒ la sección existe, va después de `## Contract`, trae una entrada por fila con los cinco campos y respeta el orden; **sin** el campo (y con la lista vacía) ⇒ el render es **byte-idéntico** al del producto sin la feature **en la misma revisión**. El RED **no** afirma nada *entre* revisiones: el `PACKET.md` entero **no** se congela (las fuentes de instrucción y sus digests cambian legítimamente) — la prueba *entre* revisiones es el caso de U6 (V-5).
  - **PD-6**: el paquete del rol lleva las filas dentro; el de un rol sin filas aplicables **no** lleva la sección (byte-idéntico).
  - **PD-13** (parte de render): el oráculo vigente de la presencia de secciones (`tests/test_005_003_t6_packet_contract.py`:747; `tests/test_004_003_t1_reviewfix.py`:167-169) sigue verde **sin cambio**: la comprobación es **por presencia**, no por conjunto exhaustivo ⇒ una sección nueva no los rompe.
- **Regresiones:** `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_004_003_t2_plan_review.py`, `tests/test_005_003_t6_packet_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_packet_prepare.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED + focales GREEN; regresiones verdes; `make validate`.

### U3 — El principio: una casa y las dos obligaciones

- **Archivos:**
  - `skills/cdad-cycle/references/design-principles.md` (**nuevo**): la sección «General before specific» con **el texto del principio** y **su límite** («the principle improves design judgement; it does not increase the justifications that agents must produce»). Es la **única casa** del texto normativo.
  - `skills/cdad-cycle/SKILL.md`: una **fila** en §«How to read the references» (la tabla que el validador ya mira) que dice cuándo cargar el archivo.
  - `sources/roles/architect.md`: **una línea** con la obligación del architect («en las decisiones relevantes, considera las alternativas generales y específicas y explica el criterio elegido») + el **puntero** al archivo canónico + la prohibition de re-enunciar.
  - `sources/roles/reviewer.md`: **una línea** con el criterio del reviewer (duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades, acoplamiento) y el **límite** («the absence of an abstraction is not, by itself, a defect») + el puntero; y el **deber sobre la tabla** (comparar con `docs/adr/`; el cambio respeta las decisiones vigentes de su rol) con el puntero a su procedimiento.
  - `skills/cdad-cycle/packets/roles/architect.md` y `packets/roles/reviewer.md`: la **obligación mínima** + el puntero (obligatorio: en la ruta de paquete el rol **no** carga el skill ⇒ el puntero solo no es resoluble — spec §2.6, D-2).
  - `skills/cdad-cycle/references/stage-4-review.md`: la **sección** con el procedimiento del deber del reviewer sobre la tabla (dueño canónico, como la calibración).
  - `agents/cdad-architect.md`, `agents/cdad-architect-odoo.md`, `agents/claude-code/cdad-architect*.md`, `agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer*.md`: **salidas declaradas** de `scripts/cdad-generate.py` (`Makefile`:15-18) — **nunca** se editan a mano.
  - `tests/validate-consistency.sh`: el **bloque de texto** que fija la fuente única, la obligación del architect, el criterio del reviewer y el límite.
- **RED:** `tests/test_006_004_u3_principle_single_source.py` (nuevo) + el bloque bash —
  - **PD-10**: el archivo canónico existe y lleva el principio **y** su límite; el **texto normativo aparece en un único archivo** del árbol instalable (`grep -rl` sobre `skills/`, `sources/`, `agents/` devuelve **exactamente** ese archivo); la fuente del architect y la del reviewer **nombran** la obligación y **apuntan** al archivo; **control negativo**: ninguna de las dos fuentes (ni sus bloques estáticos, ni los agentes generados) **copia** el texto del principio; el criterio del reviewer nombra las cuatro consecuencias y el límite; `SKILL.md` tiene la fila en la tabla de referencias.
  - **PD-8** (parte del reviewer): `references/stage-4-review.md` nombra las dos comprobaciones (alineación con `docs/adr/`; respeto de las decisiones vigentes del rol).
  - **PD-13** (parte de agentes): los agentes generados contienen el texto tras `make agents`; `make staging` es **determinista** (dos corridas, mismos bytes) — control de V-2; el **bloque estático** de los 14 pares rol/subfase queda **por debajo** del techo de 12000 bytes (V-4: la medición se repite y se registra).
- **Regresiones:** `tests/test_cdad_generate.py`, `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_static_block_ceiling.py`, `tests/test_005_007_t1_progressive_detail_rule.py` (el substage del reviewer **no** se toca ⇒ su oráculo no cambia), `tests/test_005_007_t6_templates.py`, `tests/test_006_003_u3_texts_without_profiles.py` (ningún agente declara `model:`), `tests/test_bash_policy_selection.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED de texto verde; `make staging` determinista; regresiones verdes; `make validate`; **medición** del bloque estático registrada.

### U4 — La tabla y su upkeep: plantilla y procedimiento (B-1)

- **Alcance declarado:** esta unidad toca **sólo** las superficies de **plantilla** y **procedimiento**. **No** comprueba la tabla viva ni el ADR-034: eso es de U7, y su gate corre después de U5 (§1.1).
- **Archivos:**
  - `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`: la sección **`## Current decisions`** como **primer H2** después de la introducción, con la **forma de la fila** (archivo, estado, resumen de una línea, roles, referencia) y la nota que declara las exclusiones y que el estado lo declara quien mantiene la tabla. (El bootstrap la instala sin cambios: `references/bootstrap.md`:66-83 copia la plantilla.)
  - `skills/cdad-cycle/references/stage-5-merge.md`: en §5.4 (la decisión sobre el ADR), el orquestador **agrega la fila** al aprobarse un ADR y **marca la anterior como obsoleta** conservándola, con su reemplazo. **El exit gate de stage 5 no cambia** (control negativo: el gate tiene las mismas casillas).
  - `skills/cdad-cycle/references/re-entry.md`: **dos superficies, en el orden de general a específico** (spec §2.5, DEC-13):
    1. **Paso 3 (MATERIALIZE) del protocolo de materialización** (`:60-65`) — la **regla general** del CAS: el digest de `expected_previous_sha256` es **siempre el digest base** (la versión del destino sobre la que se preparó la propuesta), **nunca** el digest actual del destino; ante un conflicto, la vía es **re-despachar** al rol con un **paquete nuevo** sobre la **base nueva**; **no** se fusiona a mano ni se **actualiza el digest esperado** para forzar el paso. La regla se escribe **aquí** y no en el caso particular, porque es general (afecta a toda materialización con CAS).
    2. **Sección `### Scribe`** — el **caso de la tabla**: dos escritores; el **orquestador escribe sus propias filas directamente en `docs/`** con su commit (`docs(memory):`); la propuesta del scribe llega por materialización, con la base que el orquestador registró al preparar su paquete.
  - `tests/validate-consistency.sh`: el bloque de texto de la **plantilla** y de las **dos referencias** (upkeep de stage-5, exit gate sin casillas nuevas, regla general del CAS y su caso de la tabla). **Este bloque NO mira `docs/systemPatterns.md` ni `docs/adr/`**: ese es el bloque de U7.
- **RED:** `tests/test_006_004_u4_decisions_table.py` (nuevo) + el bloque bash —
  - **PD-7**: la plantilla contiene la sección; la sección está en el lugar declarado (primer H2 tras la introducción); **control negativo**: el exit gate de `references/stage-5-merge.md` **no** ganó casillas.
  - **PD-8**: `references/stage-5-merge.md` nombra el upkeep (agregar la fila al aprobar un ADR; marcar la anterior como obsoleta).
  - **PD-9**: `references/re-entry.md`, paso 3 MATERIALIZE, declara el digest **base**, la prohibición de usar el actual, la de actualizar el digest esperado, y el **re-despacho** con paquete nuevo sobre la base nueva; su sección `### Scribe` declara los dos escritores y que el orquestador escribe sus filas directamente en `docs/`.
  - **Control negativo de B-1**: el bloque de texto de esta unidad **no** exige la existencia de `docs/systemPatterns.md` ni de `docs/adr/ADR-034-…` ⇒ `make validate` es verde **sin** la siembra.
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_005_006_t5_acceptance.py` (el bootstrap instala los archivos del Memory Bank), `tests/test_004_002_t1_policy.py` (la clase `documentation`), `tests/test_003_002_t2_reviewfix.py` (los kinds del scribe → sus archivos), `tests/test_006_005_u7_scribe_role_report.py` (el kind `scribe-systemPatterns` → `docs/systemPatterns.md` con CAS), `tests/test_role_packets.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED de texto verde; regresiones verdes; `make validate` — **sin** requerir la tabla viva ni el ADR-034.

### U5 — La siembra de este repo (no es unidad de código)

- **Qué produce:** dos **documentos del proyecto**, materializados por el **orquestador** (ADR-003; `sources/roles/orchestrator.md`:106-112 — puede escribir `docs/**` y hacer `git add docs/**` + `git commit` con prefijo `docs(memory):`), **no** por el implementer (su alcance de escritura es el producto):
  1. `docs/systemPatterns.md`: la sección `## Decisiones vigentes` como **primer H2**, con las **26 filas** de la spec §12 (25 vigentes + 1 obsoleta), la nota de exclusiones (los 8 *Proposed*) y la nota de que el estado lo declara quien mantiene la tabla.
  2. `docs/adr/ADR-034-principio-general-antes-especifico.md`: el ADR **redactado por el architect** (texto en la entrega de esta sesión) **materializado con el estado aprobado**, su texto **apuntando** a la fuente única del principio sin re-enunciarlo.
- **Las tres fases, separadas (O-1):** (1) **borrador** — el architect entrega el ADR con `**Status**: Proposed`; (2) **aprobación** — la autoridad vigente lo aprueba (el orquestador bajo la HITL delegada; el dueño puede vetarla) y la evidencia queda registrada; (3) **materialización** — el orquestador escribe el documento con el estado **aprobado** y siembra la fila `vigente`. La fila `vigente` **exige** la fase (2) cumplida; y el documento materializado **no** vuelve a `Proposed`.
- **Precondición:** la **aprobación** del ADR-034 por la autoridad vigente — una decisión no aprobada no se siembra como `vigente`.
- **Verificación:** la **materialización misma** y la **aprobación registrada**; la comprobación de contenido (presencia de la sección, de la fila de ADR-034, de la nota de exclusiones, existencia del archivo de cada fila y estado aprobado del ADR) **no** se exige aquí: es el gate de **U7**, que corre después.
- **El inventario, aquí, es evidencia (B-3).** Esta unidad **acredita una vez** el inventario sembrado —**25** filas vigentes, **1** obsoleta, **8** `Proposed** excluidos— y lo deja registrado en su evidencia. Ese conteo **no** entra en `tests/validate-consistency.sh` ni en ninguna otra aserción permanente: el validador lleva **sólo invariantes duraderas** (§1.2, DEC-15).
- **Commits:** el orquestador materializa y commitea con el prefijo `docs(memory):` (el canal que ya usa el Memory Bank), **después** de la aprobación del usuario de los borradores (ADR-006, `references/stage-5-merge.md`:53-68).
- **Owner:** orquestador (materialización) con la aprobación de la autoridad vigente.

### U7 — La verificación de la siembra (no es unidad de código) — **nueva en la revisión 2**, **corregida en la revisión 3 (B-3)**

- **Por qué existe (B-1):** las comprobaciones sobre la **tabla viva** y el **ADR-034** necesitan una unidad cuyo gate sea **posterior** a la materialización de U5. En U4 producían una dependencia circular: el gate de U4 exigía documentos de una unidad pendiente (DEC-14).
- **Qué produce:** el **bloque de texto de la siembra** en `tests/validate-consistency.sh` (el bloque de U4 cubre plantilla y procedimiento; este cubre la tabla viva y el ADR-034) y su **control negativo**.
- **Qué comprueba — CAPA 1, invariantes duraderas (lo único que va en el validador permanente):**
  1. `docs/systemPatterns.md` tiene la sección `## Decisiones vigentes` como **primer H2**;
  2. **cada** fila apunta a un archivo que **existe** en `docs/adr/` — la dirección es **fila → archivo**, **no** al revés: el validador **no** exige que todo ADR tenga fila (el estado de un ADR no es derivable: M4, D-3);
  3. **toda** fila `obsoleto` nombra su reemplazo, y ese reemplazo **existe**;
  4. **todo** `roles` de **toda** fila pertenece al vocabulario cerrado (los cinco roles delegados más `orchestrator`);
  5. la fila de **ADR-034** existe, `vigente`, con los roles `architect` y `reviewer` y con la referencia al archivo canónico del skill;
  6. la nota declara que **el estado lo declara quien mantiene la tabla** (D-3) — la nota **declara la regla**, no enumera un inventario cerrado;
  7. el ADR-034 **materializado** existe, **no** está `Proposed` (reconoce la aprobación como acto separado, O-1), **apunta** a la fuente única y **no** re-enuncia el texto del principio (INV-1, O-2).
  **Lo que el bloque NO contiene:** ningún conteo (ni el número de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas) ⇒ **aprobar un ADR nuevo o reemplazar una decisión no obliga a tocar el validador** (B-3, DEC-15).
- **CAPA 2, evidencia puntual (no va en el validador):** el inventario sembrado —**25** filas vigentes, **1** obsoleta, **8** `Proposed` excluidos— se **acredita una vez**, en la evidencia de aceptación de U5 y de U7 (§1.2).
- **RED (y por qué no puede ser otro):** el RED de esta unidad **no** puede ser «la tabla no existe» — eso reintroduciría exactamente el defecto B-1 (una comprobación que sólo puede pasar si otra unidad pendiente ya entregó su producto). Su RED es el **control negativo del comprobador**, con **tres casos sobre copias descartables**: (i) una tabla con una fila que apunta a un ADR inexistente ⇒ el bloque **detecta y reporta** la desalineación (el mismo hecho que E4 exige del reviewer); (ii) una tabla a la que se **agrega un ADR aprobado** (una fila `vigente` más) ⇒ el bloque **pasa**; (iii) una tabla en la que se **reemplaza** una decisión (su fila pasa a `obsoleto` con su reemplazo, y ese reemplazo existe) ⇒ el bloque **pasa**. Además, el RED declara que el bloque existe, cubre las siete comprobaciones enumeradas y **no** contiene ningún conteo del inventario.
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_004_002_t1_policy.py`, `tests/test_006_005_u7_scribe_role_report.py`.
- **Owner:** RED: test-writer (el bloque y su control negativo); GREEN: verificador — la producción que se verifica es la materialización de U5 (cerrada antes de que U7 corra).
- **Gate:** el bloque de texto de la siembra **pasa** con la tabla viva y el ADR-034 ya materializados por U5 y con el ADR-034 aprobado; el control negativo **detecta** la tabla desalignada y **acepta** la aprobación nueva y el reemplazo (los tres casos del RED); `make validate` verde. **Ninguna unidad pendiente** es condición de este gate.

### U6 — El recorrido de aceptación (no es unidad de código)

- **Escenario (PD-12, contra E1..E7 de §3.1 de la spec):** en un proyecto **descartable** (nunca el HOME, nunca el proyecto activo):
  - **(E1)** un ADR aprobado produce su fila en la tabla del proyecto; el siguiente paquete del rol nombrado **la lleva** dentro (`## Current decisions`), y el `REQUEST.json` la declara; un rol **no** nombrado no la lleva;
  - **(E2)** un ADR reemplazado deja la fila vieja **obsoleta** (con su reemplazo) en la tabla y **fuera** del paquete; al intentar declararla en un paquete, el CLI **rechaza** nombrando su sucesor;
  - **(E3)** el paquete de un rol sin filas aplicables es **byte-idéntico** al de hoy; el de un rol al que se le declara una fila ajena es **rechazado** nombrando la fila y el rol;
  - **(E4)** una fila que apunta a un ADR inexistente produce un **hallazgo** del reviewer con `file:line`, veredicto y condición de cierre (no una puerta);
  - **(E5)** un proyecto sin ADR: `prepare` rc=0, sin sección, render byte-idéntico;
  - **(E6)** la casa del principio **existe en el árbol instalado** y el paquete del architect y del reviewer la nombran;
  - **(E7 — la cadena del CAS, DEC-13)** el recorrido completo, con los **digests** de cada paso:
    1. **D0** — el destino `docs/systemPatterns.md` en su estado base; el orquestador lo **registra** al preparar el paquete del scribe (ese es el digest base que se declarará);
    2. **propuesta** — el scribe entrega su `systemPatterns.md` redactado **sobre D0**;
    3. **D1** — el orquestador **escribe su fila directamente en `docs/`** y **commitea** ⇒ el destino pasa a D1;
    4. **rechazo** — la materialización de la propuesta **con la base D0** falla con el conflicto nombrado («current digest does not match expected_previous_sha256 (CAS): refusing to overwrite»);
    5. **re-despacho** — el orquestador **re-despacha al scribe con un paquete nuevo**, cuya base es **D1** (la nueva);
    6. **propuesta nueva** — el scribe entrega su documento redactado **sobre D1**;
    7. **materialización exitosa** — se materializa con el digest base **D1**;
    8. **documento final** — conserva **la fila nueva** (que venía en D1) **y los cambios del scribe**; y la evidencia **identifica los bytes aplicados** (el diff del documento final contra D1).
    **Lo que NO se permite en este recorrido:** fusionar a mano, o retocar el digest esperado para que el CAS pase.
  - **además (V-5)**: la corrida de dos fases (publicar con las fuentes anteriores → cambiar una fuente → recibir) produce el **rechazo** que nombra la diferencia con el render canónico, y la política declarada dice las dos salidas.
- **Evidencia:** los paquetes y sus `REQUEST.json`, los rc, la comparación byte a byte del caso E3, el texto del hallazgo del caso E4, la salida real de la corrida de dos fases, y **la cadena del CAS completa con los digests base y actual de cada paso, el texto del rechazo y el diff que identifica los bytes aplicados**. Se entrega como **documento de evidencia** en la carpeta de la spec (no en `tests/`). Sin generalizar (spec §7).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (CLI no disponible, proyecto no inicializable, estado incoherente), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el owner/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo.

**Resultado de la evaluación: esta feature NO reemplaza ningún oráculo vigente.** Es la consecuencia de DEC-1 (el campo es **opcional** y el render es aditivo), DEC-2 (la forma de la fila es **nueva**: no había ninguna) y de INV-2 (sin el campo nuevo, el render no cambia).

| Superficie acoplada | Test | Evaluación |
|---|---|---|
| **El conjunto cerrado del request** | `tests/test_packet_prepare.py`, `tests/test_003_002_t1_receive.py` | **NO APLICA — el oráculo no cambia.** El conjunto se **extiende** con una propiedad declarada (`plan_task` y `agent` ya lo hicieron así: `cdad_packet.py`:870); la clausura no se relaja ⇒ los tests que comprueban que una clave desconocida se rechaza **siguen verdes sin cambio**. El RED de U1 **vuelve a comprobar** el caso (control negativo explícito): una clave cualquiera distinta de `current_decisions` sigue rechazándose. |
| **La forma de las secciones del paquete** | `tests/test_005_003_t6_packet_contract.py`:747; `tests/test_004_003_t1_reviewfix.py`:167-169 | **NO APLICA — la comprobación es por presencia, no por conjunto exhaustivo** ⇒ una sección nueva no los rompe. El RED de U2 lo **vuelve a comprobar** como control negativo. |
| **La composición del paquete y el bloque estático** | `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_static_block_ceiling.py` | **NO APLICA — el oráculo no cambia.** El bloque estático **crece** (dos líneas de deber en `packets/roles/architect.md` y `packets/roles/reviewer.md`, ~150-300 bytes cada uno) ⇒ el caso más cargado pasa de 3031 a ≈**3400** bytes, muy por debajo del techo de **12000** (V-4). El RED de U3 **mide** el bloque y lo registra; si superara el techo, el RED falla (y la respuesta **no** es subir el techo). |
| **Los digests de las fuentes de instrucción** | `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` se compone con la subfase pineada byte a byte) | **NO APLICA — ningún test fija un digest literal de una fuente de instrucción.** Medido: las 13 apariciones de 64 hexadecimales en `tests/*.py` son digests de **specs y artefactos**, no de `packets/`. El paquete se recomputa en cada corrida ⇒ sigue verde. |
| **Los agentes generados** | `tests/test_cdad_generate.py`, `tests/validate-consistency.sh`:138-142 | **NO APLICA — el oráculo no cambia; los agentes son salidas declaradas.** Las fuentes de rol cambian ⇒ `make agents` **regenera**; el validador comprueba que los agentes **contienen** lo que la fuente declara, no una versión anterior. El RED de U3 **vuelve a comprobar** la propagación y la **determinismo** de `make staging` (dos corridas, mismos bytes). |
| **La materialización del `systemPatterns.md` del scribe** | `tests/test_006_005_u7_scribe_role_report.py`:151, :181; `tests/test_003_002_t2_reviewfix.py`:723-779 | **NO APLICA — no se toca `cdad_result.py` ni `assets/artifact-policy.json`.** El kind `scribe-systemPatterns` → `docs/systemPatterns.md` con CAS ya existe; esta feature **no** añade ninguna comprobación nueva en `materialize` (la regla del digest base es de **procedimiento**, spec L-7). El RED de U4 **no** modifica esos archivos: los **ejecuta**. |
| **El exit gate de stage 5** | derivación textual sobre `skills/cdad-cycle/references/stage-5-merge.md`:163-178 | **NO APLICA — el gate no cambia (Q6).** El RED de U4 lo comprueba como **control negativo**: el gate tiene las mismas casillas que antes de la feature. |
| **La subfase del reviewer** | `tests/test_005_007_t1_progressive_detail_rule.py`:295-307 | **NO APLICA — la subfase no se toca.** El deber del reviewer sobre la tabla vive en el **rol** (fuente + bloque estático) y en su `reference` canónica, no en la subfase ⇒ el oráculo del marcador `detail` sigue verde sin cambio. |
| **El esquema del request** | `assets/packet-request.schema.json` (documento, no validado en runtime: medido, ningún test lo valida) | **APLICA PARCIALMENTE — se **agrega** la propiedad `current_decisions` para que el documento sea veraz.** La brecha preexistente (`agent` ausente) **no** se corrige: es spec L-6, fuera de alcance. |
| **`tests/validate-consistency.sh` (los dos bloques nuevos)** | el propio validador (`make validate`) | **NO APLICA — el validador sólo **crece**: el bloque de U4 (plantilla + procedimiento) y el de U7 (tabla viva + ADR-034) se **agregan**; no se modifica ni se elimina ninguna aserción vigente.** El bloque de U7 nace después de la materialización de U5 ⇒ `make validate` es verde en U4 **sin** la siembra, y verde en U7 **con** ella. Ese bloque lleva **sólo invariantes duraderas** y **ningún conteo del inventario** (B-3, DEC-15): no reemplaza ningún oráculo y, además, **admite** aprobaciones y reemplazos nuevos. |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije que un request con una propiedad nueva debe rechazarse (es decir, que exija el conjunto cerrado *sin* `current_decisions`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva. Los REDs de U2, U3 y U4 declaran lo mismo respecto de la forma de las secciones, del bloque estático y de los agentes generados; el RED de U7 declara lo mismo respecto del validador, y sus casos son **controles negativos añadidos** (fila desalineada, ADR aprobado nuevo, decisión reemplazada), no oráculos reemplazados — y declara además que el bloque que añade **no fija ningún conteo del inventario** (B-3, DEC-15).

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED**: esta spec y este plan se revisan con la superficie vigente de 006-006 (`draft-plan` + `plan-review` sobre un borrador **no aprobado**), en sesión separada del autor; sus bloqueantes van al architect o se descartan con razón escrita por la autoridad que aprueba; y recién entonces viene el RED (DEC-12).
- **El ADR-034** lo aprueba la autoridad vigente (el orquestador bajo la HITL delegada; el dueño puede vetarla). **U5 no se ejecuta antes de esa aprobación** (una fila `vigente` exige una decisión aprobada). La aprobación es un acto **posterior y separado** de la redacción del borrador (INV-14), y su evidencia se registra.
- **El orden de las unidades es parte del cierre**: **U4 pasa su gate sin la siembra** (verifica sólo plantilla y procedimiento); **U5** (la siembra) depende de **U3 y U4** y su gate es la **materialización + la aprobación registrada**; **U7** (la verificación de la siembra) corre **después** de U5 ⇒ el orden ejecutable es `U1 → U2 → U3 → U4 → U5 → U7 → U6`, sin saltarse dependencias ni ampliar permisos (§1.1).
- **La política de compatibilidad (L-1) queda declarada antes del recorrido**: el caso de dos fases (V-5) se ejecuta en U6 y su salida real se pega en la evidencia.
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature, salvo el deber añadido).
- El recorrido real de U6 queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan pasan por la revisión independiente, la aprobación es de la autoridad vigente, y el cierre materializa la tabla sembrada con el prefijo `docs(memory):`.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y fallando por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3, U4 y U7; make staging determinista (dos corridas, mismos bytes) en U3. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). ORDEN Y GATES: cada unidad pasa su gate sin depender de documentos de una unidad pendiente; U4 verifica solo plantilla y procedimiento, U5 materializa los documentos del proyecto y U7 verifica la siembra YA materializada. A-1: esta feature NO reemplaza ningun oraculo vigente (ver plan 4): el conjunto cerrado del request se EXTIENDE con una propiedad declarada (current_decisions) sin relajar la clausura; la forma de las secciones del paquete se comprueba por presencia, no por conjunto exhaustivo; ningun test fija un digest literal de una fuente de instruccion; el exit gate de stage 5 no cambia; la subfase del reviewer no se toca; los agentes son salidas declaradas y make agents los regenera. Los REDs anaden casos y vuelven a comprobar los controles negativos, no cambian oraculos. Aditividad: sin el campo nuevo el render es byte-identico DENTRO de una misma revision del producto; entre revisiones no se promete compatibilidad y la politica (terminarlo bajo la revision con la que se publico, o preparar uno nuevo) queda declarada, con su caso de dos fases en U6. Fila: conjunto cerrado de seis claves (file, state, summary, roles, reference, superseded_by condicional); file debe existir en el proyecto; state en {vigente, obsoleto}; roles de vocabulario cerrado (los cinco roles delegados mas orchestrator); summary de una linea; superseded_by exigido si state es obsoleto y prohibido si es vigente. Admision: toda fila declarada debe nombrar al rol del paquete; una fila obsoleto no es admisible en un paquete; el tope es 32 filas por paquete y falla cerrado nombrando el numero y el tope. La fila viaja en el request (opcional, aditivo) y el render emite la seccion Current decisions solo con filas. Principio: fuente unica en references/design-principles.md (el texto normativo aparece en un solo archivo del arbol instalable); las obligaciones del architect y del reviewer viven en la fuente de cada rol y en su bloque estatico, y apuntan al dueno canonico sin copiar el texto; el limite (la falta de una abstraccion no es defecto) queda escrito y verificado por test de texto. Upkeep: el orquestador agrega la fila al aprobarse un ADR y marca la anterior como obsoleta; el exit gate de stage 5 NO cambia. CAS: el digest declarado en la autorizacion es siempre el digest BASE sobre el que se preparo la propuesta, nunca el digest actual del destino; ante un conflicto, la via es re-despachar al rol con un paquete nuevo sobre la base nueva; no se fusiona a mano ni se actualiza el digest esperado para forzar el paso; el orquestador escribe sus propias filas directamente en docs/ con su commit. Siembra: docs/systemPatterns.md gana la seccion Decisiones vigentes (primer H2) con la nota de que el estado lo declara quien mantiene la tabla y la nota de exclusiones. El INVENTARIO sembrado (25 filas vigentes, 1 obsoleta, 8 ADR Proposed excluidos) es EVIDENCIA PUNCTUAL de la aceptacion de U5 y U7, NO una asercion permanente. El validador permanente (tests/validate-consistency.sh) lleva SOLO invariantes duraderas que admiten aprobaciones y reemplazos nuevos: cada fila apunta a un archivo que EXISTE (direccion fila -> archivo, no al reves); toda fila obsoleto nombra un reemplazo que EXISTE; todo roles pertenece al vocabulario cerrado (los cinco roles delegados mas orchestrator); la fila de ADR-034 existe; y la nota declara que el estado lo declara quien mantiene la tabla. CIERRE DEL COMPROBADOR, en un caso descartable: agregar un ADR aprobado y reemplazar una decision PASAN el comprobador, y una fila con archivo inexistente FALLA.",
  "tasks": [
    {
      "id": "U1",
      "objective": "El encargo: la fila declarada, su forma y el tope. request.current_decisions como propiedad opcional aditiva (la clausura del conjunto de campos NO se relaja); validacion de la forma de la fila con conjunto cerrado de seis claves (file, state, summary, roles, reference y superseded_by condicional: exigido si state es obsoleto, prohibido si es vigente); file debe existir en el proyecto; state de vocabulario cerrado {vigente, obsoleto}; summary de una linea; roles no vacio y dentro del vocabulario cerrado (los cinco roles delegados mas orchestrator); la regla de que toda fila declarada nombra el rol del paquete (fail-closed, nombrando la fila y el rol); la regla de que una fila obsoleto no es admisible en un paquete; el tope de 32 filas por paquete (fail-closed, nombrando el numero y el tope); la bandera repetible --current-decision que parsea JSON y conserva el orden declarado; y la propiedad opcional del esquema del request.",
      "produce": [],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "skills/cdad-cycle/assets/packet-request.schema.json"
      ],
      "focal_tests": [
        "tests/test_006_004_u1_decisions_field.py"
      ],
      "observable_checks": [
        "la forma buena de la fila es aceptada y el REQUEST.json la lleva con las filas en el orden declarado (PD-1, PD-6)",
        "clave desconocida, state fuera del vocabulario, superseded_by ausente con obsoleto, superseded_by presente con vigente, file inexistente, roles vacio, rol fuera del vocabulario y summary con salto de linea se rechazan con rc distinto de cero, sin publicar y con el state byte-identico (PD-1)",
        "una fila que no nombra al rol del paquete se rechaza nombrando la fila y el rol; una fila que nombra a otro rol delegado se rechaza por la misma regla (PD-2)",
        "una fila obsoleto no es admisible en un paquete y el rechazo nombra la fila y su superseded_by (PD-3)",
        "32 filas se admiten y 33 se rechazan nombrando el numero y el tope, sin publicar (PD-4)",
        "el producto instalado renderiza el paquete con las filas byte a byte igual que el del repo (V-1)",
        "receive revalida el request con el conjunto ampliado: recibe un paquete con filas y rechaza uno con una fila malformada (V-3)"
      ],
      "regressions": [
        "tests/test_packet_prepare.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packets.py",
        "tests/test_003_002_t1_receive.py",
        "tests/test_003_002_t2_materialize.py",
        "tests/test_004_003_t1_draft_contract.py",
        "tests/test_004_003_t1_reviewfix.py",
        "tests/test_004_003_t2_plan_review.py",
        "tests/test_004_003_t4_validation_fields.py",
        "tests/test_005_012_t1_register_transition_base.py",
        "tests/test_static_block_ceiling.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "detail": "next"
    },
    {
      "id": "U2",
      "objective": "La seccion aditiva del render: el render emite la seccion Current decisions solo cuando hay filas, inmediatamente despues de la seccion Contract y antes del bloque de plan-task, con una entrada por fila y en el orden declarado (file, state, summary, roles, reference); sin el campo (o con la lista vacia) el render es byte-identico al del producto sin la feature dentro de la misma revision; y la invocacion de prepare con la bandera --current-decision queda declarada en la plantilla de handoff, sin re-enunciar la regla de la fila.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U1"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "skills/cdad-cycle/references/handoff-prompts.md"
      ],
      "focal_tests": [
        "tests/test_006_004_u2_decisions_section.py"
      ],
      "observable_checks": [
        "con filas, la seccion existe, va despues de Contract, trae una entrada por fila con los cinco campos y respeta el orden declarado (PD-5)",
        "sin el campo y con la lista vacia, el render es byte-identico dentro de la misma revision; el RED no afirma nada entre revisiones (PD-5, PD-13)",
        "el paquete de un rol sin filas aplicables no lleva la seccion (PD-6)",
        "los oraculos vigentes de presencia de secciones siguen verdes sin cambio de oraculo (PD-13)"
      ],
      "regressions": [
        "tests/test_role_packet_render.py",
        "tests/test_role_packets.py",
        "tests/test_004_003_t2_plan_review.py",
        "tests/test_005_003_t6_packet_contract.py",
        "tests/test_004_003_t1_reviewfix.py",
        "tests/test_packet_prepare.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "detail": "next"
    },
    {
      "id": "U3",
      "objective": "El principio: una casa y las dos obligaciones. El archivo nuevo skills/cdad-cycle/references/design-principles.md lleva el texto del principio y su limite (el principio mejora el juicio de diseno; no aumenta las justificaciones que los agentes deben producir) y es su unica casa; SKILL.md gana la fila que dice cuando cargarlo; la fuente del architect y la del reviewer declaran su obligacion (una linea) y apuntan al dueno canonico sin copiar el texto; el bloque estatico de cada rol lleva la obligacion minima y el puntero, porque en la ruta de paquete el rol no carga el skill; el criterio del reviewer nombra las cuatro consecuencias reales y el limite (la falta de una abstraccion no es defecto); references/stage-4-review.md, dueno canonico, recibe el procedimiento del deber del reviewer sobre la tabla (alinear con docs/adr/ y el respeto de las decisiones vigentes de su rol); los agentes generados se regeneran con make agents; y el test de texto fija la fuente unica, las dos obligaciones y el limite.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U2"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/references/design-principles.md",
        "skills/cdad-cycle/SKILL.md",
        "skills/cdad-cycle/references/stage-4-review.md",
        "sources/roles/architect.md",
        "sources/roles/reviewer.md",
        "skills/cdad-cycle/packets/roles/architect.md",
        "skills/cdad-cycle/packets/roles/reviewer.md",
        "agents/cdad-architect.md",
        "agents/cdad-architect-odoo.md",
        "agents/cdad-reviewer.md",
        "agents/cdad-reviewer-odoo.md",
        "agents/claude-code/cdad-architect.md",
        "agents/claude-code/cdad-architect-odoo.md",
        "agents/claude-code/cdad-reviewer.md",
        "agents/claude-code/cdad-reviewer-odoo.md"
      ],
      "focal_tests": [
        "tests/test_006_004_u3_principle_single_source.py"
      ],
      "observable_checks": [
        "el archivo canonico existe y lleva el principio y su limite (PD-10)",
        "el texto normativo del principio aparece en un unico archivo del arbol instalable: grep -rl sobre skills/, sources/ y agents/ devuelve exactamente ese archivo (PD-10, INV-1)",
        "la fuente del architect y la del reviewer nombran la obligacion y apuntan al dueno canonico; control negativo: ninguna copia el texto del principio (PD-10, INV-12)",
        "el criterio del reviewer nombra las cuatro consecuencias reales y el limite de que la falta de una abstraccion no es defecto (PD-10)",
        "references/stage-4-review.md nombra las dos comprobaciones del deber del reviewer sobre la tabla (PD-8)",
        "SKILL.md tiene la fila del archivo nuevo en la tabla de referencias (PD-10)",
        "los agentes generados contienen el texto tras make agents y make staging es determinista: dos corridas producen los mismos bytes (PD-13, V-2)",
        "el bloque estatico de los 14 pares rol/subfase se mide y queda por debajo del techo declarado de 12000 bytes (PD-13, V-4)"
      ],
      "regressions": [
        "tests/test_cdad_generate.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packets.py",
        "tests/test_static_block_ceiling.py",
        "tests/test_005_007_t1_progressive_detail_rule.py",
        "tests/test_005_007_t6_templates.py",
        "tests/test_006_003_u3_texts_without_profiles.py",
        "tests/test_bash_policy_selection.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "detail": "next"
    },
    {
      "id": "U4",
      "objective": "La tabla y su upkeep, SOLO en las superficies de plantilla y procedimiento. La plantilla del Memory Bank gana la seccion Current decisions como primer H2 tras la introduccion, con la forma de la fila (archivo, estado, resumen de una linea, roles, referencia) y la nota que declara las exclusiones y que el estado lo declara quien mantiene la tabla; el bootstrap la instala sin cambios. references/stage-5-merge.md declara, en la decision sobre el ADR, que el orquestador agrega la fila al aprobarse un ADR y marca la anterior como obsoleta conservandola con su reemplazo, SIN tocar el exit gate de stage 5. references/re-entry.md declara la REGLA GENERAL del CAS (paso 3 MATERIALIZE: el digest de expected_previous_sha256 es siempre el digest BASE sobre el que se preparo la propuesta, nunca el digest actual del destino; ante un conflicto, la via es re-despachar al rol con un paquete nuevo sobre la base nueva; no se fusiona a mano ni se actualiza el digest esperado para forzar el paso) y, en la re-entry del scribe, el caso de la tabla (dos escritores; el orquestador escribe sus propias filas directamente en docs/ con su commit; el del scribe llega por materializacion). El bloque de texto de tests/validate-consistency.sh fija SOLO la plantilla y las dos referencias. Esta unidad NO comprueba la tabla viva ni el ADR-034: esos los verifica U7, despues de la materializacion de U5.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U3"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md",
        "skills/cdad-cycle/references/stage-5-merge.md",
        "skills/cdad-cycle/references/re-entry.md",
        "tests/validate-consistency.sh"
      ],
      "focal_tests": [
        "tests/test_006_004_u4_decisions_table.py"
      ],
      "observable_checks": [
        "la plantilla contiene la seccion y esta en el lugar declarado (PD-7)",
        "control negativo: el exit gate de stage 5 no ganho casillas (PD-7, PD-8)",
        "stage-5-merge.md nombra el upkeep (agregar la fila al aprobar un ADR; marcar la anterior como obsoleta) (PD-8)",
        "re-entry.md, paso 3 MATERIALIZE, declara la regla general del CAS: el digest declarado es el digest BASE sobre el que se preparo la propuesta, nunca el actual; ante conflicto, re-despacho con paquete nuevo sobre la base nueva; sin fusion a mano ni actualizacion del digest esperado (PD-9, DEC-13)",
        "re-entry.md, seccion Scribe, declara el caso de la tabla: dos escritores, el orquestador escribe sus filas directamente en docs/ con su commit, el del scribe llega por materializacion (PD-8, PD-9)",
        "el bloque de texto de la plantilla y de las dos referencias pasa; el bloque NO exige la tabla viva ni el ADR-034 (B-1)"
      ],
      "regressions": [
        "tests/test_005_006_t2_intake.py",
        "tests/test_005_006_t5_acceptance.py",
        "tests/test_004_002_t1_policy.py",
        "tests/test_003_002_t2_reviewfix.py",
        "tests/test_006_005_u7_scribe_role_report.py",
        "tests/test_role_packets.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "RED: test-writer; GREEN: implementer",
      "detail": "next"
    },
    {
      "id": "U5",
      "objective": "La siembra de este repo: el orquestador materializa dos documentos del proyecto (docs/systemPatterns.md con la seccion Decisiones vigentes como primer H2, sus 26 filas -25 vigentes y 1 obsoleta-, la nota de exclusiones de los 8 ADR Proposed y la nota de que el estado lo declara quien mantiene la tabla; y docs/adr/ADR-034-principio-general-antes-especifico.md). El CONTEO del inventario (25 vigentes, 1 obsoleta, 8 Proposed excluidos) es la EVIDENCIA PUNCTUAL de esta unidad: se acredita una vez, aqui, y NO entra en el validador permanente (B-3, DEC-15). Precondicion: la APROBACION del ADR-034 por la autoridad vigente, porque una fila vigente exige una decision aprobada; el borrador entregado por el architect dice Proposed y su aprobacion es un acto POSTERIOR y SEPARADO, cuya evidencia queda en el estado. El ADR-034 materializado lleva el estado aprobado, apunta a la fuente unica del principio y no lo re-enuncia. Materializacion y commit por el orquestador con el prefijo docs(memory): tras la aprobacion del usuario de los borradores. Esta unidad NO se gatea con el bloque de texto de la siembra (eso es de U7): su gate es la materializacion misma mas la aprobacion registrada.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U3",
        "U4"
      ],
      "parallel": [],
      "files": [
        "docs/systemPatterns.md",
        "docs/adr/ADR-034-principio-general-antes-especifico.md"
      ],
      "focal_tests": [
        "tests/validate-consistency.sh"
      ],
      "observable_checks": [
        "EVIDENCIA PUNCTUAL, no asercion permanente: la tabla sembrada tiene la seccion Decisiones vigentes como primer H2, con 25 filas vigentes y 1 obsoleta, y cada fila apunta a un archivo que existe en docs/adr/ (PD-11, DEC-15)",
        "EVIDENCIA PUNCTUAL: la nota de exclusiones declara los 8 ADR Proposed y el motivo (es una fotografia de la siembra: al aprobarse uno pasa a fila, la lista se actualiza y el validador NO se toca); la nota sobre el estado declara que lo declara quien mantiene la tabla (PD-11, D-3, DEC-15)",
        "la fila de ADR-034 existe con state vigente, los roles architect y reviewer, y la referencia al archivo canonico del skill (PD-11)",
        "el ADR-034 materializado existe y lleva el estado APROBADO, con la evidencia de la aprobacion registrada; el borrador Proposed es una fase anterior y distinta (PD-11, O-1)",
        "el commit de la materializacion lleva el prefijo docs(memory): y lo ejecuta el orquestador tras la aprobacion del usuario (ADR-006)",
        "el conteo del inventario NO se comprueba en ninguna asercion permanente: aprobar un ADR nuevo o reemplazar una decision NO obliga a tocar tests/validate-consistency.sh (DEC-15, B-3)"
      ],
      "regressions": [],
      "integration_gate": "materializacion por el orquestador con la aprobacion de la autoridad vigente registrada; el ADR-034 materializado con estado aprobado",
      "owner": "orchestrator (materializacion); la autoridad vigente aprueba el ADR-034 y los borradores",
      "detail": "next"
    },
    {
      "id": "U7",
      "objective": "La verificacion de la siembra, DESPUES de la materializacion de U5, en dos capas (B-3, DEC-15). CAPA 1 - INVARIANTES DURADERAS, en el validador permanente tests/validate-consistency.sh: SOLO propiedades que admiten aprobaciones y reemplazos nuevos, NUNCA el numero de filas. La seccion Decisiones vigentes existe como primer H2 de docs/systemPatterns.md; cada fila apunta a un archivo que EXISTE (direccion fila -> archivo, no al reves); toda fila obsoleto nombra un reemplazo que EXISTE; todo roles de toda fila pertenece al vocabulario cerrado (los cinco roles delegados mas orchestrator); la fila de ADR-034 existe, vigente, con los roles architect y reviewer y con la referencia al archivo canonico del skill; la nota declara que el estado lo declara quien mantiene la tabla; y el ADR-034 materializado existe, NO esta Proposed (la comprobacion reconoce la aprobacion como acto separado y NO exige que siga pendiente), apunta a la fuente unica y no re-enuncia el texto del principio. CAPA 2 - EVIDENCIA PUNCTUAL, en la aceptacion de U5 y U7 y NO en el validador: el inventario sembrado (25 filas vigentes, 1 obsoleta, 8 ADR Proposed excluidos) se acredita una vez, con la evidencia de la unidad. CIERRE DEL COMPROBADOR, en un caso descartable: agregar un ADR aprobado (una fila vigente mas) y reemplazar una decision (marcar su fila obsoleto con su reemplazo) PASAN el comprobador; una fila que apunta a un archivo inexistente FALLA. Es una unidad de VERIFICACION: su gate corre despues de U5 y no exige ningun documento de una unidad pendiente. Su RED no puede ser la ausencia de la tabla (eso reintroduciria el defecto B-1): su RED es el CONTROL NEGATIVO DEL COMPROBADOR (los tres casos del cierre, sobre copias descartables) mas la declaracion de que el bloque existe y lleva SOLO invariantes duraderas.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U5"
      ],
      "parallel": [],
      "files": [
        "tests/validate-consistency.sh"
      ],
      "focal_tests": [
        "tests/validate-consistency.sh"
      ],
      "observable_checks": [
        "el validador permanente comprueba que la tabla viva tiene la seccion Decisiones vigentes como primer H2 (PD-11)",
        "el validador permanente comprueba que cada fila apunta a un archivo que EXISTE, en la direccion fila -> archivo y no al reves (PD-11, DEC-15)",
        "el validador permanente comprueba que toda fila obsoleto nombra un reemplazo que EXISTE (PD-11, DEC-15)",
        "el validador permanente comprueba que todo roles de toda fila pertenece al vocabulario cerrado (PD-11, DEC-15)",
        "el validador permanente comprueba que la fila de ADR-034 existe, vigente, con los roles architect y reviewer y con la referencia al archivo canonico del skill, y que la nota declara que lo declara quien mantiene la tabla (PD-11, D-3)",
        "el ADR-034 materializado existe, no esta Proposed, apunta a la fuente unica y no re-enuncia el texto del principio (PD-11, INV-1, O-1)",
        "el validador permanente NO contiene ningun conteo del inventario: ni el numero de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas (PD-11, DEC-15, B-3)",
        "EVIDENCIA PUNCTUAL: el inventario sembrado (25 vigentes, 1 obsoleta, 8 Proposed excluidos) queda acreditado en la evidencia de U5 y U7, no en el validador (DEC-15)",
        "cierre del comprobador, en un caso descartable: agregar un ADR aprobado y reemplazar una decision PASAN el comprobador, y una fila con archivo inexistente FALLA (PD-11, E4)"
      ],
      "regressions": [
        "tests/test_005_006_t2_intake.py",
        "tests/test_004_002_t1_policy.py",
        "tests/test_006_005_u7_scribe_role_report.py"
      ],
      "integration_gate": "el bloque de texto de la siembra pasa con la tabla viva y el ADR-034 ya materializados por U5 y con el ADR-034 aprobado por la autoridad vigente; el control negativo del comprobador detecta la tabla desalineada; y el caso descartable demuestra que agregar un ADR aprobado y reemplazar una decision siguen PASANDO el comprobador (el validador no fija el inventario)",
      "owner": "RED: test-writer (el bloque y su control negativo); GREEN: verificador - la produccion que se verifica es la materializacion de U5",
      "detail": "next"
    },
    {
      "id": "U6",
      "objective": "Recorrido de aceptacion en un proyecto descartable: un ADR aprobado produce su fila y el siguiente paquete del rol nombrado la lleva; un ADR reemplazado deja la fila vieja obsoleta en la tabla y fuera del paquete, y declararla en un paquete se rechaza nombrando su sucesor; un rol sin filas aplicables recibe un paquete byte-identico al de hoy y la declaracion de una fila ajena se rechaza nombrando la fila y el rol; una fila que apunta a un ADR inexistente produce un hallazgo del reviewer con file:line, veredicto y condicion de cierre, no una puerta; un proyecto sin ADR prepara con rc cero, sin seccion y con render byte-identico; la casa del principio existe en el arbol instalado y la nombran el paquete del architect y del reviewer; la corrida de dos fases (publicar con las fuentes anteriores, cambiar una fuente, recibir) produce el rechazo que nombra la diferencia con el render canonico, con la politica declarada que dice las dos salidas; y la CADENA DEL CAS: D0 (base) -> propuesta del scribe sobre D0 -> D1 (el orquestador escribe su fila directamente en docs/ y commitea) -> la materializacion de la propuesta con la BASE D0 se RECHAZA nombrando el conflicto -> re-despacho al scribe con un PAQUETE NUEVO sobre la base D1 -> la propuesta nueva (base D1) se materializa con exito -> el documento final conserva la fila nueva Y los cambios del scribe, y la evidencia identifica los bytes aplicados.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U1",
        "U2",
        "U3",
        "U4",
        "U5",
        "U7"
      ],
      "parallel": [],
      "files": [],
      "focal_tests": [],
      "observable_checks": [
        "los paquetes y sus REQUEST.json declaran las filas en el orden declarado y los rc son los esperados (PD-12, PD-6)",
        "la comparacion byte a byte del paquete de un rol sin filas aplicables coincide con el render vigente (PD-5, E3)",
        "el texto del hallazgo del caso de tabla desalineada trae file:line, veredicto y condicion de cierre (PD-8, E4)",
        "el proyecto sin ADR prepara con rc cero, sin seccion y con render byte-identico (PD-7, E5)",
        "la casa del principio existe en el arbol instalado y la nombran los paquetes del architect y del reviewer (PD-10, E6)",
        "la salida real de la corrida de dos fases queda adjunta: los dos rc y el texto del diagnostico (V-5, L-1)",
        "la cadena del CAS queda adjunta completa: el rc del rechazo con la BASE D0 y su texto, el rc del re-despacho con exito y el diff que identifica los bytes aplicados (PD-9, DEC-13, V-6)",
        "el documento final conserva la fila nueva y los cambios del scribe: se verifica por presencia de la fila y por comparacion con la base D1 (PD-9, E7)",
        "las versiones y configuraciones observadas quedan declaradas y el resultado no se generaliza (spec 7)"
      ],
      "regressions": [],
      "integration_gate": "recorrido con evidencia declarada; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con motivo y evidencia del intento, sin corrida simulada",
      "owner": "orchestrator con el reviewer; evidencia en la carpeta de la spec",
      "detail": "next"
    }
  ]
}
```

## 7. Revisión 2 — qué cambió respecto de draft-001

| Hallazgo | Cambio en el plan | Dónde |
|---|---|---|
| **B-1** | U4 queda acotada a **plantilla + procedimiento**; su bloque de texto **no** mira la tabla viva ni el ADR-034 y su gate no exige ningún documento ajeno. U5 pasa a gatearse por la **materialización + la aprobación registrada** (no por el bloque de texto). **U7 (nueva)** verifica la tabla viva y el ADR-034, con gate **posterior** a U5. El orden pasa a `U1→U2→U3→U4→U5→U7→U6`, y U6 depende de U7. | §1, §1.1, §2, §3 (U4, U5, U7, U6), §6 |
| **B-2** | U4 escribe la **regla general del CAS** en el paso 3 (MATERIALIZE) de `references/re-entry.md` (digest base, nunca el actual; re-despacho; sin fusión a mano ni retocar el digest) y el **caso de la tabla** en su sección `### Scribe` (el orquestador escribe directo en `docs/`). U6 demuestra la **cadena completa** en 8 pasos, con digests, el rechazo nombrado, el re-despacho y los **bytes aplicados**. | §3 (U4), §3 (U6, E7), §6 |
| **O-1** | U5 declara las **tres fases** (borrador `Proposed` → aprobación → materialización con estado **aprobado**); U7 comprueba el estado **aprobado** y **no** exige que el ADR siga pendiente. | §3 (U5, U7), §6 |
| **O-2** | U7 comprobará, sobre el ADR **materializado**, que apunta a la fuente única y **no** re-enuncia el texto del principio; el ADR-034 entregado se corrige en consecuencia. | §3 (U7), ADR-034 |

## 8. Revisión 3 — qué cambió respecto de draft-002

| Hallazgo | Cambio en el plan | Dónde |
|---|---|---|
| **B-3** | El **validador permanente** (`tests/validate-consistency.sh`) deja de llevar el **inventario** y queda con **invariantes duraderas** que admiten aprobaciones y reemplazos nuevos: cada fila apunta a un archivo existente; toda fila `obsoleto` nombra un reemplazo existente; todo `roles` ∈ vocabulario cerrado; la fila de ADR-034 existe; la nota declara que el estado lo declara quien mantiene la tabla. El **inventario** (25 vigentes · 1 obsoleta · 8 `Proposed` excluidos) queda como **evidencia puntual** de U5 y U7. El **cierre** del comprobador pasa a ser un **caso descartable** de tres casos: **agregar un ADR aprobado** pasa, **reemplazar** una decisión pasa, una fila con archivo inexistente **falla**. | §1.2, §2 (U5, U7), §3 (U5, U7), §4, §6 (U5, U7, `validation_strategy`) |
| **O-3** | La frase del cierre que conservaba la circularidad como obligación vigente se sustituye por el **orden corregido** (`U1 → U2 → U3 → U4 → U5 → U7 → U6`), coherente con §1.1. | §5 |

Lo demás de `draft-002` **se conserva**.

Status: **BORRADOR — SIN APROBAR** (draft-003). La aprobación es un acto separado de la autoridad vigente, y precede al RED de cualquier unidad.
===END plan.md===

===BEGIN adr-034.md===
# ADR-034: El principio de general antes que específico se materializa en un único archivo del skill instalable, y obliga al architect a explicar el criterio y al reviewer a evaluar consecuencias reales

- **Status**: Proposed (redactado por el architect el 2026-10-20; **a la espera de la aprobación** de la autoridad vigente —el orquestador bajo la HITL delegada del epic-006, con veto del dueño—)
- **Date**: 2026-10-20
- **Deciders**: Pablo (dueño: fijó el principio de general antes que específico en la enmienda 005 del plan del epic, 2026-10-18) + orquestador Claude (HITL delegada de epic-006: aprueba el ADR) + architect (redacción; **no aprueba**)
- **Confidence**: Alta
- **Aprobación**: *pendiente* — el owner puede vetarla. **Evidencia disponible para la decisión:** contrato `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005, sha256 `d6da11db…9809`) y §10 (enmienda 003); `docs/specs/006-004-active-decisions-table/discovery.md` §4.1-4.3; `docs/specs/006-004-active-decisions-table/spec.md` §2.6 y DEC-9/DEC-10; `plan.md` §3 U3.
- **Fases (declaradas, tres actos distintos):** (1) este documento es el **borrador** que entrega el architect, con estado `Proposed`; (2) su **aprobación** es un acto **posterior y separado** de la autoridad vigente, cuya evidencia se registra; (3) sólo después lo materializa el orquestador en `docs/adr/`, y **el materializado lleva el estado aprobado**. La fila de la tabla que lo nombra no se declara `vigente` antes de (2). Una comprobación posterior reconoce la aprobación separada: **no** exige que este documento siga `Proposed`.

## Contexto y problema

El principio de general antes que específico **no se reproduce aquí**. Su texto normativo y el de su **límite** viven en **un único archivo del skill instalable**, que es su casa: `skills/cdad-cycle/references/design-principles.md`. La fuente contractual de ambos —la，很容易 lo que el dueño aprobó— es `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005, 2026-10-18), que además enumera sus cuatro obligaciones y el alcance del cambio de contrato de rol. Este ADR **registra la decisión** y **apunta** a esas dos fuentes; quien necesite el texto exacto del principio o de su límite, lo lee allí (o en la casa canónica), y **no** lo encuentra re-enunciado en este documento.

Lo que el principio sí era —y esto sí es materia de este ADR— era **un cambio de contrato de rol**. Nombraba cuatro obligaciones (registro del principio y su límite, fuente única instalable, deber del architect, criterio del reviewer) y fijaba además dos límites de alcance: se aplica a las decisiones **que crean una frontera, duplican un mecanismo o comprometen la evolución** (no exige justificar cada elección), y **la falta de una abstracción no es, por sí sola, un defecto** para el reviewer.

El problema que el principio no resolvía por sí solo era **de distribución**. Un principio registrado en un ADR no gobierna el trabajo siguiente si ningún rol lo recibe: el rol no abre el `docs/adr/` del proyecto, y en la ruta de paquete **no carga el skill** (su contrato es el paquete). Un ADR sin regla instalada es una declaración; una regla sin regla instalada es una declaración sin efecto. De ahí la exigencia de la enmienda 005: **fuente única instalable**, con los roles **referenciándola**, y la regla de que *una decisión que cambia la metodología de CDAD no está terminada hasta que su regla está en el skill o el agente instalable* (enmienda 003, §10.4).

## Opciones consideradas

### Opción A: el principio vive en el ADR y los roles lo reciben por el paquete (ADOPTADA)

- El texto normativo del principio **y** el de su límite viven en **un único archivo del skill instalable** (`skills/cdad-cycle/references/design-principles.md`), que es su casa. Este ADR **registra la decisión** y **apunta** a ese archivo; no lo re-enuncia.
- La **obligación del architect** («en las decisiones relevantes, considera las alternativas generales y específicas y explica el criterio elegido») y el **criterio del reviewer** («evalúa consecuencias reales: duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento; la falta de una abstracción, por sí sola, no es un defecto») se declaran como **deber** en la fuente de cada rol y en su bloque estático de paquete, con el **puntero** al archivo canónico.
- El **deber del reviewer sobre la tabla de decisiones** (alinear la tabla con `docs/adr/`; comprobar que el cambio respeta las decisiones vigentes de su rol) tiene su **procedimiento** en la referencia canónica del reviewer, con el mismo patrón de «dueño canónico único» que ya usa la calibración de la revisión.
- **Pros:** una sola casa del texto normativo, verificable mecánicamente (el texto aparece en un único archivo del árbol instalable); el deber de cada rol llega **completo** por las dos superficies que existen en las dos rutas (cuerpo del agente generado y bloque estático del paquete), incluso en la ruta de paquete donde el skill no se carga; el principio se **distribuye** con el mismo mecanismo que las decisiones vigentes (la tabla «Decisiones vigentes» y su sección en el paquete), de modo que la Feature 006-004 es su vehículo y no un añadido aparte; el límite del principio queda **junto al principio**, en el archivo canónico, y no puede separarse de él.
- **Contras:** el texto normativo y el deber de rol están en **archivos distintos** (el primero en una *reference*, el segundo en las fuentes de rol), lo que exige una regla explícita de no-copia y un test que la vigile; y la lectura íntegra del principio depende de que el rol alcance el skill en la ruta de paquete (limitación ya aceptada en el producto con el puntero vigente a la referencia de calibración).

### Opción B: el principio vive en el propio ADR y basta con que el rol lo reciba en el paquete

- **Pros:** cero archivos nuevos; el ADR es el lugar natural de una decisión.
- **Contras:** el ADR vive en el **proyecto**, no en el **skill instalable** ⇒ (i) el texto normativo **no viaja** a un proyecto que no tenga ese ADR, y CDAD necesita el principio en **todos** los proyectos, no en el que lo decidió; (ii) la ruta de paquete no puede resolver un puntero a un archivo del proyecto que el rol no tiene por qué leer; (iii) el principio quedaría duplicado en cada proyecto que lo adopte, con la divergencia que el propio principio condena. **Descartada.**

### Opción C: el principio en `SKILL.md` (el contrato mínimo siempre cargado)

- **Pros:** llega a todos los runtimes sin trabajo adicional; no depende de que nadie cargue una referencia.
- **Contras:** `SKILL.md` se carga **siempre**, en todos los roles y en todas las etapas ⇒ una regla de diseño para dos roles (architect y reviewer) **cargaría a todos** los que no la necesitan (test-writer, implementer, scribe), que es exactamente el error de «especializar al revés» y el que la enmienda 005 quiere evitar. Además rompe el patrón vigente del repo (un dueño canónico en `references/`, y los consumidores lo referencian sin copiarlo). **Descartada.**

### Opción D: el principio en la referencia de la revisión (`stage-4-review.md`)

- **Pros:** el archivo ya es el dueño canónico de la calibración del reviewer y ya se cita desde la fuente del rol.
- **Contras:** mezclaría **dos dueños** en un archivo (la calibración de la revisión y el principio general de diseño) ⇒ dos reglas que pueden evolucionar por separado, cada una afecta a un conjunto distinto de roles, en el mismo sitio. Además el principio no es sólo del reviewer: el architect lo debe aplicar y el reviewer sólo lo evalúa. **Descartada.**

## Decisión

1. **El principio de general antes que específico y su límite tienen una casa única, instalable:** `skills/cdad-cycle/references/design-principles.md`. Ese archivo es la **única** casa del texto normativo; el árbol `skills/cdad-cycle/` viaja completo al entorno instalado, de modo que la regla está disponible sin que el proyecto tenga que depender de ella. **Este ADR no re-enuncia el texto del principio ni el de su límite** (la regla de una sola casa; el deber de rol es *duty*, no principio). Quien quiera el texto exacto, lo lee en ese archivo; el contrato que lo respalda es `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005).
2. **El deber del architect** se declara en la fuente del architect y en su bloque estático de paquete, con el puntero al archivo canónico: *en las decisiones relevantes, considera las alternativas generales y específicas y explica el criterio elegido*; el principio y su límite **no** se re-enuncian allí.
3. **El deber del reviewer** se declara en la fuente del reviewer y en su bloque estático de paquete, con el puntero al archivo canónico: *evalúa consecuencias reales —duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento— y la falta de una abstracción, por sí sola, no es un defecto*. El **procedimiento** de su comprobación sobre la tabla de decisiones vigentes vive en su referencia canónica (dueño canónico, como la calibración).
4. **El límite del principio es parte del principio:** el archivo canónico lleva, junto al texto, **su límite**, definido en ese mismo archivo. Este ADR **no lo reproduce** (la regla de una sola casa). El principio **no** exige justificar cada elección: se aplica a las decisiones que crean una frontera, duplican un mecanismo o comprometen la evolución.
5. **El principio se distribuye por el mecanismo de las decisiones vigentes:** la feature 006-004 crea la sección «Decisiones vigentes» en la tabla del proyecto, y el paquete de cada rol lleva las filas vigentes que lo nombran. La fila de esta decisión es la **primera** de la tabla sembrada: nombra el archivo del skill como la referencia donde vive la regla.
6. **La decisión no está terminada hasta que su regla está en el árbol instalable.** La fila de la tabla declara la referencia; el reviewer comprueba que el archivo existe en la instalación y que el cambio respeta la decisión vigente de su rol. La fila de una decisión cuya regla todavía no está instalada **no** se declara vigente.

## Reasons

1. **Un principio que no llega a quien lo debe aplicar no gobierna nada.** El rol no abre el `docs/adr/` del proyecto; en la ruta de paquete no carga el skill. Un principio sin mecanismo de distribución es una declaración sin efecto, y el problema que la enmienda 003 enuncia —«un ADR registrado no gobierna el trabajo siguiente si ningún rol lo recibe»— se repetiría, con más autoridad, con el ADR de un principio.
2. **Una casa, comprobable.** El patrón de «dueño canónico único» ya es el del repo (la calibración de la revisión, el detalle progresivo, la política de evidencia): un archivo que dice cuándo se carga y al que los demás apuntan. La consecuencia útil es **mecánica**: el texto normativo aparece en **un único archivo** del árbol instalable, y eso se verifica con un `grep` sobre el árbol. Un principio repetido en tres sitios se puede comprobar leyendo tres sitios; uno repetido en tres sitios **se puede comprobar que no se repita**.
3. **El deber de rol es otra cosa que el principio, y por eso puede vivir en la fuente del rol.** «Considera las alternativas y explica el criterio» y «evalúa consecuencias reales» son **obligaciones**, no el principio: se pueden enunciar en una línea, se pueden comprobar por derivación textual y no necesitan el texto completo. Confundir ambas cosas es lo que produce la duplicación que el principio condena: si el deber fuera una copia del principio, habría dos principios.
4. **El límite evita el modo de fallo conocido de los principios.** Sin el límite explícito, un principio de diseño se convierte en un producto de justificaciones: cada elección pasa a exigir una comparación de alternativas, el costo de la relación crece con el tamaño del proyecto y la calidad de la justificación baja. El límite —definido y citado junto al principio en su archivo canónico— es lo que mantiene el principio barato de obedecer. Y el límite del reviewer —*la falta de una abstracción no es, por sí sola, un defecto*— es lo que evita el otro extremo: convertir «prefiero lo general» en «todo debe estar abstraído», que produce acoplamiento por el otro lado.
5. **El vehículo es el mismo que el de las decisiones.** La feature 006-004 no necesita un canal nuevo para el principio: la tabla de decisiones vigentes y su sección en el paquete distribuyen **filas**, y esta decisión es una fila más. Un mecanismo de distribución por principio habría sido un segundo camino para el mismo problema, con la divergencia que la enmienda 005 quiere evitar.

## Consequences

- **Positivas.** El principio tiene una casa comprobable y un deber por rol que llega a los dos runtimes y por las dos rutas (cuerpo del agente generado y bloque estático del paquete); el límite queda escrito junto al principio, en su archivo canónico, y el límite del reviewer queda escrito donde el reviewer lo lee; la fila de esta decisión es la primera de la tabla sembrada, de modo que el mecanismo de distribución y el principio **se refuerzan mutuamente**: la feature que crea la tabla es la que entrega el principio. La regla «no re-enunciar» es verificable con un `grep` sobre el árbol instalable, de modo que la duplicación futura es un fallo detectable y no una degradación silenciosa.
- **Negativas / límites declarados.** (a) El texto normativo y el deber de rol están en archivos distintos ⇒ hace falta una regla de no-copia **explícita** y un test que la vigile; sin ese test, la separación se degrada en duplicación. (b) En la **ruta de paquete** el rol **no carga el skill** ⇒ un puntero al archivo canónico **no** es resoluble por el rol: recibe el **deber completo** y la **dirección** a seguir, no la lectura íntegra del principio. Es la **misma** limitación que ya acepta el puntero vigente a la referencia de calibración, no un defecto nuevo. (c) El **texto normativo está en inglés** (el árbol del skill está en inglés) mientras que la decisión del dueño está escrita en español: el ADR traduce el sentido, pero **no** es la fuente ⇒ una divergencia de traducción sería un defecto de la traducción, no una segunda fuente. (d) La fila de esta decisión **no puede** ser `vigente` hasta que la regla esté en el árbol instalable ⇒ hay un orden real (el archivo primero, la fila después) que el gate de la tabla debe respetar.
- **No cambia.** El modelo de la revisión y su calibración (`references/stage-4-review.md`), los nombres de los roles y sus artefactos, la tabla cerrada de destinos, la tabla de tipos de artefacto, el exit gate de stage 5, el estado de la máquina de estados y el vocabulario de estado de los ADR: nada de eso se modifica con este ADR. El principio **tampoco** crea un mecanismo de aprobación nuevo ni un gate: su efecto es de criterio, y su efecto se verifica por derivación textual y por el comportamiento del reviewer.

## Notas

- **Contrato normativo:** `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005 — el principio y su límite, y las cuatro obligaciones) y §10 (enmienda 003 — la tabla de decisiones vigentes y la regla de que la fila guarda la referencia; fuera de alcance: índices generados, gates de cita obligatoria y cambios en `status`).
- **Código y documentos de producto:** `skills/cdad-cycle/references/design-principles.md` (**nuevo** — la casa del principio y de su límite), `skills/cdad-cycle/references/stage-4-review.md` (el procedimiento del deber del reviewer sobre la tabla), `skills/cdad-cycle/SKILL.md` (la tabla de referencias), `sources/roles/architect.md`, `sources/roles/reviewer.md` (las obligaciones), `skills/cdad-cycle/packets/roles/architect.md`, `skills/cdad-cycle/packets/roles/reviewer.md` (las obligaciones en la ruta de paquete) y los agentes generados por `scripts/cdad-generate.py`.
- **Distribución (el vehículo):** `docs/specs/006-004-active-decisions-table/spec.md` §2.5-2.6 y §12 (la tabla sembrada, con esta decisión como fila) y `plan.md` §3 U3 (la casa y las obligaciones), U4 (la tabla y su upkeep), U5 (la siembra de este repo, que materializa este ADR como `docs/adr/ADR-034-principio-general-antes-especifico.md`) y U7 (la verificación de la siembra, que corre después de la materialización).
- **Numeración:** **ADR-034** (este). El número lo consume el artefacto que se materializa primero; `plan.md` §12 lo tenía reservado como «ADR-033» hasta que ADR-033 lo tomó la decisión de modelos (nota de ADR-033: «pasa a ADR-034 porque el número lo consume el artefacto que se materializa primero»).
- **Límites honestos de este registro:** el principio es un **criterio de diseño**, no un mecanismo verificable: el producto no puede comprobar que un architect haya considerado la alternativa general, ni que un reviewer haya evaluado las cuatro consecuencias. Lo que sí es verificable es **la existencia y la unicidad de la casa**, **la presencia de los dos deberes** y **la presencia del límite** (deriva textual y `grep` sobre el árbol instalable), y el efecto real del criterio se observa en las revisiones, no en un test. La **aprobación** de este ADR es un acto **posterior y separado** de esta redacción, y la fila de la tabla que lo nombra no se declara vigente antes de esa aprobación.

Status: **Proposed** — a la espera de la aprobación de la autoridad vigente.
===END adr-034.md===

---

## Hallazgo → cambio → línea

Líneas de la **nueva** versión (que el orquestador materializa); entre paréntesis, la línea del `draft-002` que se sustituye.

| Hallazgo | Cambio | Dónde (nuevo · viejo) |
|---|---|---|
| **B-3** (BLOCKING) | El **validador permanente** deja de llevar el inventario: `tests/validate-consistency.sh` queda con **sólo invariantes duraderas** (cada fila → archivo existente; fila `obsoleto` → reemplazo existente; `roles` ∈ vocabulario cerrado; fila de ADR-034 existe; la nota declara que el estado lo declara quien mantiene la tabla). El inventario (25/1/8) queda como **evidencia puntual** de U5/U7. Cierre verificable: agregar un ADR aprobado **pasa**, reemplazar una decisión **pasa**, fila con archivo inexistente **falla**. | spec §0.2 (24-31 · nuevo) · spec §2.4 (128-129 · nuevo) · spec PD-11 (170 · 160) · spec INV-15 (203-204 · nuevo) · spec DEC-15 (221-222 · nuevo) · spec §9 (260-261 · nuevo) · spec §11 (299-301 · nuevo) · spec §12 (309, 352, 357 · 294, 337, 342) · plan §1.2 (32-45 · nuevo) · plan §2 U5/U7 (53-54 · 42-43) · plan §3 U5 (138-139 · nuevo) · plan §3 U7 (143-160 · 131-144) · plan §4 (202, 204 · 186, 188) · plan §6 (`validation_strategy`, U5, U7 · 207, 376-433) · plan §8 (496-505 · nuevo) |
| **O-3** (OPTIONAL) | La frase del cierre que conservaba la circularidad como obligación vigente se sustituye por el **orden corregido** (U4 pasa su gate sin la siembra → U5 depende de U3/U4 → U7 corre después → `U1→U2→U3→U4→U5→U7→U6`). | plan §5 (210 · **194**) |
| — | El **ADR-034 no cambia**: no fija ningún conteo del inventario, así que B-3/O-3 no lo alcanzan. Se entrega **verbatim** (sha256 `6e714bb1b5bc1a8e2fbd70e6c23e63c5b4e5004d28970aecdecd4e63336f070d`, el mismo que registró `plan-review-002.md`). Materializar como `docs/specs/006-004-active-decisions-table/adr-034-draft.md`. | adr-034-draft.md (sin cambios) |

---

## Evidencia

**Archivos modificados en el repositorio: ninguno.** El rol es read-only (`write_scope: []`) y la herramienta de escritura/edición está **denegada** por el guardarraíl del rol (verificado: `write` → `Permission denied: edit`). El texto de esta entrega va **en la respuesta** para que el orquestador lo materialice (ADR-003). Temporales de trabajo: **fuera del repositorio**, en `/tmp/opencode/` (`new_plan_tasks.json`, `apply_edits.py`, `spec-003.md`, `plan-003.md`).

**Comandos ejecutados y salida:**

```sh
$ sha256sum docs/epics/epic-006-opencode-concurrency/plan.md docs/cdad-policy.json
d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809  docs/epics/epic-006-opencode-concurrency/plan.md
f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711  docs/cdad-policy.json
# ⇒ contrato y política coinciden con el paquete

$ sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/architect.md \
           skills/cdad-cycle/packets/substages/architect-draft.md
37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110  skills/cdad-cycle/packets/common.md
268804ca7edb2245f85b0fa493c033f09193fc39696b5d56596d25ff9e5cc3b8  skills/cdad-cycle/packets/roles/architect.md
cfa0a2b51dd22ee1e3b26ffafb2d0dcbd0c311a384e8c9c465b793ede5073ddc  skills/cdad-cycle/packets/substages/architect-draft.md
# ⇒ las tres fuentes de instrucción coinciden con los digests del paquete

$ python3 /tmp/opencode/apply_edits.py
EDITS APPLIED OK
  spec  sec-0.2 new-lines 22-33 / PD-11 170 / INV-15 203-204 / DEC-15 221-222 / …
  plan  sec-1.2 new-lines 32-45 / u7-ficha 143-160 / cierre-orden 210 / plan-tasks 222-488
plan-tasks validators: OK
spec lines: 360 plan lines: 510

$ git status --short
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-18.md  → (real: 2026-10-19)
# ⇒ estado final IDÉNTICO al inicial: ningún cambio de producto ni de repo
```

Comprobaciones de contenido aplicadas: los 12 reemplazos de la spec y los 11 del plan se aplicaron con **exactamente una** ocurrencia cada uno (aserción del script; el primer intento falló y abortó al detectar 0 ocurrencias en `plan.md:194` — el archivo decía «empezarse», no «empezar» — y se corrigió antes de producir salida). El bloque `plan-tasks` regenerado pasa `_check_plan_tasks` y `_check_plan_validation_plan` del propio producto (`skills/cdad-cycle/scripts/cdad_packet.py`), con DAG `U1→U2→U3→U4→U5→U7→U6` y U6 dependiendo de U7.

**Commit:** ninguno (rol read-only, `write_scope: []`).

**Estado de aprobación:** esta entrega queda **BORRADOR — SIN APROBAR** (draft-003). No aprueba la spec, ni el plan, ni el ADR-034, ni las filas de la tabla (INV-6). La aprobación de cada acto es posterior y separada de la autoridad vigente.

**Abstenciones / VERIFY:** (a) **no** se ejecutó la suite completa ni `make validate` (política del paquete: la corre quien cierra; además el RED de esta feature aún no existe); (b) el **cierre verificable** de B-3 (agregar un ADR aprobado / reemplazar una decisión / fila inexistente) queda **escrito como RED de U7**, no ejecutado: su evidencia es la corrida de U6/U7; (c) **VERIFY** para quien implemente: el nombre exacto de la aserción nueva en `tests/validate-consistency.sh` y el modo exacto de parsear las filas de la tabla en el bloque (la tabla del proyecto no tiene formato de máquina: el bloque debe tolerar el formato de tabla del §12); (d) la afirmación «el 25 es la fotografía de la siembra» se apoya en el inventario medido hoy (33 ADR en `docs/adr/`, 8 *Proposed* excluidos: 012, 016, 025-030), re-verificado en disco en esta sesión.