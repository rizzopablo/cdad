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
