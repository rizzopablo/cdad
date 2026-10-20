# 006-004-active-decisions-table — PLAN (etapa 2, borrador draft-004)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (superficie vigente de 006-006: `draft-plan` + `plan-review` sobre un borrador no aprobado; DEC-12 de la spec).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §10 y §12 (sha256 `d6da11db…9809`, verificado en disco). Spec: la de esta carpeta (misma entrega). Decisiones de entrada: `docs/epics/epic-006-opencode-concurrency/execution.md`:399-415.
Decisiones de entrada de esta revisión (orquestador, 2026-10-20): la **regla general del CAS por digest base** (spec DEC-13) y la **separación de las comprobaciones de siembra** (spec DEC-14), que introduce **U7**.
Dictamen aplicado: `docs/specs/006-004-active-decisions-table/plan-review-001.md` (2 BLOCKING · 2 OPTIONAL) — los cuatro hallazgos están corregidos (§7) — y `docs/specs/006-004-active-decisions-table/plan-review-002.md` (1 BLOCKING · 1 OPTIONAL), corregidos en la revisión 3 (§8), y `docs/specs/006-004-active-decisions-table/plan-review-003.md` (1 BLOCKING · 0 OPTIONAL nuevos), corregido en esta revisión (§9).
Insumo: `docs/specs/006-004-active-decisions-table/discovery.md`. Base medida: HEAD `a9cc7ab`. La revisión 4 (§9) **no cambia ninguna medición** (es una corrección del contrato del validador, no del producto); HEAD observado en esta revisión: `7122769`.
Medición de partida: el bloque estático máximo ocupa **3031** bytes (`reviewer/plan-review`) con techo declarado de **12000** (`cdad_packet.py`:1063-1079) ⇒ holgura **8969**; el mínimo, **1309** (`scribe/memory`). El tope de filas por paquete es **32** (spec §2.4) y el conjunto vigente sembrado es de **25** filas.

## 1. Orden y dependencias

`U1 (el encargo: la fila, su forma y el tope) → U2 (la sección aditiva del render) → U3 (el principio: una casa y las dos obligaciones) → U4 (la tabla y su upkeep: plantilla y procedimiento) → U5 (la siembra: materialización de los documentos del proyecto) → U7 (la verificación de la siembra) → U6 (el recorrido de aceptación)`.

- **U1 → U2**: la sección del render **consume** el campo que U1 define y valida; sin U1 no hay qué renderizar.
- **U2 → U3 → U4**: U3 fija **el texto de rol** (la casa del principio y el deber del reviewer); U4 fija **el documento del proyecto** (la sección de la plantilla, el upkeep de stage-5 y la reconciliación de la re-entry) y **consume** el texto de U3 (el deber del reviewer que U3 escribe es el mismo que U4 nombra en el recorrido). U3 precede a U4 porque U4 **reutiliza** el deber declarado en U3, no lo re-declara.
- **U5** depende de U3 y U4: siembra la tabla (que nombra ADR-034) y materializa el ADR-034 (que apunta a la casa del principio). **Precondición de U5**: la **aprobación** del ADR-034 por la autoridad vigente — la fila de una decisión que aún no está aprobada no puede ser `vigente`. **El gate de U5 es la materialización misma más la aprobación registrada**: U5 **no** se gatea con el bloque de texto que mira la tabla viva (ese bloque es de U7).
- **U7** depende de U5: verifica la **tabla viva**. Su gate corre **después** de la materialización ⇒ **no exige ningún documento de una unidad pendiente** (DEC-14, B-1).
- **U6** depende de todo (U1–U5 y U7): es el recorrido real.
- **Ninguna unidad es `parallel` con otra**: U1 y U2 tocan el mismo archivo (`skills/cdad-cycle/scripts/cdad_packet.py`), y U3 y U4 se tocan (`sources/roles/reviewer.md`, `packets/roles/reviewer.md`); el paralelismo inseguro lo rechaza el CLI (`cdad_packet.py`:3503-3523, «unsafe parallelism»).
- Ninguna unidad empieza sin su RED declarado y sin la revisión de spec/plan hecha.

### 1.1 Por qué U4 ya no puede gatear la tabla viva (B-1)

En `draft-001`, U4 incorporaba a `tests/validate-consistency.sh` comprobaciones sobre la **tabla viva** y sobre la **existencia del ADR-034**, y exigía `make validate` verde. Pero **ambos documentos los produce U5**, que depende de U4: al llegar al GREEN de U4 sus productores siguen pendientes, y el implementer no puede escribirlos (su alcance es el producto) ni el orquestador puede ejecutar U5 respetando la dependencia declarada. El remedio es **separar por superficie** y conservar los responsables:

| Superficie | Dueño | Unidad | Gate |
|---|---|---|---|
| Plantilla del Memory Bank y referencias del skill (upkeep de stage-5, reconciliación de la re-entry) | implementer (texto del producto) | **U4** | texto verde + regresiones + `make validate` — **sin** la tabla viva ni el ADR-034 |
| Documentos del proyecto (`docs/systemPatterns.md`, `docs/adr/ADR-034-…md`) | orquestador (ADR-003) | **U5** | materialización + **aprobación** del ADR-034 registrada |
| Verificación de la tabla viva | verificador (orquestador), sobre la producción de U5 | **U7** (nueva) | bloque de texto verde **después** de U5 + control negativo del comprobador |

Cada unidad pasa su gate **sin documentos de unidades pendientes**: U4 no mira lo que U5 producirá; U5 no exige su propio bloque de verificación; U7 sí lo exige, y U5 ya está cerrada cuando U7 corre.

### 1.2 Qué NO es una invariante: ni el inventario ni la identidad de una decisión (B-3)

El inventario inicial de la tabla es una **fotografía**, no una propiedad del proyecto: aprobar un ADR nuevo **añade** una fila y reemplazar una decisión **cambia** el estado de una fila. Fijarlo en el validador permanente obligaría a **modificar los tests** después de cada cambio legítimo del inventario — justo el procedimiento normal que esta feature introduce (dictamen B-3).

Y hay una **segunda** fotografía, más fina: la **identidad** de una decisión. La revisión 3 quitó los **conteos** del validador, pero dejó en él una comprobación **por identidad** —«la fila de ADR-034 existe, `vigente`, con los roles `architect` y `reviewer` y con la referencia al archivo canónico», más el **archivo** ADR-034 comprobado por nombre—. Esa condición tampoco es duradera: un upkeep **lícito** —aprobar un ADR que **reemplaza** a ADR-034, marcar la fila vieja `obsoleto` con su sucesor y sembrar la fila sucesora `vigente`— la rompe, y el procedimiento normal obligaría a **modificar tests históricos** o a conservar una **vigencia falsa** (dictamen `plan-review-003.md`). Por eso la verificación se parte en **dos capas**:

| Capa | Qué lleva | Dónde vive | ¿Admite cambios de inventario **y** de identidad? |
|---|---|---|---|
| **Invariantes duraderas** (sólo **propiedades de coherencia**, sin nombrar **ningún** ADR) | la sección `## Decisiones vigentes` es el **primer H2** de `docs/systemPatterns.md`; cada fila apunta a un archivo **existente** y **dentro de `docs/adr/`** (dirección **fila → archivo**); toda fila `obsoleto` nombra un reemplazo **existente**; todo `roles` ∈ vocabulario cerrado (los cinco roles delegados + `orchestrator`); **ningún** archivo apuntado por una fila re-enuncia el texto del principio; la nota declara que **el estado lo declara quien mantiene la tabla** | `tests/validate-consistency.sh` — bloque de **U7** | **Sí**: agregar una decisión o reemplazar **cualquiera** —ADR-034 incluida— **no** obliga a tocar el validador |
| **Evidencia puntual de la siembra** | el inventario sembrado: **25** filas vigentes, **1** obsoleta, **8** `Proposed` excluidos; **la ficha de la fila de ADR-034**: existe, `vigente`, roles `architect` y `reviewer`, referencia al archivo canónico; y el **archivo** ADR-034 materializado: existe, con el estado **aprobado** (no `Proposed`), apuntando a la fuente única y sin re-enunciar el principio | evidencia de aceptación de **U5** y **U7** | n/a: se **reemplaza**, no se **comprueba** |

**Regla.** El validador permanente **no lleva conteos** (ni el número de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas) **ni excepciones por identidad**: **no nombra ningún ADR** y **no exige** el estado, los roles ni la referencia de ninguna fila en particular. Sus comprobaciones son de **coherencia** ⇒ se cumplen con la tabla sembrada, con la tabla después de **agregar** una decisión y con la tabla después de **reemplazar** cualquiera de ellas.

**Cierre del comprobador (caso descartable, el mismo bloque y sin editarlo).** Tres casos, ejecutados con **el mismo** `tests/validate-consistency.sh` (con su digest medido antes y después ⇒ prueba de que el comprobador **no se editó**):
1. **Agregar un ADR aprobado** (un archivo nuevo en `docs/adr/` + su fila `vigente`) ⇒ **pasa**.
2. **Reemplazar expresamente ADR-034**: su fila pasa a `obsoleto` con su `superseded_by`, y la fila sucesora queda `vigente` con su archivo existente ⇒ **pasa**. (El **archivo** ADR-034 **se conserva**: el reemplazo cambia la fila, no borra el documento.)
3. Una fila que apunta a un archivo **inexistente** ⇒ **falla**, nombrando la desalineación.

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | **El encargo: la fila declarada, su forma y el tope.** `request.current_decisions` (opcional, aditivo), la validación de la forma de la fila (conjunto cerrado, `file` existente, `state` de vocabulario cerrado, `summary` de una línea, `roles` de vocabulario cerrado, `superseded_by` condicional), la regla «la fila nombra el rol del paquete», la regla «sólo lo vigente viaja», el **tope de 32** fail-closed, la bandera `--current-decision` y la propiedad del esquema | — | PD-1, PD-2, PD-3, PD-4, PD-6 | RED + focales GREEN + regresiones de contrato/packets (A-1) + `make validate` |
| **U2** | **La sección aditiva del render:** `## Current decisions` se emite **sólo** con filas, después de `## Contract`, con una entrada por fila en el orden declarado; sin filas el render es **byte-idéntico** (intra-revisión). La invocación de `prepare` con la bandera, declarada en la plantilla de handoff | U1 | PD-5, PD-6, PD-13 | RED + focales GREEN + regresiones de render (A-1) + `make validate` |
| **U3** | **El principio: una casa y las dos obligaciones.** `references/design-principles.md` (nuevo) con el principio y su límite; la fila en la tabla de referencias de `SKILL.md`; la **obligación del architect** y el **criterio del reviewer** (con el límite «la falta de abstracción no es defecto») en la fuente de cada rol y en su bloque estático; el **deber del reviewer sobre la tabla** con su procedimiento en `references/stage-4-review.md`; el test de texto | U2 | PD-8, PD-10, PD-13 | RED de texto + regresiones de generación/paquetes (A-1) + `make staging` determinista + `make validate` |
| **U4** | **La tabla y su upkeep, sólo en plantilla y procedimiento:** la sección en la plantilla del Memory Bank; el **upkeep del orquestador** en `references/stage-5-merge.md` (sin tocar el exit gate); la **regla general del CAS por digest base** y la reconciliación por re-despacho en `references/re-entry.md`; el test de texto de esas superficies | U3 | PD-7, PD-8, PD-9, PD-13 | RED de texto + regresiones de la skill (A-1) + `make validate` — **sin** la tabla viva ni el ADR-034 |
| **U5** | **La siembra de este repo** (no es unidad de código): `docs/systemPatterns.md` con la sección `## Decisiones vigentes` y sus 26 filas, y `docs/adr/ADR-034-principio-general-antes-especifico.md` con el estado **aprobado**. El **inventario** sembrado (25/1/8) **y la ficha de la fila de ADR-034** (existe, `vigente`, roles `architect` y `reviewer`, referencia al archivo canónico) son la **evidencia puntual** de esta unidad, **no** una aserción permanente (§1.2). **Documentos del proyecto: los materializa el orquestador** (ADR-003; `sources/roles/orchestrator.md`:106-112) | U3, U4 | PD-11 | materialización por el orquestador + **aprobación** del ADR-034 registrada (sin el bloque de texto de la siembra: eso es de U7) |
| **U7** | **La verificación de la siembra** (no es unidad de código): el bloque de texto de `tests/validate-consistency.sh` que comprueba la **tabla viva** con **invariantes duraderas** que **no nombran ningún ADR** —**nunca** con el número de filas ni con la identidad de una decisión (§1.2)— y su **control negativo**: el caso descartable que **admite** una aprobación nueva, **admite el reemplazo expreso de ADR-034** y **falla** con una fila que apunta a un archivo inexistente, **todo con el mismo comprobador y sin editarlo** | U5 | PD-11 | bloque de texto verde **después** de la materialización de U5 + control negativo del comprobador |
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
- **Verificación:** la **materialización misma** y la **aprobación registrada**; la comprobación de contenido (presencia de la sección, de la nota de exclusiones, existencia del archivo de cada fila y estado aprobado del ADR) **no** se exige aquí: es el gate de **U7**, que corre después.
- **El inventario, aquí, es evidencia (B-3).** Esta unidad **acredita una vez** el inventario sembrado —**25** filas vigentes, **1** obsoleta, **8** `Proposed` excluidos— y lo deja registrado en su evidencia. Ese conteo **no** entra en `tests/validate-consistency.sh` ni en ninguna otra aserción permanente: el validador lleva **sólo invariantes duraderas** (§1.2, DEC-15).
- **La ficha de ADR-034, también aquí, es evidencia (B-3, cierre).** Esta unidad **acredita una vez**, además, **la ficha de la fila de ADR-034** (existe, `vigente`, roles `architect` y `reviewer`, referencia al archivo canónico) y **el estado del archivo ADR-034 materializado** (existe, con el estado **aprobado** —no `Proposed`—, apuntando a la fuente única y sin re-enunciar el principio). **Ninguna** de las dos cosas se comprueba en el validador permanente (§1.2, DEC-16): una comprobación por identidad obligaría a tocar los tests en cada cambio legítimo del inventario, y un upkeep lícito puede reemplazar ADR-034 (su fila pasa a `obsoleto` con su sucesor) **sin** que el validador deje de ser verde.
- **Commits:** el orquestador materializa y commitea con el prefijo `docs(memory):` (el canal que ya usa el Memory Bank), **después** de la aprobación del usuario de los borradores (ADR-006, `references/stage-5-merge.md`:53-68).
- **Owner:** orquestador (materialización) con la aprobación de la autoridad vigente.

### U7 — La verificación de la siembra (no es unidad de código) — **nueva en la revisión 2**, **corregida en la revisión 3 (B-3: inventarios)**, **cerrada en la revisión 4 (B-3: identidad)**

- **Por qué existe (B-1):** las comprobaciones sobre la **tabla viva** necesitan una unidad cuyo gate sea **posterior** a la materialización de U5. En U4 producían una dependencia circular: el gate de U4 exigía documentos de una unidad pendiente (DEC-14).
- **Qué produce:** el **bloque de texto de la siembra** en `tests/validate-consistency.sh` (el bloque de U4 cubre plantilla y procedimiento; este cubre la tabla viva) y su **control negativo**.
- **Qué comprueba — CAPA 1, invariantes duraderas (lo único que va en el validador permanente), sin excepciones por identidad:**
  1. `docs/systemPatterns.md` tiene la sección `## Decisiones vigentes` como **primer H2**;
  2. **cada** fila apunta a un archivo que **existe** y está **dentro de `docs/adr/`** — la dirección es **fila → archivo**, **no** al revés: el validador **no** exige que todo ADR tenga fila (el estado de un ADR no es derivable: M4, D-3);
  3. **toda** fila `obsoleto` nombra su reemplazo, y ese reemplazo **existe**;
  4. **todo** `roles` de **toda** fila pertenece al vocabulario cerrado (los cinco roles delegados más `orchestrator`);
  5. **ningún** archivo apuntado por una fila **re-enuncia** el texto normativo del principio (la casa única se extiende a las filas: la comprobación es sobre **la fila**, no sobre un ADR nombrado);
  6. la nota declara que **el estado lo declara quien mantiene la tabla** (D-3) — la nota **declara la regla**, no enumera un inventario cerrado;
  7. **el propio bloque no nombra ningún ADR** (control negativo sobre el bloque: un `grep` acotado a sus líneas que no encuentra `ADR-0NN`).
  **Lo que el bloque NO contiene:** ningún conteo (ni el número de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas) **ni ninguna comprobación por identidad** (no exige el estado, los roles ni la referencia de ninguna fila en particular; no nombra ningún ADR) ⇒ **agregar un ADR o reemplazar cualquier decisión —ADR-034 incluida— no obliga a tocar el validador** (B-3, DEC-15, DEC-16).
- **CAPA 2, evidencia puntual (no va en el validador):** el inventario sembrado —**25** filas vigentes, **1** obsoleta, **8** `Proposed` excluidos—, **la ficha de la fila de ADR-034** (existe, `vigente`, roles `architect` y `reviewer`, referencia al archivo canónico) y **el archivo ADR-034 materializado** (existe, con el estado **aprobado**, no `Proposed`, apuntando a la fuente única y sin re-enunciar el principio) se **acreditan una vez**, en la evidencia de aceptación de U5 y U7 (§1.2).
- **RED (y por qué no puede ser otro):** el RED de esta unidad **no** puede ser «la tabla no existe» — eso reintroduciría exactamente el defecto B-1 (una comprobación que sólo puede pasar si otra unidad pendiente ya entregó su producto). Su RED es el **control negativo del comprobador**, con **tres casos sobre copias descartables**, ejecutados **con el mismo bloque** (el RED mide el digest del bloque antes y después de los tres y comprueba que **no cambió** ⇒ prueba de que el comprobador no se editó para admitir el reemplazo): (i) una tabla con una fila que apunta a un ADR inexistente ⇒ el bloque **detecta y reporta** la desalineación (el mismo hecho que E4 exige del reviewer); (ii) una tabla a la que se **agrega un ADR aprobado** (un archivo nuevo en `docs/adr/` + su fila `vigente`) ⇒ el bloque **pasa**; (iii) una tabla en la que se **reemplaza expresamente ADR-034** (su fila pasa a `obsoleto` con su `superseded_by` —**el archivo de ADR-034 se conserva**— y la fila sucesora queda `vigente` con su archivo existente) ⇒ el bloque **pasa**. Además, el RED declara que el bloque existe, cubre las comprobaciones enumeradas, **no nombra ningún ADR** y **no contiene ningún conteo del inventario**.
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_004_002_t1_policy.py`, `tests/test_006_005_u7_scribe_role_report.py`.
- **Owner:** RED: test-writer (el bloque y su control negativo); GREEN: verificador — la producción que se verifica es la materialización de U5 (cerrada antes de que U7 corra).
- **Gate:** el bloque de texto de la siembra **pasa** con la tabla viva ya materializada por U5 y con el ADR-034 aprobado; el control negativo **detecta** la tabla desalignada y **acepta** la aprobación nueva y el **reemplazo expreso de ADR-034**, con el **mismo** bloque y sin editarlo (los tres casos del RED, con el digest del bloque verificado antes y después); `make validate` verde. **Ninguna unidad pendiente** es condición de este gate.

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
| **`tests/validate-consistency.sh` (los dos bloques nuevos)** | el propio validador (`make validate`) | **NO APLICA — el validador sólo **crece**: el bloque de U4 (plantilla + procedimiento) y el de U7 (tabla viva) se **agregan**; no se modifica ni se elimina ninguna aserción vigente.** El bloque de U7 nace después de la materialización de U5 ⇒ `make validate` es verde en U4 **sin** la siembra, y verde en U7 **con** ella. Ese bloque lleva **sólo invariantes duraderas**, **ningún conteo del inventario** y **ninguna comprobación por identidad** (B-3, DEC-15, DEC-16): no reemplaza ningún oráculo y, además, **admite** aprobaciones y reemplazos nuevos —incluido el de ADR-034— sin tocarlo. |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije que un request con una propiedad nueva debe rechazarse (es decir, que exija el conjunto cerrado *sin* `current_decisions`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva. Los REDs de U2, U3 y U4 declaran lo mismo respecto de la forma de las secciones, del bloque estático y de los agentes generados; el RED de U7 declara lo mismo respecto del validador, y sus casos son **controles negativos añadidos** (fila desalignada, ADR aprobado nuevo, **decisión reemplazada —ADR-034 expresamente—**), no oráculos reemplazados — y declara además que el bloque que añade **no fija ningún conteo del inventario** y **no contiene ninguna comprobación por identidad** (B-3, DEC-15, DEC-16).

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED**: esta spec y este plan se revisan con la superficie vigente de 006-006 (`draft-plan` + `plan-review` sobre un borrador **no aprobado**), en sesión separada del autor; sus bloqueantes van al architect o se descartan con razón escrita por la autoridad que aprueba; y recién entonces viene el RED (DEC-12).
- **El ADR-034** lo aprueba la autoridad vigente (el orquestador bajo la HITL delegada; el dueño puede vetarla). **U5 no se ejecuta antes de esa aprobación** (una fila `vigente` exige una decisión aprobada). La aprobación es un acto **posterior y separado** de la redacción del borrador (INV-14), y su evidencia se registra.
- **El orden de las unidades es parte del cierre**: **U4 pasa su gate sin la siembra** (verifica sólo plantilla y procedimiento); **U5** (la siembra) depende de **U3 y U4** y su gate es la **materialización + la aprobación registrada**; **U7** (la verificación de la siembra) corre **después** de U5 ⇒ el orden ejecutable es `U1 → U2 → U3 → U4 → U5 → U7 → U6`, sin saltarse dependencias ni ampliar permisos (§1.1).
- **El validador permanente no fija la identidad de ninguna decisión**: la fila de ADR-034 puede volverse `obsoleto` por el upkeep —con su sucesor `vigente`— sin que el validador deje de ser verde, y sin tocar `tests/validate-consistency.sh` (DEC-16, INV-16).
- **La política de compatibilidad (L-1) queda declarada antes del recorrido**: el caso de dos fases (V-5) se ejecuta en U6 y su salida real se pega en la evidencia.
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature, salvo el deber añadido).
- El recorrido real de U6 queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan pasan por la revisión independiente, la aprobación es de la autoridad vigente, y el cierre materializa la tabla sembrada con el prefijo `docs(memory):`.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y fallando por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3, U4 y U7; make staging determinista (dos corridas, mismos bytes) en U3. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). ORDEN Y GATES: cada unidad pasa su gate sin depender de documentos de una unidad pendiente; U4 verifica solo plantilla y procedimiento, U5 materializa los documentos del proyecto y U7 verifica la siembra YA materializada. A-1: esta feature NO reemplaza ningun oraculo vigente (ver plan 4): el conjunto cerrado del request se EXTIENDE con una propiedad declarada (current_decisions) sin relajar la clausura; la forma de las secciones del paquete se comprueba por presencia, no por conjunto exhaustivo; ningun test fija un digest literal de una fuente de instruccion; el exit gate de stage 5 no cambia; la subfase del reviewer no se toca; los agentes son salidas declaradas y make agents los regenera. Los REDs anaden casos y vuelven a comprobar los controles negativos, no cambian oraculos. Aditividad: sin el campo nuevo el render es byte-identico DENTRO de una misma revision del producto; entre revisiones no se promete compatibilidad y la politica (terminarlo bajo la revision con la que se publico, o preparar uno nuevo) queda declarada, con su caso de dos fases en U6. Fila: conjunto cerrado de seis claves (file, state, summary, roles, reference, superseded_by condicional); file debe existir en el proyecto; state en {vigente, obsoleto}; roles de vocabulario cerrado (los cinco roles delegados mas orchestrator); summary de una linea; superseded_by exigido si state es obsoleto y prohibido si es vigente. Admision: toda fila declarada debe nombrar el rol del paquete; una fila obsoleto no es admisible en un paquete; el tope es 32 filas por paquete y falla cerrado nombrando el numero y el tope. La fila viaja en el request (opcional, aditivo) y el render emite la seccion Current decisions solo con filas. Principio: fuente unica en references/design-principles.md (el texto normativo aparece en un solo archivo del arbol instalable); las obligaciones del architect y del reviewer viven en la fuente de cada rol y en su bloque estatico, y apuntan al dueno canonico sin copiar el texto; el limite (la falta de una abstraccion no es defecto) queda escrito y verificado por test de texto. Upkeep: el orquestador agrega la fila al aprobarse un ADR y marca la anterior como obsoleta; el exit gate de stage 5 NO cambia. CAS: el digest declarado en la autorizacion es siempre el digest BASE sobre el que se preparo la propuesta, nunca el digest actual del destino; ante un conflicto, la via es re-despachar al rol con un paquete nuevo sobre la base nueva; no se fusiona a mano ni se actualiza el digest esperado para forzar el paso; el orquestador escribe sus propias filas directamente en docs/ con su commit. Siembra: docs/systemPatterns.md gana la seccion Decisiones vigentes (primer H2) con la nota de que el estado lo declara quien mantiene la tabla y la nota de exclusiones. El INVENTARIO sembrado (25 filas vigentes, 1 obsoleta, 8 ADR Proposed excluidos), la FICHA DE LA FILA DE ADR-034 (existe, vigente, roles architect y reviewer, referencia al archivo canonico) y el estado del ARCHIVO ADR-034 materializado son EVIDENCIA PUNCTUAL de la aceptacion de U5 y U7, NO una asercion permanente. El validador permanente (tests/validate-consistency.sh) lleva SOLO invariantes duraderas SIN EXCEPCIONES POR IDENTIDAD: no nombra ningun ADR, no exige el estado, los roles ni la referencia de ninguna fila en particular, y no lleva ningun conteo; sus comprobaciones son de coherencia: cada fila apunta a un archivo que EXISTE y esta dentro de docs/adr/ (direccion fila -> archivo, no al reves); toda fila obsoleto nombra un reemplazo que EXISTE; todo roles pertenece al vocabulario cerrado (los cinco roles delegados mas orchestrator); NINGUN archivo apuntado por una fila re-enuncia el texto del principio; y la nota declara que el estado lo declara quien mantiene la tabla. CIERRE DEL COMPROBADOR, en un caso descartable, con el MISMO bloque y sin editarlo (digest del bloque verificado antes y despues): agregar un ADR aprobado y reemplazar EXPRESAMENTE ADR-034 (su fila obsoleto con su reemplazo, la fila sucesora vigente) PASAN el comprobador, y una fila con archivo inexistente FALLA.",
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
        "una fila que no nombra el rol del paquete se rechaza nombrando la fila y el rol; una fila que nombra a otro rol delegado se rechaza por la misma regla (PD-2)",
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
        "control negativo: el exit gate de stage 5 no ganhou casillas (PD-7, PD-8)",
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
      "objective": "La siembra de este repo: el orquestador materializa dos documentos del proyecto (docs/systemPatterns.md con la seccion Decisiones vigentes como primer H2, sus 26 filas -25 vigentes y 1 obsoleta-, la nota de exclusiones de los 8 ADR Proposed y la nota de que el estado lo declara quien mantiene la tabla; y docs/adr/ADR-034-principio-general-antes-especifico.md). El CONTEO del inventario (25 vigentes, 1 obsoleta, 8 Proposed excluidos) Y LA FICHA DE LA FILA DE ADR-034 (existe, vigente, roles architect y reviewer, referencia al archivo canonico) son la EVIDENCIA PUNCTUAL de esta unidad: se acreditan una vez, aqui, y NO entran en el validador permanente (B-3, DEC-15, DEC-16). Precondicion: la APROBACION del ADR-034 por la autoridad vigente, porque una fila vigente exige una decision aprobada; el borrador entregado por el architect dice Proposed y su aprobacion es un acto POSTERIOR y SEPARADO, cuya evidencia queda en el estado. El ADR-034 materializado lleva el estado aprobado, apunta a la fuente unica del principio y no lo re-enuncia. Materializacion y commit por el orquestador con el prefijo docs(memory): tras la aprobacion del usuario de los borradores. Esta unidad NO se gatea con el bloque de texto de la siembra (eso es de U7): su gate es la materializacion misma mas la aprobacion registrada.",
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
        "EVIDENCIA PUNCTUAL: la ficha de la fila de ADR-034 existe con state vigente, los roles architect y reviewer, y la referencia al archivo canonico del skill; NO es una asercion permanente (PD-11, DEC-16)",
        "EVIDENCIA PUNCTUAL: el ADR-034 materializado existe y lleva el estado APROBADO, con la evidencia de la aprobacion registrada; el borrador Proposed es una fase anterior y distinta (PD-11, O-1)",
        "el commit de la materializacion lleva el prefijo docs(memory): y lo ejecuta el orquestador tras la aprobacion del usuario (ADR-006)",
        "el conteo del inventario y la ficha de ADR-034 NO se comprueban en ninguna asercion permanente: aprobar un ADR nuevo, reemplazar una decision o reemplazar EXPRESAMENTE ADR-034 NO obliga a tocar tests/validate-consistency.sh (DEC-15, DEC-16, B-3)"
      ],
      "regressions": [],
      "integration_gate": "materializacion por el orquestador con la aprobacion de la autoridad vigente registrada; el ADR-034 materializado con estado aprobado",
      "owner": "orchestrator (materializacion); la autoridad vigente aprueba el ADR-034 y los borradores",
      "detail": "next"
    },
    {
      "id": "U7",
      "objective": "La verificacion de la siembra, DESPUES de la materializacion de U5, en dos capas (B-3, DEC-15, DEC-16). CAPA 1 - INVARIANTES DURADERAS, en el validador permanente tests/validate-consistency.sh: SOLO propiedades de coherencia que admiten aprobaciones y reemplazos nuevos, NUNCA el numero de filas y NUNCA una comprobacion por identidad (no nombra ningun ADR y no exige el estado, los roles ni la referencia de ninguna fila en particular). La seccion Decisiones vigentes existe como primer H2 de docs/systemPatterns.md; cada fila apunta a un archivo que EXISTE y esta dentro de docs/adr/ (direccion fila -> archivo, no al reves); toda fila obsoleto nombra un reemplazo que EXISTE; todo roles de toda fila pertenece al vocabulario cerrado (los cinco roles delegados mas orchestrator); NINGUN archivo apuntado por una fila re-enuncia el texto normativo del principio; la nota declara que el estado lo declara quien mantiene la tabla; y el propio bloque no nombra ningun ADR (control negativo sobre el bloque). CAPA 2 - EVIDENCIA PUNCTUAL, en la aceptacion de U5 y U7 y NO en el validador: el inventario sembrado (25 filas vigentes, 1 obsoleta, 8 ADR Proposed excluidos), la ficha de la fila de ADR-034 (existe, vigente, roles architect y reviewer, referencia al archivo canonico) y el archivo ADR-034 materializado (existe, con el estado aprobado, apuntando a la fuente unica y sin re-enunciar el principio) se acreditan una vez, con la evidencia de la unidad. CIERRE DEL COMPROBADOR, en un caso descartable, con el MISMO bloque y sin editarlo (digest del bloque medido antes y despues de los tres casos): agregar un ADR aprobado (una fila vigente mas) y reemplazar EXPRESAMENTE ADR-034 (su fila pasa a obsoleto con su reemplazo, y la fila sucesora queda vigente con su archivo existente) PASAN el comprobador; una fila que apunta a un archivo inexistente FALLA. Es una unidad de VERIFICACION: su gate corre despues de U5 y no exige ningun documento de una unidad pendiente. Su RED no puede ser la ausencia de la tabla (eso reintroduciria el defecto B-1): su RED es el CONTROL NEGATIVO DEL COMPROBADOR (los tres casos del cierre, sobre copias descartables, con el mismo bloque) mas la declaracion de que el bloque existe, lleva SOLO invariantes duraderas, no nombra ningun ADR y no contiene ningun conteo del inventario.",
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
        "el validador permanente comprueba que cada fila apunta a un archivo que EXISTE y esta dentro de docs/adr/, en la direccion fila -> archivo y no al reves (PD-11, DEC-15)",
        "el validador permanente comprueba que toda fila obsoleto nombra un reemplazo que EXISTE (PD-11, DEC-15)",
        "el validador permanente comprueba que todo roles de toda fila pertenece al vocabulario cerrado (PD-11, DEC-15)",
        "el validador permanente comprueba que NINGUN archivo apuntado por una fila re-enuncia el texto del principio (PD-11, DEC-16)",
        "el validador permanente comprueba que la nota declara que el estado lo declara quien mantiene la tabla (PD-11, D-3)",
        "el validador permanente NO nombra ningun ADR y NO exige el estado, los roles ni la referencia de ninguna fila en particular (PD-11, DEC-16, INV-16)",
        "el validador permanente NO contiene ningun conteo del inventario: ni el numero de filas, ni el de vigentes, ni el de obsoletas, ni el de excluidas (PD-11, DEC-15, B-3)",
        "EVIDENCIA PUNCTUAL: el inventario sembrado (25 vigentes, 1 obsoleta, 8 Proposed excluidos) y la ficha de la fila de ADR-034 quedan acreditados en la evidencia de U5 y U7, no en el validador (DEC-15, DEC-16)",
        "cierre del comprobador, en un caso descartable, con el MISMO bloque y sin editarlo: agregar un ADR aprobado y reemplazar EXPRESAMENTE ADR-034 PASAN el comprobador, y una fila con archivo inexistente FALLA; el digest del bloque es el mismo antes y despues de los tres casos (PD-11, E4, V-7)"
      ],
      "regressions": [
        "tests/test_005_006_t2_intake.py",
        "tests/test_004_002_t1_policy.py",
        "tests/test_006_005_u7_scribe_role_report.py"
      ],
      "integration_gate": "el bloque de texto de la siembra pasa con la tabla viva ya materializada por U5 y con el ADR-034 aprobado por la autoridad vigente; el control negativo del comprobador detecta la tabla desalineada; y el caso descartable demuestra que agregar un ADR aprobado y reemplazar EXPRESAMENTE ADR-034 siguen PASANDO el comprobador con el MISMO bloque, cuyo digest no cambia (el validador no fija el inventario ni la identidad de una decision)",
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

## 9. Revisión 4 — qué cambió respecto de draft-003

| Hallazgo | Cambio en el plan | Dónde |
|---|---|---|
| **B-3 (resto)** — el validador permanente conservaba una **excepción por identidad**: exigía que la fila de **ADR-034** existiera, `vigente`, con los roles `architect` y `reviewer` y con la referencia al archivo canónico, y comprobaba el **archivo** ADR-034 por nombre. Un upkeep lícito —aprobar un ADR que reemplaza a ADR-034— rompe esa condición | El **validador permanente** queda con **invariantes duraderas sin excepciones por identidad**: **no nombra ningún ADR** y sus comprobaciones son de **coherencia** (fila → archivo existente bajo `docs/adr/`; fila `obsoleto` → reemplazo existente; `roles` ∈ vocabulario cerrado; **ninguna** fila re-enuncia el texto del principio; la nota declara quién declara el estado) ⇒ **agregar** una decisión o **reemplazar cualquiera** —ADR-034 incluida— no obliga a tocarlo. La **ficha de la fila de ADR-034** (existencia, estado, roles, referencia inicial) y el **estado del archivo ADR-034 materializado** pasan a la **evidencia puntual** de U5/U7. El **cierre del comprobador** se completa: el caso descartable **agrega** un ADR aprobado, **reemplaza expresamente ADR-034** (fila `obsoleto` + fila sucesora `vigente`) y **rechaza** una fila con archivo inexistente, **con el mismo bloque y sin editarlo** (digest del bloque medido antes y después). U5 deja de gatear contenido que sólo U7 verifica y **acredita** la ficha de ADR-034. | §1.2, §2 (U5, U7), §3 (U5, U7), §4, §5, §6 (U5, U7, `validation_strategy`) |

Lo demás de `draft-003` **se conserva**.

Status: **BORRADOR — SIN APROBAR** (draft-004). La aprobación es un acto separado de la autoridad vigente, y precede al RED de cualquier unidad.
