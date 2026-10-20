Contract sha256 verified against the packet. Here are the three deliverables.

===BEGIN spec.md===
# 006-004-active-decisions-table — SPEC (etapa 2, borrador draft-001)

Estado: **BORRADOR — SIN APROBAR**. Esta entrega no lleva marca de aprobación y no la lleva nunca por el dictamen de la revisión de borrador (INV-6). La aprobación es un acto separado de la autoridad vigente (`skills/cdad-cycle/references/stage-2-specification.md`:88-120).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §10 (enmienda 003) y §12 (enmienda 005) — sha256 `d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809`, **verificado en disco** y coincidente con el del paquete `exec-006-004-active-decisions-table-001`.
Decisiones de entrada (orquestador, HITL delegada, 2026-10-20): `docs/epics/epic-006-opencode-concurrency/execution.md`:399-415 — diseño **O1**, **Q1**..**Q6**, tope de filas fail-closed, y ADR-034 como fuente única del principio.
Insumo: `docs/specs/006-004-active-decisions-table/discovery.md` (etapa 1, mismo autor).
Base medida: HEAD `a9cc7ab`. **El discovery se escribió antes de que 006-006 fuera construido**; por eso esta spec **re-verifica** las superficies que aquel documento cita: el bloque estático, el conjunto de campos del request y las funciones del render se miden **hoy** (mediciones M1..M8 abajo), no se copian.
Anonimización: rutas relativas al repositorio; sin rutas del host, endpoints, ids de sesión ni credenciales; el proyecto consumidor no se nombra.
**Numeración (declarada):** `DEC-n` numera las **decisiones** de esta spec; `D-1..D-6` numera la **deuda declarada** (§10), con la numeración heredada del discovery de esta feature para no colisionar con las decisiones.

## 0. Intención y necesidad del usuario real

- **Actor**: quien dirige el ciclo en un proyecto (el dueño, o el orquestador bajo HITL delegada) y, en el otro extremo, el **rol delegado** que recibe el encargo (architect, reviewer, implementer, test-writer, scribe).
- **Lo que quiere, en sus palabras**: «que la decisión que aprobamos gobierne el trabajo siguiente, sin que nadie tenga que abrir `docs/adr/` para adivinar qué sigue vigente».
- **Punto de partida legítimo**: el proyecto tiene `docs/adr/` con sus decisiones y `docs/systemPatterns.md` con sus convenciones. Hoy esa segunda superficie **no dice qué decisiones están en vigor**, y el paquete de un rol **no dice nada de ellas**.
- **Primer resultado útil**: cuando el orquestador aprueba un ADR y prepara el siguiente paquete, ese paquete **lleva** la decisión vigente que gobierna a ese rol —con el archivo donde está, su estado, un resumen de una línea y el lugar donde vive su regla—; y el proyecto muestra, en un solo lugar, qué decisiones están en vigor, cuáles ya no y por qué.

**La necesidad está medida, no supuesta** (discovery §0, reverificado hoy):

- **M1** — `grep -rn "Decisiones vigentes\|Current decisions" skills/ sources/ agents/ tests/ install.sh` → **0**. La sección es **nueva**, no una reorganización.
- **M2** — `ls docs/adr/ADR-*.md | wc -l` → **33**, y **no existe `docs/adr/README.md`** en este repo: hoy el proyecto **no tiene índice de decisiones** (el problema literal de la enmienda 003).
- **M3** — El **paquete es el único canal que puede llevar las filas a todos los roles**: el alcance de lectura por defecto del test-writer es `contract` + `tests` (`cdad_packet.py`:1238-1248) ⇒ `docs/systemPatterns.md` **queda fuera de su alcance** y un `--input docs/systemPatterns.md` sería **rechazado** (`cdad_packet.py`:1030-1031). «Dejar el archivo y que el rol lo lea» **no** cumple el requisito para todos los roles: las filas tienen que **viajar en el paquete**.
- **M4** — El estado de un ADR **no es derivable**: 33 archivos con **cuatro vocabularios y tres formatos** de estado distintos, 8 *Proposed*, 2 reemplazados (uno **parcialmente**) y 1 *Verified* ⇒ la columna «estado» **la declara quien mantiene la tabla**, no se re-deriva.
- **M5** — El **precedente exacto ya existe y es aditivo**: `request.plan_task` (opcional, `cdad_packet.py`:870) + `_plan_task_sections` (`:3796`) emiten dos secciones **sólo cuando el campo está declarado**, y el render sin el campo es **byte-idéntico** (`tests/test_006_006_u1_draft_object_form.py`:432). Ese es el molde de `## Current decisions`.
- **M6** — El techo del bloque estático **no aprieta**: `CDAD_STATIC_BLOCK_LIMIT`, default **12000** bytes (`cdad_packet.py`:1063-1079); medido hoy, máximo **3031** (`reviewer/plan-review`), mínimo **1309** (`scribe/memory`) ⇒ **holgura mínima 8969 bytes** en los 14 pares rol/subfase.
- **M7** — **No hay operación de CLI ni clase de transición para la aprobación de un ADR**: `TRANSITION_CLASSES` = `delivery, advance, gate, closure, late-delivery, disposition` (`cdad_packet.py`:5204-5205) y el state no tiene ningún campo de ADR ⇒ «agregar la fila al aprobarse un ADR» es, hoy, una **declaración de procedimiento** del orquestador (que ya tiene `docs/**` y el git), no una operación de producto.
- **M8** — La **tensión real con «fuente única»**: en la **ruta de paquete** el rol **no carga el skill** (directiva del rol: «Do not load or reload `cdad-cycle`… the packet is the execution contract») ⇒ un puntero a `<skill-dir>/references/x.md` **no es resoluble** por el rol en esa ruta. La **obligación operativa** tiene que entrar por la superficie que sí viaja: el **cuerpo del agente generado** (`sources/roles/*.md` → `agents/*.md`) y/o el **bloque estático del paquete** (`packets/roles/*.md`).

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
- **R-12 (la fila no aprueba nada).** Las filas no tienen efecto de aprobación: el recibo queda `semantic_status: pending` y `approval_effect: false`, como hoy (`cdad_result.py`:737-739). Una decisión **vigente** no es una **aprobación**: son hechos distintos (ADR-014).
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

### 2.5 La tabla del proyecto: plantilla, upkeep y las dos responsabilidades

- **La sección y su título.** La plantilla del Memory Bank (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`) gana la sección **`## Current decisions`** (plantilla en inglés) como **primer H2** después de la introducción; en este repo la instancia viva (`docs/systemPatterns.md`) usa **`## Decisiones vigentes`** en el mismo lugar. El **título no es una dependencia del producto** (Q5): el CLI no parsea el documento ⇒ el título es libre; la **forma de la fila** sí es la del producto.
- **El bootstrap no se toca**: `references/bootstrap.md`:66-83 copia la plantilla ⇒ un proyecto nuevo nace con la sección (vacía) y con `docs/adr/README.md` (la guía de cómo escribir ADR, que **no** es un índice — M2).
- **Responsabilidad 1 — el orquestador mantiene la tabla.** En `references/stage-5-merge.md` §5.4 (la decisión sobre el ADR), el orquestador **agrega la fila** al aprobarse un ADR y **marca la fila del reemplazado como `obsoleto`** conservándola, con su `superseded_by`. El **exit gate de stage 5 no cambia** (Q6): no se agrega ninguna casilla nueva al gate (`references/stage-5-merge.md`:163-178).
- **Responsabilidad 2 — el reviewer revisa la tabla.** El **dueño canónico de la comprobación** es `references/stage-4-review.md` (la referencia canónica del reviewer), que gana una sección corta con las dos comprobaciones: (a) **alineación** — cada fila apunta a un archivo que existe en `docs/adr/`, y el contraste entre el conjunto de filas y el directorio; (b) **respeto** — el cambio respeta las decisiones vigentes **de su rol** (las filas que el paquete le lleva). La **regla de rol** (`sources/roles/reviewer.md` + `packets/roles/reviewer.md`) la **referencia** y no la copia, con el mismo patrón que la calibración (`sources/roles/reviewer.md`:44-46).
- **La re-entry (Q6).** `references/re-entry.md` §Scribe gana la reconciliación: la tabla tiene **dos escritores** —el orquestador en la aprobación del ADR, y el scribe opcionalmente en el cierre (el `systemPatterns.md` ya entra al paquete del scribe, `references/stage-5-merge.md`:36-47)— y el **orquestador resuelve el conflicto por CAS**: la materialización del scribe se hace contra el digest **actual** de `docs/systemPatterns.md`, y si el destino cambió ⇒ **conflicto** (`cdad_result.py`:841-847, «refusing to overwrite»), no sobrescritura silenciosa. La fila del orquestador **manda**; el resto de los cambios del scribe se aplican.

### 2.6 El principio de general antes que específico: una casa, dos obligaciones, un límite

- **La casa (una sola).** `skills/cdad-cycle/references/design-principles.md` —un archivo **nuevo** del skill instalable— lleva la sección «General before specific» con **el texto del principio** y **su límite** («el principio mejora el juicio de diseño; no aumenta las justificaciones que los agentes deben producir»). Se elige una *reference* y no `SKILL.md` porque ése es el patrón del repo —«dueño canónico único» en `references/` y puntero desde el rol (`references/stage-4-review.md`:8-10)— y porque `SKILL.md` se carga siempre: meter ahí una regla de diseño para dos roles carga a todos. El árbol `skills/cdad-cycle/` viaja completo al entorno instalado (`install.sh`:370-378) ⇒ **no hace falta tocar el instalador**.
- **La fuente única, verificada.** El texto normativo del principio aparece en **un solo archivo** del árbol instalable (`skills/`, `sources/`, `agents/`). Los consumidores lo **referencian**; el deber del rol es **duty**, no principio, y por eso vive en la fuente del rol (una línea) y no es una copia.
- **Obligación del architect** (una línea, en `sources/roles/architect.md` y en `packets/roles/architect.md`): en las decisiones relevantes, **considera las alternativas generales y específicas y explica el criterio elegido**; el principio y su límite viven en el archivo citado y **no se re-enuncian aquí**.
- **Criterio del reviewer** (una línea, en `sources/roles/reviewer.md` y en `packets/roles/reviewer.md`, con el procedimiento en `references/stage-4-review.md`): evalúa **consecuencias reales** —duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento— y **la falta de una abstracción, por sí sola, no es un defecto**.
- **Por qué el bloque estático también lleva la obligación (D-2 del discovery).** En la **ruta de paquete** el rol **no carga el skill** ⇒ un puntero a `<skill-dir>/references/…` no es resoluble por el rol. El bloque estático **sí viaja** (y su digest viaja en `instruction_sources`), de modo que la **obligación operativa** llega completa por esa vía. La lectura íntegra del principio depende de que el rol alcance el skill: es la **misma limitación** que ya acepta el puntero vigente a `references/stage-4-review.md`, no un defecto nuevo (§10, D-2).
- **El ADR-034** apunta al archivo del skill como la regla que materializa. La fila de la tabla lo referencia igual ⇒ el mecanismo de §10.4 del plan («una decisión que cambia la metodología no está terminada hasta que su regla está en el skill instalable; la fila guarda la referencia») queda servido por la **misma** fila.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **La forma de la fila se valida y falla cerrado.** Una fila con `file`, `state`, `summary`, `roles` y `reference` válidos es aceptada; una clave **desconocida** ⇒ rc≠0 nombrando la clave; `state` fuera de `{vigente, obsoleto}` ⇒ rc≠0 nombrando el valor y el vocabulario; `superseded_by` **ausente** con `state: obsoleto` ⇒ rc≠0; `superseded_by` **presente** con `state: vigente` ⇒ rc≠0; `file` inexistente ⇒ rc≠0 nombrando la ruta; `roles` vacío ⇒ rc≠0; un nombre de rol fuera del vocabulario ⇒ rc≠0 nombrando el valor; `summary` con salto de línea ⇒ rc≠0. | el `REQUEST.json` del paquete en el caso bueno; rc≠0 y **sin publicación** (`out-dir` sin entradas, state byte-idéntico) en cada negativo, con el mismo control que `assert_rejected_without_publication` (`tests/test_004_003_t4_validation_fields.py`:399-423) |
| **PD-2** | **La fila nombra al rol del paquete.** Una fila que nombra al rol del paquete es admitida; una fila que **no** lo nombra ⇒ rc≠0 **nombrando la fila y el rol del paquete**; una fila que nombra a otro roldelegado (pero no al del paquete) ⇒ rc≠0 por la misma regla. | los rc de `prepare` y el texto del diagnóstico; el `REQUEST.json` del caso bueno |
| **PD-3** | **Sólo lo vigente viaja.** Una fila `obsoleto` **no** es admisible en un paquete ⇒ rc≠0 nombrando la fila y su `superseded_by`; la fila obsoleta **conserva su sitio** en la tabla del proyecto (no se borra). | rc≠0 del `prepare` con la fila obsoleta; el texto de la tabla del proyecto tras el rechazo (la fila sigue) |
| **PD-4** | **El tope de filas falla cerrado.** 32 filas admitidas; 33 ⇒ rc≠0 nombrando el número declarado y el tope; el estado queda byte-idéntico y no se publica nada. | los dos rc; el conteo de filas del `REQUEST.json`; el `out-dir` vacío en el rechazo |
| **PD-5** | **La sección del render es aditiva y byte-idéntica sin filas.** Sin `current_decisions` (o con la lista vacía) el render es **byte-idéntico** al del producto sin la feature **en la misma revisión**; con filas, el render emite `## Current decisions` **después de `## Contract`**, con una entrada por fila, en el orden declarado, con `file`, `state`, `summary`, `roles` y `reference`. | comparación byte a byte del render con y sin el campo, **en la misma revisión** (el `PACKET.md` entero **no** se congela: las fuentes de instrucción y sus digests cambian legítimamente entre revisiones — L-1); el texto de la sección en el caso con filas |
| **PD-6** | **Las filas viajan en el encargo, no en un archivo que el rol debe abrir.** El `REQUEST.json` lleva `current_decisions` con las filas en el orden declarado; el paquete del rol las lleva en la sección; el paquete de un rol **sin** filas aplicables no lleva la sección (byte-idéntico); el test-writer **sigue** sin poder leer `docs/` (su alcance no cambia) y **sí** recibe las filas que lo gobiernan. | el `REQUEST.json`; el `PACKET.md`; los `read_scope` del paquete del test-writer (sin cambios) |
| **PD-7** | **La plantilla trae la sección y un proyecto sin ADR no queda bloqueado.** La plantilla del Memory Bank contiene `## Current decisions`; el bootstrap la instala (copia literal de la plantilla); un proyecto **sin** ADR prepara cualquier rol con rc=0 y **sin** sección; la sección vacía **no** es una fila. | `grep` sobre `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`; el `prepare` rc=0 de un proyecto sin `docs/adr/`; el render sin sección |
| **PD-8** | **Las dos responsabilidades están escritas donde se aplican.** `references/stage-5-merge.md` dice que el orquestador **agrega la fila** al aprobarse un ADR y **marca la anterior como obsoleta**; el **exit gate de stage 5 no cambia** (no hay casilla nueva). `references/stage-4-review.md` dice que el reviewer **compara la tabla con `docs/adr/`** y que **el cambio respeta las decisiones vigentes de su rol**; la fuente del rol y su bloque estático **referencian** esa regla y no la copian. | derivación textual sobre las tres superficies (el patrón de derivación del proposal de 006-006) + el control negativo: el **exit gate** de `references/stage-5-merge.md` tiene el **mismo** número de casillas que antes |
| **PD-9** | **La re-entry reconcilia la tabla y no la pisa.** En la re-entry del scribe, si el `docs/systemPatterns.md` cambió desde el digest que el scribeursorsoreMaterializó, la materialización se **rechaza por CAS** («refusing to overwrite») y el orquestador **reconcilia** (aplica la fila del orquestador y vuelve a materializar contra el digest actual); la fila del orquestador **manda**. | el texto de `references/re-entry.md` (derivación) + el caso real de conflicto CAS en el recorrido de U6 (V-6) |
| **PD-10** | **La fuente única, las dos obligaciones y el límite.** `skills/cdad-cycle/references/design-principles.md` existe y lleva el principio **y** su límite; el texto normativo del principio aparece en **un único archivo** del árbol instalable (`skills/`, `sources/`, `agents/`); la fuente del architect y la del reviewer **nombran** la obligación y **apuntan** al archivo canónico, y **no** copian el texto del principio; el criterio del reviewer nombra las cuatro consecuencias reales y el límite («la falta de una abstracción, por sí sola, no es un defecto»); `SKILL.md` §«How to read the references» tiene una fila para el archivo nuevo. | el test de texto de `tests/validate-consistency.sh` (bloque nuevo): unicidad por `grep -rl` sobre el árbol instalable; presencia de las obligaciones; **control negativo** de copia; el límite presente en las dos superficies del reviewer |
| **PD-11** | **La siembra de este repo (Q3).** `docs/systemPatterns.md` tiene la sección `## Decisiones vigentes` como **primer H2**, con **25 filas vigentes** (las 24 decisiones en vigor existentes + `ADR-034`) y **1 fila obsoleta** (`ADR-007`, con su reemplazo); `ADR-034` es una de ellas; los **8 ADR *Proposed*** no son filas y la tabla **declara** las exclusiones; **cada** fila apunta a un archivo que existe en `docs/adr/`; el `ADR-034` existe, tiene el estado *Proposed* (a la espera de la aprobación del dueño) y **apunta a la fuente única** del principio sin re-enunciar su texto. | el bloque de texto nuevo de `tests/validate-consistency.sh` (presencia de la sección, de la fila de ADR-034, de la nota de exclusiones, y un bucle que comprueba que **cada** fila apunta a un archivo existente) + el `ADR-034` en `docs/adr/` |
| **PD-12** | **El recorrido de aceptación (U6) en un proyecto descartable.** (a) un ADR aprobado produce una fila y el siguiente paquete del rol nombrado **la lleva**; (b) un ADR reemplazado deja la fila vieja **obsoleta** en la tabla y **fuera** del paquete; (c) un rol no nombrado **no** recibe la fila y su paquete es byte-idéntico al de hoy; (d) un proyecto sin ADR funciona sin cambios; (e) el reviewer **detecta** una tabla desalineada (una fila que apunta a un archivo inexistente) como **hallazgo** con `file:line`, veredicto y condición de cierre —no como puerta—; (f) la regla del principio **existe en el árbol instalado** y el paquete del architect y del reviewer la nombran. | los paquetes y sus `REQUEST.json`; los rc; el texto del hallazgo del reviewer; la comparación byte a byte del caso (c); la existencia del archivo de referencia en la instalación |
| **PD-13** | **Las guardas vigentes siguen verdes.** El paquete sin el campo nuevo no cambia (byte-idéntico, intra-revisión); el bloque estático de los 14 pares rol/subfase queda **por debajo** del techo declarado de 12000 bytes tras las adiciones; `make validate` verde; `make staging` es **determinista** (dos corridas, mismos bytes) y los agentes generados contienen las obligaciones; el CLI instalado (el producto instalado) renderiza la sección igual que el del repo. | `tests/test_static_block_ceiling.py` + la **medición** del bloque estático en el RED; salida de `make validate`; comparación byte a byte de dos `make staging`; el patrón de producto instalado de `tests/test_004_003_t2_plan_review.py`:290 |

### 3.1 Escenarios de recorrido (E1..E6) — la vara

Cada escenario es la **intención** de la feature expresada como recorrido comprobable: si todas las PD de su fila pasan, el escenario tiene que funcionar **de verdad**. Un escenario no cubierto es un hueco: se cubre o se declara.

| Escenario | Qué tiene que funcionar (recorrido) | PD que lo garantizan | Hueco declarado |
|---|---|---|---|
| **E1** | **Se aprueba un ADR y el siguiente paquete del rol nombrado lo lleva.** El dueño aprueba el ADR y el orquestador lo commitea en `docs/adr/ADR-NNN-*.md`; el orquestador **agrega la fila** a la sección «Decisiones vigentes» de `docs/systemPatterns.md` (archivo, `state: vigente`, resumen de una línea, roles que deben consumirla, referencia) y la commitea con prefijo `docs(memory):`; al preparar el paquete de ese rol, **declara** la fila; el rol la recibe **dentro** del paquete y la cita. Si el rol no está nombrado, esa fila **no** está. | PD-1, PD-2, PD-5, PD-6, PD-8, PD-11 | **Ninguno** para el recorrido mecánico. **Declarado**: la **completitud** (que el orquestador declare *todas* las filas del rol) **no** está garantizada mecánicamente: la garantía del producto es «toda fila declarada nombra a este rol», no «toda fila vigente fue declarada» (D-1). |
| **E2** | **Una decisión se reemplaza: la vieja queda obsoleta en la tabla y no se distribuye.** Se aprueba `ADR-034` que reemplaza a `ADR-0XX`: el orquestador **marca la fila vieja** como `obsoleto (reemplazado por ADR-034)` **conservándola** y **agrega** la nueva como `vigente`; al preparar el paquete, la fila **vigente** viaja y la **obsoleta no** (y, si se intentara declararla, el producto **rechaza** nombrando su sucesor). | PD-3, PD-5, PD-8, PD-12 | **Ninguno** mecánico. **Cota declarada**: la fila vieja sobrevive **sólo** en la tabla del proyecto; el paquete no la lleva ni la marca. |
| **E3** | **Un rol no nombrado no lo recibe.** La fila declara `roles: architect, reviewer`; al preparar un paquete de `test-writer`, la fila **no** viaja; y si el orquestador la declara de todos modos, `prepare` **falla** nombrando la fila y el rol. Un rol sin ninguna fila aplicable ⇒ paquete **byte-idéntico** al de hoy. | PD-2, PD-5, PD-6, PD-12 | **Ninguno**. La diferencia entre «no declarada» y «declarada para otro rol» es **ruidosa y recuperable** en los dos casos. |
| **E4** | **El reviewer detecta una tabla desalineada con `docs/adr/`.** Una fila apunta a `docs/adr/ADR-099-lo-que-sea.md` (que no existe) o el directorio y la tabla no coinciden; el reviewer (read-only, alcance `repository-read` ⇒ puede leer `docs/systemPatterns.md` **y** `docs/adr/`) lo detecta y lo reporta con `file:line`, `Verdict: BLOCKING` + `Bucket` (regla de observables de `references/verdict-tuple.md`), consecuencia y **condición de cierre verificable** (regla 2 de la calibración). | PD-8, PD-12 | **Declarado**: **no es un gate duro** (fuera de alcance: «gates de cita obligatoria») ⇒ es un hallazgo, con la severidad que le corresponda por efecto real. Y **no re-deriva** el estado de los ADR (D-3): contrasta el conjunto que la tabla declara. |
| **E5** | **Un proyecto sin ADR no queda bloqueado.** Proyecto nuevo: `docs/adr/` vacío y la sección recién instalada, vacía; `prepare` de cualquier rol ⇒ **rc=0**, **sin** sección, render **byte-idéntico**; ninguna regla nueva bloquea a un proyecto que no adopte ADR. | PD-7, PD-9, PD-12 | **Ninguno**. La sección vacía **no** es una fila: la lista vacía no emite sección. |
| **E6** | **Una decisión metodológica no está terminada hasta que su regla está en el skill instalable.** Se aprueba `ADR-034`; su fila dice **dónde vive** la regla (`skills/cdad-cycle/references/design-principles.md`); el paquete del architect y del reviewer **nombran** ese archivo; un revisor puede verificar que el archivo **existe** en el árbol instalado (`install.sh`:370-378 garantiza que `skills/cdad-cycle/` viaja completo). | PD-10, PD-11, PD-12 | **Ninguno** mecánico. **Declarado**: el CLI **no** verifica el `reference` (puede apuntar al árbol instalado, que el CLI no resuelve) ⇒ la comprobación es del **reviewer** (E4/E6), no del producto (L-4). |

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
- **INV-12 — La regla de rol no se duplica.** La fuente del rol y su bloque estático **declaran la obligación** y **apuntan** al dueño canónico; el texto del principio **no** se copia en ninguna otra superficie del árbol instalable.

## 5. Decisiones (DEC-n)

- **DEC-1 — Diseño O1: un campo opcional del request + una sección aditiva del render.** *Adoptada por el orquestador (O1).* *Rechazadas:* (a) **O2** — que el CLI lea la tabla del proyecto y filtre por rol: metería el **formato de un documento de proyecto** dentro del producto (el CLI hoy verifica el **digest** del documento sin conocer su formato, `cdad_packet.py`:971-1002) y ataría el byte del paquete al estado de la tabla; (b) **O3** — texto libre en `--objective`/`--invariant`: sin sección, sin verificación de «la fila nombra a este rol», y sobrecarga semántica del canal de invariantes; (c) **O4** — la tabla como `--input`: el path debe estar en el alcance de lectura (`cdad_packet.py`:1030-1031) ⇒ para el test-writer habría que **ampliar** el alcance (o falla), y el paquete no lleva las filas.
- **DEC-2 — La fila tiene una forma cerrada de seis claves, con `superseded_by` condicional.** *Razón:* una forma única sirve **a la vez** al documento del proyecto y al request ⇒ el orquestador construye el request desde la tabla sin traducción, y el producto valida una **forma** que el proyecto ya respeta. *Rechazada:* la forma de **cinco** claves con el reemplazo dentro del `state` (texto libre): el vínculo «quién reemplaza a quién» dejaría de ser verificable.
- **DEC-3 — El estado de la fila es `vigente` | `obsoleto`, y el binario del plan se respeta.** Una fila con `state: obsoleto` **no** es admisible en un paquete (R-6) ⇒ el producto conserva la regla del plan («el paquete lleva las filas **vigentes** que lo nombran») y la hace verificable. *Rechazada:* un tercer estado (`parcialmente reemplazado`): ampliaría el vocabulario de estado que el plan fija, y el caso real (ADR-008) se resuelve en la fila con `state: vigente` y el resumen que nombra la parte reemplazada (DEC-4). *Consecuencia declarada:* el vínculo con el reemplazante **no viaja** en el paquete (no puede: la fila obsoleta no viaja) ⇒ se conoce por la tabla del proyecto.
- **DEC-4 — ADR-008 es una fila `vigente`, no `obsoleto`.** Medido: `docs/adr/ADR-008-…md`:3-9 declara `**Status:** **Verified** … **parcialmente reemplazado por ADR-033** … el resto sigue vigente`. Declarar la fila `obsoleto` **afirmaría** un reemplazo total que nadie ha declarado; declarar `vigente` **sin más** ocultaría la parte reemplazada. ⇒ `state: vigente` y el `summary` nombra el alcance residual y el reemplazo parcial. El ADR-033 lo confirma por su cuenta («su retiro formal es una decisión aparte»).
- **DEC-5 — El vocabulario de consumidores de una fila incluye `orchestrator`.** El orquestador es un rol del producto (`sources/roles/orchestrator.md`, `agents/cdad-orchestrator.md`) pero **no** es un rol despachado por paquete. Medido: **7** de los 33 ADR (002, 004, 012, 016, 018, 021, 023) no nombran **ninguno** de los cinco roles delegados; de ellos, **5** están en vigor (002, 004, 018, 021, 023) y gobiernan **exactamente** la conducta del orquestador (dónde se desarrolla y se instala, quién aprueba, quién declara la clase de una referencia, el arranque desde reposo, la interfaz de delegación). Sin `orchestrator` en el vocabulario, esas cinco decisiones **no** podrían tener fila ⇒ el índice perdería precisamente las decisiones másueras del ciclo. *Consecuencia declarada:* una fila que nombra sólo `orchestrator` **no viaja** en ningún paquete (no existe un paquete de orquestador); el orquestador la consume leyendo la tabla, que él mismo mantiene. *Rechazada:* un vocabulario de **cinco** ⇒ la tabla quedaría incompleta por construcción.
- **DEC-6 — El tope es 32 filas por paquete, fail-closed.** Justificación medida en §2.4. *Rechazados:* un tope **atado al número de filas de la tabla** (sería un tope que se mueve solo, y por tanto ningún tope); un tope **por bytes** (la sección no tiene techo propio y el byte de la fila depende del texto libre del `summary` ⇒ un tope de bytes no es determinista sin normalizar el texto); **sin tope** (el paquete crece sin control: D-6).
- **DEC-7 — El `reference` no lo verifica el CLI.** Puede apuntar al árbol instalado del skill, que el CLI no resuelve ⇒ el producto no puede comprobarlo sin conocer la instalación. *Consecuencia:* la comprobación es del **reviewer** (E4/E6), que sí puede leer el proyecto y la instalación. *Rechazada:* verificar el `reference` contra el proyecto: daría una garantía **falsa** (el archivo puede estar en el árbol instalado, no en el proyecto).
- **DEC-8 — La fila viaja como `--current-decision` (JSON, repetible), no como archivo.** *Razón:* un solo mecanismo, sin un segundo artefacto que pueda divergir de la tabla, sin ambigüedad de parseo (el `summary` es texto libre: un separador textual lo rompería) y con la fila **en el request** (JSON) desde el primer momento. *Rechazada:* un `--current-decisions <archivo.json>`: crea un segundo lugar donde vive el contenido de las decisiones, y obliga a decidir quién lo escribe y con qué garantía de frescura.
- **DEC-9 — El principio se materializa en un archivo **nuevo** del skill, no en `SKILL.md` ni en el `stage-2`.** *Razón:* el patrón del repo (un dueño canónico en `references/`, los consumidores lo referencian) y el hecho de que `SKILL.md` se carga siempre (una regla de diseño para dos roles cargaría a todos). *Rechazada:* `SKILL.md` (carga universal) y `references/stage-4-review.md` (es el dueño de la **calibración** del reviewer, no del principio de diseño: mezclar dos dueños crea dos fuentes).
- **DEC-10 — El deber del reviewer vive en `references/stage-4-review.md`, con puntero desde la fuente del rol y su bloque estático.** *Razón:* el mismo patrón que la calibración (`sources/roles/reviewer.md`:44-46 → `references/stage-4-review.md`:8-10). *Rechazada:* enunciar el procedimiento completo en el bloque de rol (duplicaría la regla en dos superficies y lo haría divergir) y en el substage de la subfase (el deber es **del rol**, no de una subfase: aplica a la revisión del resultado y a la del borrador).
- **DEC-11 — La tabla se mantiene en el evento «ADR aprobado», no en el cierre de cada feature.** (Q6, del orquestador.) El exit gate de stage 5 **no** cambia. *Razón:* el evento que crea una decisión es su aprobación; el cierre de una feature puede no tener decisión nueva, y atar ahí la tabla la deja envejecer sin evento que la mueva. *Consecuencia:* el upkeep es **procedimiento**, no producto (D-4) ⇒ por eso la fila se declara al preparar el paquete, y la completitud no está garantizada mecánicamente (D-1).
- **DEC-12 — La revisión del borrador de esta spec sigue el procedimiento vigente de 006-006.** 006-006 ya está construida (el gate 2→3 con la revisión de borrador es la superficie vigente): esta spec y este plan se revisan con `draft-plan` + `plan-review` (la revisión del **borrador**, sobre un borrador no aprobado, que es exactamente lo que 006-006 habilitó), y la aprobación es de la autoridad vigente. *Razón:* la feature 006-004 **no** reimplementa la revisión; la usa.

## 6. Desconocidos (V-n) y su resolución

- **V-1 — ¿El CLI instalado renderiza la sección con la misma forma?** Lo **no medido** es el render del producto **instalado** con `--current-decision` (el árbol instalado viaja completo, `install.sh`:376, pero el CLI instalado es otro proceso). *Resolución:* el RED de U1/U2 renderiza **desde el producto instalado** y compara byte a byte con el render del repo (el patrón de `tests/test_004_003_t2_plan_review.py`:290).
- **V-2 — ¿`make staging` sigue siendo determinista con las fuentes de rol cambiadas?** *Resolución:* dos corridas de `make staging` con comparación byte a byte de los agentes de architect y de reviewer; si no lo fuera, es un defecto de 004-001 ya cubierto por sus propios tests (`tests/test_cdad_generate.py`).
- **V-3 — ¿`receive` revalida el request con el conjunto ampliado?** `cdad_result.py`:561 llama a `validate_request`, que es **la misma función** que usa `prepare` ⇒ el conjunto cerrado ampliado aplica en ambos lados. *Resolución:* el RED **recibe** un paquete cuyo request lleva `current_decisions` (hoy sería rechazado) y otro con una fila malformada (hoy también): el RED lo demuestra, no lo supone.
- **V-4 — ¿El bloque estático sigue bajo el techo tras las adiciones?** Medido hoy: máximo **3031** bytes (`reviewer/plan-review`) con techo **12000** ⇒ holgura **8969**. Las adiciones previstas (dos líneas de deber en `packets/roles/architect.md` y `packets/roles/reviewer.md`, ~150-300 bytes cada una) llevan el peor caso a ≈**3400** bytes. *Resolución:* la **medición** se repite en el RED de U3/U4 y se registra; si superara el techo, el RED falla (y la respuesta **no** es subir el techo).
- **V-5 — ¿La política de compatibilidad entre revisiones se comporta como queda declarada?** Lo **no medido** es la corrida de dos fases con el CLI real (publicar con las fuentes anteriores → cambiar las fuentes → recibir después). *Resolución:* el caso de PD-16(c) de 006-006, reproducido aquí (esta feature **también** cambia dos de las tres fuentes de instrucción: `packets/roles/architect.md` y `packets/roles/reviewer.md`), se ejecuta en U6 y su salida real se pega en la evidencia.
- **V-6 — ¿Cómo se comporta el conflicto CAS sobre `docs/systemPatterns.md` cuando el orquestador ya escribió la tabla?** Medido en el código: la materialización con `expected_previous_sha256` que no coincide con el destino ⇒ `ResultError` «conflict: … (CAS): refusing to overwrite» (`cdad_result.py`:841-847); y con `expected_previous_sha256` nulo sobre un destino divergente ⇒ «(create-only)». Lo **no medido** es la **corrida real** con los dos escritores. *Resolución:* el caso de PD-9 se ejecuta en U6 (el orquestador escribe la fila; el scribe propone un `systemPatterns.md`; la materialización falla con el conflicto nombrado; el orquestador reconcilia y vuelve a materializar contra el digest actual) y su salida real se pega en la evidencia; si el comportamiento real difiere de lo declarado, **se corrige la declaración** (no al revés).

## 7. Medición de la aceptación

- Se mide lo **observado**: el rc de cada comando, el contenido del `REQUEST.json`, el texto de la sección renderizada, la comparación byte a byte de los renders, la **medición** del bloque estático, la salida de `make validate`, los bytes de las dos `make staging` y el texto de las derivaciones.
- **«Desconocido» no es cero** y no se generaliza el resultado de un recorrido. La evidencia de que la **vara** (E1..E6) funciona es el **recorrido real** (PD-12), no una simulación: un recorrido que no atrapa ningún defecto es **buen resultado** y se declara igual.
- La **suite completa** la corre **una vez**, quien cierra (política declarada en el paquete); las unidades citan su propia evidencia focal y las regresiones de su ficha.
- **No** se fijan reducciones porcentuales, tiempos ni tamaños como meta. El tope de 32 (§2.4) **no** es una meta de rendimiento: es un límite de seguridad declarado.

## 8. Fuera de alcance

1. **Índices generados** (una `docs/adr/README.md` índice o cualquier tabla derivada por herramienta) — excluido por el plan §10.
2. **Gates de cita obligatoria** (que el paquete exija citar el ADR, o que el reviewer tenga una puerta que la exija) — excluido por el plan §10. E4 es un **hallazgo**, no una puerta.
3. **Cambios en `status`**: ni el campo `**Status**` de los ADR (no se normaliza el vocabulario: M4) ni el `status` de la máquina de estados. El «estado» de la tabla es una propiedad de la **fila**, que es el diseño del propio plan (Q4).
4. **El exit gate de stage 5** — no se le agrega ninguna casilla (Q6).
5. **Un kind, subfase, agente, stage, tipo de artefacto o verbo nuevos**: se reutilizan `prepare`, el campo opcional del request, el kind `scribe-systemPatterns` y el materializador existente (`assets/artifact-policy.json`:13).
6. **Que el CLI lea o parsee el documento del proyecto** (O2, DEC-1).
7. **Una operación de CLI o una clase de transición para la aprobación de un ADR** (D-4): el upkeep de la tabla es procedimiento del orquestador, no estado verificable por el producto.
8. **La revisión formal del resultado** (etapa 4) y su calibración: se tocan **sólo** para añadirles el deber del reviewer; su texto vigente no se altera.
9. **El CLI instalado en el HOME del dueño**: el despliegue es del owner (`docs/epics/…/plan.md` §6); esta feature prepara el candidato y su receta, no despliega.
10. **Migrar, reescribir o normalizar** los 33 ADR existentes: no se toca ninguno de ellos (salvo **crear** `ADR-034`).
11. **Retirar formalmente ADR-001 y ADR-005**: su contenido operativo (el mapa de modelos por agente) ya no tiene efecto desde ADR-033, pero **su retiro formal es una decisión del dueño** (ADR-033 §Notas). La tabla los refleja **en vigor** con un `summary` que lo dice, en vez de afirmar un reemplazo que nadie ha declarado.

## 9. Riesgos residuales

- **La completitud de la tabla no está garantizada mecánicamente** (D-1): el producto garantiza «la fila declarada nombra a este rol», no «toda fila vigente fue declarada». *Mitigación:* el procedimiento de upkeep (DEC-11) + el deber del reviewer (PD-8), que compara la tabla con `docs/adr/`. *Riesgo residual:* **declarado** — un orquestador distraído puede preparar un paquete sin la fila que le corresponde; el reviewer lo ve, pero no lo bloquea.
- **El puntero al archivo del principio no es resoluble en la ruta de paquete** (D-2): el rol no carga el skill. *Mitigación:* la **obligación** viaja en el bloque estático y en el cuerpo del agente; el **principio íntegro** queda como dirección a seguir cuando el rol alcance el skill. *Riesgo residual:* el mismo del patrón vigente (puntero a `references/stage-4-review.md`), **declarado**.
- **Una fila puede quedar desactualizada** si el orquestador aprueba un ADR y no actualiza la tabla. *Mitigación:* el upkeep es un evento con nombre (aprobación de un ADR) y el reviewer lo contrasta. *Riesgo residual:* **declarado**; el exit gate de stage 5 **no** lo cubre (Q6) ⇒ es deuda (D-5).
- **El estado de la fila es una declaración, no un hecho derivado** (D-3): 4 vocabularios, 3 formatos, 8 *Proposed*, 1 reemplazo parcial. *Mitigación:* la tabla **declara**; el reviewer contrasta contra el conjunto declarado, no contra una re-derivación. *Riesgo residual:* **declarado** — una tabla mal declarada es posible y la revisión la expone, no la impide.
- **Un paquete en vuelo se invalida al cambiar las fuentes de instrucción** — y esta feature cambia dos (`packets/roles/architect.md`, `packets/roles/reviewer.md`). *Mitigación:* la política declarada (L-1), con su caso en U6. *Riesgo residual:* **declarado y aceptado** (mismo precedente que 006-006 D-12).
- **El estado «obsoleto» de una fila no viaja** ⇒ el rol que recibe el paquete **no ve** que la decisión fue reemplazada (sólo ve la nueva). *Mitigación:* la fila nueva nombra su `reference`; la historia queda en la tabla del proyecto. *Riesgo residual:* **declarado y aceptado** — es exactamente lo que el plan pide («la fila vieja se conserva, la distribución se detiene»).
- **La fila puede grows sin que nadie lo note** si el orquestador declara filas irrelevantes. *Mitigación:* R-5 (la fila debe nombrar al rol) + el tope (R-7). *Riesgo residual:* **declarado** — el tope acota el volumen, no la pertinencia.
- **Dos escritores de la tabla** (orquestador y scribe): el orquestador escribe la fila; el scribe puede proponer un `systemPatterns.md` completo. *Mitigación:* CAS + reconciliación declarada (PD-9). *Riesgo residual:* **declarado** — el conflicto es ruidoso y no hay sobrescritura silenciosa.

## 10. Límites y deuda declarada

- **L-1 — Deuda de compatibilidad entre revisiones (heredada del precedente de 006-006).** Un paquete publicado antes de un cambio de las fuentes de instrucción **no** es recibible después (los digests de las fuentes son parte de la identidad del paquete: `cdad_packet.py`:1080-1094 compone y publica sus digests; la recepción re-renderiza y compara, `cdad_result.py`:563-566). **No** se corrige el renderer. La política declarada (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo) y su caso demonstrativo están en U6. Deuda **declarada**, no defecto: es inherente al contrato de paquete, y esta feature lo **toca** (dos de las tres fuentes) ⇒ lo declara.
- **L-2 — Deuda del puntero no resoluble en la ruta de paquete** (D-2): la lectura íntegra del principio depende de que el rol alcance el skill. Patrón vigente, limitación ya aceptada.
- **L-3 — Deuda de la completitud de la tabla** (D-1): el upkeep es procedimiento; la garantía del producto es de **forma**, no de completitud. La alternativa O2 (CLI que lee la tabla) queda sobre la mesa con su coste declarado (acoplar el producto a un formato de documento).
- **L-4 — Deuda de la verificación del `reference`** (DEC-7): el CLI no lo comprueba; la comprobación es del reviewer. El `file` sí se comprueba (existe en el proyecto).
- **L-5 — Deuda del exit gate de stage 5** (D-5): el gate no menciona `docs/systemPatterns.md` ⇒ la tabla tiene **un** escritor declarado (el orquestador) y el kind `scribe-systemPatterns` queda como capacidad latente; el procedimiento de la re-entry del scribe declara la reconciliación, pero el **gate** no la exige.
- **L-6 — Deuda del esquema del request** (D-6): `assets/packet-request.schema.json` declara `additionalProperties: false` y **no** incluye `agent` (añadido por 006-005) ⇒ el esquema ya no describe el request vigente. Esta feature **agrega** su propiedad (`current_decisions`) para no agravar la brecha; **no** corrige la de `agent` (fuera de alcance). El esquema no se valida en runtime (medido: ningún test lo valida) ⇒ la brecha es documental, no funcional.
- **D-1 a D-6 (numeración del discovery, conservada):** (D-1) el bloque estático no tiene dueño de las filas ⇒ completitud no garantizada mecánicamente; (D-2) el puntero a la referencia del principio no es resoluble en la ruta de paquete; (D-3) el estado de los ADR no es uniforme ⇒ la tabla no puede derivarse de los archivos; (D-4) no hay operación de CLI ni clase de transición para la aprobación de un ADR ⇒ el upkeep es procedimiento; (D-5) el exit gate de stage 5 y el procedimiento del scribe no mencionan `docs/systemPatterns.md`; (D-6) el paquete puede crecer sin tope ⇒ esta feature lo acota con un tope declarado y fail-closed (DEC-6).

## 11. Trazabilidad con el contrato de la épica

| Aceptación (plan §10, enmienda 003) | PD |
|---|---|
| 1. La plantilla del Memory Bank suma la sección «Decisiones vigentes»: una fila por ADR con archivo, estado (vigente u obsoleto, y cuál lo reemplaza), resumen en una línea y roles que deben consumirlo | PD-7, PD-11 |
| 2. El orquestador la mantiene: agrega la fila al aprobarse un ADR y marca el reemplazado como obsoleto. El paquete de cada rol lleva las filas vigentes que lo nombran | PD-2, PD-3, PD-5, PD-6, PD-8, PD-9 |
| 3. El reviewer revisa que la tabla coincida con los ADR del repo y que el cambio respete las decisiones vigentes de su rol | PD-8, PD-12 (E4) |
| 4. Una decisión que cambia la metodología no está terminada hasta que su regla está en el skill o el agente instalable; la fila guarda la referencia | PD-10, PD-11 |
| Aceptación: plantilla y referencias actualizadas (stage-5, re-entry, reviewer); un test de texto que fija la sección y las dos responsabilidades; `make validate` y la suite pasan | PD-7, PD-8, PD-9, PD-10, PD-13 |

| Aceptación (plan §12, enmienda 005) | PD |
|---|---|
| 1. ADR-034 registra el principio y su límite; lo redacta el architect y lo aprueba el dueño | PD-11 (el ADR entregado) + la aprobación, acto separado (INV-6) |
| 2. Fuente única instalable: el principio vive en un solo lugar del skill; los roles lo referencian | PD-10, INV-1, INV-12 |
| 3. Architect: considera alternativas generales y específicas en las decisiones relevantes y explica el criterio elegido | PD-10 |
| 4. Reviewer: evalúa consecuencias reales (duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento); la falta de una abstracción, por sí sola, no es un defecto | PD-8, PD-10 |
| Vehículo: se construye junto con 006-004, que lo distribuye como primera fila de «Decisiones vigentes» | PD-11 (ADR-034 es fila de la tabla sembrada) |
| Aceptación: ADR-034 aprobado; un test de texto fija la fuente única, la obligación del architect, el criterio del reviewer y el límite; `make validate` y la suite pasan | PD-10, PD-13 |

**Garantía propia de la feature** (no es un ítem de aceptación de la épica): la fila viaja **en** el paquete —no por el alcance de lectura— y **falla cerrado** cuando su forma, su rol, su estado o su cantidad no son admisibles ⇒ PD-1..PD-6, PD-13.

## 12. La siembra de este repo (Q3)

**Qué se siembra.** `docs/systemPatterns.md` gana la sección `## Decisiones vigentes` como **primer H2** (después de la introducción), con una tabla de una fila por decisión.

**La regla de siembra (declarada, con su evidencia).** Se siembra una fila por decisión **en vigor** (Accepted/Verified) y una por cada decisión **reemplazada** (marcada `obsoleto` con su reemplazo). **Los 8 ADR *Proposed* no son filas** (Q1: no gobiernan). Los roles de cada fila se declaran **al aprobarse el ADR** (Q2) y, en esta siembra, se derivan del **texto operativo** de cada ADR: los roles cuyo trabajo la decisión constrain hoy. Una decisión cuya regla es el propio ADR lleva la **referencia** = el propio ADR; una decisión cuya regla vive en el skill lleva la **referencia** = el archivo del skill.

**Filas sembradas (25 vigentes + 1 obsoleta = 26):**

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
1. **Los 8 ADR *Proposed*** (012, 016, 025, 026, 027, 028, 029, 030): no gobiernan trabajo alguno hasta su aprobación (Q1). Se listan en la nota de la tabla para que el conjunto sea auditable.
2. **Nada más**: las 24 decisiones en vigor tienen fila (24 + ADR-034 = 25 vigentes) y la única reemplazada tiene su fila obsoleta.

**La nota de la tabla.** La sección incluye, bajo la tabla, una nota breve que declara: (a) la lista de ADR excluidos y el motivo; (b) que el **estado de una fila lo declara quien mantiene la tabla** y no se re-deriva de los ADR (D-3); (c) que la **referencia** es el lugar donde vive la regla que la decisión implanta. Sin esa nota, el conjunto parecería completo por casualidad.

**Verificación de la siembra** (PD-11): un bloque de texto en `tests/validate-consistency.sh` comprueba la presencia de la sección, de la fila de ADR-034, de la nota de exclusiones, y que **cada** fila apunte a un archivo que **existe** en `docs/adr/`. El `ADR-034` se materializa aparte (documento del proyecto, U5) y lo aprueba el dueño.

Status: **BORRADOR — SIN APROBAR** (draft-001). La aprobación es un acto separado de la autoridad vigente.
===END spec.md===

===BEGIN plan.md===
# 006-004-active-decisions-table — PLAN (etapa 2, borrador draft-001)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (superficie vigente de 006-006: `draft-plan` + `plan-review` sobre un borrador no aprobado; DEC-12 de la spec).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §10 y §12 (sha256 `d6da11db…9809`, verificado en disco). Spec: la de esta carpeta (misma entrega). Decisiones de entrada: `docs/epics/epic-006-opencode-concurrency/execution.md`:399-415.
Insumo: `docs/specs/006-004-active-decisions-table/discovery.md`. Base medida: HEAD `a9cc7ab`.
Medición de partida: el bloque estático máximo ocupa **3031** bytes (`reviewer/plan-review`) con techo declarado de **12000** (`cdad_packet.py`:1063-1079) ⇒ holgura **8969**; el mínimo, **1309** (`scribe/memory`). El tope de filas por paquete es **32** (spec §2.4) y el conjunto vigente sembrado es de **25** filas.

## 1. Orden y dependencias

`U1 (el encargo: la fila, su forma y el tope) → U2 (la sección aditiva del render) → U3 (el principio: una casa y las dos obligaciones) → U4 (la tabla y su upkeep) → U5 (la siembra de este repo) → U6 (el recorrido de aceptación)`.

- **U1 → U2**: la sección del render ** consume** el campo que U1 define y valida; sin U1 no hay qué renderizar.
- **U2 → U3 → U4**: U3 fija **el texto de rol** (la casa del principio y el deber del reviewer); U4 fija **el documento del proyecto** (la sección de la plantilla, el upkeep de stage-5 y la reconciliación de la re-entry) y **consume** el texto de U3 (el deber del reviewer que U3 escribe es el mismo que U4 nombra en el recorrido). U3 precede a U4 porque U4 **reutiliza** el deber declarado en U3, no lo re-declara.
- **U5** depende de U3 y U4: siembra la tabla (que nombra ADR-034) y materializa el ADR-034 (que apunta a la casa del principio). **Precondición de U5**: la **aprobación** del ADR-034 por la autoridad vigente — la fila de una decisión que aún no está aprobada no puede ser `vigente`.
- **U6** depende de todo: es el recorrido real.
- **Ninguna unidad es `parallel` con otra**: U1 y U2 tocan el mismo archivo (`skills/cdad-cycle/scripts/cdad_packet.py`), y U3 y U4 se tocan (`sources/roles/reviewer.md`, `packets/roles/reviewer.md`); el paralelismo inseguro lo rechaza el CLI (`cdad_packet.py`:3503-3523, «unsafe parallelism»).
- Ninguna unidad empieza sin su RED declarado y sin la revisión de spec/plan hecha.

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | **El encargo: la fila declarada, su forma y el tope.** `request.current_decisions` (opcional, aditivo), la validación de la forma de la fila (conjunto cerrado, `file` existente, `state` de vocabulario cerrado, `summary` de una línea, `roles` de vocabulario cerrado, `superseded_by` condicional), la regla «la fila nombra al rol del paquete», la regla «sólo lo vigente viaja», el **tope de 32** fail-closed, la bandera `--current-decision` y la propiedad del esquema | — | PD-1, PD-2, PD-3, PD-4, PD-6 | RED + focales GREEN + regresiones de contrato/packets (A-1) + `make validate` |
| **U2** | **La sección aditiva del render:** `## Current decisions` se emite **sólo** con filas, después de `## Contract`, con una entrada por fila en el orden declarado; sin filas el render es **byte-idéntico** (intra-revisión). La invocación de `prepare` con la bandera, declarada en la plantilla de handoff | U1 | PD-5, PD-6, PD-13 | RED + focales GREEN + regresiones de render (A-1) + `make validate` |
| **U3** | **El principio: una casa y las dos obligaciones.** `references/design-principles.md` (nuevo) con el principio y su límite; la fila en la tabla de referencias de `SKILL.md`; la **obligación del architect** y el **criterio del reviewer** (con el límite «la falta de abstracción no es defecto») en la fuente de cada rol y en su bloque estático; el **deber del reviewer sobre la tabla** con su procedimiento en `references/stage-4-review.md`; el test de texto | U2 | PD-8, PD-10, PD-13 | RED de texto + regresiones de generación/paquetes (A-1) + `make staging` determinista + `make validate` |
| **U4** | **La tabla y su upkeep:** la sección en la plantilla del Memory Bank; el **upkeep del orquestador** en `references/stage-5-merge.md` (sin tocar el exit gate); la **reconciliación por CAS** en `references/re-entry.md`; el test de texto | U3 | PD-7, PD-8, PD-9, PD-13 | RED de texto + regresiones de la skill (A-1) + `make validate` |
| **U5** | **La siembra de este repo** (no es unidad de código): `docs/systemPatterns.md` con la sección `## Decisiones vigentes` y sus 26 filas, y `docs/adr/ADR-034-principio-general-antes-especifico.md`. **Documentos del proyecto: los materializa el orquestador** (ADR-003; `sources/roles/orchestrator.md`:106-112) | U3, U4 | PD-11 | texto de la tabla verificado por el bloque de `tests/validate-consistency.sh`; ADR-034 aprobado por la autoridad vigente |
| **U6** | **El recorrido de aceptación** (no es unidad de código): E1..E6 sobre un proyecto **descartable** | U1–U5 | PD-12, PD-9, PD-13 | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1 — El encargo: la fila declarada, su forma y el tope

- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_packet.py`, **cuatro** zonas:
    1. el **conjunto cerrado del request** (`optional = {"plan_task", "agent"}`, `:870`) extendido **de forma aditiva** con `current_decisions` — la clausura **no** se relaja: cualquier otra clave desconocida sigue rechazándose;
    2. la **validación de la forma de la fila** y las reglas de admisión (conjunto cerrado de claves; `file` existe en el proyecto; `state` ∈ {`vigente`,`obsoleto`}; `summary` de una línea; `roles` no vacío y dentro del vocabulario cerrado de seis —los cinco roles delegados más `orchestrator`—; `superseded_by` exigido si `state == "obsoleto"` y prohibido si `state == "vigente"`); la regla «**toda fila declarada nombra al rol del paquete**»; la regla «**una fila `obsoleto` no es admisible en un paquete**»; el **tope de 32** fail-closed;
    3. `prepare` (`:4778`): la bandera **repetible** `--current-decision` (`:6730` y vicinity, junto a `--input`/`--invariant`), el parseo JSON de cada valor y la construcción de `request["current_decisions"]` **en el orden declarado** (junto a `:5016`, donde se declara `plan_task`);
    4. `skills/cdad-cycle/assets/packet-request.schema.json`: la propiedad opcional `current_decisions` (el esquema queda veraz; la brecha preexistente de `agent` **no** se corrige — spec L-6).
- **RED:** `tests/test_006_004_u1_decisions_field.py` (nuevo) —
  - **PD-1**: la forma buena es aceptada; clave desconocida ⇒ rc≠0 nombrando la clave; `state` fuera del vocabulario ⇒ rc≠0 nombrando el valor; `superseded_by` ausente con `obsoleto` ⇒ rc≠0; `superseded_by` presente con `vigente` ⇒ rc≠0; `file` inexistente ⇒ rc≠0 nombrando la ruta; `roles` vacío ⇒ rc≠0; rol fuera del vocabulario ⇒ rc≠0; `summary` con salto de línea ⇒ rc≠0. En cada negativo: **sin publicación** (out-dir vacío, state byte-idéntico — el control de `tests/test_004_003_t4_validation_fields.py`:399-423).
  - **PD-2**: la fila que nombra al rol ⇒ admitida; la que no lo nombra ⇒ rc≠0 **nombrando la fila y el rol**; la que nombra a otro roldelegado ⇒ rc≠0 por la misma regla.
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

### U4 — La tabla y su upkeep

- **Archivos:**
  - `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`: la sección **`## Current decisions`** como **primer H2** después de la introducción, con la **forma de la fila** (archivo, estado, resumen de una línea, roles, referencia) y la nota que declara las exclusiones y que el estado lo declara quien mantiene la tabla. (El bootstrap la instala sin cambios: `references/bootstrap.md`:66-83 copia la plantilla.)
  - `skills/cdad-cycle/references/stage-5-merge.md`: en §5.4 (la decisión sobre el ADR), el orquestador **agrega la fila** al aprobarse un ADR y **marca la anterior como obsoleta** conservándola, con su reemplazo. **El exit gate de stage 5 no cambia** (control negativo: el gate tiene las mismas casillas).
  - `skills/cdad-cycle/references/re-entry.md`: en §Scribe, la **reconciliación por CAS** de la tabla (dos escritores; el orquestador resuelve; un conflicto se **rechaza** y no sobrescribe).
  - `tests/validate-consistency.sh`: el bloque de texto de la plantilla y de las dos referencias.
- **RED:** `tests/test_006_004_u4_decisions_table.py` (nuevo) + el bloque bash —
  - **PD-7**: la plantilla contiene la sección; la sección está en el lugar declarado (primer H2 tras la introducción); **control negativo**: el exit gate de `references/stage-5-merge.md` **no** ganó casillas.
  - **PD-8**: `references/stage-5-merge.md` nombra el upkeep (agregar la fila al aprobar un ADR; marcar la anterior como obsoleta) y `references/re-entry.md` nombra la reconciliación.
  - **PD-9**: el texto de la re-entry declara el comportamiento ante conflicto (rechazo por CAS, no sobrescritura) y que la fila del orquestador manda.
  - **PD-11** (la parte verificable sin materializar): el bloque bash comprueba, sobre `docs/systemPatterns.md`, que la sección existe, que la fila de ADR-034 existe, que la nota de exclusiones existe, y que **cada** fila apunta a un archivo que **existe** en `docs/adr/`. (La tabla en sí la materializa el orquestador en U5.)
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_005_006_t5_acceptance.py` (el bootstrap instala los archivos del Memory Bank), `tests/test_004_002_t1_policy.py` (la clase `documentation`), `tests/test_003_002_t2_reviewfix.py` (los kinds del scribe → sus archivos), `tests/test_006_005_u7_scribe_role_report.py` (el kind `scribe-systemPatterns` → `docs/systemPatterns.md` con CAS), `tests/test_role_packets.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED de texto verde; regresiones verdes; `make validate`.

### U5 — La siembra de este repo (no es unidad de código)

- **Qué produce:** dos **documentos del proyecto**, materializados por el **orquestador** (ADR-003; `sources/roles/orchestrator.md`:106-112 — puede escribir `docs/**` y hacer `git add docs/**` + `git commit` con prefijo `docs(memory):`), **no** por el implementer (su alcance de escritura es el producto):
  1. `docs/systemPatterns.md`: la sección `## Decisiones vigentes` como **primer H2**, con las **26 filas** de la spec §12 (25 vigentes + 1 obsoleta), la nota de exclusiones (los 8 *Proposed*) y la nota de que el estado lo declara quien mantiene la tabla.
  2. `docs/adr/ADR-034-principio-general-antes-especifico.md`: el ADR redactado por el architect (texto en la entrega de esta sesión), con `**Status**: Proposed` hasta su aprobación.
- **Precondición:** la **aprobación** del ADR-034 por la autoridad vigente (el orquestador bajo la HITL delegada; el dueño puede vetarla) — una decisión no aprobada no se siembra como `vigente`.
- **Verificación:** el bloque de texto de U4 (presencia de la sección, de la fila de ADR-034, de la nota de exclusiones y **existencia del archivo de cada fila**) + el texto del ADR (que apunta a la fuente única y **no** re-enuncia el principio).
- **Commits:** el orquestador materializa y commitea con el prefijo `docs(memory):` (el canal que ya usa el Memory Bank), **después** de la aprobación del usuario de los borradores (ADR-006, `references/stage-5-merge.md`:53-68).
- **Owner:** orquestador (materialización) con la aprobación de la autoridad vigente.

### U6 — El recorrido de aceptación (no es unidad de código)

- **Escenario (PD-12, contra E1..E6 de §3.1 de la spec):** en un proyecto **descartable** (nunca el HOME, nunca el proyecto activo):
  - **(E1)** un ADR aprobado produce su fila en la tabla del proyecto; el siguiente paquete del rol nombrado **la lleva** dentro (`## Current decisions`), y el `REQUEST.json` la declara; un rol **no** nombrado no la lleva;
  - **(E2)** un ADR reemplazado deja la fila vieja **obsoleta** (con su reemplazo) en la tabla y **fuera** del paquete; al intentar declararla en un paquete, el CLI **rechaza** nombrando su sucesor;
  - **(E3)** el paquete de un rol sin filas aplicables es **byte-idéntico** al de hoy; el de un rol al que se le declara una fila ajena es **rechazado** nombrando la fila y el rol;
  - **(E4)** una fila que apunta a un ADR inexistente produce un **hallazgo** del reviewer con `file:line`, veredicto y condición de cierre (no una puerta);
  - **(E5)** un proyecto sin ADR: `prepare` rc=0, sin sección, render byte-idéntico;
  - **(E6)** la casa del principio **existe en el árbol instalado** y el paquete del architect y del reviewer la nombran;
  - **además (V-5)**: la corrida de dos fases (publicar con las fuentes anteriores → cambiar una fuente → recibir) produce el **rechazo** que nombra la diferencia con el render canónico, y la política declarada dice las dos salidas;
  - **además (V-6)**: el caso del **conflicto CAS** de la tabla (el orquestador escribe la fila; el scribe propone un `systemPatterns.md`; la materialización falla con el conflicto nombrado; el orquestador reconcilia y vuelve a materializar contra el digest actual).
- **Evidencia:** los paquetes y sus `REQUEST.json`, los rc, la comparación byte a byte del caso E3, el texto del hallazgo del caso E4, la salida real de la corrida de dos fases y la del conflicto CAS. Se entrega como **documento de evidencia** en la carpeta de la spec (no en `tests/`). Sin generalizar (spec §7).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (CLI no disponible, proyecto no inicializable, estado incoherente), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el owner/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo.

**Resultado de la evaluación: esta feature NO reemplaza ningún oráculo vigente.** Es la consecuencia de DEC-1 (el campo es **opcional** y el render es aditivo), DEC-2 (la forma de la fila es **nueva**: no había ninguna) y de INV-2 (sin el campo nuevo, el render no cambia).

| Superficie acoplada | Test | Evaluación |
|---|---|---|
| **El conjunto cerrado del request** | `tests/test_packet_prepare.py`, `tests/test_003_002_t1_receive.py` | **NO APLICA — el oráculo no cambia.** El conjunto se **extiende** con una propiedad declarada (`plan_task` y `agent` ya lo hicieron así: `cdad_packet.py`:870); la clausura no se relaja ⇒ los tests que comprueban que una clave desconocida se rechaza **siguen verdes sin cambio**. El RED de U1 **vuelve a comprobar** el caso (control negativo explícito): una clave cualquiera distinta de `current_decisions` sigue rechazándose. |
| **La forma de las secciones del paquete** | `tests/test_005_003_t6_packet_contract.py`:747; `tests/test_004_003_t1_reviewfix.py`:167-169 | **NO APLICA — la comprobación es por presencia, no por conjunto exhaustivo** ⇒ una sección nueva no los rompe. El RED de U2 lo **vuelve a comprobar** como control negativo. |
| **La composición del paquete y el bloque estático** | `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_static_block_ceiling.py` | **NO APLICA — el oráculo no cambia.** El bloque estático **crece** (dos líneas de deber en `packets/roles/architect.md` y `packets/roles/reviewer.md`, ~150-300 bytes cada uno) ⇒ el caso más cargado pasa de 3031 a ≈**3400** bytes, muy por debajo del techo de **12000** (V-4). El RED de U3 **mide** el bloque y lo registra; si superara el techo, el RED falla (y la respuesta **no** es subir el techo). |
| **Los digests de las fuentes de instrucción** | `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` se compone con la subfase pineada byte a byte) | **NO APLICA — ningún test fija un digest literal de una fuente de instrucción.** Medido: los 13出现 de 64 hexadecimales en `tests/*.py` son digests de **specs y artefactos**, no de `packets/`. El paquete se recomputa en cada corrida ⇒ sigue verde. |
| **Los agentes generados** | `tests/test_cdad_generate.py`, `tests/validate-consistency.sh`:138-142 | **NO APLICA — el oráculo no cambia; los agentes son salidas declaradas.** Las fuentes de rol cambian ⇒ `make agents` **regenera**; el validador comprueba que los agentes **contienen** lo que la fuente declara, no una versión anterior. El RED de U3 **vuelve a comprobar** la propagación y la **determinismo** de `make staging` (dos corridas, mismos bytes). |
| **La materialización del `systemPatterns.md` del scribe** | `tests/test_006_005_u7_scribe_role_report.py`:151, :181; `tests/test_003_002_t2_reviewfix.py`:723-779 | **NO APLICA — no se toca `cdad_result.py` ni `assets/artifact-policy.json`.** El kind `scribe-systemPatterns` → `docs/systemPatterns.md` con CAS ya existe; esta feature **no** añade ninguna comprobación nueva en `materialize`. El RED de U4 **no** modifica esos archivos: los **ejecuta**. |
| **El exit gate de stage 5** | derivación textual sobre `skills/cdad-cycle/references/stage-5-merge.md`:163-178 | **NO APLICA — el gate no cambia (Q6).** El RED de U4 lo comprueba como **control negativo**: el gate tiene las mismas casillas que antes de la feature. |
| **La subfase del reviewer** | `tests/test_005_007_t1_progressive_detail_rule.py`:295-307 | **NO APLICA — la subfase no se toca.** El deber del reviewer sobre la tabla vive en el **rol** (fuente + bloque estático) y en su **reference** canónica, no en la subfase ⇒ el oráculo del marcador `detail` sigue verde sin cambio. |
| **El esquema del request** | `assets/packet-request.schema.json` (documento, no validado en runtime: medido, ningún test lo valida) | **APLICA PARCIALMENTE — se **agrega** la propiedad `current_decisions` para que el documento sea veraz.** La brecha preexistente (`agent` ausente) **no** se corrige: es spec L-6, fuera de alcance. |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije que un request con una propiedad nueva debe rechazarse (es decir, que exija el conjunto cerrado *sin* `current_decisions`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva. Los REDs de U2, U3 y U4 declaran lo mismo respecto de la forma de las secciones, del bloque estático y de los agentes generados.

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED**: esta spec y este plan se revisan con la superficie vigente de 006-006 (`draft-plan` + `plan-review` sobre un borrador **no aprobado**), en sesión separada del autor; sus bloqueantes van al architect o se descartan con razón escrita por la autoridad que aprueba; y recién entonces viene el RED (DEC-12).
- **El ADR-034** lo aprueba la autoridad vigente (el orquestador bajo la HITL delegada; el dueño puede vetarla). **U5 no se ejecuta antes de esa aprobación** (una fila `vigente` exige una decisión aprobada).
- **La política de compatibilidad (L-1) queda declarada antes del recorrido**: el caso de dos fases (V-5) se ejecuta en U6 y su salida real se pega en la evidencia.
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature, salvo el deber añadido).
- El recorrido real de U6 queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan pasan por la revisión independiente, la aprobación es de la autoridad vigente, y el cierre materializa la tabla sembrada con el prefijo `docs(memory):`.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y fallando por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3 y U4; make staging determinista (dos corridas, mismos bytes) en U3. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). A-1: esta feature NO reemplaza ningun oraculo vigente (ver plan 4): el conjunto cerrado del request se EXTIENDE con una propiedad declarada (current_decisions) sin relajar la clausura; la forma de las secciones del paquete se comprueba por presencia, no por conjunto exhaustivo; ningun test fija un digest literal de una fuente de instruccion; el exit gate de stage 5 no cambia; la subfase del reviewer no se toca; los agentes son salidas declaradas y make agents los regenera. Los REDs anaden casos y vuelven a comprobar los controles negativos, no cambian oraculos. Aditividad: sin el campo nuevo el render es byte-identico DENTRO de una misma revision del producto; entre revisiones no se promete compatibilidad y la politica (terminarlo bajo la revision con la que se publico, o preparar uno nuevo) queda declarada, con su caso de dos fases en U6. Fila: conjunto cerrado de seis claves (file, state, summary, roles, reference, superseded_by condicional); file debe existir en el proyecto; state en {vigente, obsoleto}; roles de vocabulario cerrado (los cinco roles delegados mas orchestrator); summary de una linea; superseded_by exigido si state es obsoleto y prohibido si es vigente. Admision: toda fila declarada debe nombrar al rol del paquete; una fila obsoleto no es admisible en un paquete; el tope es 32 filas por paquete y falla cerrado nombrando el numero y el tope. La fila viaja en el request (opcional, aditivo) y el render emite la seccion Current decisions solo con filas. Principio: fuente unica en references/design-principles.md (el texto normativo aparece en un solo archivo del arbol instalable); las obligaciones del architect y del reviewer viven en la fuente de cada rol y en su bloque estatico, y apuntan al dueno canonico sin copiarlo; el limite (la falta de una abstraccion no es defecto) queda escrito y verificado por test de texto. Upkeep: el orquestador agrega la fila al aprobarse un ADR y marca la anterior como obsoleta; el exit gate de stage 5 NO cambia; la re-entry del scribe reconcilia por CAS y no sobrescribe. Siembra: docs/systemPatterns.md gana la seccion Decisiones vigentes (primer H2) con 25 filas vigentes y 1 obsoleta, la nota de exclusiones (los 8 ADR Proposed) y la nota de que el estado lo declara quien mantiene la tabla; cada fila apunta a un archivo que existe en docs/adr/. ADR-034: lo redacta el architect y lo aprueba la autoridad vigente; no re-enuncia el texto del principio, lo referencia. Recorrido de aceptacion (U6) en un proyecto descartable: E1..E6 con evidencia real; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con motivo y evidencia del intento, sin corrida simulada.",
  "tasks": [
    {
      "id": "U1",
      "objective": "El encargo: la fila declarada, su forma y el tope. request.current_decisions como propiedad opcional aditiva (la clausura del conjunto de campos NO se relaja); validacion de la forma de la fila con conjunto cerrado de seis claves (file, state, summary, roles, reference y superseded_by condicional: exigido si state es obsoleto, prohibido si es vigente); file debe existir en el proyecto; state de vocabulario cerrado {vigente, obsoleto}; summary de una linea; roles no vacio y dentro del vocabulario cerrado (los cinco roles delegados mas orchestrator); la regla de que toda fila declarada nombra al rol del paquete (fail-closed, nombrando la fila y el rol); la regla de que una fila obsoleto no es admisible en un paquete; el tope de 32 filas por paquete (fail-closed, nombrando el numero y el tope); la bandera repetible --current-decision que parsea JSON y conserva el orden declarado; y la propiedad opcional del esquema del request.",
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
      "objective": "El principio: una casa y las dos obligaciones. El archivo nuevo skills/cdad-cycle/references/design-principles.md lleva el texto del principio y su limite (el principio mejora el juicio de diseno; no aumenta las justificaciones que los agentes deben producir) y es su unica casa; SKILL.md gana la fila que dice cuando cargarlo; la fuente del architect y la del reviewer declaran su obligacion (una linea) y apuntan al dueno canonico sin copiar el texto; el bloque estatico de cada rol lleva la obligacion minima y el puntero, porque en la ruta de paquete el rol no carga el skill; el criterio del reviewer nombra las cuatro consecuencias reales y el limite (la falta de una abstraccion, por si sola, no es un defecto); references/stage-4-review.md, dueno canonico, recibe el procedimiento del deber del reviewer sobre la tabla (alinear con docs/adr/ y el respeto de las decisiones vigentes de su rol); los agentes generados se regeneran con make agents; y el test de texto fija la fuente unica, las dos obligaciones y el limite.",
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
      "objective": "La tabla y su upkeep. La plantilla del Memory Bank gana la seccion Current decisions como primer H2 tras la introduccion, con la forma de la fila (archivo, estado, resumen de una linea, roles, referencia) y la nota que declara las exclusiones y que el estado lo declara quien mantiene la tabla; el bootstrap la instala sin cambios. references/stage-5-merge.md declara, en la decision sobre el ADR, que el orquestador agrega la fila al aprobarse un ADR y marca la anterior como obsoleta conservandola con su reemplazo, SIN tocar el exit gate de stage 5. references/re-entry.md declara, en la re-entry del scribe, la reconciliacion por CAS de la tabla: hay dos escritores, el orquestador resuelve, y un conflicto se rechaza sin sobrescribir. El test de texto fija la seccion, las dos responsabilidades y la ausencia de casillas nuevas en el exit gate.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U3"
      ],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md",
        "skills/cdad-cycle/references/stage-5-merge.md",
        "skills/cdad-cycle/references/re-entry.md"
      ],
      "focal_tests": [
        "tests/test_006_004_u4_decisions_table.py"
      ],
      "observable_checks": [
        "la plantilla contiene la seccion y esta en el lugar declarado (PD-7)",
        "control negativo: el exit gate de stage 5 no ganho casillas (PD-7, PD-8)",
        "stage-5-merge.md nombra el upkeep (agregar la fila al aprobar un ADR; marcar la anterior como obsoleta) y re-entry.md nombra la reconciliacion por CAS (PD-8, PD-9)",
        "el texto de la re-entry declara que un conflicto se rechaza y no sobrescribe, y que la fila del orquestador manda (PD-9)",
        "sobre docs/systemPatterns.md: la seccion existe, la fila de ADR-034 existe, la nota de exclusiones existe y cada fila apunta a un archivo que existe en docs/adr/ (PD-11)"
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
      "objective": "La siembra de este repo: el orquestador materializa dos documentos del proyecto (docs/systemPatterns.md con la seccion Decisiones vigentes como primer H2, sus 26 filas -25 vigentes y 1 obsoleta-, la nota de exclusiones de los 8 ADR Proposed y la nota de que el estado lo declara quien mantiene la tabla; y docs/adr/ADR-034-principio-general-antes-especifico.md con Status Proposed hasta su aprobacion). Precondicion: la aprobacion del ADR-034 por la autoridad vigente, porque una fila vigente exige una decision aprobada. Verificacion: el bloque de texto de U4 (presencia de la seccion, de la fila de ADR-034, de la nota de exclusiones y existencia del archivo de cada fila) y el texto del ADR, que apunta a la fuente unica sin re-enunciar el principio. Materializacion y commit por el orquestador con el prefijo docs(memory): tras la aprobacion del usuario de los borradores.",
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
        "docs/systemPatterns.md tiene la seccion Decisiones vigentes como primer H2, con 25 filas vigentes y 1 obsoleta, y cada fila apunta a un archivo que existe en docs/adr/ (PD-11)",
        "la nota de exclusiones declara los 8 ADR Proposed y el motivo, y la nota sobre el estado declara que lo declara quien mantiene la tabla (PD-11, D-3)",
        "la fila de ADR-034 existe con state vigente, los roles architect y reviewer, y la referencia al archivo canonico del skill (PD-11)",
        "docs/adr/ADR-034-principio-general-antes-especifico.md existe, tiene Status Proposed hasta su aprobacion, apunta a la fuente unica y no re-enuncia el texto del principio (PD-11, INV-1)",
        "el commit de la materializacion lleva el prefijo docs(memory): y lo ejecuta el orquestador tras la aprobacion del usuario (ADR-006)"
      ],
      "regressions": [],
      "integration_gate": "materializacion por el orquestador con la aprobacion de la autoridad vigente; verificacion por el bloque de texto de tests/validate-consistency.sh",
      "owner": "orchestrator (materializacion); la autoridad vigente aprueba el ADR-034 y los borradores",
      "detail": "next"
    },
    {
      "id": "U6",
      "objective": "Recorrido de aceptacion en un proyecto descartable: un ADR aprobado produce su fila y el siguiente paquete del rol nombrado la lleva; un ADR reemplazado deja la fila vieja obsoleta en la tabla y fuera del paquete, y declararla en un paquete se rechaza nombrando su sucesor; un rol sin filas aplicables recibe un paquete byte-identico al de hoy y la declaracion de una fila ajena se rechaza nombrando la fila y el rol; una fila que apunta a un ADR inexistente produce un hallazgo del reviewer con file:line, veredicto y condicion de cierre, no una puerta; un proyecto sin ADR prepara con rc cero, sin seccion y con render byte-identico; la casa del principio existe en el arbol instalado y la nombran el paquete del architect y el del reviewer; y la corrida de dos fases (publicar con las fuentes anteriores, cambiar una fuente, recibir) produce el rechazo que nombra la diferencia con el render canonico, con la politica declarada que dice las dos salidas; y el caso del conflicto CAS de la tabla muestra el rechazo y la reconciliacion.",
      "produce": [],
      "consume": [],
      "depends_on": [
        "U1",
        "U2",
        "U3",
        "U4",
        "U5"
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
        "la salida real del conflicto CAS queda adjunta: el rc, el texto del conflicto y la reconciliacion posterior (V-6, PD-9)",
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

Status: **BORRADOR — SIN APROBAR** (draft-001). La aprobación es un acto separado de la autoridad vigente, y precede al RED de cualquier unidad.
===END plan.md===

===BEGIN adr-034.md===
# ADR-034: El principio de general antes que específico se materializa en un único archivo del skill instalable, y obliga al architect a explicar el criterio y al reviewer a evaluar consecuencias reales

- **Status**: Proposed (redactado por el architect el 2026-10-20; **a la espera de la aprobación** de la autoridad vigente —el orquestador bajo la HITL delegada del epic-006, con veto del dueño—)
- **Date**: 2026-10-20
- **Deciders**: Pablo (dueño: fijó el principio de general antes que específico en la enmienda 005 del plan del epic, 2026-10-18) + orquestador Claude (HITL delegada de epic-006: aprueba el ADR) + architect (redacción; **no aprueba**)
- **Confidence**: Alta
- **Aprobación**: *pendiente* — el owner puede vetarla. **Evidencia disponible para la decisión:** contrato `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005, sha256 `d6da11db…9809`) y §10 (enmienda 003); `docs/specs/006-004-active-decisions-table/discovery.md` §4.1-4.3; `docs/specs/006-004-active-decisions-table/spec.md` §2.6 y DEC-9/DEC-10; `plan.md` §3 U3.

## Contexto y problema

La enmienda 005 del plan del epic (aprobada por el dueño el 2026-10-18) fijó un principio de diseño para CDAD: *buscar la solución más simple que cubra los casos conocidos y los requisitos declarados; compartir lo que responde a la misma responsabilidad y conservar las diferencias que tengan una razón real; una solución general puede ser un contrato común con implementaciones distintas, no necesariamente código compartido; dos fragmentos parecidos no son por eso la misma responsabilidad; evaluar tanto el costo de especializar como el de generalizar, sin convertir particularidades accidentales en reglas generales ni introducir abstracciones que todavía no aportan utilidad.* Y agregó su **límite**: *el principio mejora el juicio de diseño; no aumenta las justificaciones que los agentes deben producir.*

El principio no era una observación: era **un cambio de contrato de rol**. Nombraba cuatro obligaciones (registro del principio y su límite, fuente única instalable, deber del architect, criterio del reviewer) y fijaba además dos límites de alcance: se aplica a las decisiones **que crean una frontera, duplican un mecanismo o comprometen la evolución** (no exige justificar cada elección), y **la falta de una abstracción, por sí sola, no es un defecto** para el reviewer.

El problema que el principio no resolvía por sí solo era **de distribución**. Un principio registrado en un ADR no gobierna el trabajo siguiente si ningún rol lo recibe: el rol no abre el `docs/adr/` del proyecto, y en la ruta de paquete **no carga el skill** (su contrato es el paquete). Un ADR sin regla instalada es una declaración; una regla sin regla instalada es una declaración sin efecto. De ahí la exigencia de la enmienda 005: **fuente única instalable**, con los roles **referenciándola**, y la regla de que *una decisión que cambia la metodología de CDAD no está terminada hasta que su regla está en el skill o el agente instalable* (enmienda 003, §10.4).

## Opciones consideradas

### Opción A: el principio vive en el ADR y los roles lo reciben por el paquete (ADOPTADA)

- El texto normativo del principio **y** de su límite viven en **un único archivo del skill instalable** (`skills/cdad-cycle/references/design-principles.md`), que es su casa. Este ADR **registra la decisión** y **apunta** a ese archivo; no lo re-enuncia.
- La **obligación del architect** («en las decisiones relevantes, considera las alternativas generales y específicas y explica el criterio elegido») y el **criterio del reviewer** («evalúa consecuencias reales: duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento; la falta de una abstracción, por sí sola, no es un defecto») se declaran como **deber** en la fuente de cada rol y en su bloque estático de paquete, con el **puntero** al archivo canónico.
- El **deber del reviewer sobre la tabla de decisiones** (alinear la tabla con `docs/adr/`; comprobar que el cambio respeta las decisiones vigentes de su rol) tiene su **procedimiento** en la referencia canónica del reviewer, con el mismo patrón de «dueño canónico único» que ya usa la calibración de la revisión.
- **Pros:** una sola casa del texto normativo, verificable mecánicamente (el texto aparece en un único archivo del árbol instalable); el deber de cada rol llega **completo** por las dos superficies que existen en las dos rutas (cuerpo del agente generado y bloque estático del paquete), incluso en la ruta de paquete donde el skill no se carga; el principio se **distribuye** con el mismo mecanismo que las decisiones vigentes (la tabla «Decisiones vigentes» y su sección en el paquete), de modo que la Feature 006-004 es su vehículo y no un añadido aparte; el límite del principio («no aumenta las justificaciones») queda **junto al principio**, y no puede separarse de él.
- **Contras:** el texto normativo y el deber de rol están en **archivos distintos** (el primero en una *reference*, el segundo en las fuentes de rol), lo que exige una regla explícita de no-copia y un test que la vigile; y la lectura íntegra del principio depende de que el rol alcance el skill en la ruta de paquete (limitación ya aceptida en el producto con el puntero vigente a la referencia de calibración).

### Opción B: el principio vive en el propio ADR y basta con que el rol lo reciba en el paquete

- **Pros:** cero archivos nuevos; el ADR es el lugar natural de una decisión.
- **Contras:** el ADR vive en el **proyecto**, no en el **skill instalable** ⇒ (i) el texto normativo **no viaja** a un proyecto que no tenga ese ADR, y CDAD necesita el principio en **todos** los proyectos, no en el que lo decidió; (ii) la ruta de paquete no puede resolver un puntero a un archivo del proyecto que el rol no tiene por qué leer; (iii) el principio quedaría duplicado en cada proyecto que lo adopte, con la divergencia que el propio principio condena. **Descartada.**

### Opción C: el principio en `SKILL.md` (el contrato mínimo siempre cargado)

- **Pros:** llega a todos los runtimes sin trabajo adicional; no depende de que nadie cargue una referencia.
- **Contras:** `SKILL.md` se carga **siempre**, en todos los roles y en todas las etapas ⇒ una regla de diseño para dos roles (architect y reviewer) **cargaría a todos** los que no la necesitan (test-writer, implementer, scribe), que es exactamente el error de «especializar al revés» y el que la enmienda 005 quiere evitar. Además rompe el patrón vigente del repo (un dueño canónico en `references/`, y los consumidores lo referencian sin copiarlo). **Descartada.**

### Opción D: el principio en la referencia de la revisión (`stage-4-review.md`)

- **Pros:** el archivo ya es el dueño canónico de la calibración del reviewer y ya se cita desde la fuente del rol.
- **Contras:** mezclaría **dos dueños** en un archivo (la calibración de la revisión y el principio general de diseño) ⇒ dos reglas que pueden evolucionar por separado, cada una影响的 a un conjunto distinto de roles, en el mismo sitio. Además el principio no es sólo del reviewer: el architect lo debe aplicar y el reviewer sólo lo evalúa. **Descartada.**

## Decisión

1. **El principio de general antes que específico y su límite tienen una casa única, instalable:** `skills/cdad-cycle/references/design-principles.md`. Ese archivo es la **única** casa del texto normativo; el árbol `skills/cdad-cycle/` viaja completo al entorno instalado, de modo que la regla está disponible sin que el proyecto tenga que后期的 de ella. **Este ADR no re-enuncia el texto del principio ni el de su límite** (la regla de una sola casa; el deber de rol es *duty*, no principio).
2. **El deber del architect** se declara en la fuente del architect y en su bloque estático de paquete, con el puntero al archivo canónico: *en las decisiones relevantes, considera las alternativas generales y específicas y explica el criterio elegido*; el principio y su límite **no** se re-enuncian allí.
3. **El deber del reviewer** se declara en la fuente del reviewer y en su bloque estático de paquete, con el puntero al archivo canónico: *evalúa consecuencias reales —duplicación que puede divergir, complejidad innecesaria, pérdida de capacidades y acoplamiento— y la falta de una abstracción, por sí sola, no es un defecto*. El **procedimiento** de su comprobación sobre la tabla de decisiones vigentes vive en su referencia canónica (dueño canónico, como la calibración).
4. **El límite del principio es parte del principio:** el archivo canónico lleva, junto al texto, el límite de que *el principio mejora el juicio de diseño; no aumenta las justificaciones que los agentes deben producir*. El principio **no** exige justificar cada elección: se aplica a las decisiones que crean una frontera, duplican un mecanismo o comprometen la evolución.
5. **El principio se distribuye por el mecanismo de las decisiones vigentes:** la feature 006-004 crea la sección «Decisiones vigentes» en la tabla del proyecto, y el paquete de cada rol lleva las filas vigentes que lo nombran. La fila de esta decisión es la **primera** de la tabla sembrada: nombra el archivo del skill como la referencia donde vive la regla.
6. **La decisión no está terminada hasta que su regla está en el árbol instalable.** La fila de la tabla declara la referencia; el reviewer comprueba que el archivo existe en la instalación y que el cambio respeta la decisión vigente de su rol. La fila de una decisión cuya regla todavía no está instalada **no** se declara vigente.

## Reasons

1. **Un principio que no llega a quien lo debe aplicar no gobierna nada.** El rol no abre el `docs/adr/` del proyecto; en la ruta de paquete no carga el skill. Un principio sin mecanismo de distribución es una declaración sin efecto, y el problema que la enmienda 003 enuncia —«un ADR registrado no gobierna el trabajo siguiente si ningún rol lo recibe»— se repetiría, con más autoridad, con el ADR de un principio.
2. **Una casa, comprobable.** El patrón de «dueño canónico único» ya es el del repo (la calibración de la revisión, el detalle progresivo, la política de evidencia): un archivo que dice cuándo se carga y al que los demás apuntan. La consecuencia útil es **mecánica**: el texto normativo aparece en **un único archivo** del árbol instalable, y eso se verifica con un `grep` sobre el árbol. Un principio repetido en tres sitios se puede comprobar leyendo tres sitios; uno repetido en tres sitios **se puede comprobar que no se repita**.
3. **El deber de rol es otra cosa que el principio, y por eso puede vivir en la fuente del rol.** «Considera las alternativas y explica el criterio» y «evalúa consecuencias reales» son **obligaciones**, no el principio: se pueden enunciar en una línea, se pueden comprobar por derivación textual y no necesitan el texto completo. Confundir ambas cosas es lo que produce la duplicación que el principio condena: si el deber fuera una copia del principio, habría dos principios.
4. **El límite evita el modo de fallo conocido de los principios.** Sin el límite explícito, un principio de diseño se convierte en un.producto de justifications: cada elección pasa a exigir una comparación de alternativas, el costo de la relación crece con el tamaño del proyecto y la calidad de la justificación baja. El límite —*no aumenta las justificaciones que los agentes deben producir*— es lo que mantiene el principio barato de obedecer. Y el límite del reviewer —*la falta de una abstracción, por sí sola, no es un defecto*— es lo que evita el otro extremo: convertir «prefiero lo general» en «todo debe estar abstraído», que produce acoplamiento por el otro lado.
5. **El vehículo es el mismo que el de las decisiones.** La feature 006-004 no necesita un canal nuevo para el principio: la tabla de decisiones vigentes y su sección en el paquete distribuyen **filas**, y esta decisión es una fila más. Un mecanismo de distribución por principio habría sido un segundo camino para el mismo problema, con la divergencia que la enmienda 005 quiere evitar.

## Consequences

- **Positivas.** El principio tiene una casa comprobable y un deber por rol que llega a los dos runtimes y por las dos rutas (cuerpo del agente generado y bloque estático del paquete); el límite queda escrito junto al principio y el límite del reviewer queda escrito donde el reviewer lo lee; la fila de esta decisión es la primera de la tabla sembrada, de modo que el mecanismo de distribución y el principio se eosinisten: la feature que crea la tabla es la que entrega el principio. La regla «no re-enunciar» es verificable con un `grep` sobre el árbol instalable, de modo que la duplicación futura es un fallo detectable y no una degradación silenciosa.
- **Negativas / límites declarados.** (a) El texto normativo y el deber de rol están en archivos distintos ⇒ hace falta una regla de no-copia **explícita** y un test que la vigile; sin ese test, la separación se degrada en duplicación. (b) En la **ruta de paquete** el rol **no carga el skill** ⇒ un puntero al archivo canónico **no es resoluble** por el rol: recibe el **deber completo** y la **dirección** a seguir, no la lectura íntegra del principio. Es la **misma** limitación que ya acepta el puntero vigente a la referencia de calibración, no un defecto nuevo. (c) El **texto normativo está en inglés** (el árbol del skill está en inglés) mientras que la decisión del dueño está escrita en español: el ADR traduce el sentido, pero **no** es la fuente ⇒ una divergencia de traducción sería un defecto de la traducción, no una segunda fuente. (d) La fila de esta decisión **no puede** ser `vigente` hasta que la regla esté en el árbol instalable ⇒ hay un orden real (el archivo primero, la fila después) que el gate de la tabla debe respetar.
- **No cambia.** El modelo de la revisión y su calibración (`references/stage-4-review.md`), los nombres de los roles y sus artefactos, la tabla cerrada de destinos, la tabla de tipos de artefacto, el exit gate de stage 5, el estado de la máquina de estados y el vocabulario de estado de los ADR: nada de eso se modifica con este ADR. El principio **tampoco** crea un mecanismo de aprobación nuevo ni un gate: su efecto es de criterio, y suSkip se verifica por derivación textual y por el comportamiento del reviewer.

## Notas

- **Contrato normativo:** `docs/epics/epic-006-opencode-concurrency/plan.md` §12 (enmienda 005 — el principio y su límite, y las cuatro obligaciones) y §10 (enmienda 003 — la tabla de decisiones vigentes y la regla de que la fila guarda la referencia; fuera de alcance: índices generados, gates de cita obligatoria y cambios en `status`).
- **Código y documentos de producto:** `skills/cdad-cycle/references/design-principles.md` (**nuevo** — la casa del principio y de su límite), `skills/cdad-cycle/references/stage-4-review.md` (el procedimiento del deber del reviewer sobre la tabla), `skills/cdad-cycle/SKILL.md` (la tabla de referencias), `sources/roles/architect.md`, `sources/roles/reviewer.md` (las obligaciones), `skills/cdad-cycle/packets/roles/architect.md`, `skills/cdad-cycle/packets/roles/reviewer.md` (las obligaciones en la ruta de paquete) y los agentes generados por `scripts/cdad-generate.py`.
- **Distribución (el vehículo):** `docs/specs/006-004-active-decisions-table/spec.md` §2.5-2.6 y §12 (la tabla sembrada, con esta decisión como fila) y `plan.md` §3 U3 (la casa y las obligaciones), U4 (la tabla y su upkeep) y U5 (la siembra de este repo, que materializa este ADR como `docs/adr/ADR-034-principio-general-antes-especifico.md`).
- **Numeración:** **ADR-034** (este). El número lo consume el artefacto que se materializa primero; `plan.md` §12 lo tenía reservado como «ADR-033» hasta que ADR-033 lo tomó la decisión de modelos (nota de ADR-033: «pasa a ADR-034 porque el número lo consume el artefacto que se materializa primero»).
- **Límites honestos de este registro:** el principio es un **criterio de diseño**, no un mecanismo verificable: el producto no puede comprobar que un architect haya considerado la alternativa general, ni que un reviewer haya evaluado las cuatro consecuencias. Lo que sí es verificable es **la existencia y la unicidad de la casa**, **la presencia de los dos deberes** y **la presencia del límite** (deriva textual y `grep` sobre el árbol instalable), y el efecto real del criterio se observa en las revisiones, no en un test. La **aprobación** de este ADR es un acto **posterior y separado** de esta redacción, y la fila de la tabla que lo nombra no se declara vigente antes de esa aprobación.

Status: **Proposed** — a la espera de la aprobación de la autoridad vigente.
===END adr-034.md===

---

# Informe de rol — architect, borrador de spec y plan de `006-004-active-decisions-table`

**Paquete:** `006-004-active-decisions-table-architect-draft-001` · **Contrato:** `approved-epic-plan` → `docs/epics/epic-006-opencode-concurrency/plan.md` §10 y §12 (sha256 `d6da11db…9809`, **recalculado en disco** y coincidente con el del paquete).
**Modo:** solo lectura. **Archivos modificados por esta sesión: ninguno.** No hay commit propio (el rol no escribe; ADR-003).
**Entrega:** texto final de tres documentos delimitados con marcadores literales: `spec.md`, `plan.md`, `adr-034.md`. El orquestador los materializa en `docs/specs/006-004-active-decisions-table/`.

**Fuentes leídas:** `docs/epics/epic-006-opencode-concurrency/plan.md` (§10, §12), `execution.md`:399-415, `docs/specs/006-004-active-decisions-table/discovery.md`, `docs/specs/006-006-spec-plan-review/{spec,plan}.md` (forma de referencia), `skills/cdad-cycle/scripts/cdad_packet.py` (`:63`, `:71`, `:82`, `:846-905`, `:1030`, `:1050-1121`, `:1238-1248`, `:3796-3853`, `:4778-5054`, `:6692-6760`), `cdad_result.py` (`:92-95`, `:690-712`, `:737-739`, `:745-757`, `:841-847`), `sources/roles/{architect,reviewer,orchestrator}.md`, `agents/cdad-orchestrator.md`, `skills/cdad-cycle/packets/{common,roles/*,substages/*}.md`, `skills/cdad-cycle/references/{stage-2-specification,stage-4-review,stage-5-merge,re-entry,bootstrap,handoff-prompts}.md`, `skills/cdad-cycle/assets/{memory-bank-templates/systemPatterns.md,memory-bank-templates/adr-README.md,adr-template/ADR.md,artifact-policy.json,packet-request.schema.json}`, `skills/cdad-cycle/SKILL.md` (tabla de referencias), `scripts/cdad-generate.py`, `tests/validate-consistency.sh`, `tests/test_role_packet_render.py`, `tests/test_static_block_ceiling.py`, `tests/test_006_006_u1_draft_object_form.py`, `docs/adr/ADR-001…033` (33 archivos), `docs/systemPatterns.md` (885 líneas), `Makefile`, `install.sh`:355-385.

**Verificaciones medidas en esta sesión (no copiadas del discovery, que se escribió antes de que 006-006 fuera construido):**

```
### M1 — la sección no existe en ninguna superficie del producto
$ grep -rn "Decisiones vigentes\|Current decisions" skills/ sources/ agents/ tests/ install.sh | wc -l
0
### M2 — ADR del repo
$ ls docs/adr/ADR-*.md | wc -l
33
### M3 — bloque estático por par rol/subfase (ceiling 12000)
  max 3031  reviewer/plan-review   headroom 8969
  min 1309  scribe/memory            headroom 10691
### M4 — conjunto cerrado del request
$ grep -n 'optional = ' skills/cdad-cycle/scripts/cdad_packet.py
870:    optional = {"plan_task", "agent"}
### M5 — el esquema del request ya no describe el request vigente
$ grep -c '"agent"' skills/cdad-cycle/assets/packet-request.schema.json
0        (la propiedad existe en el request, no en el esquema; ningún test valida el esquema)
### M6 — contrato recalculado en disco
$ sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809   (coincide con el paquete)
### M7 — «orchestrator» es un rol del producto (fuente + agente generado), no un rol despachado por paquete
$ ls agents/cdad-orchestrator.md sources/roles/orchestrator.md
agents/cdad-orchestrator.md   sources/roles/orchestrator.md
### M8 — ningún test fija un digest literal de una fuente de instrucción
$ grep -rnE "[0-9a-f]{64}" tests/*.py | grep -v "sha256(" | wc -l
13      (los 13 son digests de specs y artefactos, no de packets/)
### M9 — roles delegados nombrados por cada ADR (prosa, 5 roles)
sin ninguno de los 5: ADR-002, 004, 012, 016, 018, 021, 023  (7)
  de ellos en vigor: 002, 004, 018, 021, 023  (5) — gobiernan al orquestador
### M10 — estado del repo al cierre
$ git status --short
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-and-reproducible-*.md   (2 findings no trackeados)
$ git log --oneline -1
a9cc7ab docs(state): 006-004 draft spec/plan preparado
```

> Las tres entradas no versionadas y la modificación del state **preexistían** a esta sesión (las dejó la preparación del paquete: commit `1880824`); esta sesión no las tocó.

**Comandos ejecutados (solo lectura):**

```bash
git log --oneline -5 && git status --short
sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
sed -n '1,352p'  docs/epics/epic-006-opencode-concurrency/plan.md
sed -n '395,415p' docs/epics/epic-006-opencode-concurrency/execution.md
sed -n '1,427p'  docs/specs/006-004-active-decisions-table/discovery.md
sed -n '1,346p'  docs/specs/006-006-spec-plan-review/spec.md
sed -n '1,391p'  docs/specs/006-006-spec-plan-review/plan.md
grep -n "optional = \|^def validate_request\|^def render_packet\|^def prepare\|^def _plan_task_sections\|^def _default_scopes\|OBJECT_FORM_CONTRACT_KEYS = \|^ROLE_SUBSTAGES = \|SCOPE_CLASSES = " skills/cdad-cycle/scripts/cdad_packet.py
sed -n '840,905p;1046,1125p;1238,1250p;3796,3853p;4960,5060p;6690,6760p' skills/cdad-cycle/scripts/cdad_packet.py
cat -n skills/cdad-cycle/packets/{common.md,roles/architect.md,roles/reviewer.md,substages/architect-draft.md}
cat -n skills/cdad-cycle/assets/memory-bank-templates/{systemPatterns.md,adr-README.md}
cat -n skills/cdad-cycle/assets/adr-template/ADR.md
cat -n skills/cdad-cycle/assets/{artifact-policy.json,packet-request.schema.json}
cat -n sources/roles/{architect,reviewer}.md
sed -n '1,60p' skills/cdad-cycle/references/stage-4-review.md
sed -n '1,120p' skills/cdad-cycle/references/stage-2-specification.md
sed -n '1,90p;155,200p' skills/cdad-cycle/references/stage-5-merge.md
sed -n '55,95p' skills/cdad-cycle/references/bootstrap.md
sed -n '1,100p;479,620p' skills/cdad-cycle/references/handoff-prompts.md
sed -n '125,200p;268,320p' skills/cdad-cycle/references/re-entry.md
sed -n '450,475p' skills/cdad-cycle/SKILL.md
sed -n '55,120p' scripts/cdad-generate.py
sed -n '1,100p;100,200p' tests/validate-consistency.sh
sed -n '1,80p' tests/test_role_packet_render.py
cat -n tests/test_static_block_ceiling.py
sed -n '1,50p' tests/test_006_006_u1_draft_object_form.py
sed -n '1,50p' skills/cdad-cycle/assets/spec-template/spec.md
python3 - <<'PY'   # bloque estático por par rol/subfase vs. techo 12000
python3 - <<'PY'   # inventario de estados y roles por ADR (33)
grep -rnE "[0-9a-f]{64}" tests/*.py | grep -v "sha256(" | wc -l
grep -rn "Decisiones vigentes\|Current decisions" skills/ sources/ agents/ tests/ install.sh | wc -l
ls docs/adr/ADR-*.md | wc -l ; ls docs/adr/README.md
sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
```

**Decisiones que el orquestador ya había cerrado y que esta spec respeta sin re-discutirlas:** O1 (campo opcional + sección aditiva), Q1 (filas de lo en vigor y de lo reemplazado; los *Proposed* no son filas), Q2 (los roles los declara quien aprueba el ADR; el reviewer verifica que existan, no que sean los correctos), Q3 (siembra con ADR-034 primero y las decisiones en vigor justificables con evidencia, declarando las exclusiones), Q4 (sin cambios en `status`: ni el de los ADR ni el de la máquina de estados), Q5 (título libre; `## Current decisions` en la plantilla, `## Decisiones vigentes` en este repo, primer H2), Q6 (el orquestador mantiene la tabla al aprobarse un ADR; el exit gate de stage 5 no cambia), tope de filas fail-closed (valor 32 propuesto en §2.4) y ADR-034 como fuente única del principio.

**Lo que esta spec añade por decisión propia, y conviene que la autoridad que apruebe lo mire:** (a) el vocabulario de consumidores de una fila **incluye `orchestrator`** — sin él, las 5 decisiones en vigor que gobiernan al orquestador (002, 004, 018, 021, 023) no podrían tener fila y el índice quedaría incompleto por construcción (DEC-5); (b) el tope es **32** con su justificación medida (§2.4); (c) el estado «obsoleto» **no viaja** en el paquete (R-6), lo que hace verificable la regla del plan; (d) **ADR-008** se siembra como `vigente` y no `obsoleto`, porque su reemplazo es **parcial** y nadie ha declarado un reemplazo total (DEC-4); (e) el deber del reviewer sobre la tabla tiene su **procedimiento** en `references/stage-4-review.md` (dueño canónico) y la **obligación mínima** en la fuente del rol y en su bloque estático, porque en la ruta de paquete el rol no carga el skill (DEC-10, D-2).

**Dudas acotadas que quedan para la autoridad que aprueba (no bloquean el RED):** (1) el ADR-034 se entrega con `**Status**: Proposed` y su aprobación queda como acto separado — la U5 del plan **no** puede ejecutarse antes de esa aprobación; (2) la fila de ADR-010 se siembra `vigente` con su alcance acotado y su regla de vencimiento declarados en el `summary`, y la de ADR-001/ADR-005 `vigente` con la nota de que su contenido operativo no tiene efecto desde ADR-033 y su retiro formal es decisión del dueño — si la autoridad prefiere que esas tres queden **fuera** de la tabla, es un cambio de la fila, no del mecanismo (y se declara en la nota de exclusiones).

**Commit:** **ninguno** — el rol architect es read-only y no escribe (ADR-003; `sources/roles/architect.md`:38-43). El artefacto de esta sesión es el texto final de los tres documentos, que el orquestador materializa y registra como entrega.