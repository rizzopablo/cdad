# 006-006-spec-plan-review — PLAN (etapa 2, borrador draft-001)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (PD-21 del plan de 006-005, y §13.3 de la enmienda 006: la revisión del borrador precede al RED).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §13 (sha256 `d6da11db…9809`). Spec: la de esta carpeta (misma entrega). Decisiones: `docs/epics/epic-006-opencode-concurrency/execution.md`:379-388.
Base medida: HEAD `7f39e24`. Medición: el bloque estático del paquete del reviewer ocupa **2728 bytes** con techo declarado de **12000** (`skills/cdad-cycle/scripts/cdad_packet.py`:1015-1027). Anonimización como en la spec.
Base de los fixtures: `DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"` (`tests/test_004_003_t1_draft_contract.py`:47), usado por **11** archivos de test — **esta feature no toca ninguno** (D-2, §4).

## 1. Orden y dependencias

`U1 (objeto declarado en el CLI) → U5 (exención registrada) → U2 (fuente canónica) → U3 (recorrido y gate) → U4 (rol y agentes) → U6 (recorrido de aceptación)`.

- **U1 y U5 tocan el mismo archivo** (`skills/cdad-cycle/scripts/cdad_packet.py`), en zonas distintas (la del contrato/`prepare` y la del registro de transiciones): la ejecución es **secuencial** y ninguna se declara `parallel` con otra (paralelismo inseguro: el CLI lo rechaza, `cdad_packet.py`:3490-3506).
- **U2 → U3 → U4** es una cadena de textos: U2 fija **qué se revisa** (el dueño único), U3 lo enruta en el recorrido y el gate, U4 lo propaga al rol y a los agentes generados. U2 precede a U3 y U3 precede a U4 porque cada uno consume el texto del anterior.
- **U6** depende de todo: es el recorrido real.
- Ninguna unidad empieza sin su RED declarado y sin la revisión de spec/plan hecha (gate 2→3 con el criterio nuevo, PD-10).

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1** | **El objeto declarado en el contrato:** `contract.object_kind`, el acompañante `spec_path`/`spec_sha256`/`spec_version`, los checks del plan **sólo** sobre el documento de forma `plan`, `inputs` por documento, el render que nombra la forma, y la ayuda de diagnóstico | — | PD-1, PD-2, PD-3, PD-4, PD-5, PD-15 | RED + focales GREEN + regresiones de contrato/packets (A-1) + `make validate` |
| **U5** | **La exención registrada:** tres banderas opcionales (+ un interruptor) en la clase `gate` de `register-transition`, con `exempted_by`, `delegated`, `requested_by` y `reason` en la entrada | U1 | PD-9, PD-1 (forja) | RED + focales GREEN + regresiones de transiciones/estado + `make validate` |
| **U2** | **La fuente canónica de «qué se revisa»:** el substage generalizado al objeto de especificación y la regla de rol sin plan-centrismo, **conservando** sus obligaciones vigentes | U1 | PD-6 (procedimiento), PD-12 | RED de texto + regresiones de 005-007 (detalle progresivo) + `make validate` |
| **U3** | **El recorrido principal y el gate:** subfase y exit gate de la etapa 2, criterio del gate 2→3, re-entry del dictamen, invocación con la forma y la identidad doble | U2 | PD-10, PD-14 | RED de texto (deriva) + regresiones de la skill + `make validate` |
| **U4** | **El rol y los agentes generados:** la fuente del reviewer declara etapa 2, el artefacto `plan-review.md` y la revisión de borrador; `make agents` | U3 | PD-11 | RED de texto + `make staging` determinista + `make validate` |
| **U6** | **Recorrido de aceptación** (no es unidad de código): E1..E5 sobre un proyecto **descartable** | U1–U5 | PD-13, PD-8, PD-14 | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1 — El objeto declarado en el contrato

- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_packet.py`, **cuatro zonas**:
    1. el conjunto cerrado de claves del contrato (`contract_keys`:879-883) extendido de forma aditiva con `object_kind`, `spec_path`, `spec_sha256`, `spec_version`; la **forja** (:890-898) extended para que un kind `approved-*` que declare cualquiera de ellas se rechace antes de publicar;
    2. `prepare` (:4671-4699): las banderas `--object-kind`, `--spec-path`, `--spec-version`; el digest del acompañante **calculado de los bytes** (no afirmado); la regla todo-o-nada; el rechazo si el acompañante no existe; el acompañante sólo con principal de forma `plan`;
    3. la rama de checks (:4718-4721): se aplica **al documento principal si su forma es `plan`**; la ayuda de diagnóstico que nombra `--object-kind` cuando la forma no fue declarada y la puerta `plan-tasks` rechaza;
    4. la construcción de `inputs` (:4790-4792, una entrada por documento fijado, con su `purpose`) y el render (:998-1059: metadata :1028, sección `## Contract` :1045-1047, sección `## Inputs` :1051-1052 — **aditivas**: sin las claves nuevas el render es byte-idéntico).
- **RED:** `tests/test_006_006_u1_draft_object_form.py` (nuevo) —
  - **PD-1**: `object_kind: spec` y `object_kind: plan` en el `REQUEST.json`; valor fuera del conjunto cerrado ⇒ rc≠0 **nombrando el valor**; clave desconocida ⇒ rc≠0; kind `approved-*` con `object_kind` ⇒ **rechazo sin publicar** (out-dir vacío, state byte-idéntico).
  - **PD-2 (control negativo explícito):** **sin** `--object-kind`, un borrador sin bloque `plan-tasks` **sigue rechazándose** con el diagnóstico vigente que nombra `plan-tasks` — *el oráculo de `tests/test_004_003_t4_validation_fields.py`:427 se conserva; este caso es su control negativo dentro del RED nuevo, no una reescritura del oráculo vigente*; un bloque malformado **sigue rechazándose**; el render de un paquete sin las claves nuevas es **byte-idéntico** al del HEAD medido.
  - **PD-3**: con `--object-kind spec`, un borrador de spec **sin** `plan-tasks` es aceptado y publica paquete; los mismos bytes declarados `plan` ⇒ rc≠0; la spec del `REQUEST.json` **no** contiene el token `plan-tasks` (no hay tareas artificiales inyectadas).
  - **PD-4**: `--spec-path` + `--spec-version` ⇒ `spec_path`, `spec_sha256` (igual a `sha256sum` del archivo) y `spec_version` en el contrato; acompañante inexistente ⇒ rc≠0 nombrando la ruta; `spec_path` sin `spec-version` (y el inverso) ⇒ rc≠0 nombrando la clave; acompañante con principal de forma `spec` ⇒ rc≠0; kind `approved-*` con el acompañante ⇒ rechazo por forja.
  - **PD-5**: `inputs` con una entrada por documento, en orden (principal, acompañante), con `purpose` `«draft spec for review»` / `«draft plan for review»`; el render nombra la forma y la identidad del acompañante; **control negativo**: render byte-idéntico sin las claves nuevas.
  - **PD-15**: los cuatro guardas vigentes (draft con otra subfase; plan-review sobre kind aprobado; draft para rol ≠ reviewer; forja ampliada) **verdes sin cambio de oráculo**.
  - Fixture: proyecto descartable con el patrón de `tests/test_004_003_t2_plan_review.py` (`PrepareProject`), con **fixtures propios** (no el compartido `DRAFT_PLAN_RELPATH`): un borrador de spec y un borrador de plan, ambos con digest y versión propios.
- **Regresiones:** `tests/test_004_003_t1_draft_contract.py`, `tests/test_004_003_t1_reviewfix.py`, `tests/test_004_003_t2_plan_review.py`, `tests/test_004_003_t2_reviewfix.py`, `tests/test_004_003_t3_plan_checks.py`, `tests/test_004_003_t4_validation_fields.py`, `tests/test_005_007_t2_progressive_plan_validator.py`, `tests/test_005_007_t6_templates.py`, `tests/test_005_007_reviewfix_blockings.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t2_reviewfix.py`, `tests/test_006_005_u2_opencode_module.py`, `tests/test_packet_prepare.py`, `tests/test_role_packet_render.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED declarado y fallando por la razón correcta; GREEN focal; las regresiones listadas verdes **sin cambio de oráculo**; `make validate`. La **installed product** (V-1) se verifica en el RED: el CLI instalado renderiza el paquete con la forma declarada, byte a byte igual que el del repo (el patrón de `tests/test_004_003_t2_plan_review.py`:290).

### U5 — La exención registrada

- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — la clase `gate` de `register_transition` (la construcción de la entrada, ~:5849-5856) y su parser (~:6432-6472). Tres banderas opcionales y un interruptor: `--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`; admisibles **sólo** con `--transition gate` (fuera de esa clase ⇒ rc≠0 nombrando la clase). La entrada suma `exempted_by`, `reason`, `requested_by` y `delegated` **sólo** cuando las banderas están presentes. **No** se toca la regla de una sola aprobación vigente (PD-14, :5789) ni el pin de la aprobación: la exención **viaja en la misma entrada** que la aprobación.
- **RED:** `tests/test_006_006_u5_exemption_record.py` (nuevo) — **PD-9**: la invocación con las cuatro banderas escribe una entrada de `stage_history` con `exempted_by`, `reason`, `requested_by` y `delegated`; la invocación **sin** ellas escribe una entrada **sin** esos campos (control negativo); las banderas fuera de la clase `gate` ⇒ rc≠0 nombrando la clase; la entrada de exención **no habilita construcción** (un `prepare` de un rol de construcción sigue rechazando sin la aprobación con su pin); **V-4**: la aprobación con exención sigue siendo **vigente** para el cierre (PD-8(b)) y una segunda aprobación sin `--supersedes` **sigue** rechazándose.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED + focales; regresiones de transiciones verdes; `make validate`.

### U2 — La fuente canónica de «qué se revisa»

- **Archivos:**
  - `skills/cdad-cycle/packets/substages/reviewer-plan-review.md` (una sola línea): el objeto pasa de «un PLAN DRAFT» al **objeto de especificación** — intención declarada, restricciones y decisiones aplicables, **spec**, **plan cuando existe**, contratos y capacidades necesarias para ejecutar y obtener evidencia — conservando **verbatim** sus obligaciones vigentes: separación entre validación estructural y juicio semántico, el juicio sobre la intención (un plan/spec coherente que no la alcanza es bloqueante), la taxonomía del efecto, el umbral de confianza, el verdict-tuple, la sección `## Abstentions`, «la revisión no es aprobación» y el **consumo del marcador `detail` por referencia** a su regla canónica (regresión de 005-007 PD-12). **Se le suma** la obligación de que el dictamen **nambre el objeto revisado y su digest** (D-9, PD-6).
  - `skills/cdad-cycle/packets/roles/reviewer.md` (una sola línea): la regla «qué revisar» deja de ser plan-céntrica — «el objeto que el contrato declara, **con su forma declarada** (spec o plan)».
- **RED:** `tests/test_006_006_u2_review_procedure.py` (nuevo) — deriva textual: el substage nombra la spec **y** el plan, no dice «PLAN DRAFT» como objeto único, conserva las obligaciones vigentes (juicio sobre la intención; separación estructural/semántico; `## Abstentions`; «never mark the reviewed draft approved»; el marcador `detail` **por referencia**, sin re-enunciar la regla) y **exige** nombrar el objeto y su digest; la regla de rol dice «el objeto que el contrato declara» y no «the plan draft». **Control negativo**: el substage **no** re-enuncia la regla de detalle progresivo (la referencia, no la copia).
- **Regresiones:** `tests/test_005_007_t1_progressive_detail_rule.py` (el substage debe seguir consumiendo el marcador **por referencia** — su oráculo **no** cambia), `tests/test_005_007_t6_templates.py`, `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` se compone con el substage sha-pinned byte a byte), `tests/test_role_packet_render.py`, `tests/test_role_packets.py`.
- **Gate:** RED de texto verde; regresiones verdes; `make validate`; **medición del bloque estático** (`common.md` + `roles/reviewer.md` + `substages/reviewer-plan-review.md`) registrada y **por debajo del techo de 12000 bytes** (V-5: la holgura medida hoy es de 9272).

### U3 — El recorrido principal y el gate

- **Archivos:**
  - `skills/cdad-cycle/references/stage-2-specification.md`: la subfase de la etapa 2 (preparar/despachar el paquete `plan-review` sobre el borrador, recibir el dictamen, rutear los bloqueantes al architect o a la autoridad, re-review focal si la corrección cambió el diseño, y recién entonces la aprobación) y el **exit gate** (que nombra el artefacto `plan-review.md` y la condición de bloqueantes). **Además**, la **forma declarada de la exención** (los cuatro campos) queda enunciada aquí, que es el dueño canónico del procedimiento de la etapa 2.
  - `skills/cdad-cycle/SKILL.md`: un criterio en el **gate 2→3** (espejo del gate 4→5, `SKILL.md`:361-366) y el **mapa del ciclo** (la flecha Stage 2→Stage 3, hoy rotulada «gate: spec.md approved by the user», :299) que nombra la revisión del borrador.
  - `skills/cdad-cycle/references/re-entry.md`: la re-entry del **dictamen de borrador** (qué hacer con él: corregir, re-review focal, exención) junto a la re-entry del architect (:148-172).
  - `skills/cdad-cycle/references/handoff-prompts.md`: la plantilla del reviewer (`plan-review`) que declara la invocación **con la forma** (`--object-kind`) y la identidad doble (`--spec-path`, `--spec-version`), **sin re-enunciar el procedimiento** (que sigue en el substage).
- **RED:** `tests/test_006_006_u3_review_route_and_gate.py` (nuevo) — deriva textual sobre las cuatro superficies: el exit gate de la etapa 2 y el gate 2→3 nombran el artefacto `plan-review.md` y la condición de bloqueantes; el mapa del ciclo nombra la revisión; la re-entry del dictamen existe; la plantilla declara las banderas de la forma y de la identidad doble y **no** re-enuncia el procedimiento. **Control negativo (PD-10):** el CLI **no** verifica la existencia del dictamen (ningún camino nuevo de rechazo) — se comprueba que `prepare` sigue aceptando un paquete `plan-review` cuyo dictamen **no** existe.
- **Regresiones:** `tests/test_005_006_t2_intake.py`, `tests/test_role_packet_render.py`, `tests/test_role_packets.py`, `tests/test_cdad_generate.py`, `tests/test_005_007_t1_progressive_detail_rule.py`, `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_003_002_t2_materialize.py`.
- **A-1:** **ninguna** (§4).
- **Gate:** RED de texto verde; regresiones verdes; `make validate`.

### U4 — El rol y los agentes generados

- **Archivos:**
  - `sources/roles/reviewer.md` (fuente editable): la fila de la tabla de contrato (:48) declara **etapas 2 y 4**, el artefacto `plan-review.md` **además** de `review.md`, y el texto de la fila dice que la revisión de borrador es parte del rol; la sección de directiva nombra la revisión de **borrador no aprobado** como parte del encargo del rol. El resto del texto (calibración, taxonomía, veredicto, aislamiento) **no se toca**.
  - `agents/cdad-reviewer.md`, `agents/cdad-reviewer-odoo.md`, `agents/claude-code/cdad-reviewer.md`, `agents/claude-code/cdad-reviewer-odoo.md`: **salidas declaradas** de `scripts/cdad-generate.py` (`Makefile`:15-18) — **nunca se editan a mano**.
- **RED:** `tests/test_006_006_u4_reviewer_role_agents.py` (nuevo) — la fuente nombra la etapa 2, el artefacto `plan-review.md` y la revisión de borrador; los **cuatro** agentes generados lo contienen tras `make agents`; `make staging` es **determinista** (dos corridas, mismos bytes) — control de V-2; y `make validate` verde.
- **Regresiones:** `tests/test_cdad_generate.py`, `tests/test_role_packet_render.py`, `tests/test_005_006_t2_intake.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_006_002_u1_delegation_section.py`, `tests/test_006_002_u3_runtime_references.py`, `tests/test_006_003_u3_texts_without_profiles.py`, `tests/test_006_005_u4_single_entry.py` (si existe con ese nombre; si no, el test de texto equivalente de U4 de 006-005).
- **A-1:** **ninguna** (§4).
- **Gate:** `make staging` determinista; RED de texto verde; regresiones verdes; `make validate`.

### U6 — Recorrido de aceptación (no es unidad de código)

- **Escenario (PD-13, contra E1..E5 de §3.1 de la spec):** en un proyecto **descartable** (nunca el HOME, nunca el proyecto activo):
  - **(E1)** un borrador de **spec sin plan** se revisa: `prepare --role reviewer --substage plan-review --contract-kind draft-plan --contract-path <spec> --plan-version <v> --object-kind spec` ⇒ rc=0; el paquete lleva la forma en la metadata y el `purpose` «draft spec for review»; el dictamen se recibe (`semantic_status: pending`) y se materializa en `docs/specs/<F>/plan-review.md` con sha idéntico; **el estado no registra aprobación**;
  - **(E2)** un borrador de **spec + plan**: el contrato fija los dos por digest (`--object-kind plan` + `--spec-path`/`--spec-version`); los checks del plan se aplican **al plan**; el paquete lleva los dos documentos; el dictamen nombra ambos digests;
  - **(E3)** un borrador de **otra** feature (`docs/specs/<B>/spec.md`) con la ejecución de **A**: rc=0; el paquete muestra `feature_id` = A y el `contract.path` de B; el dictamen se materializa **sólo** en `docs/specs/<A>/` y nombra el objeto y su digest; un target en `docs/specs/<B>/` ⇒ rc≠0;
  - **(E4)** tras editar el borrador, `sha256sum` del archivo ≠ el digest fijado en el `REQUEST.json` de la revisión ⇒ la revisión anterior no cubre esos bytes ⇒ re-review focal requerida (y se registra el caso de bytes sin cambiar, donde el digest coincide);
  - **(E5)** el dictamen **no** aprueba: sin marca de aprobación, recibo `pending`, `approval_effect: false`, y `prepare` para el test-writer **sigue rechazando** sin la entrada de aprobación con su pin.
- **Evidencia:** los tres paquetes y sus `REQUEST.json` (digests y forma), los tres recibos, los tres dictámenes materializados con su carpeta destino, el estado antes/después (sin aprobación), la comparación de digests del caso E4, y las versiones/configuraciones observadas. Se entrega como **documento de evidencia** en la carpeta de la spec (no en `tests/`). Sin generalizar (spec §7).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (CLI no disponible, proyecto no inicializable, estado incoherente), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el owner/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo.

**Resultado de la evaluación: esta feature NO reemplaza ningún oráculo vigente.** Es la consecuencia de D-2 (la forma por omisión es `plan`):

| Superficie acoplada | Test | Evaluación |
|---|---|---|
| **La puerta `plan-tasks`** | `tests/test_004_003_t4_validation_fields.py`:427 (`test_pd8_plan_without_the_block_is_rejected`) | **NO APLICA — el oráculo se conserva sin cambio.** El fixture declara un borrador **sin** `--object-kind` ⇒, por omisión, su forma es `plan` ⇒ los checks del plan se aplican ⇒ el rechazo y el diagnóstico vigente (que nombra `plan-tasks`) siguen siendo los exactos. El RED de U1 lo **vuelve a comprobar como control negativo** (mismo fixture, sin la bandera ⇒ mismo rechazo), de modo que el oráculo vigente queda **fijado**, no sólo no-roto. *Lo que sí se declara en el RED de U1:* el caso **nuevo** «mismos bytes declarados `spec` ⇒ aceptado», que es un caso **adicional**, no un reemplazo. |
| **Los fixtures compartidos** | `DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"` (`tests/test_004_003_t1_draft_contract.py`:47), usado por **11** archivos de test: `test_003_002_t2_reviewfix.py`, `test_004_003_t1_draft_contract.py`, `test_004_003_t1_reviewfix.py`, `test_004_003_t2_plan_review.py`, `test_004_003_t2_reviewfix.py`, `test_004_003_t3_plan_checks.py`, `test_004_003_t4_validation_fields.py`, `test_005_007_reviewfix_blockings.py`, `test_005_007_t2_progressive_plan_validator.py`, `test_005_007_t6_templates.py`, `test_006_005_u2_opencode_module.py` | **NO APLICA — ningún fixture compartido se modifica.** La ruta del fixture sigue siendo válida (es un borrador de forma `plan` por omisión) y su contenido sigue siendo un plan con `plan-tasks`. Los tests nuevos de U1 usan **fixtures propios** (spec y plan, con digest y versión propios). Esto evita la coordinación con el test-writer sobre fixtures compartidos que la opción O3 del discovery habría exigido. |
| **El contrato del paquete** | `tests/test_004_003_t2_plan_review.py` (el paquete `plan-review` lleva el plan, el contrato y la versión) | **NO APLICA.** El paquete sin las claves nuevas renderiza **byte-idéntico** (PD-5, control negativo) y su `REQUEST.json` conserva las claves actuales. El RED de U1 **extiende** este patrón con el caso de la forma `spec` en el archivo **nuevo**, sin tocar el test vigente. |
| **La materialización del dictamen** | `tests/test_003_002_t2_reviewfix.py`:871-904 (la fila `reviewer/plan-review` con contrato `draft-plan` se materializa) | **NO APLICA.** No se toca `cdad_result.py`: el kind `plan-review` y su destino ya existen (`assets/artifact-policy.json`:9; `cdad_result.py`:681-706). D-9 **rechaza** añadir la comprobación del digest en la parte, precisamente para no tener que reescribir este oráculo ni el de `tests/test_006_005_u2_opencode_module.py`:1378-1392. |
| **El kind derivado de la entrega** | `tests/test_006_005_u2_opencode_module.py`:1378-1392 (PD-23) | **NO APLICA.** Sin cambios en la tabla cerrada ni en el derivador. |
| **El substage y la regla de rol** | `tests/test_005_007_t1_progressive_detail_rule.py`:295-307 (el substage consume el marcador `detail` por referencia) | **NO APLICA — el oráculo no cambia, pero es un acoplado de U2.** La reescritura del substage (U2) **debe conservar** la mención del marcador `detail` y la **referencia** a su regla canónica. Si el RED de U2 las perdiera, ese test **fallaría**: es la red de seguridad, no un reemplazo. |
| **La exclusión de una segunda aprobación vigente** | `tests/test_005_012_t3_closure_dispatch_resolution.py` | **NO APLICA.** La exención **viaja en la misma entrada** que la aprobación (D-6): no hay una segunda entrada que compita. El RED de U5 lo comprueba en los dos sentidos (la aprobación con exención es vigente; una segunda aprobación sin `--supersedes` sigue rechazándose). |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije la puerta `plan-tasks` **para un borrador de forma `spec`** (es decir, que exija que una spec sea rechazada por no traer `plan-tasks`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva.

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED** (epic §13.3, y laoilustración de 006-005: esta misma spec y este mismo plan son la **primera recepción posible** de la capacidad que la feature introduce — con la diferencia declarada de que el paquete que se revisa aquí es un `draft-plan` sobre un **borrador de plan**, que es exactamente la superficie que ya existe). La revisión que esta feature habilita para las specs (E1) **no** está disponible hasta que U1 esté en verde: se declara esta dependencia, no se la disimula.
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature).
- El recorrido real de U6 (PD-13) queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan de 006-006 pasan por la revisión independiente que la propia feature introduce (o, si el gate 2→3 de esta feature no está aún en verde, por la superficie vigente `plan-review`/`draft-plan` sobre este plan), y la aprobación es de la autoridad vigente.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3, U4 y U5; make staging determinista en U4. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). A-1: esta feature NO reemplaza ningun oráculo vigente (ver plan §4): el oráculo de tests/test_004_003_t4_validation_fields.py:427 se conserva porque la forma por omision es plan, y los 11 archivos que comparten el fixture DRAFT_PLAN_RELPATH no se tocan; los REDs nuevos anaden casos, no cambian oraculos. Los gates del dueno que estaban pendientes YA ESTAN REGISTRADOS (execution.md:260 PD-19 aprobada; execution.md:262 modelo y credencial fuera de runtimes.json): no hay gate del dueno que esperar antes de un RED, y las unidades lo citan como precondicion cumplida.",
  "tasks": [
    {
     "id": "U1",
     "objective": "El objeto declarado en el contrato: contract.object_kind (spec|plan, por omision plan) como extension aditiva; el acompanante spec_path/spec_sha256/spec_version con digest calculado de los bytes y regla todo-o-nada; los checks del plan aplicados solo al documento de forma plan; inputs con una entrada por documento fijado y su purpose; render aditivo que nombra la forma y la identidad del acompanante (byte-identico sin las claves nuevas); ayuda de diagnostico que nombra la bandera cuando la forma no fue declarada.",
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
      "el render nombra la forma y el acompanante, y es byte-identico sin las claves nuevas (PD-5)",
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
     "objective": "La exencion registrada: tres banderas opcionales y un interruptor en la clase gate de register-transition (--exempted-by, --exemption-reason, --requested-by, --delegated), admisibles solo en esa clase; la entrada suma exempted_by, reason, requested_by y delegated solo cuando las banderas estan; la exencion viaja en la MISMA entrada que la aprobacion, sin alterar el pin ni la regla de una sola aprobacion vigente.",
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
      "la aprobacion con exencion sigue vigente para el cierre y una segunda aprobacion sin --supersedes sigue rechazada (V-4)"
     ],
     "regressions": [
      "tests/test_005_012_t1_register_transition_base.py",
      "tests/test_005_012_t3_closure_dispatch_resolution.py",
      "tests/test_005_012_t4_late_delivery.py",
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
     "objective": "El recorrido principal y el gate: subfase de revision de borrador y exit gate en stage-2-specification.md (con la forma declarada de la exencion enunciada alli), un criterio en el gate 2->3 de SKILL.md y el mapa del ciclo, la re-entry del dictamen en re-entry.md, y la invocacion con la forma y la identidad doble en handoff-prompts.md; el gate es supervisado y el CLI no verifica la existencia del dictamen.",
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
      "control negativo: prepare sigue aceptando un paquete plan-review cuyo dictamen no existe (el gate no es un bloqueo del CLI) (PD-10)"
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
     "objective": "Recorrido de aceptacion en un proyecto descartable: una spec sin plan se revisa y su dictamen aterriza en la carpeta de la feature; un borrador spec+plan fija los dos digests; un borrador de otra feature se revisa y su dictamen aterriza en la carpeta de la feature activa nombrando el objeto; tras editar el borrador el digest cambia y la re-review focal queda requerida; ninguno de los tres deja estado de aprobacion.",
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
      "las versiones y configuraciones observadas quedan declaradas y el resultado no se generaliza (spec 7)"
     ],
     "regressions": [],
     "integration_gate": "recorrido con evidencia declarada; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con motivo y evidencia del intento, sin corrida simulada",
     "owner": "orchestrator con el reviewer; evidencia en la carpeta de la spec"
    }
  ]
}
```

