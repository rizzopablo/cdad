Todas las verificaciones están hechas. Emito la entrega draft-003 (solo B-3 corregido; todo lo demás igual que draft-002).

===BEGIN spec.md===
# 006-006-spec-plan-review — SPEC (etapa 2, borrador draft-003)

Estado: **BORRADOR — SIN APROBAR**. Esta entrega no lleva marca de aprobación y no la lleva nunca por el dictamen de la revisión de borrador (INV-1). La aprobación es un acto separado de la autoridad vigente (`skills/cdad-cycle/references/stage-2-specification.md`:46-85).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §13 (enmienda 006) — sha256 `d6da11db…9809`, verificado contra el paquete `exec-006-006-spec-plan-review-001` y recalculado en disco.
Decisiones de entrada (orquestador, HITL delegada, mantenidas el 2026-10-20): `docs/epics/epic-006-opencode-concurrency/execution.md`:379-388.
Decisiones de entrada de esta revisión (orquestador, HITL delegada, 2026-10-20, transmitidas por el paquete `exec-006-006-spec-plan-review-001`, substage `draft-002`): **B-1** política de compatibilidad; **B-2** identidad de la exención; **O-1** y **O-2** correcciones de plan.
Decisión de esta revisión (orquestador, HITL delegada, 2026-10-20, substage `draft-003`): **B-3** — los campos de exención entran al payload canónico de la transición **SOLO cuando se declaran**; sin exención, el payload y la identidad quedan **byte-idénticos** a los del producto actual, de modo que **las identidades históricas se conservan** y **no hay enmienda** de 005-014 PD-23 ni de 006-005 PD-19(b).
Insumo: `docs/specs/006-006-spec-plan-review/discovery.md` (etapa 1, mismo autor).
Dictámenes que motivan este borrador: `docs/specs/006-006-spec-plan-review/plan-review-001.md` (2 bloqueantes · 2 opcionales, aplicados en draft-002) y `docs/specs/006-006-spec-plan-review/plan-review-002.md` (1 bloqueante — **B-3** —, aplicado en este borrador).
Base medida: el **código** no cambió desde el HEAD `7f39e24` (verificado: `git log 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/` vacío; el HEAD documental vigente es `6c8ad04`). Todas las citas de código son de ese HEAD y nombran además el símbolo (los números de línea pueden correrse).
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

**Correcciones de draft-002 (conservadas).** Dictamen: `plan-review-001.md` (2 B · 2 O). Las cuatro correcciones están aplicadas y son **deliberadas**, no cosméticas:

| Hallazgo | Resolución en draft-002 (conservada) |
|---|---|
| **B-1** — la compatibilidad prometida contradice el cambio de las fuentes de instrucción | §2.1 R-9/R-10 reescritos (compatibilidad **acotada a una revisión**), PD-2 y PD-5 reescritos, **PD-16** nueva (política + caso que la demuestra), **INV-10** reescrito, **D-12** y **V-6** nuevas, **E7** nuevo, deuda declarada (§10) |
| **B-2** — la exención no participa en la identidad de la transición: puede desaparecer como no-op | §2.7 (cláusula de identidad) y **PD-9** ampliados, **INV-12** nueva, **D-13** nueva; el plan da a U5 la zona de la identidad y los dos casos del RED |
| **O-1** — faltan las regresiones acopladas al gate | plan U5 suma `tests/test_005_012_t2_gate_authority.py` y `tests/test_005_012_t5_approval_vigency.py` a sus regresiones |
| **O-2** — el control negativo de PD-10 prueba el punto equivocado | **PD-10** reescrito: el control prepara un rol de construcción **con aprobación vigente y sin dictamen** (⇒ **no** se rechaza: el gate es supervisado), **distinto** del rechazo **sin aprobación** de PD-14 |

**Correcciones de este borrador (draft-003).** Dictamen: `plan-review-002.md` (1 bloqueante). La corrección es **deliberada** y no cosmética: cambia la **forma** del payload de identidad y, con ella, lo que la feature promete sobre el estado ya registrado.

| Hallazgo | Resolución en este borrador |
|---|---|
| **B-3** — añadir campos nulos cambia también las identidades históricas sin exención | §2.7 reescrito: **R-11** (el bloque `exemption` es **condicional**: se añade **una** clave y **sólo** cuando la exención se declara), **R-12** (el bloque lleva **exactamente** los campos declarados), **R-13** (sin exención el payload y la `transition_key` son **byte-idénticos** a los del producto vigente ⇒ identidades históricas conservadas); **PD-9 reescrita** (identidad condicional + **recorrido de dos revisiones** en `gate`, `closure` y `disposition`); **INV-12** reescrito y **INV-13** nueva; **D-13** reescrito (con la alternativa de draft-002 explícitamente rechazada) y **D-14** nueva (**no hay enmienda** de 005-014 PD-23 ni de 006-005 PD-19(b)); **V-7** nueva; §10 declara que la deuda 005-014 **E-4 no se amplía**; el plan da a U5 la zona condicional del payload, el recorrido de dos revisiones y **dos regresiones nuevas** (`tests/test_005_014_closure_replay.py`, `tests/test_006_005_u5_disposition_failed.py`) |

**Lo que B-3 deja de prometer (declarado, no oculto):** el payload de identidad **deja de ser uniforme** (la regla vigente es «toda clave presente; un insumo ausente vale `null`»). La regla que la sustituye es **condicional** y está escrita (R-11/R-12): **una** clave nueva, presente **sólo** en las invocaciones que declaran la exención. Es el precio de conservar las identidades ya registradas; sin ese precio, una feature de la etapa 2 cambiaría la identidad de **todas** las transiciones —incluidas las de otras clases y las escritas por revisiones anteriores del producto— y rompería garantías ya aprobadas.

**Lo que B-1 deja de prometer (declarado, no oculto):** esta feature **cambia dos de las fuentes de instrucción** que el render del paquete embebe literalmente (`cdad_packet.py`:1000-1004 compone los bytes actuales; :1037-1044 los publica con su digest) y la recepción **vuelve a renderizar y compara** (`cdad_result.py`:563-566). Por lo tanto **no hay** garantía de que un paquete publicado antes de este cambio siga siendo recibible después de él. La garantía de render byte-idéntico vale **dentro de una misma revisión** del producto. El mecanismo y su juicio ya existen en el repo (005-003 T6, dictamen F3) y se **reutilizan**, no se inventan (D-12).

## 1. Descripción funcional

La feature hace tres cosas, en este orden:

1. **Un borrador de especificación tiene forma legal en la superficie de revisión.** Hoy el kind `draft-plan` modela un plan: el nombre, el `purpose` del input (`cdad_packet.py`:4790-4792: «draft plan for review»), el procedimiento («Review a PLAN DRAFT», `packets/substages/reviewer-plan-review.md`:1) y la regla de rol («the plan draft for `draft-plan`», `packets/roles/reviewer.md`:1) son plan-céntricos, y el CLI exige el bloque `plan-tasks` a cualquier borrador. La feature **declara la forma del objeto en el encargo** (extensión aditiva de `contract`), y **los checks estructurales del plan se aplican sólo al documento cuya forma es `plan`**. Una spec sin plan se revisa **sin tareas artificiales**: no se mete un bloque `plan-tasks` vacío dentro de la spec (§2.1, §2.2).
2. **La revisión entra en el recorrido principal y en el gate.** El procedimiento canónico dice **qué se revisa** (una sola fuente: `packets/substages/reviewer-plan-review.md`, generalizado al *objeto de especificación*); `stage-2-specification.md` la declara como subfase de la etapa 2 y su exit gate la nombra; `SKILL.md` gana un criterio en el gate 2→3 (espejo del gate 4→5, `SKILL.md`:361-366); `re-entry.md` gana la re-entry del dictamen y la **declaración de la política de compatibilidad** (§2.1 R-10, D-12); `handoff-prompts.md` gana la invocación con la forma. El rol reviewer y los agentes generados nombran la revisión de borrador (§2.5, §2.8).
3. **La identidad y la trazabilidad del objeto revisado quedan fijadas.** El contrato fija por digest el documento principal y, cuando la revisión cubre spec y plan, **los dos**; el paquete los lleva como `inputs`; el dictamen nombra el objeto y su digest; una corrección produce digest nuevo ⇒ la revisión anterior no cubre los bytes nuevos ⇒ toca re-review focal (§2.3, §2.4).

**Lo que NO hace:** no crea kind, subfase, agente, stage, tipo de artefacto ni verbo nuevos; no amplía la tabla cerrada de destinos; no renombra `draft-plan`/`plan-review`/`plan_version`; no convierte el gate 2→3 en un bloqueo duro del CLI; no toca la revisión final del resultado (etapa 4), que se mantiene en sesión nueva; **no promete compatibilidad entre revisiones del producto** (R-10) ni **cambia el renderer** para tolerar fuentes distintas (D-12); **no cambia la identidad de ninguna transición ya registrada** (§2.7 R-13, D-14).

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
- **R-9 (el paquete nombra la forma).** `inputs` lleva **una entrada por documento fijado**, en orden fijo (principal primero, acompañante después), con su `purpose`: `«draft spec for review»` para la spec, `«draft plan for review»` para el plan. La sección `## Contract` del render nombra la forma (`- form: spec` \| `- form: plan`) y, si hay acompañante, su ruta, digest y versión. **Sin las claves nuevas, dentro de una misma revisión del producto, el render es byte-idéntico** al de esa revisión (el bloque `## Contract` y `## Inputs` sólo crecen cuando el contrato declara algo nuevo) — el patrón aditivo ya establecido (006-005 PD-7). **La garantía es intra-revisión**: ver R-10 y PD-16.
- **R-10 (compatibilidad acotada a una revisión del producto).** El contrato **no** promete compatibilidad **entre revisiones** del producto. Un paquete publicado con una revisión dada de las fuentes de instrucción **se recibe con esa misma revisión**: o se termina bajo la revisión con la que se publicó, o se prepara un paquete nuevo bajo la revisión vigente. Los digests de las fuentes de instrucción **son parte de la identidad del paquete** (`cdad_packet.py`:1000-1004 compone los bytes actuales de las tres fuentes; :1037-1044 las publica con su digest) y la recepción **vuelve a renderizar y compara** (`cdad_result.py`:563-566) ⇒ un paquete publicado antes de un cambio de esas fuentes **no** es recibible después de ese cambio, y ese rechazo es la **conducta correcta** (ruidosa y recuperable), no un defecto que esta feature pueda corregir sin romper la identidad del paquete. La garantía de render byte-idéntico de R-9 vale **dentro de una misma revisión** (paquetes sin las claves nuevas). **Precedente declarado y no reabierto:** el mismo mecanismo fue juzgado en 005-003 T6 (dictamen F3, `.cdad/inbox/005-003-orientation-reduction-reviewer-review-001-review.md`:85-96) como **consecuencia inherente** al contrato de paquete —«no compromete el resultado, la evidencia ni el uso previsto… el fallo es ruidoso y recuperable»— con disposición de **deuda declarable** y **sin corregir el renderer**. Esta feature aplica ese mismo precedente a su propio cambio, que toca dos de las fuentes incluidas literalmente en el render (D-12, PD-16).

**Superficie afectada, medida:** `cdad_packet.py` — `contract_keys` (:879-883), guarda de forja (:890-898), validación del contrato (:920-950), `prepare` (:4671-4699), checks del plan (:4718-4721), construcción de `inputs` (:4790-4792), render (:998-1059, metadata :1028, `## Contract` :1045-1047, `## Inputs` :1051-1052), tabla de banderas (:2011, :6409-6413).

### 2.2 Los checks del plan se aplican sólo al documento cuya forma es `plan`

Hoy la rama es binaria: `if is_declared_draft:` ⇒ `_plan_tasks_from_contract` + `_check_plan_tasks` + `_check_plan_validation_plan` sobre los bytes del contrato (`cdad_packet.py`:4718-4721). Con la forma declarada, la rama pasa a ser **condicional a la forma del documento principal**:

| Forma del principal | ¿Checks del plan? | Efecto observable |
|---|---|---|
| `plan` (o ausente ⇒ `plan`) | **sí** | igual que hoy: sin bloque `plan-tasks` ⇒ rechazo; bloque malformado ⇒ rechazo; checks estructurales y por tarea aplicados |
| `spec` | **no** | una spec sin `plan-tasks` se acepta; **no** se inventan tareas ni se mete un bloque artificial en la spec |
| `plan` + spec acompañante | **sí, sólo sobre el principal** | la spec acompañante **nunca** se juzga por las reglas del plan |

**Consecuencia de ordenamiento:** el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 («un plan sin el bloque `plan-tasks` es rechazado») **se conserva sin cambio de oráculo**, porque la forma por omisión es `plan` (R-4). Este es el punto que la opción O2 del discovery anticipaba como coste («reescribir el oráculo»); con el valor por omisión **ese coste no se paga** (plan §4, A-1).

**Ayuda al diagnóstico (declarada):** cuando la puerta `plan-tasks` rechaza y la forma **no** fue declarada, el diagnóstico nombra la bandera que la declara (`--object-kind spec`). No cambia la Fail-Closed: el rechazo sigue siendo el mismo y sigue sin publicar nada; sólo el mensaje señala la salida legítima. El oráculo vigente del test sólo exige que el stderr nombre el token `plan-tasks` (`assert_rejected_without_publication`:399-423), de modo que la ayuda es compatible con él.

### 2.3 Identidad doble: los dos documentos fijados por digest

Cuando la revisión cubre spec y plan, el contrato lleva **las dos identidades**: `path`/`sha256`/`plan_version` (plan) y `spec_path`/`spec_sha256`/`spec_version` (spec). Los dos digests se **verifican contra los bytes** en `prepare` (`cdad_packet.py`:945-950 para el principal; el mismo control para el acompañante). Consecuencias:

- **Un cambio posterior en cualquiera de los dos documentos se detecta mecánicamente**: se compara el digest actual del archivo con el digest fijado en el `REQUEST.json` del paquete de revisión (con `sha256sum`, el mismo instrumento que usa el propio CLI). No hay comando nuevo: la comparación la hace el orquestador, y el paquete conserva el registro.
- **La revisión anterior no cubre los bytes nuevos**: un digest distinto ⇒ toca re-review **focal** (regla 4 de la calibración, `references/stage-4-review.md`:28-32), no una ronda nueva completa.
- **El dictamen declara el objeto y su digest**: obligación de procedimiento (§2.5) y **mecánicamente recuperable** por la cadena recibo → paquete → `REQUEST.json` → digests fijados. **No** se añade una comprobación nueva en `materialize` (D-9): el CAS de `materialize` protege el destino, y atar el texto libre de la parte a un digest volvería frágil (un error tipográfico del revisor convertiría la recepción en un fallo tardío) sin ganancia real, porque la trazabilidad ya es recuperable.

### 2.4 Revisar el borrador de otra feature (y por qué el dictamen vive en la carpeta de la feature activa)

El contrato de un borrador puede apuntar a **cualquier** documento del proyecto (`_project_path` sólo garantiza que esté dentro de la raíz; la restricción a `docs/specs/<feature>/` **no** existe — deuda ADR-013 O-C, declarada y **fuera de alcance**). Por eso es admisible, y necesario, revisar el borrador de **otra** feature.

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
- **Declaración de la política de compatibilidad** (`references/re-entry.md`, R-10, D-12, PD-16(b)): el reference nombra, en el punto donde el orquestador consulta la re-entry, que un paquete rechazado por diferir de su render canónico fue publicado bajo otra revisión de las fuentes de instrucción, y nombra **las dos salidas** (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la revisión vigente). Es **declaración de procedimiento**, no un cambio del renderer: el CLI no distingue hoy la causa concreta del rechazo y esta feature **no** lo cambia (D-12).
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

**Por qué la exención va en la entrada de aprobación y no en una entrada libre:** (a) la exención **es** una forma de pasar el gate 2→3, así que pertenece al acto que lo abre; (b) atada a la aprobación, **no puede flotar** ni vivir en un `stage` que habilite construcción por su cuenta; (c) la entrada de aprobación conserva su pin de contrato y su `approved_by` — la exención **no** cambia lo que la aprobación autoriza, sólo **declara cómo** se pasó el criterio de revisión.

**La exención participa en la identidad de la transición — pero sólo cuando se declara (B-2, corregido por B-3).** La identidad de una transición es el sha256 de su payload canónico (`cdad_packet.py`:5015-5063, serialización en :5066-5079) y el **no-op** se decide **antes de escribir** (:5766-5770). El payload vigente **no** incluye la exención ⇒ dos invocaciones que sólo difieren en la exención producirían **la misma** clave ⇒ la segunda devolvería **éxito sin registrar** la exención (o su cambio), y el `stage_history` **perdería** información **sin decirlo**. Por eso los cuatro campos de la exención **entran en el payload de identidad**; **pero** — y esto es lo que B-3 obliga a precisar — **sólo en las invocaciones que los declaran**. La forma es **condicional**, no uniforme: sin exención declarada, el payload **no cambia ni en una clave**, y la identidad de una transición ya registrada **queda exactamente como estaba**.

**Reglas de la identidad (R-11..R-13; las R-1..R-10 son de §2.1):**

- **R-11 (el bloque de exención es condicional).** El payload canónico se construye **exactamente** como hoy (16 claves, `cdad_packet.py`:5045-5063) y **sólo** cuando la invocación declara la exención (alguna de las cuatro banderas) se le añade **una** clave nueva, `exemption`. Sin exención declarada: **ni una clave, ni un valor** ⇒ la serialización canónica (`json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))` sobre UTF-8, :5077-5079) es **byte-idéntica** a la del producto vigente ⇒ la `transition_key` es **la misma** ⇒ una transición registrada por la revisión anterior del producto es reconocida como **la misma** transición por la nueva.
- **R-12 (contenido del bloque).** El bloque `exemption` lleva **exactamente** los campos declarados —`exempted_by`, `reason`, `requested_by`, `delegated`— con el valor declarado por su bandera; los campos **no** declarados **no están** en el bloque (no como `null`: no están). El bloque es la **imagen** de los mismos campos que la entrada escribe (planos, en la entrada) ⇒ el payload sigue siendo un espejo fiel de los insumos con efecto (:5028-5031) y sigue siendo el **preimagen** de la clave (oráculo vigente: `tests/test_005_012_t1_register_transition_base.py`:1212 recomputa `canonical_digest(payload)` y lo compara con la `transition_key`; un payload con una clave que no sea parte de la fórmula **no** puede recomputar la clave).
- **R-13 (la identidad histórica se conserva; no hay enmienda).** Consecuencia medible: para una invocación **sin** exención, el payload y la `transition_key` son **byte-idénticos** a los del producto vigente. De ahí, y **sin tocar** ninguna garantía previa: (a) la repetición idéntica sigue siendo un **no-op** —rc=0, **sin** segunda entrada, estado byte-idéntico, salida que nombra la entrada existente (PD-11)— **también** cuando la entrada la registró una revisión anterior del producto; (b) **no hay enmienda** de **005-014 PD-23** (replay de cierre, `docs/specs/005-014-closure-replay/spec.md`:45-53 y :104-110), ni de **006-005 PD-19(b)** (disposición idempotente, `docs/specs/006-005-native-path-parity/spec.md`:219), ni de **005-012 PD-11** (no-op del `gate`): sus oráculos siguen vigentes **sin cambio de oráculo**; y (c) la deuda **005-014 E-4** (entradas registradas con la fórmula **anterior**, sin `transition_key_payload`, `docs/specs/005-014-closure-replay/spec.md`:158) **no se amplía**: sigue REFERIDA a esas entradas, y esta feature **no migra ni recomputa claves históricas** — lo que se conserva es la identidad de las entradas que **ya** llevan `transition_key_payload`, que es un caso distinto.

**Repetición idéntica** (misma exención) ⇒ mismo payload ⇒ misma clave ⇒ **no-op**: rc=0, **sin** segunda entrada, state byte-idéntico, salida que nombra la entrada existente (PD-11 vigente, `tests/test_005_012_t2_gate_authority.py`:630).
**Repetición que cambia la exención** ⇒ payload distinto ⇒ clave distinta ⇒ **no** es un no-op: o bien se registra por la **vía permitida** (`--supersedes <transition_key>` nombrando la entrada previa, que el producto **ya valida**: la entrada nombrada debe existir, ser de la misma feature y el mismo `contract_path`, :5812-5820), o bien se **rechaza explícitamente** por la regla de una sola aprobación vigente (:5821-5829) — **nunca** éxito sin registrar. Este caso incluye el paso **de sin exención a con exención** y el inverso: el bloque aparece o desaparece ⇒ el payload cambia ⇒ la clave cambia.

La exención sigue **dentro de la misma entrada** que la aprobación (D-6): no hay una segunda entrada que compita, y el pin de la aprobación no cambia (INV-7).

**Nada de esto habilita construir:** la exención no altera el pin de aprobación, no crea un kind nuevo y no modifica la comprobación de la etapa de construcción.

### 2.8 El rol y los agentes

`sources/roles/reviewer.md` (fuente editable; los agentes son **salidas declaradas** de `scripts/cdad-generate.py`, `Makefile`:15-18) pasan a declarar: la etapa 2 además de la 4; el artefacto `plan-review.md` (además de `review.md`); y la revisión de **borrador** (no aprobado) como parte del rol. La fila de la tabla de contrato (`sources/roles/reviewer.md`:48) y el texto generado (`agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer*.md`) quedan alineados; `make agents` es **determinista** (dos corridas, mismos bytes) y `make validate` sigue verde.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **La forma del objeto se declara en el encargo.** El contrato acepta `object_kind` con valores `spec` \| `plan`; el valor viaja al `REQUEST.json` y a la metadata del paquete; un valor fuera del conjunto cerrado ⇒ rc≠0 **nombrando el valor**; una clave cualquiera no declarada ⇒ rc≠0 (el conjunto sigue cerrado); un kind `approved-*` que declare `object_kind` ⇒ **rechazo antes de publicar** (forja). | `REQUEST.json` del paquete en los tres casos; rc≠0 en cada negativo; `out-dir` sin entradas y state byte-idéntico en cada rechazo (el mismo control que `assert_rejected_without_publication`, `tests/test_004_003_t4_validation_fields.py`:399-423) |
| **PD-2** | **Por omisión, la forma es `plan` y el comportamiento vigente no cambia.** Sin `object_kind`: el objeto se trata como plan; los checks del plan se aplican; un borrador sin bloque `plan-tasks` **sigue rechazándose** con el diagnóstico vigente; un paquete con bloque malformado **sigue rechazándose**; el render de un paquete sin las claves nuevas es **byte-idéntico al de la misma revisión** medida — la garantía es **intra-revisión** (R-10, PD-16), no entre revisiones. | el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 **sin cambio de oráculo** (control negativo explícito en el RED); comparación byte a byte del render de un paquete con y sin las claves nuevas **contra el HEAD de la revisión en curso**; el test de bloque malformado (`tests/test_004_003_t4_validation_fields.py`:529) verde sin cambios |
| **PD-3** | **Una spec se revisa sin tareas artificiales.** Con `object_kind: spec`, un borrador de spec **sin** bloque `plan-tasks` es aceptado y publica paquete; con `object_kind: plan` (o ausente) el mismo archivo es rechazado; la spec **no** contiene ni se le inyecta bloque `plan-tasks`; los checks de plan **nunca** se aplican a un documento de forma `spec`. | `prepare` rc=0 con la spec; rc≠0 con los mismos bytes declarados como `plan`; el `REQUEST.json` de la spec **no** contiene el token `plan-tasks`; inspección: la rama de checks se decide por la forma declarada |
| **PD-4** | **La identidad doble fija los dos documentos por digest.** Con `--spec-path`/`--spec-version`: el contrato lleva `spec_path`, `spec_sha256` (calculado de los bytes) y `spec_version`; el digest **coincide** con `sha256sum` del archivo; un archivo acompañante **inexistente** ⇒ rc≠0 nombrando la ruta; `spec_path` sin `spec_version` (o al revés) ⇒ rc≠0 nombrando la clave ausente; el acompañante exige principal de forma `plan`; un kind `approved-*` que declare el acompañante ⇒ rechazo por forja. | los tres campos del `REQUEST.json`; `sha256sum` del acompañante comparado con el campo; los tres negativos con rc≠0 y sin publicación |
| **PD-5** | **El paquete lleva los documentos fijados y su forma.** `inputs` lleva una entrada por documento (principal primero), con `purpose` `«draft spec for review»` / `«draft plan for review»`; la sección `## Contract` del render nombra la forma y, si hay acompañante, su ruta, digest y versión; **sin** las claves nuevas el render es byte-idéntico **dentro de la misma revisión** (R-10, PD-16); la metadata del paquete lleva el contrato completo. | el `REQUEST.json` (`inputs`) y el `PACKET.md` renderizado (sección `## Contract`); comparación byte a byte del render antes/después **en la misma revisión** |
| **PD-6** | **El dictamen nombra el objeto y su digest, y vive en la carpeta de la feature activa.** Con un borrador de **otra** feature: `prepare` rc=0 con `--contract-path` de esa feature; el paquete muestra `feature_id` (la ejecución) ≠ la carpeta del `contract.path`; el dictamen se materializa **sólo** en `docs/specs/<feature activa>/` con el kind `plan-review`; un target en la carpeta de **otra** feature ⇒ rc≠0 (la tabla de destinos no se amplía); el procedimiento exige que el dictamen nombre el objeto y su digest. | `REQUEST.json` (los dos identificadores, comparables); `materialize` rc=0 con sha idéntico hacia `docs/specs/<feature activa>/plan-review.md`; `materialize` rc≠0 hacia `docs/specs/<otra>/`; texto del substage (deriva) |
| **PD-7** | **El dictamen no equivale a aprobación.** El texto del dictamen **no** contiene marca de aprobación; el recibo queda `semantic_status: pending`; la autorización de materialización exige `approval_effect: false` (`cdad_result.py`:737-739); el estado **no** registra aprobación al recibir ni al materializar; la aprobación de la spec es un acto **posterior y separado** (el pin de `stage_history`). | el texto de la entrega (grep de la marca de aprobación); los campos del recibo; el estado antes/después; la entrada de `stage_history` que habilita construcción es la de aprobación, con su pin |
| **PD-8** | **Un cambio posterior en el objeto se detecta.** Tras la revisión, cambiar el documento principal (o el acompañante) cambia su digest; el digest fijado en el `REQUEST.json` de la revisión **no** coincide con `sha256sum` del archivo ⇒ la revisión anterior no cubre esos bytes ⇒ toca re-review focal; con bytes sin cambiar, el digest fijado coincide y no hay re-review. | comparación `sha256sum` contra el `contract.sha256` / `contract.spec_sha256` del `REQUEST.json`, antes y después de la edición; los dos casos |
| **PD-9** | **La exención es del owner, explícita y registrada, y participa en la identidad de la transición — sólo cuando se declara.** `register-transition --transition gate` con `--exempted-by` + `--exemption-reason` (+ `--requested-by`, `--delegated`) escribe una entrada de `stage_history` con `exempted_by`, `reason`, `requested_by` y `delegated`; **sin** esas banderas la entrada **no** lleva esos campos; las banderas son **inadmisibles** fuera de la clase `gate`; la entrada de exención **no** habilita construcción por sí sola (el pin de aprobación sigue siendo el que manda). **Identidad (B-2, corregido por B-3):** los cuatro campos de la exención entran en el payload de identidad (`transition_key_payload`) **sólo cuando la invocación los declara** (R-11/R-12): **con** exención declarada, el payload lleva **un** bloque `exemption` con **exactamente** los campos declarados, y la `transition_key` se **recomputa** desde él; **sin** exención declarada, el payload **no** lleva bloque y es **byte-idéntico** al del producto vigente (R-13) ⇒ la repetición idéntica es **no-op** (rc=0, sin segunda entrada, state byte-idéntico, salida que nombra la entrada existente) y la repetición que **cambia** la exención (incluido el paso de *sin* exención a *con* exención y el inverso) **no** es no-op: se **registra** por `--supersedes` (la entrada previa permanece en el historial y la nueva la marca) **o** se **rechaza explícitamente** nombrando la entrada vigente y la vía permitida — **nunca** rc=0 sin registrar. **Recorrido de dos revisiones (R-13):** para `gate`, `closure` y `disposition`, una transición registrada por la revisión anterior del producto (identidad = la del producto vigente, reproducida con la **fórmula de identidad anterior**, congelada) es reconocida como **la misma** por el producto nuevo: la repetición de la misma orden **sin** exención es **no-op** (rc=0, salida que nombra la entrada existente, **sin** segunda entrada, estado **byte-idéntico**). | el `stage_history` del estado tras cada invocación; el rechazo de las banderas fuera de la clase; el rol de construcción sigue bloqueado sin la aprobación con su pin; el `transition_key_payload` de la entrada: **con** exención, un bloque `exemption` con exactamente los campos declarados; **sin** exención, **sin** bloque y **byte-idéntico** al del producto vigente (comparación byte a byte contra la fórmula anterior congelada); la `transition_key` se **recomputa** desde el payload (`canonical_digest(payload)`, el mecanismo que ya verifica `tests/test_005_012_t1_register_transition_base.py`:1212); los **dos** casos de repetición (idéntica → no-op; cambiada → registrada o rechazada); el **recorrido de dos revisiones** en sus tres clases (gate, closure, disposition) |
| **PD-10** | **El gate 2→3 y el exit gate de la etapa 2 declaran la evidencia de la revisión.** `SKILL.md` (gate 2→3) y `stage-2-specification.md` (exit gate) nombran el artefacto `plan-review.md` y la condición de bloqueantes; `re-entry.md` tiene la re-entry del dictamen; `handoff-prompts.md` declara la invocación con la forma. **Ninguna de estas superficies es un bloqueo del CLI.** **Control negativo (O-2):** con una aprobación `specification` **vigente** (pin que coincide con los bytes del contrato) y **sin** dictamen, `prepare` de un rol de construcción **se acepta** (rc=0) — el gate es **supervisado**, no un bloqueo del CLI; y, en el caso **distinto** de **sin** aprobación, el mismo `prepare` **se rechaza** con el diagnóstico `approval pending` (PD-14). Los dos casos se comprueban **en el mismo RED** y no se confunden. | deriva textual sobre las tres superficies (el patrón de deriva del proposal §6) + **los dos** controles negativos: (i) con aprobación vigente y sin dictamen ⇒ rc=0 (no se rechaza); (ii) sin aprobación ⇒ rc≠0 con `approval pending` |
| **PD-11** | **El rol y los agentes generados nombran la revisión de borrador.** `sources/roles/reviewer.md` declara la etapa 2, el artefacto `plan-review.md` y la revisión de borrador; los cuatro agentes generados lo contienen tras `make agents`; `make staging` es determinista (dos corridas, mismos bytes); `make validate` verde. | el texto de la fuente y el de los cuatro agentes generados; comparación byte a byte de dos corridas de `make staging`; salida de `make validate` |
| **PD-12** | **El procedimiento conserva sus obligaciones y su frugalidad de fuente.** El substage sigue separando validación estructural de juicio semántico, sigue exigiendo el juicio sobre la intención (un plan/spec coherente que no la alcanza es bloqueante), sigue **sin** re-enunciar la regla de detalle progresivo (la referencia por referencia) y sigue **sin** aprobar; el bloque estático del paquete del reviewer sigue por debajo del techo declarado. | los tests de 005-007 (`tests/test_005_007_t1_progressive_detail_rule.py`:295-307) verdes sin cambio; tamaño del bloque estático (`common.md` + `roles/reviewer.md` + `substages/reviewer-plan-review.md`) con la medición y el techo (`cdad_packet.py`:1015-1027) |
| **PD-13** | **El recorrido de aceptación (U6) en un proyecto descartable.** En un proyecto **descartable** (nunca el proyecto activo, nunca el HOME): (a) un borrador de **spec sin plan** se revisa, se recibe y su dictamen se materializa en `docs/specs/<F>/`; (b) un borrador de **spec + plan** se revisa con los dos digests fijados; (c) un borrador de **otra** feature se revisa y su dictamen aterriza en la carpeta de la feature activa nombrando el objeto; (d) tras corregir el borrador, el digest cambia y la re-review focal queda requerida; (e) **ninguno** de los tres reviews deja estado de aprobación; (f) el **caso de la política de compatibilidad**: un paquete publicado con las fuentes anteriores, recibido después del cambio, **es rechazado** nombrando la causa, con la salida declarada (PD-16); (g) un borrador coherente que **no alcanza la intención** produce un dictamen que declara el bloqueante (juicio semántico: la evidencia es el texto del dictamen, no una comprobación del producto). Se declaran versión y configuración observadas y **no se generaliza**. | los tres paquetes, sus `REQUEST.json` (digests), los tres recibos (`pending`), los tres dictámenes materializados con su carpeta destino, el estado resultante (sin aprobación), la comparación de digests del caso (d), la **corrida de dos fases** del caso (f) con su salida real, y el texto del dictamen del caso (g) |
| **PD-14** | **La revisión no habilita construir y no es insumo del test-writer.** Con el dictamen recibido y materializado, `prepare` para el rol test-writer **sigue rechazando** sin la entrada de aprobación con su pin; el dictamen no aparece entre las entradas del paquete del test-writer; la revisión del **resultado** (etapa 4) no se toca. | el rechazo de `prepare` (test-writer) con el diagnóstico de `approval pending`; los `inputs` del paquete del test-writer; la superficie de la etapa 4 sin cambios (grep) |
| **PD-15** | **Los guardas vigentes de pairing y de rol siguen verdes.** `draft-plan` con otra subfase ⇒ rechazo; `plan-review` sobre un kind aprobado ⇒ rechazo; `draft-plan` para un rol ≠ reviewer ⇒ rechazo; un kind `approved-*` que declare las claves nuevas ⇒ rechazo (forja). Los cuatro casos son los de `cdad_packet.py`:909-919, :920-942 y :4693-4696, ampliados por PD-1/PD-4. | los tests vigentes de 004-003 T1/T2 (`tests/test_004_003_t1_draft_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_004_003_t2_reviewfix.py`) verdes sin cambio de oráculo + los casos nuevos de forja |
| **PD-16** | **La compatibilidad está acotada a una revisión del producto, y su política está declarada y demostrada.** (a) **Dentro de una misma revisión**: un paquete sin las claves nuevas renderiza byte-idéntico (R-9, PD-2, PD-5). (b) **Entre revisiones**: un paquete publicado con las fuentes anteriores **no** es recibible después del cambio: `validate-packet`/`receive` ⇒ **rc≠0**, con un diagnóstico que nombra la **diferencia con el render canónico** (la causa: el render canónico cambió, y las fuentes de instrucción son parte de él — `cdad_result.py`:563-566). **No** hay promesa de recepción: la política es **terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la revisión vigente**, y esa salida queda **declarada** en el reference que el orquestador consulta (`re-entry.md`). (c) **El caso que lo demuestra**: publicar con las fuentes anteriores y recibir después del cambio ⇒ el resultado **observado** es el rechazo que nombra la causa, y el resultado **declarado** nombra la salida. | (a) comparación byte a byte del render **en la misma revisión**; (b) el rc≠0 y el texto del diagnóstico de `validate-packet`/`receive`; la derivación textual de `re-entry.md` (nombra la política y **las dos salidas**); (c) la **corrida de dos fases** (publicar con las fuentes anteriores → cambiar las fuentes → recibir) con su salida real pegada en la evidencia de U6 |

### 3.1 Escenarios de recorrido (E1..E7) — la vara

Cada escenario es la **intención** de la feature expresada como recorrido comprobable: si todas las PD de su fila pasan, el escenario tiene que funcionar **de verdad**. Un escenario no cubierto es un hueco: se cubre o se declara.

| Escenario | Qué tiene que funcionar (recorrido) | PD que lo garantizan | Hueco declarado |
|---|---|---|---|
| **E1** | **Una feature mediana (spec sin plan) puede ser revisada.** El architect entrega el borrador de la spec; el orquestador prepara el encargo de revisión con la **forma declarada** (`--object-kind spec`); el reviewer revisa en **sesión independiente**; el dictamen se recibe y se materializa como `docs/specs/<F>/plan-review.md`; el state **no** registra aprobación; la aprobación viene aparte. | PD-1, PD-3, PD-5, PD-7, PD-10, PD-12, PD-13, PD-14, PD-15 | **Ninguno** para el recorrido mecánico. **Declarado**: la revisión es *supervisada* — el CLI no verifica que el dictamen exista ni que sus bloqueantes estén resueltos; esa comprobación es del gate y de la autoridad (Q2, §13.4). |
| **E2** | **Una feature compleja (spec + plan) se revisa como un objeto único, con las dos identidades fijadas.** El contrato fija el plan **y** la spec por digest; el paquete lleva los dos documentos; los checks del plan se aplican **al plan** y no a la spec; el dictamen nombra **ambos** digests; una corrección en cualquiera de los dos invalida la cobertura de la revisión anterior. | PD-1, PD-2, PD-3, PD-4, PD-5, PD-8, PD-13, PD-15 | **Ninguno**. La **identidad doble** (Q4) es por digest, no por cadena de versiones: la versión de cada documento viaja **junto a** su digest, y el digest es lo comparable con `sha256sum`. |
| **E3** | **Un borrador que enmienda la spec de OTRA feature se puede revisar** — la necesidad que vino del proyecto consumidor, donde no se pudo pedir la review de un borrador de spec y el reviewer rechazó dos paquetes con razón (contrato por defecto = spec aprobada; el plan de la épica no es admisible para el reviewer; `draft-plan` exige `plan-tasks`). En la ejecución de la feature **A**, el objeto es `docs/specs/<B>/spec.md`: el paquete nombra el objeto exacto con su digest y **deja visible** que la feature activa es A y el objeto es de B; el dictamen aterriza en `docs/specs/<A>/` (la carpeta del gate que lo consume) **nombrando el objeto y su digest**; nada se materializa en la carpeta de B. | PD-1, PD-4, PD-5, PD-6, PD-7, PD-13 | **Ninguno** mecánico. **Cota declarada (Q3)**: el dictamen **no** puede vivir en la carpeta de la otra feature sin tocar la tabla cerrada de destinos — **fuera de alcance** de esta feature (y declarado como deuda, §8). |
| **E4** | **La re-review tras la corrección es focal y verificable.** El architect corrige → versión nueva → digest nuevo; la revisión anterior **no** cubre los bytes nuevos (comprobable, no declarativo); la re-review verifica **los bloqueantes acordados contra su condición de cierre** y las regresiones del arreglo (calibración, regla 4), sin abrir una caza de variantes nueva. | PD-8, PD-10, PD-12, PD-13 | **Ninguno** mecánico. **Declarado**: la re-review es **focal por la calibración**, no por una regla absoluta (§13.2: «no hay regla absoluta»); el caso de una corrección puramente mecánica puede no requerir re-review separada (calibración, regla 6). |
| **E5** | **El dictamen no aprueba ni habilita construir.** El dictamen no lleva marca de aprobación; el recibo queda `pending`; `materialize` exige `approval_effect: false`; el estado no registra aprobación; el test-writer sigue bloqueado sin el pin de aprobación de la spec. | PD-7, PD-14, PD-15 | **Ninguno**. |
| **E6** | **Un plan (o una spec) coherente entre sí pero que NO alcanza la intención es rechazado.** El revisor lo declara **bloqueante**; el architect lo corrige o la autoridad lo descarta con razón escrita; el gate 2→3 no se pasa con el bloqueante abierto. | PD-10, PD-12, PD-13 | **Declarado**: el «no alcanza la intención» es un **juicio semántico** del revisor; el producto no lo puede verificar. Lo que el producto garantiza es la **vara**: la intención viaja **como escenarios de recorrido** (§3.1) y el revisor traza cada escenario por las PD. La evidencia de que la vara funciona es el recorrido real (PD-13, caso (g)). |
| **E7** | **Un paquete publicado antes de un cambio de las fuentes de instrucción no se recibe después del cambio, y la política dice qué hacer.** Se publica un paquete de revisión con las fuentes vigentes en ese momento; se cambia una fuente de instrucción (lo que hace U2 sobre el substage y la regla de rol); la recepción de ese paquete **falla** con el rechazo que nombra la causa; el orquestador **no** intenta «arreglar» el paquete: aplica la política (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo) y la salida está **declarada** donde se consulta. | PD-16, PD-2, PD-5, PD-13 | **Ninguno** mecánico. **Declarado**: el producto **no** distingue en el mensaje la causa concreta (fuentes de instrucción vs. cualquier otro cambio del render) y **no** ofrece la salida; la salida es una **declaración del reference**, verificada por derivación textual, no por el CLI (D-12). |

## 4. Invariantes (INV-n)

- **INV-1.** La revisión de borrador **no aprueba nada**: nunca una marca de aprobación en el dictamen, nunca `semantic_status` distinto de `pending`, nunca `approval_effect: true`, nunca una entrada de estado que habilite construcción por su cuenta.
- **INV-2.** **El objeto revisado siempre está fijado por digest.** Una revisión sin digest fijado no es una revisión: el paquete lo lleva, el dictamen lo nombra y la cadena recibo → paquete → `REQUEST.json` lo hace recuperable.
- **INV-3.** **La forma se declara; nunca se infiere.** Ni por el contenido del documento (token `plan-tasks`), ni por su ruta (`spec.md`/`plan.md`), ni por el nombre del kind. La forma viaja en el encargo.
- **INV-4.** **Sin kind, subfase, agente, stage, tipo de artefacto ni verbo nuevos.** Se reutilizan `draft-plan`, `plan-review`, el rol reviewer, la etapa 2 y el kind `plan-review` → `docs/specs/<feature>/`. Los nombres se conservan **con la deuda declarada** (§10).
- **INV-5.** **Las reglas del plan no juzgan a una spec.** Los checks estructurales y por tarea se aplican exclusivamente al documento cuya forma es `plan`; una spec nunca se rechaza por no traer un bloque `plan-tasks`.
- **INV-6.** **Falla cerrado por omisión.** Sin `object_kind` declarado, el objeto se trata como plan: el comportamiento vigente se conserva y el olvido de la bandera produce un rechazo, nunca una aceptación silenciosa.
- **INV-7.** **La exención es del owner, explícita y registrada, y no amplía la autoridad.** La exención se registra en la entrada que abre el gate, con `exempted_by`, `delegated`, `requested_by` y `reason`; no cambia el pin de la aprobación, no habilita construcción y no se concede por defecto (Q5).
- **INV-8.** **El dictamen no es insumo del test-writer.** No entra en el paquete del test-writer, no lo habilita y no altera el aislamiento de ese rol.
- **INV-9.** **Una sola fuente por regla.** «Qué se revisa» vive en un único archivo (`packets/substages/reviewer-plan-review.md`); el rol, la plantilla y la re-entry lo **referencian**. La calibración sigue teniendo un único dueño (`references/stage-4-review.md`).
- **INV-10.** **El cambio es aditivo y no reescribe lo vigente — dentro de una misma revisión del producto.** Sin las claves nuevas, el render es byte-idéntico **en la misma revisión** y los oráculos vigentes se conservan (PD-2, PD-15). **Entre revisiones no se promete compatibilidad**: un paquete publicado antes de un cambio de las fuentes de instrucción se recibe con la revisión con la que se publicó, o se prepara uno nuevo bajo la revisión vigente (R-10, PD-16); los digests de las fuentes **son parte de la identidad del paquete** y la recepción los compara (`cdad_result.py`:563-566).
- **INV-11.** **El paquete no miente sobre lo que lleva.** El `purpose` de cada input describe la forma real del documento; la sección `## Contract` nombra la forma y la identidad acompañante.
- **INV-12.** **Nada se pierde en silencio.** La exención participa en la identidad de la transición **cuando se declara**: una repetición idéntica es un no-op y una repetición que la cambia —incluido el paso de *sin* exención a *con* exención y el inverso— se registra o se rechaza, **nunca** un éxito que no registre el cambio (PD-9, D-13).
- **INV-13.** **La identidad de una transición registrada sin exención no cambia por el despliegue de esta feature.** El payload y la `transition_key` son **byte-idénticos** a los del producto vigente (R-11/R-13) ⇒ las garantías de idempotencia ya aprobadas (005-012 PD-11, 005-014 PD-23, 006-005 PD-19(b)) siguen vigentes **sin enmienda** y las identidades históricas se conservan. La exención, **al declararse**, sí cambia la identidad: es lo que impide que un cambio de exención desaparezca como no-op.

## 5. Decisiones (D-n)

- **D-1 — La forma la declara el encargo (`contract.object_kind`), no el objeto.** Adoptada por el orquestador (O2). *Rechazadas:* (a) **inferencia por el contenido** (O1: si el documento lleva el token `plan-tasks`, es un plan) — infiere y además **relaja** la puerta de un plan mal formado, rompiendo el oráculo vigente de PD-8; (b) **inferencia por la ruta** (O3: `docs/specs/<X>/spec.md` es spec, `plan.md` es plan) — infiere, impone una restricción de rutas que hoy no existe (deuda ADR-013 O-C) y **rompe los fixtures compartidos** (11 archivos de test usan `DRAFT_PLAN_RELPATH`); (c) **bloque `plan-tasks` vacío dentro de la spec** (O4: hoy pasa) — mete un bloque artificial en el spec, deja el `purpose` mintiendo («draft plan for review» para una spec), mantiene el procedimiento plan-céntrico y deja el modelo mental intacto: el próximo agente repetirá el rodeo. Es el rodeo que 006-005 ya usó (commits `82f8806`, `b9a52a3`) y por eso queda **declarado como parche de emergencia**, no como diseño.
- **D-2 — El valor por omisión de la forma es `plan`.** Consecuencia: **el oráculo vigente `tests/test_004_003_t4_validation_fields.py`:427 se conserva sin cambio** y los **11 archivos de test** que comparten el fixture `DRAFT_PLAN_RELPATH` (`tests/test_004_003_t1_draft_contract.py`:47) **no se tocan** — no hay coordinación de fixtures compartidos con el test-writer. Es la dirección fail-closed: el olvido de la bandera **rechaza**, no acepta.
- **D-3 — La identidad doble viaja como dos documentos fijados, no como una cadena de versiones.** El principal es el plan cuando existe; la spec es el acompañante, fijada por `spec_path`/`spec_sha256`/`spec_version`. *Rechazada:* la versión como cadena de caracteres — el digest es lo único comparable con `sha256sum`; una cadena puede coincidir mientras los bytes no.
- **D-4 — Los checks del plan se aplican al documento cuya forma es `plan`.** Regla única, sin excepciones ni listas de excepciones.
- **D-5 — La revisión es obligatoria y proporcional; la exención es del owner, explícita y registrada.** Q5 y Q1. La profundidad la fija la calibración vigente; no se exige familia ni modelo (A-5 vigente).
- **D-6 — La exención se registra en la entrada que abre el gate**, con tres banderas opcionales nuevas sobre la clase `gate` ya existente. *Rechazadas:* (a) una entrada libre en `stage_history` — flotaría sin relación con el gate y no la verifica nadie; (b) una clase de transición nueva — amplía superficie en la maquinaria de 005-012 para un caso periférico; (c) la exención como texto dentro del `note` — la información deja de ser estructurada y por tanto no es verificable; (d) la exención como `approved_by` — confunde «quién exime» con «quién aprueba», que la decisión Q1 mantiene separados.
- **D-7 — «Qué se revisa» tiene un dueño único y el resto lo referencia.** El substage se generaliza al objeto de especificación; `packets/roles/reviewer.md`, `sources/roles/reviewer.md`, `handoff-prompts.md` y `re-entry.md` lo referencian. *Rechazada:* una segunda regla para el caso «spec sola» — dos dueños derivan.
- **D-8 — La tabla de destinos no se amplía.** El dictamen de un borrador de otra feature vive en la carpeta de la feature activa y nombra el objeto. *Rechazada:* materializar en la carpeta del objeto — tocaría la tabla cerrada (`cdad_result.py`:672-678) y ampliaría el alcance de la feature (Q3).
- **D-9 — «El dictamen nombra el digest» es obligación de procedimiento, no un enforcement nuevo en `materialize`.** Razón: el CAS de `materialize` protege el destino, no el objeto; la trazabilidad del objeto es **ya recuperable** por la cadena recibo → paquete → `REQUEST.json`; y atar el texto libre de la parte a un digest volvería frágil la recepción (un error tipográfico del revisor = fallo tardío) sin ganancia real. *Rechazada:* la comprobación en `materialize` — exigiría A-1 sobre dos tests de materialización (`tests/test_003_002_t2_reviewfix.py`:871-904 y `tests/test_006_005_u2_opencode_module.py`:1378-1392) a cambio de una garantía que la trazabilidad ya da.
- **D-10 — El gate 2→3 es supervisado.** Criterio en el gate y en el exit gate; el CLI no lo bloquea. *Rechazada:* un bloqueo duro en el CLI — el §13.4 lo excluye explícitamente.
- **D-11 — Se conservan los nombres.** `draft-plan`, `plan-review`, `plan_version` y el artefacto `plan-review.md`. La deuda está declarada (§10) y no se renombra en esta feature.
- **D-12 — La compatibilidad se acota a una revisión del producto; la consecuencia se declara, no se corrige.** El contrato no promete recepción de paquetes publicados antes de un cambio de las fuentes de instrucción: el paquete se recibe con la revisión con la que se publicó, o se prepara uno nuevo. *Razón:* los digests de las fuentes de instrucción **son parte de la identidad del paquete** (`cdad_packet.py`:1000-1004, :1037-1044) y la recepción re-renderiza y compara (`cdad_result.py`:563-566): la incompatibilidad es **inherente** al contrato de paquete, no un defecto introducido por esta feature — que además **toca dos de esas fuentes** (el substage y la regla de rol). *Precedente:* el mismo mecanismo fue juzgado en 005-003 T6 (dictamen F3, `.cdad/inbox/005-003-orientation-reduction-reviewer-review-001-review.md`:85-96) como consecuencia inherente, ruidosa y recuperable, con disposición de **deuda declarable** y **sin corregir el renderer**; esta feature aplica ese mismo precedente a su propio cambio. *Rechazadas:* (a) **prometer compatibilidad entre revisiones** — es falso y el mismo cambio de fuentes la contradice (B-1); (b) **comparar sólo el contrato y no las fuentes** — el paquete sigue embebiendo las fuentes, luego la incompatibilidad persiste; (c) **corregir el renderer** para tolerar fuentes distintas — cambia la identidad del paquete y su detección de deriva, amplía la superficie y excede el alcance; (d) **que el diagnóstico distinga la causa concreta** — no lo hace hoy y exigirlo no aporta garantía nueva: la **salida** (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo) se **declara** donde el orquestador la consulta (`re-entry.md`), como en el precedente.
- **D-13 — La exención entra en la identidad de la transición, pero sólo cuando se declara.** Los cuatro campos (`exempted_by`, `reason`, `requested_by`, `delegated`) forman parte del payload canónico de identidad **únicamente** en las invocaciones que los declaran, como **un** bloque `exemption` condicional (R-11/R-12). *Razón:* el no-op se decide por la clave **antes de escribir** (`cdad_packet.py`:5766-5770) y el payload vigente no incluye la exención (:5015-5063) ⇒ una repetición que la cambia devolvería **éxito sin registrar** y el `stage_history` perdería la información **en silencio** (B-2). *La forma (corregida por B-3):* **condicional**, porque una forma uniforme cambiaría la identidad de **todas** las transiciones, incluidas las ya registradas y las de las demás clases. *Rechazadas:* (a) **dejar la exención fuera de la identidad**, como hoy — pierde datos en silencio; (b) una **segunda entrada** para la exención — competiría con la aprobación vigente y rompería la regla de una sola aprobación (PD-14, D-6); (c) **permitir la sobreescritura silenciosa** de la exención — contradice el principio append-only (INV-3) y la regla de vigencia; la vía es `--supersedes` (que el producto ya valida) o el rechazo explícito; (d) **las cuatro claves siempre presentes con `null`** — es el diseño de draft-002, y B-3 loMq muestra con medición: la clave cambia **también** para las invocaciones sin exención y para las demás clases, con lo que una repetición idéntica deja de ser no-op y pasa a ser rechazo (gate), rechazo por feature cerrada (closure) o segunda entrada (disposition); (e) **un grupo con las cuatro claves y `null` en las no declaradas** — el mismo defecto con otro nombre: la mere presencia del grupo cambia la clave de todas las invocaciones; (f) **enmendar** 005-014 PD-23 y 006-005 PD-19(b) para aceptar las claves nuevas — sería cambiar garantías aprobadas por comodidad de una feature, y no es necesario (D-14).
- **D-14 — La identidad histórica se conserva; no hay enmienda de garantías anteriores.** El despliegue de esta feature **no** cambia la `transition_key` de ninguna transición registrada sin exención (R-13) ⇒ **no** hay enmienda de 005-014 PD-23 (replay de cierre), ni de 006-005 PD-19(b) (disposición idempotente), ni de 005-012 PD-11 (no-op del `gate`): sus oráculos siguen verdes **sin cambio de oráculo**, y sus archivos de test se **añaden** a las regresiones de U5 (`tests/test_005_014_closure_replay.py`, `tests/test_006_005_u5_disposition_failed.py`) para que la presencia del bloque condicional no pueda alterarlos en silencio. *Razón:* una feature que cambia la identidad de lo ya registrado debe **declarar** la enmienda y su alcance; aquí no hace falta, porque el cambio es condicional. *Rechazadas:* (a) **migrar o recomputar** las claves históricas — el state no se reescribe (append-only, INV-3) y no hace falta; (b) **ampliar** la deuda 005-014 E-4 — sigue REFERIDA a las entradas **sin** `transition_key_payload`, que esta feature no toca.

## 6. Desconocidos (V-n) y su resolución

- **V-1 — ¿El producto instalado (copia por archivo) renderiza el paquete con la forma declarada?** El árbol `skills/cdad-cycle/` viaja completo al instalarse (`install.sh`:376) y el substage viaja con él; lo **no medido** es el render del CLI instalado con `--object-kind`. *Resolución:* RED de la **installed product** (el patrón de `tests/test_004_003_t2_plan_review.py`:290, que ya renderiza `plan-review` desde el producto instalado sin el repo fuente), con comparación byte a byte contra el render del repo.
- **V-2 — ¿`cdad-generate.py` sigue siendo determinista con la fuente del rol cambiada?** *Resolución:* dos corridas de `make staging` con comparación byte a byte de los cuatro agentes del reviewer; si no fuera determinista, es un defecto de 004-001 ya cubierto por sus propios tests.
- **V-3 — ¿`receive` revalida el request con el conjunto de claves ampliado?** `cdad_result.py`:561 llama a `validate_request`, que es **la misma función** que `prepare` usa ⇒ el conjunto cerrado ampliado aplica en ambos lados. *Resolución:* RED que **recibe** un paquete cuyo contrato lleva `object_kind` (hoy sería rechazado por el conjunto cerrado); el RED lo demuestra, no lo supone.
- **V-4 — ¿La entrada de exención interfiere con la regla de «una sola aprobación `specification` vigente» (PD-14)?** La regla exige `stage == "specification"` **y** un pin de contrato; la exención viaja **en la misma entrada** que la aprobación, no en una entrada nueva ⇒ no hay una segunda aprobación que compita. *Resolución:* RED que registra la aprobación con exención y verifica que el cierre (PD-8(b)) la reconoce como vigente, y que una segunda aprobación sin `--supersedes` **sigue** rechazándose.
- **V-5 — ¿El techo del bloque estático admite el substage generalizado?** Medido: el bloque del reviewer/plan-review ocupa **2728 bytes** con un techo declarado de **12000** (`cdad_packet.py`:1015-1027) ⇒ holgura de 9272. *Resolución:* la medición se repite en el RED de U2 y se registra; si el substage generalizado la superara, el RED falla (y la respuesta es **no** subir el techo).
- **V-6 — ¿La política de compatibilidad se comporta como queda declarada cuando el paquete se publica con unas fuentes y se recibe con otras?** Lo **no medido** es la corrida de dos fases con el CLI real (publicar con las fuentes anteriores → cambiar las fuentes → recibir después del cambio). *Resolución:* el caso de PD-16(c) se ejecuta sobre una **copia desechable** del producto y su salida real se pega en la evidencia de U6; si el comportamiento real difiere de la política declarada, **se corrige la política** (no al revés).
- **V-7 — ¿El recorrido de dos revisiones produce de verdad el no-op con el producto real?** Lo **no medido** es la corrida real del recorrido (registrar una transición, comprobar que su identidad es la de la revisión anterior del producto, y repetir la misma orden con el producto vigente) sobre un proyecto descartable, con el CLI real como subproceso. *Resolución:* el caso de PD-9 (recorrido de dos revisiones, en sus tres clases) se ejecuta en el RED de U5 y su salida real (los rc, la salida del no-op, el conteo de entradas y el sha256 del estado antes/después) se pega en la evidencia de U6; si el comportamiento real difiere de lo declarado, **se corrige la declaración** (no al revés).

## 7. Medición de la aceptación

- Se mide lo **observado**: rc de cada comando, digests fijados y observados, carpetas destino de los dictámenes, campos de los recibos, el estado antes/después, el tamaño del bloque estático y los bytes de los dos `make staging`. **«Desconocido» no es cero** y **no se generaliza** el resultado de un recorrido.
- La **política de compatibilidad** se mide con la corrida de dos fases (PD-16(c)): los **rc** de la recepción y el **texto** del diagnóstico; la **declaración** de la salida se mide por derivación textual sobre `re-entry.md` (PD-16(b)).
- La **identidad de la transición** se mide con el **recorrido de dos revisiones** (PD-9): para `gate`, `closure` y `disposition`, la **comparación byte a byte** del `transition_key_payload` escrito contra el que produce la fórmula de identidad anterior (congelada), y los **rc**, la salida del no-op, el **conteo de entradas** y el **sha256 del estado antes/después** de la repetición sin exención.
- **No** se fijan reducciones porcentuales, tiempos ni tamaños como meta.
- La evidencia de que la **vara** (E1-E7) funciona es el recorrido real (PD-13), no una simulación: un recorrido que no atrapa ningún defecto es **buen resultado** y se declara igual (epic §13, «recepción real»).
- La **suite completa** la corre **una vez**, quien cierra (política declarada en el paquete); las unidades citan su propia evidencia focal y las regresiones de su ficha.

## 8. Fuera de alcance

1. **Ampliar la tabla cerrada de destinos** para que el dictamen de un borrador de otra feature viva en la carpeta de esa feature (D-8; Q3 lo excluye).
2. **Renombrar** `draft-plan` / `plan-review` / `plan_version` (D-11; deuda de nombre, §10). El nombre `draft-spec` que se mencionó en `execution.md`:352 **queda derogado** por `execution.md`:362-364.
3. **Un comando de comparación de digests** o de detección automática de deriva: la comparación la hace el orquestador con `sha256sum` y el `REQUEST.json` (D-9, PD-8).
4. **El bloqueo duro del gate 2→3 en el CLI** (D-10; §13.4).
5. **La revisión formal del resultado** (etapa 4) y la calibración: no se tocan.
6. **La deuda ADR-013 O-C** (restringir el `contract.path` a `docs/specs/<feature>/`): declarada, no se cierra aquí.
7. **El transporte, la delegación, la política de Bash** y las features 006-003/006-004/006-005: no se tocan.
8. **La autorización y el modelo**: la revisión no exige familia ni modelo (A-5 vigente) y no habilita construir.
9. **Corregir el renderer para tolerar fuentes de instrucción distintas** (D-12): fuera de alcance; la consecuencia y su salida se **declaran**.
10. **Migrar, reescribir o recomputar las claves históricas** ya registradas (D-14): fuera de alcance; esta feature **no** cambia ninguna.

## 9. Riesgos residuales

- **El olvido de `--object-kind` se manifiesta como un error poco informativo** (la puerta `plan-tasks`). *Mitigación:* la ayuda de diagnóstico que nombra la bandera (PD-3) sin relajar el rechazo. *Riesgo residual:* mínimo y en la dirección segura.
- **La deuda de nombre proyecta una imagen falsa** (una «plan-review» de una spec). *Mitigación:* deuda declarada (§10) y el `purpose`/la forma correctos en el paquete. *Riesgo residual:* aceptado por decisión del owner (Q6).
- **El gate supervisado puede ser saltado** por un orquestador que no siga el procedimiento (el CLI no verifica la existencia del dictamen). *Riesgo residual:* **declarado y aceptado** por §13.4; la mitigación es la disciplina del gate, no el enforcement.
- **La exención puede volverse costumbre** (es más barata que revisar). *Mitigación:* Q5 la prohíbe **por defecto** y la exige del owner, explícita y registrada; la entrada queda en `stage_history`, visible.
- **La re-review focal depende del juicio del revisor** sobre si la corrección cambió el diseño. *Riesgo residual:* la calibración (reglas 4 y 6) lo gobierna; no hay regla absoluta (§13.2) y así queda declarado.
- **Un paquete en vuelo se invalida al cambiar las fuentes de instrucción** — y esta feature cambia dos de ellas. *Mitigación:* la política declarada (D-12, PD-16): o se termina bajo la revisión con la que se publicó, o se prepara uno nuevo; el rechazo es ruidoso y nombra la diferencia con el render canónico. *Riesgo residual:* **declarado y aceptado** (precedente 005-003 F3): el mensaje **no** distingue la causa concreta ni ofrece la salida, y la salida depende de que el orquestador consulte la declaración.
- **Una exención puede seguir perdiéndose si alguien la declara fuera del verbo.** *Mitigación:* la exención sólo existe como campo estructurado de la entrada del `gate` (D-6) y **participa en la identidad cuando se declara** (D-13, R-11/R-12), de modo que una repetición que la cambia no puede ser un no-op silencioso. *Riesgo residual:* la exención sigue siendo un **acto de autoridad declarado, no una firma** (§10).
- **El payload de identidad deja de ser uniforme** (la regla vigente es «toda clave presente; un insumo ausente vale `null`») y una implementación descuidada podría volver a cambiar la identidad de todo lo registrado — el defecto exacto que B-3 señala. *Mitigación:* la regla es **una sola** (R-11: el bloque `exemption` se añade *sólo* cuando hay exención declarada; R-12: el bloque lleva exactamente los campos declarados), el **recorrido de dos revisiones** (PD-9) la comprueba en las **tres** clases, y el oráculo vigente del payload (005-012 PD-10, que recomputa la clave desde lo escrito) sigue verde. *Riesgo residual:* **declarado** — la uniformidad del payload vigente queda sustituida por una regla condicional; es el precio de conservar las identidades históricas, y queda escrito en R-11/R-13 y D-13.

## 10. Límites y deuda declarada

- **Deuda de nombre (decidida, Q6).** El kind `draft-plan`, la subfase `plan-review`, el artefacto `plan-review.md` y el campo `plan_version` **se conservan** aunque la revisión sea de una spec. Consecuencias aceptadas: `plan_version` transporta la versión del documento principal (que puede ser una spec); el `purpose` del input sí distingue la forma («draft spec for review» / «draft plan for review»); el nombre del kind y de la subfase siguen diciendo «plan». **Condición de cierre:** cuando exista una revisión del nombre, el cambio debe tocar el enum cerrado de kinds (`cdad_packet.py`:52-53), los enums de schema (`assets/packet-request.schema.json`, `assets/result-receipt.schema.json`, `assets/active-packet.schema.json`), la plantilla y los oráculos de 004-003 — es un trabajo **acotado pero de coordinación**, y esta feature no lo hace.
- **Deuda de la puerta `plan-tasks`.** El nombre del token y del bloque sigue diciendo «plan-tasks» aunque el objeto pueda ser una spec. Se conserva por el mismo motivo.
- **Deuda ADR-013 O-C.** El `contract.path` de un borrador puede ser cualquier ruta del proyecto: no hay restricción a `docs/specs/<feature>/`. Declarada en el discovery; **fuera de alcance** (§8.6).
- **Deuda de la ambientación.** El veredicto de un borrador de otra feature no puede vivir en la carpeta de esa feature (D-8, Q3).
- **Deuda de la exención en el CLI.** `delegated` y `requested_by` **sí** quedan producibles por el verbo (D-6); lo que queda fuera es la *verificación* de que la exención sea del owner y no de un tercero — la **autoridad** la verifica `register-transition` por su cuenta (`_gate_authority`), y el nombre del owner viaja como texto declarado, no como identidad criptográfica. Declarado: la exención es un acto de autoridad registrado, no una firma.
- **Deuda de la compatibilidad entre revisiones.** Un paquete publicado antes de un cambio de las fuentes de instrucción **no** es recibible después (R-10, D-12). **No** se corrige el renderer (precedente 005-003 T3/F3): la consecuencia y su salida legítima quedan **declaradas** en `re-entry.md` (PD-16) y en esta spec. Deuda **declarada**, no defecto.
- **La frontera de 005-014 E-4 no se amplía.** La deuda E-4 de 005-014 (`docs/specs/005-014-closure-replay/spec.md`:158) se refiere a las entradas registradas con la fórmula **anterior** (sin `transition_key_payload`): siguen sin reconocerse, y esta feature **no** migra ni recomputa claves históricas. Lo que esta feature conserva es la identidad de las entradas que **ya** llevan `transition_key_payload` (R-13): es un caso **distinto**, no una extensión de E-4. El cierre de B-3 es, por tanto, **por diseño** y no por deuda.

## 11. Trazabilidad con el contrato de la épica

| Aceptación (epic §13) | PD |
|---|---|
| el reviewer recibe y revisa borradores sin aprobación ficticia, incluida una spec sin plan | PD-1, PD-3, PD-5, PD-7, PD-13 |
| puede rechazar una spec y un plan coherentes entre sí que no cumplen la intención | PD-10, PD-12, PD-13 (E6) |
| el dictamen no equivale a aprobación | PD-7, PD-14 |
| un cambio en la spec o en el plan después de la revisión se detecta | PD-8, PD-4 |
| la conducta está en los artefactos instalados | PD-1..PD-6, PD-10, PD-11 (V-1) |
| `make validate` y la suite pasan | PD-11, PD-12 + plan §5 |

**Garantía propia de la feature** (no es un ítem de aceptación de la épica): la compatibilidad **acotada a una revisión**, su política declarada y su caso demostrativo → PD-16, E7.

**Garantía propia de la feature** (derivada del dictamen B-3): la identidad de las transiciones ya registradas **se conserva** —sin exención, el payload y la clave son byte-idénticos a los del producto vigente— y por tanto **no hay enmienda** de 005-014 PD-23, 006-005 PD-19(b) ni 005-012 PD-11 → PD-9 (recorrido de dos revisiones), R-11/R-12/R-13, INV-13, D-13/D-14, V-7.
===END spec.md===

===BEGIN plan.md===
# 006-006-spec-plan-review — PLAN (etapa 2, borrador draft-003)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (PD-21 del plan de 006-005, y §13.3 de la enmienda 006: la revisión del borrador precede al RED).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §13 (sha256 `d6da11db…9809`). Spec: la de esta carpeta (misma entrega). Decisiones: `docs/epics/epic-006-opencode-concurrency/execution.md`:379-388.
Correcciones de draft-003 (dictamen `docs/specs/006-006-spec-plan-review/plan-review-002.md`, 1 bloqueante): **B-3** → la exención entra en el payload de identidad **sólo cuando se declara** (spec §2.7 R-11/R-12/R-13, PD-9, INV-12/INV-13, D-13/D-14, V-7) → toca §3 U5 (la zona del payload pasa a **condicional**; el RED gana el **recorrido de dos revisiones** en `gate`, `closure` y `disposition`; las regresiones ganan `tests/test_005_014_closure_replay.py` y `tests/test_006_005_u5_disposition_failed.py`) y §4 (la fila «la identidad de la transición» reescrita: el análisis de draft-002 estaba equivocado, y por qué). Todo lo demás de draft-002 se conserva.
Base medida: el **código** no cambió desde el HEAD `7f39e24` (verificado: `git log 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/` vacío; el HEAD documental vigente es `6c8ad04`). Medición: el bloque estático del paquete del reviewer ocupa **2728 bytes** con techo declarado de **12000** (`skills/cdad-cycle/scripts/cdad_packet.py`:1015-1027). Anonimización como en la spec.
Base de los fixtures: `DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"` (`tests/test_004_003_t1_draft_contract.py`:47), usado por **11** archivos de test — **esta feature no toca ninguno** (D-2, §4).

## 1. Orden y dependencias

`U1 (objeto declarado en el CLI) → U5 (exención registrada e identificada) → U2 (fuente canónica) → U3 (recorrido y gate) → U4 (rol y agentes) → U6 (recorrido de aceptación)`.

- **U1 y U5 tocan el mismo archivo** (`skills/cdad-cycle/scripts/cdad_packet.py`), en zonas distintas (la del contrato/`prepare` y la del registro de transiciones **y su payload de identidad**): la ejecución es **secuencial** y ninguna se declara `parallel` con otra (paralelismo inseguro: el CLI lo rechaza, `cdad_packet.py`:3490-3506).
- **U2 → U3 → U4** es una cadena de textos: U2 fija **qué se revisa** (el dueño único), U3 lo enruta en el recorrido y el gate y **declara la política de compatibilidad** en `re-entry.md`, U4 lo propaga al rol y a los agentes generados. U2 precede a U3 y U3 precede a U4 porque cada uno consume el texto del anterior.
- **U6** depende de todo: es el recorrido real.
- Ninguna unidad empieza sin su RED declarado y sin la revisión de spec/plan hecha (gate 2→3 con el criterio nuevo, PD-10).

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | **El objeto declarado en el contrato:** `contract.object_kind`, el acompañante `spec_path`/`spec_sha256`/`spec_version`, los checks del plan **sólo** sobre el documento de forma `plan`, `inputs` por documento, el render que nombra la forma, y la ayuda de diagnóstico | — | PD-1, PD-2, PD-3, PD-4, PD-5, PD-15, **PD-16(a)** | RED + focales GREEN + regresiones de contrato/packets (A-1) + `make validate` |
| **U5** | **La exención registrada **e incluida en la identidad de la transición, pero sólo cuando se declara:** tres banderas opcionales (+ un interruptor) en la clase `gate` de `register-transition`, con `exempted_by`, `delegated`, `requested_by` y `reason` en la entrada, y un **bloque `exemption` condicional** en el payload de identidad (repetición idéntica = no-op; repetición que cambia la exención = registrada por `--supersedes` o rechazada, nunca éxito sin registrar) **sin** cambiar la identidad de ninguna transición ya registrada | U1 | PD-9, PD-1 (forja) | RED + focales GREEN + regresiones de transiciones/estado (incluidas las dos de O-1 y las dos nuevas de B-3) + `make validate` |
| **U2** | **La fuente canónica de «qué se revisa»:** el substage generalizado al objeto de especificación y la regla de rol sin plan-centrismo, **conservando** sus obligaciones vigentes | U1 | PD-6 (procedimiento), PD-12 | RED de texto + regresiones de 005-007 (detalle progresivo) + `make validate` |
| **U3** | **El recorrido principal y el gate:** subfase y exit gate de la etapa 2, criterio del gate 2→3, re-entry del dictamen, **declaración de la política de compatibilidad**, invocación con la forma y la identidad doble | U2 | PD-10, PD-14, **PD-16(b)** | RED de texto (deriva) + los dos controles negativos de PD-10 + regresiones de la skill + `make validate` |
| **U4** | **El rol y los agentes generados:** la fuente del reviewer declara etapa 2, el artefacto `plan-review.md` y la revisión de borrador; `make agents` | U3 | PD-11 | RED de texto + `make staging` determinista + `make validate` |
| **U6** | **Recorrido de aceptación** (no es unidad de código): E1..E7 sobre un proyecto **descartable** | U1–U5 | PD-13, PD-8, PD-14, **PD-16(c)** | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1 — El objeto declarado en el contrato

- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_packet.py`, **cuatro zonas**:
    1. el conjunto cerrado de claves del contrato (`contract_keys`:879-883) extendido de forma aditiva con `object_kind`, `spec_path`, `spec_sha256`, `spec_version`; la **forja** (:890-898) extendida para que un kind `approved-*` que declare cualquiera de ellas se rechace antes de publicar;
    2. `prepare` (:4671-4699): las banderas `--object-kind`, `--spec-path`, `--spec-version`; el digest del acompañante **calculado de los bytes** (no afirmado); la regla todo-o-nada; el rechazo si el acompañante no existe; el acompañante sólo con principal de forma `plan`;
    3. la rama de checks (:4718-4721): se aplica **al documento principal si su forma es `plan`**; la ayuda de diagnóstico que nombra `--object-kind` cuando la forma no fue declarada y la puerta `plan-tasks` rechaza;
    4. la construcción de `inputs` (:4790-4792, una entrada por documento fijado, con su `purpose`) y el render (:998-1059: metadata :1028, sección `## Contract` :1045-1047, sección `## Inputs` :1051-1052 — **aditivas**: sin las claves nuevas el render es byte-idéntico **dentro de la misma revisión** del producto; la garantía **entre** revisiones no existe, R-10/PD-16).
- **RED:** `tests/test_006_006_u1_draft_object_form.py` (nuevo) —
  - **PD-1**: `object_kind: spec` y `object_kind: plan` en el `REQUEST.json`; valor fuera del conjunto cerrado ⇒ rc≠0 **nombrando el valor**; clave desconocida ⇒ rc≠0; kind `approved-*` con `object_kind` ⇒ **rechazo sin publicar** (out-dir vacío, state byte-idéntico).
  - **PD-2 (control negativo explícito):** **sin** `--object-kind`, un borrador sin bloque `plan-tasks` **sigue rechazándose** con el diagnóstico vigente que nombra `plan-tasks` — *el oráculo de `tests/test_004_003_t4_validation_fields.py`:427 se conserva; este caso es su control negativo dentro del RED nuevo, no una reescritura del oráculo vigente*; un bloque malformado **sigue rechazándose**; el render de un paquete sin las claves nuevas es **byte-idéntico** al del HEAD medido **en esa misma revisión** (la garantía es **intra-revisión**: la prueba *entre* revisiones es PD-16, U6).
  - **PD-3**: con `--object-kind spec`, un borrador de spec **sin** `plan-tasks` es aceptado y publica paquete; los mismos bytes declarados `plan` ⇒ rc≠0; la spec del `REQUEST.json` **no** contiene el token `plan-tasks` (no hay tareas artificiales inyectadas).
  - **PD-4**: `--spec-path` + `--spec-version` ⇒ `spec_path`, `spec_sha256` (igual a `sha256sum` del archivo) y `spec_version` en el contrato; acompañante inexistente ⇒ rc≠0 nombrando la ruta; `spec_path` sin `--spec-version` (y el inverso) ⇒ rc≠0 nombrando la clave; acompañante con principal de forma `spec` ⇒ rc≠0; kind `approved-*` con el acompañante ⇒ rechazo por forja.
  - **PD-5**: `inputs` con una entrada por documento, en orden (principal, acompañante), con `purpose` `«draft spec for review»` / `«draft plan for review»`; el render nombra la forma y la identidad del acompañante; **control negativo**: render byte-idéntico sin las claves nuevas **en la misma revisión**.
  - **PD-16(a)**: la misma comparación byte a byte **es** la garantía intra-revisión; el RED **no** afirma (ni comprobaría) nada *entre* revisiones — esa parte es la **declaración** de U3 y el **caso** de U6, y su honestidad está en que la feature **no** promete compatibilidad entre revisiones (R-10).
  - **PD-15**: los cuatro guardas vigentes (draft con otra subfase; plan-review sobre kind aprobado; draft para rol ≠ reviewer; forja ampliada) **verdes sin cambio de oráculo**.
  - Fixture: proyecto descartable con el patrón de `tests/test_004_003_t2_plan_review.py` (`PrepareProject`), con **fixtures propios** (no el compartido `DRAFT_PLAN_RELPATH`): un borrador de spec y un borrador de plan, ambos con digest y versión propios.
- **Regresiones:** `tests/test_004_003_t1_draft_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_004_003_t2_plan_review.py`, `tests/test_004_003_t2_reviewfix.py`, `tests/test_004_003_t3_plan_checks.py`, `tests/test_004_003_t4_validation_fields.py`, `tests/test_005_007_t2_progressive_plan_validator.py`, `tests/test_005_007_t6_templates.py`, `tests/test_005_007_reviewfix_blockings.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t2_reviewfix.py`, `tests/test_006_005_u2_opencode_module.py`, `tests/test_packet_prepare.py`, `tests/test_role_packet_render.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED declarado y fallando por la razón correcta; GREEN focal; las regresiones listadas verdes **sin cambio de oráculo**; `make validate`. La **installed product** (V-1) se verifica en el RED: el CLI instalado renderiza el paquete con la forma declarada, byte a byte igual que el del repo (el patrón de `tests/test_004_003_t2_plan_review.py`:290).

### U5 — La exención registrada e incluida en la identidad de la transición, sólo cuando se declara

- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — **tres** zonas:
  1. el parser de `register-transition` (~:6425-6480): tres banderas opcionales y un interruptor — `--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`; admisibles **sólo** con `--transition gate` (fuera de esa clase ⇒ rc≠0 nombrando la clase);
  2. la construcción de la entrada de la clase `gate` (~:5849-5856): la entrada suma `exempted_by`, `reason`, `requested_by` y `delegated` **sólo** cuando las banderas están presentes (planos, en la entrada);
  3. **el payload canónico de identidad** (`_transition_identity_payload`, :5015-5063) y la decisión de no-op (:5766-5770) — **zona cambiada por B-3**: el payload se construye **exactamente como hoy** (16 claves) y **sólo** cuando la invocación **declara** la exención (alguna de las cuatro banderas) se le añade **una** clave, `exemption`, con **exactamente** los campos declarados (R-11/R-12). **Sin** exención declarada: **ni una clave cambia** ⇒ la serialización canónica (:5077-5079) y la `transition_key` son **byte-idénticas** a las del producto vigente (R-13) ⇒ las entradas ya registradas siguen reconociéndose como la misma transición, y la repetición idéntica de una transición registrada por la revisión anterior del producto sigue siendo un **no-op**.
- **No se toca** la decisión de no-op (:5766-5770), ni la regla de una sola aprobación vigente (PD-14, :5789-5829), ni el pin de la aprobación: la exención **viaja en la misma entrada** que la aprobación, y la vía de corrección de una exención es la que el producto **ya** ofrece (`--supersedes`, :5812-5820) o el **rechazo explícito** de :5821-5829.
- **RED:** `tests/test_006_006_u5_exemption_record.py` (nuevo) — **PD-9**:
  - la invocación con las cuatro banderas escribe una entrada de `stage_history` con `exempted_by`, `reason`, `requested_by` y `delegated`;
  - la invocación **sin** ellas escribe una entrada **sin** esos campos (control negativo);
  - las banderas fuera de la clase `gate` ⇒ rc≠0 nombrando la clase;
  - la entrada de exención **no habilita construcción** (un `prepare` de un rol de construcción sigue rechazando sin la aprobación con su pin);
  - **V-4**: la aprobación con exención sigue siendo **vigente** para el cierre (PD-8(b)) y una segunda aprobación sin `--supersedes` **sigue** rechazándose;
  - **identidad, los dos casos (B-2):** (a) **repetición idéntica** (misma exención) ⇒ rc=0, **no-op**, **sin** segunda entrada, state byte a byte idéntico y salida que nombra la entrada existente; (b) **repetición que cambia la exención** ⇒ **no** es no-op: se **registra** por `--supersedes <transition_key>` (la entrada previa sigue en el historial y la nueva la marca) **o** se **rechaza explícitamente** nombrando la entrada vigente y la vía permitida — **en ningún caso** rc=0 sin registrar; el `transition_key_payload` de la entrada lleva el bloque `exemption` con **exactamente** los campos declarados (y **sin** bloque cuando la invocación no declara exención) y la `transition_key` se **recomputa** desde él.
  - **recorrido de dos revisiones (B-3) — los tres casos**, `gate`, `closure` y `disposition`: (i) se registra la transición con el CLI real; (ii) se comprueba que el `transition_key_payload` escrito es **byte-idéntico** al que produce la **fórmula de identidad anterior** — congelada en el propio test, como copia literal de `_transition_identity_payload` y de la serialización canónica, en la forma que tenía al abrirse este RED; y que la `transition_key` es la misma; (iii) se **repite la misma orden** (sin exención) ⇒ rc=0, la salida nombra la entrada existente (su `transition_key`, la histórica), **no** hay segunda entrada y el estado queda **byte-idéntico** (sha256 antes = después). **El recorrido no es una simulación del binario anterior**: el producto anterior queda representado por **su fórmula de identidad**, que es la única parte que determina el reconocimiento entre revisiones (`_registered_transition` compara el `transition_key` exacto, :5098-5108); el resto de la entrada y los efectos sobre el estado los produce el **CLI real**. **Declarado en el propio RED**: estos tres casos son **controles de no-regresión** —pasan con el producto vigente y **deben** seguir pasando con el producto nuevo—, mientras que los casos de la exención son los que **fallan** al abrir el RED.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t2_gate_authority.py` **(O-1)**, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_012_t5_approval_vigency.py` **(O-1)**, `tests/test_005_014_closure_replay.py` **(B-3)**, `tests/test_006_005_u5_disposition_failed.py` **(B-3)**, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
  - **Por qué estas dos (O-1):** `tests/test_005_012_t2_gate_authority.py` cubre precisamente **autoridad, campos e idempotencia** del `gate` (incluido `test_pd11_identical_gate_repetition_is_noop_byte_identical`, :630 — el no-op que la identidad debe conservar) y `tests/test_005_012_t5_approval_vigency.py` la **vigencia** que U5 promete conservar (incluido `test_pd14_second_vigente_without_supersedes_fails_closed`, :341, y `test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop`, :622). Son la **regresión focal** del acoplamiento que B-2.questiona; la suite del cierre reduce el riesgo pero no la sustituye.
  - **Por qué estas dos (B-3):** `tests/test_005_014_closure_replay.py` fija el **replay de cierre** de 005-014 (PD-23: `test_pd23_identical_closure_replay_is_noop_naming_the_registered_entry`, :220 — repetir la misma orden de cierre ⇒ rc=0, no-op que nombra la entrada, estado byte-idéntico y **una sola** entrada `closure`) y `tests/test_006_005_u5_disposition_failed.py` fija la **idempotencia de la disposición** de 006-005 (PD-19(b): `test_pd19_b_identical_disposition_is_a_byte_identical_noop`, :376 — repetir la misma disposición ⇒ rc=0, **sin** segunda entrada, estado byte-idéntico). Son los dos oráculos que **se rompen** si el payload de identidad cambia para las invocaciones sin exención: el replay de cierre pasó a ser **rechazo** (rama de feature cerrada, :5622-5633) y la disposición pasó a escribir una **segunda entrada** (con el estado reescrito). Con la forma condicional de R-11/R-12 siguen verdes **sin cambio de oráculo**.
- **A-1:** **ninguna** (§4) — los oráculos vigentes de estos archivos **recomputan** la clave desde el payload escrito y comprueban campos sueltos; no fijan el conjunto de claves del payload ni un digest literal (verificado sobre el código, §4). Los dos ficheros nuevos de B-3 **tampoco** se tocan: se **ejecutan**.
- **Gate:** RED + focales; los **tres** casos del recorrido de dos revisiones verdes; regresiones de transiciones verdes (con las dos de O-1 y las dos de B-3); `make validate`.

### U2 — La fuente canónica de «qué se revisa»

- **Archivos:**
  - `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` (una sola línea): el objeto pasa de «un PLAN DRAFT» al **objeto de especificación** — intención declarada, restricciones y decisiones aplicables, **spec**, **plan cuando existe**, contratos y capacidades necesarias para ejecutar y obtener evidencia — conservando **verbatim** sus obligaciones vigentes: separación entre validación estructural y juicio semántico, el juicio sobre la intención (un plan/spec coherente que no la alcanza es bloqueante), la taxonomía del efecto, el umbral de confianza, el verdict-tuple, la sección `## Abstentions`, «la revisión no es aprobación» y el **consumo del marcador `detail` por referencia** a su regla canónica (regresión de 005-007 PD-12). **Se le suma** la obligación de que el dictamen **nambre el objeto revisado y su digest** (D-9, PD-6).
  - `skills/cdad-cycle/packets/roles/reviewer.md` (una sola línea): la regla «qué revisar» deja de ser plan-céntrica — «el objeto que el contrato declara, **con su forma declarada** (spec o plan)».
- **RED:** `tests/test_006_006_u2_review_procedure.py` (nuevo) — deriva textual: el substage nombra la spec **y** el plan, no dice «PLAN DRAFT» como objeto único, conserva las obligaciones vigentes (juicio sobre la intención; separación estructural/semántico; `## Abstentions`; «never mark the reviewed draft approved»; el marcador `detail` **por referencia**, sin re-enunciar la regla) y **exige** nombrar el objeto y su digest; la regla de rol dice «el objeto que el contrato declara» y no «the plan draft». **Control negativo**: el substage **no** re-enuncia la regla de detalle progresivo (la referencia, no la copia).
- **Regresiones:** `tests/test_005_007_t1_progressive_detail_rule.py` (el substage debe seguir consumiendo el marcador **por referencia** — su oráculo **no** cambia), `tests/test_005_007_t6_templates.py`, `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` se compone con el substage sha-pinned byte a byte), `tests/test_role_packet_render.py`, `tests/test_role_packets.py`.
- **Gate:** RED de texto verde; regresiones verdes; `make validate`; **medición del bloque estático** (`common.md` + `roles/reviewer.md` + `substages/reviewer-plan-review.md`) registrada y **por debajo del techo de 12000 bytes** (V-5: la holgura medida hoy es de 9272).

### U3 — El recorrido principal, el gate y la política de compatibilidad

- **Archivos:**
  - `skills/cdad-cycle/references/stage-2-specification.md`: la subfase de la etapa 2 (preparar/despachar el paquete `plan-review` sobre el borrador, recibir el dictamen, rutear los bloqueantes al architect o a la autoridad, re-review focal si la corrección cambió el diseño, y recién entonces la aprobación) y el **exit gate** (que nombra el artefacto `plan-review.md` y la condición de bloqueantes). **Además**, la **forma declarada de la exención** (los cuatro campos) queda enunciada aquí, que es el dueño canónico del procedimiento de la etapa 2.
  - `skills/cdad-cycle/SKILL.md`: un criterio en el **gate 2→3** (espejo del gate 4→5, `SKILL.md`:361-366) y el **mapa del ciclo** (la flecha Stage 2→Stage 3, hoy rotulada «gate: spec.md approved by the user», :299) que nombra la revisión del borrador.
  - `skills/cdad-cycle/references/re-entry.md`: la re-entry del **dictamen de borrador** (qué hacer con él: corregir, re-review focal, exención) junto a la re-entry del architect (:148-172) y, **junto a ella, la declaración de la política de compatibilidad** (B-1, R-10, D-12, PD-16(b)): que un paquete rechazado por diferir de su render canónico fue publicado bajo otra revisión de las fuentes de instrucción, y que la salida es **terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la revisión vigente**. Es **declaración de procedimiento** (derivación textual), no un cambio del renderer (D-12: el CLI no distingue hoy la causa concreta y esta feature no lo cambia).
  - `skills/cdad-cycle/references/handoff-prompts.md`: la plantilla del reviewer (`plan-review`) que declara la invocación **con la forma** (`--object-kind`) y la identidad doble (`--spec-path`, `--spec-version`), **sin re-enunciar el procedimiento** (que sigue en el substage).
- **RED:** `tests/test_006_006_u3_review_route_and_gate.py` (nuevo) — deriva textual sobre las cuatro superficies: el exit gate de la etapa 2 y el gate 2→3 nombran el artefacto `plan-review.md` y la condición de bloqueantes; el mapa del ciclo nombra la revisión; la re-entry del dictamen existe; la plantilla declara las banderas de la forma y de la identidad doble y **no** re-enuncia el procedimiento. **Control negativo de PD-10, rehecho (O-2) — los dos casos, que son distintos entre sí:**
  - **(i) con aprobación vigente y sin dictamen** (se registra una aprobación `specification` con el pin que coincide con los bytes del contrato, y **no** hay `plan-review.md`): `prepare` de un rol de construcción ⇒ **rc=0, no se rechaza** — el gate 2→3 es **supervisado** y el CLI no verifica la existencia del dictamen;
  - **(ii) sin aprobación** (el caso de PD-14): el mismo `prepare` ⇒ **rc≠0** con el diagnóstico `approval pending`.
  - El caso (i) es el que **demonstra** que el gate no es un bloqueo; el (ii) demuestra que la aprobación sí lo es. Confundirlos (O-2) es lo que hacía el control viejo.
  - **PD-16(b)**: la derivación textual de `re-entry.md` nombra la política (un paquete publicado antes de un cambio de las fuentes de instrucción no es recibible después) y **las dos salidas** (terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la revisión vigente).
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_cdad_generate.py`, `tests/test_005_007_t1_progressive_detail_rule.py`, `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_003_002_t2_materialize.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED de texto verde; los **dos** controles negativos de PD-10 verdes; regresiones verdes; `make validate`.

### U4 — El rol y los agentes generados

- **Archivos:**
  - `sources/roles/reviewer.md` (fuente editable): la fila de la tabla de contrato (:48) declara **etapas 2 y 4**, el artefacto `plan-review.md` **además** de `review.md`, y el texto de la fila dice que la revisión de borrador es parte del rol; la sección de directiva nombra la revisión de **borrador no aprobado** como parte del encargo del rol. El resto del texto (calibración, taxonomía, veredicto, aislamiento) **no se toca**.
  - `agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer.md`, `agents/claude-code/cdad-reviewer-odoo.md`: **salidas declaradas** de `scripts/cdad-generate.py` (`Makefile`:15-18) — **nunca se editan a mano**.
- **RED:** `tests/test_006_006_u4_reviewer_role_agents.py` (nuevo) — la fuente nombra la etapa 2, el artefacto `plan-review.md` y la revisión de borrador; los **cuatro** agentes generados lo contienen tras `make agents`; `make staging` es **determinista** (dos corridas, mismos bytes) — control de V-2; y `make validate` verde.
- **Regresiones:** `tests/test_cdad_generate.py`, `tests/test_role_packet_render.py`, `tests/test_005_006_t2_intake.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_006_002_u1_delegation_section.py`, `tests/test_006_002_u3_runtime_references.py`, `tests/test_006_003_u3_texts_without_profiles.py`, `tests/test_006_005_u4_single_entry.py` (si existe con ese nombre; si no, el test de texto equivalente de U4 de 006-005).
- **A-1:** **ninguna** (§4).
- **Gate:** `make staging` determinista; RED de texto verde; regresiones verdes; `make validate`.

### U6 — Recorrido de aceptación (no es unidad de código)

- **Escenario (PD-13, contra E1..E7 de §3.1 de la spec):** en un proyecto **descartable** (nunca el HOME, nunca el proyecto activo):
  - **(E1)** un borrador de **spec sin plan** se revisa: `prepare --role reviewer --substage plan-review --contract-kind draft-plan --contract-path <spec> --plan-version <v> --object-kind spec` ⇒ rc=0; el paquete lleva la forma en la metadata y el `purpose` «draft spec for review»; el dictamen se recibe (`semantic_status: pending`) y se materializa en `docs/specs/<F>/plan-review.md` con sha idéntico; **el estado no registra aprobación**;
  - **(E2)** un borrador de **spec + plan**: el contrato fija los dos por digest (`--object-kind plan` + `--spec-path`/`--spec-version`); los checks del plan se aplican **al plan**; el paquete lleva los dos documentos; el dictamen nombra ambos digests;
  - **(E3)** un borrador de **otra** feature (`docs/specs/<B>/spec.md`) con la ejecución de **A**: rc=0; el paquete muestra `feature_id` = A y el `contract.path` de B; el dictamen se materializa **sólo** en `docs/specs/<A>/` y nombra el objeto y su digest; un target en `docs/specs/<B>/` ⇒ rc≠0;
  - **(E4)** tras editar el borrador, `sha256sum` del archivo ≠ el digest fijado en el `REQUEST.json` de la revisión ⇒ la revisión anterior no cubre esos bytes ⇒ re-review focal requerida (y se registra el caso de bytes sin cambiar, donde el digest coincide);
  - **(E5)** el dictamen **no** aprueba: sin marca de aprobación, recibo `pending`, `approval_effect: false`, y `prepare` para el test-writer **sigue rechazando** sin la entrada de aprobación con su pin;
  - **(E6)** un borrador **coherente que no alcanza la intención** produce un dictamen que **declara el bloqueante** — juicio **semántico** del revisor: la evidencia es el **texto del dictamen**, no una comprobación del producto;
  - **(E7) — el caso de la política de compatibilidad (B-1, PD-16(c)):** en una **copia desechable** del producto, (i) se **publica** un paquete de revisión con las fuentes de instrucción **de ese momento**; (ii) se **cambia** una de esas fuentes (el mismo cambio de forma que U2 aplica sobre el substage y la regla de rol); (iii) se **recibe** ese paquete con la copia ya cambiada ⇒ el resultado **observado** es un **rc≠0** cuyo diagnóstico nombra la **diferencia con el render canónico** (`cdad_result.py`:563-566); y (iv) el resultado **declarado** nombra la **salida**: terminarlo bajo la revisión con la que se publicó, o preparar uno nuevo bajo la revisión vigente. La **salida** está **declarada** en `re-entry.md` (PD-16(b)) y el caso **no** la ejecuta automáticamente: el producto no la ofrece.
- **Evidencia:** los tres paquetes y sus `REQUEST.json` (digests y forma), los tres recibos, los tres dictámenes materializados con su carpeta destino, el estado antes/después (sin aprobación), la comparación de digests del caso E4, el texto del dictamen del caso E6, la **salida real de la corrida de dos fases del caso E7** (los rc de las dos recepciones y el texto del diagnóstico) y la **salida real del recorrido de dos revisiones** de U5 (PD-9: los tres rc de no-op, las tres salidas que nombran la entrada, los tres conteos de entradas y los tres sha256 del estado antes/después). Se entrega como **documento de evidencia** en la carpeta de la spec (no en `tests/`). Sin generalizar (spec §7).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (CLI no disponible, proyecto no inicializable, estado incoherente), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el owner/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo.

**Resultado de la evaluación: esta feature NO reemplaza ningún oráculo vigente.** Es la consecuencia de D-2 (la forma por omisión es `plan`), de D-13/D-14 (la identidad se **extiende de forma condicional**, no se redefine) y de R-13 (sin exención, el payload no cambia):

| Superficie acoplada | Test | Evaluación |
|---|---|---|
| **La puerta `plan-tasks`** | `tests/test_004_003_t4_validation_fields.py`:427 (`test_pd8_plan_without_the_block_is_rejected`) | **NO APLICA — el oráculo se conserva sin cambio.** El fixture declara un borrador **sin** `--object-kind` ⇒, por omisión, su forma es `plan` ⇒ los checks del plan se aplican ⇒ el rechazo y el diagnóstico vigente (que nombra `plan-tasks`) siguen siendo los exactos. El RED de U1 lo **vuelve a comprobar como control negativo** (mismo fixture, sin la bandera ⇒ mismo rechazo), de modo que el oráculo vigente queda **fijado**, no sólo no-roto. *Lo que sí se declara en el RED de U1:* el caso **nuevo** «mismos bytes declarados `spec` ⇒ aceptado», que es un caso **adicional**, no un reemplazo. |
| **Los fixtures compartidos** | `DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"` (`tests/test_004_003_t1_draft_contract.py`:47), usado por **11** archivos de test: `test_003_002_t2_reviewfix.py`, `test_004_003_t1_draft_contract.py`, `test_004_003_t1_reviewfix.py`, `test_004_003_t2_plan_review.py`, `test_004_003_t2_reviewfix.py`, `test_004_003_t3_plan_checks.py`, `test_004_003_t4_validation_fields.py`, `test_005_007_reviewfix_blockings.py`, `test_005_007_t2_progressive_plan_validator.py`, `test_005_007_t6_templates.py`, `test_006_005_u2_opencode_module.py` | **NO APLICA — ningún fixture compartido se modifica.** La ruta del fixture sigue siendo válida (es un borrador de forma `plan` por omisión) y su contenido sigue siendo un plan con `plan-tasks`. Los tests nuevos de U1 usan **fixtures propios** (spec y plan, con digest y versión propios). Esto evita la coordinación con el test-writer sobre fixtures compartidos que la opción O3 del discovery habría exigido. |
| **El contrato del paquete** | `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` lleva el plan, el contrato y la versión) | **NO APLICA.** El paquete sin las claves nuevas renderiza **byte-idéntico** (PD-5, control negativo, **dentro de la misma revisión**) y su `REQUEST.json` conserva las claves actuales. El RED de U1 **extiende** este patrón con el caso de la forma `spec` en el archivo **nuevo**, sin tocar el test vigente. |
| **La materialización del dictamen** | `tests/test_003_002_t2_reviewfix.py`:871-904 (la fila `reviewer/plan-review` con contrato `draft-plan` se materializa) | **NO APLICA.** No se toca `cdad_result.py`: el kind `plan-review` y su destino ya existen (`assets/artifact-policy.json`:9; `cdad_result.py`:681-706). D-9 **rechaza** añadir la comprobación del digest en la parte, precisamente para no tener que reescribir este oráculo ni el de `tests/test_006_005_u2_opencode_module.py`:1378-1392. |
| **El kind derivado de la entrega** | `tests/test_006_005_u2_opencode_module.py`:1378-1392 (PD-23) | **NO APLICA.** Sin cambios en la tabla cerrada ni en el derivador. |
| **El substage y la regla de rol** | `tests/test_005_007_t1_progressive_detail_rule.py`:295-307 (el substage consume el marcador `detail` por referencia) | **NO APLICA — el oráculo no cambia, pero es un acoplado de U2.** La reescritura del substage (U2) **debe conservar** la mención del marcador `detail` y la **referencia** a su regla canónica. Si el RED de U2 las perdiera, ese test **fallaría**: es la red de seguridad, no un reemplazo. |
| **La exclusión de una segunda aprobación vigente** | `tests/test_005_012_t3_closure_dispatch_resolution.py` | **NO APLICA.** La exención **viaja en la misma entrada** que la aprobación (D-6): no hay una segunda entrada que compita. El RED de U5 lo comprueba en los dos sentidos (la aprobación con exención es vigente; una segunda aprobación sin `--supersedes` sigue rechazándose). |
| **La identidad de la transición (B-2, corregido por B-3)** | `tests/test_005_012_t1_register_transition_base.py`:1212 (`test_pd10_entry_carries_a_recomputable_transition_key_payload`), `tests/test_005_012_t2_gate_authority.py`:630 (`test_pd11_identical_gate_repetition_is_noop_byte_identical`), `tests/test_005_012_t5_approval_vigency.py`:341 y :622 | **NO APLICA — el oráculo vigente no fija el conjunto de claves del payload ni un digest literal.** Comprobado sobre el código: el oráculo de :1212 **recomputa** la clave desde el payload **escrito** (`canonical_digest(payload)`) y el de :1253 comprueba **campos sueltos** del payload; ninguno fija el conjunto de claves. **Corrección al análisis de draft-002:** draft-002 sostenía que añadir los cuatro campos de la exención (con `null` cuando la invocación no los declara) dejaba esos oráculos intactos «porque los campos ausentes se normalizan igual» — **eso es falso**, y es exactamente lo que B-3 mide: los cuatro `null` cambian la clave **también** para las invocaciones **sin** exención y para las demás clases, de modo que una repetición idéntica deja de ser no-op. **Con la forma condicional (R-11/R-12) los oráculos quedan intactos por una razón distinta y verificable: el payload no cambia en absoluto cuando no hay exención declarada** — la clave y el payload son **byte-idénticos** a los del producto vigente. El RED de U5 **añade** casos (la repetición que cambia la exención, el recorrido de dos revisiones) y no toca los vigentes. |
| **La idempotencia histórica del cierre y de la disposición (B-3)** | `tests/test_005_014_closure_replay.py` (PD-23: replay idéntico = no-op, estado byte-idéntico, una sola entrada `closure`), `tests/test_006_005_u5_disposition_failed.py` (PD-19(b): disposición idéntica = no-op byte-idéntico, sin segunda entrada) | **NO APLICA — no se tocan; se **ejecutan** y se **añaden** a las regresiones de U5.** Son los dos oráculos que se rompen si el payload de identidad cambia para las invocaciones sin exención: con los cuatro `null` de draft-002, el replay de cierre habría pasado de no-op a **rechazo** (rama de feature cerrada, :5622-5633) y la disposición habría escrito una **segunda entrada** (con el estado reescrito). Con la forma condicional de R-11/R-12 siguen verdes **sin cambio de oráculo**, y su presencia en la lista de regresiones hace que una futura forma uniforme **no** pueda colarse en silencio. |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije la puerta `plan-tasks` **para un borrador de forma `spec`** (es decir, que exija que una spec sea rechazada por no traer `plan-tasks`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva. El RED de U5 declara lo mismo respecto del payload de identidad, y además declara que sus tres casos de **recorrido de dos revisiones** son **controles de no-regresión** (pasan con el producto vigente y deben seguir pasando con el nuevo), no aserciones que deban fallar al abrir el RED.

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED** (epic §13.3, y la ilustración de 006-005: esta misma spec y este mismo plan son la **primera recepción posible** de la capacidad que la feature introduce — con la diferencia declarada de que el paquete que se revisa aquí es un `draft-plan` sobre un **borrador de plan**, que es exactamente la superficie que ya existe). La revisión que esta feature habilita para las specs (E1) **no** está disponible hasta que U1 esté en verde: se declara esta dependencia, no se la disimula.
- **La declaración de la política de compatibilidad (PD-16(b)) está en `re-entry.md` antes del recorrido (U6)**: el recorrido demuestra el comportamiento; la salida que el orquestador aplica está declarada antes de que el recorrido la use.
- **El recorrido de dos revisiones de U5 (PD-9) forma parte de la evidencia de cierre**: su salida real (los rc, la salida del no-op, el conteo de entradas y el sha256 del estado antes/después, en las tres clases) se adjunta a la evidencia de U6; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con el motivo y la evidencia del intento (misma regla de bloqueo que U6).
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature).
- El recorrido real de U6 (PD-13) queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan de 006-006 pasan por la revisión independiente que la propia feature introduce (o, si el gate 2→3 de esta feature no está aún en verde, por la superficie vigente `plan-review`/`draft-plan` sobre este plan), y la aprobación es de la autoridad vigente.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3, U4 y U5; make staging determinista en U4. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). A-1: esta feature NO reemplaza ningun oráculo vigente (ver plan §4): el oráculo de tests/test_004_003_t4_validation_fields.py:427 se conserva porque la forma por omision es plan, los 11 archivos que comparten el fixture DRAFT_PLAN_RELPATH no se tocan, y los oráculos de identidad de transicion recomputan la clave desde el payload escrito sin fijar su conjunto de claves; los REDs nuevos anaden casos, no cambian oraculos. Compatibilidad (B-1): la garantia de render byte-identico vale DENTRO de una misma revision del producto; entre revisiones no se promete compatibilidad y la politica (terminarlo bajo la revision con la que se publico, o preparar uno nuevo) queda declarada en re-entry.md, con su caso demonstrativo en U6. Exencion (B-2, corregido por B-3): sus cuatro campos entran en el payload de identidad de la transicion SOLO cuando la invocacion los declara, como un bloque exemption condicional; sin exencion declarada el payload y la transition_key quedan byte-identicos a los del producto vigente, de modo que las identidades historicas se conservan y NO hay enmienda de 005-014 PD-23 ni de 006-005 PD-19(b) (D-14); la repeticion identica es no-op y la repeticion que cambia la exencion (incluido el paso de sin exencion a con exencion) se registra por --supersedes o se rechaza explicitamente, nunca exito sin registrar. El RED de U5 incluye el recorrido de dos revisiones en gate, closure y disposition (control de no-regresion: el payload escrito debe ser byte-identico al de la formula de identidad anterior, congelada, y la repeticion de la misma orden sin exencion debe ser no-op, con la misma entrada y el estado byte-identico). Los gates del dueno que estaban pendientes YA ESTAN REGISTRADOS (execution.md:260 PD-19 aprobada; execution.md:262 modelo y credencial fuera de runtimes.json): no hay gate del dueno que esperar antes de un RED, y las unidades lo citan como precondicion cumplida.",
  "tasks": [
    {
     "id": "U1",
     "objective": "El objeto declarado en el contrato: contract.object_kind (spec|plan, por omision plan) como extension aditiva; el acompanante spec_path/spec_sha256/spec_version con digest calculado de los bytes y regla todo-o-nada; los checks del plan aplicados solo al documento de forma plan; inputs con una entrada por documento fijado y su purpose; render aditivo que nombra la forma y la identidad del acompanante (byte-identico sin las claves nuevas DENTRO de la misma revision del producto); ayuda de diagnostico que nombra la bandera cuando la forma no fue declarada.",
     "produce": [],
     "consume": [],
     "depends_on": [],
     "parallel": [],
     "files": [
      "skills/cdad-cycle/scripts/cdad_packet.py"
     ],
     "focal_tests": [
      "tests/test_006_006_u1_draft_object_form.py"
     ],
     "observable_checks": [
      "prepare acepta una spec sin plan-tasks con --object-kind spec y publica paquete (PD-3)",
      "los mismos bytes declarados plan siguen rechazados y el borrador sin --object-kind sigue rechazado por la puerta plan-tasks (PD-2)",
      "el contrato lleva object_kind y, con acompanante, spec_path/spec_sha256/spec_version con el digest igual a sha256sum del archivo (PD-4)",
      "el render nombra la forma y el acompanante, y es byte-identico sin las claves nuevas dentro de la misma revision; el RED no afirma nada entre revisiones (PD-5, PD-16a)",
      "un kind approved-* que declare las claves nuevas se rechaza antes de publicar (PD-1, PD-15)"
     ],
     "regressions": [
      "tests/test_004_003_t1_draft_contract.py",
      "tests/test_004_003_t1_reviewfix.py",
      "tests/test_004_003_t2_plan_review.py",
      "tests/test_004_003_t2_reviewfix.py",
      "tests/test_004_003_t3_plan_checks.py",
      "tests/test_004_003_t4_validation_fields.py",
      "tests/test_005_007_t2_progressive_plan_validator.py",
      "tests/test_005_007_t6_templates.py",
      "tests/test_005_007_reviewfix_blockings.py",
      "tests/test_003_002_t1_receive.py",
      "tests/test_003_002_t2_materialize.py",
      "tests/test_003_002_t2_reviewfix.py",
      "tests/test_006_005_u2_opencode_module.py",
      "tests/test_packet_prepare.py",
      "tests/test_role_packet_render.py"
     ],
     "integration_gate": "@validation_strategy",
     "owner": "RED: test-writer; GREEN: implementer"
    },
    {
     "id": "U5",
     "objective": "La exencion registrada e incluida en la identidad de la transicion SOLO cuando se declara: tres banderas opcionales y un interruptor en la clase gate de register-transition (--exempted-by, --exemption-reason, --requested-by, --delegated), admisibles solo en esa clase; la entrada suma exempted_by, reason, requested_by y delegated solo cuando las banderas estan; el payload canonico de identidad se construye exactamente como hoy y, solo cuando la invocacion declara la exencion, gana una clave nueva exemption con exactamente los campos declarados; sin exencion declarada el payload y la transition_key quedan byte-identicos a los del producto vigente, de modo que las identidades historicas se conservan; la exencion viaja en la MISMA entrada que la aprobacion, sin alterar el pin ni la regla de una sola aprobacion vigente.",
     "produce": [],
     "consume": [],
     "depends_on": [
      "U1"
     ],
     "parallel": [],
     "files": [
      "skills/cdad-cycle/scripts/cdad_packet.py"
     ],
     "focal_tests": [
      "tests/test_006_006_u5_exemption_record.py"
     ],
     "observable_checks": [
      "la invocacion con las cuatro banderas escribe la entrada con exempted_by, reason, requested_by y delegated (PD-9)",
      "la invocacion sin ellas escribe una entrada sin esos campos y las banderas fuera de la clase gate se rechazan nombrando la clase (PD-9)",
      "la entrada de exencion no habilita construccion: prepare de un rol de construccion sigue rechazando sin la aprobacion con su pin (PD-9, PD-14)",
      "la aprobacion con exencion sigue vigente para el cierre y una segunda aprobacion sin --supersedes sigue rechazada (V-4)",
      "identidad: con exencion declarada, el transition_key_payload lleva un bloque exemption con exactamente los campos declarados y la transition_key se recomputa desde el payload (PD-9)",
      "identidad: la repeticion identica (misma exencion) es no-op, sin segunda entrada y con el state byte-identico (PD-9, PD-11)",
      "identidad: la repeticion que cambia la exencion no es no-op: se registra por --supersedes o se rechaza explicitamente nombrando la entrada vigente y la via; nunca rc=0 sin registrar (PD-9, B-2)",
      "recorrido de dos revisiones (B-3), en gate, closure y disposition: el payload escrito es byte-identico al de la formula de identidad anterior (congelada) y la repeticion de la misma orden sin exencion es no-op, con la misma entrada nombrada, sin segunda entrada y con el state byte-identico (PD-9, R-13, D-14)"
     ],
     "regressions": [
      "tests/test_005_012_t1_register_transition_base.py",
      "tests/test_005_012_t2_gate_authority.py",
      "tests/test_005_012_t3_closure_dispatch_resolution.py",
      "tests/test_005_012_t4_late_delivery.py",
      "tests/test_005_012_t5_approval_vigency.py",
      "tests/test_005_014_closure_replay.py",
      "tests/test_006_005_u5_disposition_failed.py",
      "tests/test_005_001_t2_replace_packet.py",
      "tests/test_005_001_t3_idle.py",
      "tests/test_006_003_rf_review_fixes.py",
      "tests/test_006_003_rf2_review_fixes.py",
      "tests/test_packet_prepare.py"
     ],
     "integration_gate": "@validation_strategy",
     "owner": "RED: test-writer; GREEN: implementer"
    },
    {
     "id": "U2",
     "objective": "La fuente canonica de que se revisa: el substage reviewer-plan-review pasa del PLAN DRAFT al objeto de especificacion (intencion, restricciones y decisiones, spec, plan cuando existe, contratos y capacidades) conservando verbatim sus obligaciones vigentes (juicio sobre la intencion, separacion estructural/semantico, abstenciones, no aprobar, marcador detail por referencia) y sumando la obligacion de nombrar el objeto y su digest; la regla del rol reviewer deja de ser plan-centrica.",
     "produce": [],
     "consume": [],
     "depends_on": [
      "U1"
     ],
     "parallel": [],
     "files": [
      "skills/cdad-cycle/packets/substages/reviewer-plan-review.md",
      "skills/cdad-cycle/packets/roles/reviewer.md"
     ],
     "focal_tests": [
      "tests/test_006_006_u2_review_procedure.py"
     ],
     "observable_checks": [
      "el substage nombra la spec y el plan como objeto de revision y exige nombrar el objeto y su digest (PD-6, PD-12)",
      "el substage conserva la mencion del marcador detail y su referencia por referencia, sin re-enunciar la regla (PD-12)",
      "la regla de rol dice el objeto que el contrato declara, con su forma declarada, y no the plan draft (PD-12)",
      "el bloque estatico del paquete del reviewer se mide y queda por debajo del techo declarado de 12000 bytes (V-5)"
     ],
     "regressions": [
      "tests/test_005_007_t1_progressive_detail_rule.py",
      "tests/test_005_007_t6_templates.py",
      "tests/test_004_003_t2_plan_review.py",
      "tests/test_role_packet_render.py",
      "tests/test_role_packets.py"
     ],
     "integration_gate": "@validation_strategy",
     "owner": "RED: test-writer; GREEN: implementer"
    },
    {
     "id": "U3",
     "objective": "El recorrido principal, el gate y la politica de compatibilidad: subfase de revision de borrador y exit gate en stage-2-specification.md (con la forma declarada de la exencion enunciada alli), un criterio en el gate 2->3 de SKILL.md y el mapa del ciclo, la re-entry del dictamen y la declaracion de la politica de compatibilidad en re-entry.md, y la invocacion con la forma y la identidad doble en handoff-prompts.md; el gate es supervisado y el CLI no verifica la existencia del dictamen.",
     "produce": [],
     "consume": [],
     "depends_on": [
      "U2"
     ],
     "parallel": [],
     "files": [
      "skills/cdad-cycle/references/stage-2-specification.md",
      "skills/cdad-cycle/SKILL.md",
      "skills/cdad-cycle/references/re-entry.md",
      "skills/cdad-cycle/references/handoff-prompts.md"
     ],
     "focal_tests": [
      "tests/test_006_006_u3_review_route_and_gate.py"
     ],
     "observable_checks": [
      "el exit gate de la etapa 2 y el gate 2->3 nombran el artefacto plan-review.md y la condicion de bloqueantes (PD-10)",
      "el mapa del ciclo y la re-entry del dictamen existen y la plantilla declara las banderas de la forma y de la identidad doble sin re-enunciar el procedimiento (PD-10)",
      "control negativo (i): con aprobacion specification vigente y sin dictamen, prepare de un rol de construccion NO se rechaza (rc=0): el gate es supervisado (PD-10)",
      "control negativo (ii): sin aprobacion, el mismo prepare se rechaza con approval pending (PD-10, PD-14); los dos casos son distintos y ambos se comprueban",
      "la declaracion de re-entry.md nombra la politica entre revisiones y sus dos salidas: terminarlo bajo la revision con la que se publico, o preparar uno nuevo bajo la revision vigente (PD-16b)"
     ],
     "regressions": [
      "tests/test_005_006_t2_intake.py",
      "tests/test_role_packet_render.py",
      "tests/test_role_packets.py",
      "tests/test_cdad_generate.py",
      "tests/test_005_007_t1_progressive_detail_rule.py",
      "tests/test_005_007_t4_architect_report_materialization.py",
      "tests/test_003_002_t2_materialize.py"
     ],
     "integration_gate": "@validation_strategy",
     "owner": "RED: test-writer; GREEN: implementer"
    },
    {
     "id": "U4",
     "objective": "El rol y los agentes generados: la fuente del reviewer declara las etapas 2 y 4, el artefacto plan-review.md ademas de review.md y la revision de borrador no aprobado; los cuatro agentes del reviewer se regeneran con make agents y make staging es determinista.",
     "produce": [],
     "consume": [],
     "depends_on": [
      "U3"
     ],
     "parallel": [],
     "files": [
      "sources/roles/reviewer.md",
      "agents/cdad-reviewer.md",
      "agents/cdad-reviewer-odoo.md",
      "agents/claude-code/cdad-reviewer.md",
      "agents/claude-code/cdad-reviewer-odoo.md"
     ],
     "focal_tests": [
      "tests/test_006_006_u4_reviewer_role_agents.py"
     ],
     "observable_checks": [
      "la fuente nombra la etapa 2, el artefacto plan-review.md y la revision de borrador, y los cuatro agentes generados lo contienen tras make agents (PD-11)",
      "make staging es determinista: dos corridas producen los mismos bytes (V-2)",
      "make validate queda verde con la tabla de roles actualizada (PD-11)"
     ],
     "regressions": [
      "tests/test_cdad_generate.py",
      "tests/test_role_packet_render.py",
      "tests/test_005_006_t2_intake.py",
      "tests/test_bash_policy_selection.py",
      "tests/test_opencode_read_map_and_steps.py",
      "tests/test_005_004_t2_installer_claims.py",
      "tests/test_006_002_u1_delegation_section.py",
      "tests/test_006_002_u3_runtime_references.py",
      "tests/test_006_003_u3_texts_without_profiles.py"
     ],
     "integration_gate": "@validation_strategy",
     "owner": "RED: test-writer; GREEN: implementer"
    },
    {
     "id": "U6",
     "objective": "Recorrido de aceptacion en un proyecto descartable: una spec sin plan se revisa y su dictamen aterriza en la carpeta de la feature; un borrador spec+plan fija los dos digests; un borrador de otra feature se revisa y su dictamen aterriza en la carpeta de la feature activa nombrando el objeto; tras editar el borrador el digest cambia y la re-review focal queda requerida; ninguno de los tres deja estado de aprobacion; un borrador coherente que no alcanza la intencion produce un dictamen con bloqueante; y el caso de compatibilidad: un paquete publicado con las fuentes anteriores, recibido despues del cambio, se rechaza nombrando la causa, con la salida declarada.",
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
     "observable_checks": [
      "los tres paquetes se preparan con rc=0 y sus REQUEST.json declaran la forma y los digests fijados (PD-13)",
      "los tres recibos quedan pending y los tres dictamen se materializan en la carpeta declarada, con sha identico (PD-7, PD-13)",
      "el estado antes y despues no registra ninguna aprobacion (PD-7, PD-14)",
      "la comparacion de sha256sum contra los digests fijados muestra el cambio del caso E4 y la coincidencia del caso sin cambio (PD-8)",
      "el dictamen del caso E6 declara el bloqueante de un borrador que no alcanza la intencion (juicio semantico; la evidencia es el texto) (PD-13, E6)",
      "la corrida de dos fases del caso E7 muestra el rechazo con su diagnostico al recibir un paquete publicado con las fuentes anteriores, y el resultado declarado nombra la salida (PD-16c)",
      "la salida real del recorrido de dos revisiones de U5 (PD-9) queda adjunta: los tres rc de no-op, las tres salidas que nombran la entrada, los tres conteos de entradas y los tres sha256 del estado antes/despues (PD-9, R-13)",
      "las versiones y configuraciones observadas quedan declaradas y el resultado no se generaliza (spec 7)"
     ],
     "regressions": [],
     "integration_gate": "recorrido con evidencia declarada; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con motivo y evidencia del intento, sin corrida simulada",
     "owner": "orchestrator con el reviewer; evidencia en la carpeta de la spec"
    }
  ]
}
```
===END plan.md===

**Hallazgo → cambio:** **B-3** (añadir campos nulos cambia también las identidades históricas sin exención) → el bloque de exención pasa a ser **condicional** (spec §2.7 **R-11/R-12/R-13**: **una** clave `exemption`, presente **sólo** cuando la invocación declara la exención, con exactamente los campos declarados; sin exención, el payload y la `transition_key` quedan **byte-idénticos** a los del producto vigente), **PD-9** reescrita (identidad condicional + **recorrido de dos revisiones** en `gate`, `closure` y `disposition`), **INV-12** reescrita y **INV-13** nueva, **D-13** reescrita (con la forma uniforme de draft-002 explícitamente rechazada) y **D-14** nueva (**no hay enmienda** de 005-014 PD-23 ni de 006-005 PD-19(b); la deuda 005-014 E-4 **no se amplía**), **V-7** nueva; plan §3 U5 (zona del payload condicional, recorrido de dos revisiones con la fórmula de identidad anterior congelada, y **dos regresiones nuevas**: `tests/test_005_014_closure_replay.py` y `tests/test_006_005_u5_disposition_failed.py`), §4 (la fila «la identidad de la transición» reescrita — el análisis de draft-002 era falso — y fila nueva para las dos regresiones de B-3), §5 y §6 (U5 objetivo/checks/regresiones y `validation_strategy`).

---

## Informe de rol (evidencia)

**Archivos modificados:** ninguno. `write_scope: []` — la entrega es el texto final de `spec.md` y `plan.md`; el orquestador materializa `docs/specs/006-006-spec-plan-review/{spec,plan}.md` (ADR-003). El repo no se tocó.

**Comandos ejecutados y salidas (extracto):**

```sh
$ sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
d6da11dbed6571039c05b237eb257388c616d290028d6c9c5ce1cf0a3baf9809  docs/epics/epic-006-opencode-concurrency/plan.md
$ sha256sum skills/cdad-cycle/packets/common.md skills/cdad-cycle/packets/roles/architect.md skills/cdad-cycle/packets/substages/architect-draft.md
37609c566bf8f827a082699745b4cc0e915e37421a34d65f98b29db179647110  skills/cdad-cycle/packets/common.md
268804ca7edb2245f85b0fa493c033f09193fc39696b5d56596d25ff9e5cc3b8  skills/cdad-cycle/packets/roles/architect.md
cfa0a2b51dd22ee1e3b26ffafb2d0dcbd0c311a384e8c9c465b793ede5073ddc  skills/cdad-cycle/packets/substages/architect-draft.md
$ git log --oneline 7f39e24..HEAD -- skills/ sources/ agents/ scripts/ assets/
(vacío — el código no cambió desde la base medida; el HEAD documental es 6c8ad04)
$ git rev-parse --short HEAD
6c8ad04
$ git status --porcelain
 M docs/.cdad-state.json
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
?? findings/superlite-transferable-ideas-2026-10-19.md
```

Las tres fuentes de instrucción coinciden **byte a byte** con los sha256 del paquete; el contrato también. El estado del repo es **idéntico al inicial**: los tres paths listados eran preexistentes y no los toqué.

**Medición propia de B-3 (no de memoria):** con las funciones reales del producto (`_transition_identity_payload` + `_transition_key` sobre payloads sintéticos de las tres clases), el digest de identidad por clase es:

```text
caso           con 4 null (draft-002)  vigente (sin exencion)   con bloque exemption
gate           206a12c3962d7ec3        77d829f0323c436b         e72aef3b181c2e5f
closure        75c6685496f4296d        6379067a2d3d392f         e0ba68ab0b860fcf
disposition    fbd15d6c1d8322fd        355246ffa7c5ab2a         85802f589cc94d4d
payload vigente (gate): 16 claves
```

Confirma el mecanismo del dictamen: los cuatro `null` cambian la clave **también** sin exención (las tres clases); con la forma condicional, la columna «vigente» **coincide** con la del producto actual (identidad histórica conservada) y la exención declarada **sí** cambia la clave (el cambio de exención no puede ser un no-op silencioso). La consecuencia por clase está verificada en el código: `gate` → rechazo de «aprobación vigente» (`:5821-5829`); `closure` → rechazo «feature ya cerrada» (`:5622-5633`); `disposition` → **segunda entrada** con estado reescrito (no hay guarda que la impida: `:5496-5545`).

**Citas de código verificadas en el HEAD medido:** `_transition_identity_payload` `:5015-5063` (16 claves, sin exención) · `_transition_key` `:5066-5079` (serialización canónica) · `_registered_transition` `:5098-5108` (compara el `transition_key` exacto ⇒ el reconocimiento entre revisiones depende **sólo** de la clave) · no-op `:5766-5770` · `--supersedes` `:5812-5820` · segunda aprobación vigente `:5821-5829` · entrada del `gate` `:5849-5856` · rama de cierre `:5606-5633` · oráculo del payload `tests/test_005_012_t1_register_transition_base.py`:1212 (recomputa `canonical_digest(payload)`) · regresiones nuevas de B-3: `tests/test_005_014_closure_replay.py`:220 (PD-23) y `tests/test_006_005_u5_disposition_failed.py`:376 (PD-19(b)).

**Commit:** ninguno (rol read-only, `write_scope: []`).

**Suite completa:** no ejecutada — la política declarada en el paquete reserva la corrida completa a quien cierra, y esta entrega es un borrador sin código.

**Abstenciones:** no certifico RED/GREEN, producto instalado ni aceptación real (esta entrega es un borrador); no atribuyo familia de modelo al autor (no acreditada en los insumos); el recorrido de dos revisiones queda especificado por sus **observables y su instrumento** (la fórmula de identidad anterior, congelada), y su corrida real es la evidencia de U5/U6, no una afirmación de este borrador.