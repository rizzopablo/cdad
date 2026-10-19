# 006-005-native-path-parity — PLAN (etapa 2, revisión draft-003)

Estado: **BORRADOR no aprobado**, insumo de la re-review focal del dictamen (`plan-review` sobre `draft-plan`, enmienda 006) y de la aprobación de la autoridad vigente, antes del RED.
Contrato: epic `plan.md` §11/§12/§13. Spec: la de esta carpeta (misma entrega). Base medida: HEAD `b82e6a3` (el dictamen midió `357c461`; `git diff 9d3b2ea..b82e6a3` es docs-only, las citas de código siguen vigentes). Anonimización como en la spec. Es un plan de feature: unidades, archivos, RED y gates.
Corrección de esta revisión: B-1 (mecanismo del exec-config en el cargo de la unidad de configuración), B-2 (tres tests acoplados al registro doble a A-1 de la unidad de entrada+registro), D-15 (defecto de kind a PD-23 de la feature), O-1/O-5 (gates del dueño declarados), O-3 (U1 partida en U1a/U1b/U1c), O-4 (salidas de `make agents` en `files` de U4) y O-8 (líneas contra el HEAD medido).

## 1. Orden y dependencias

`U1a (config) → U1b (entrada + registro) → U2`; `U1c` (agente en el paquete) es independiente de U1a/U1b y sólo condiciona a U2; `U3` y `U5` son independientes de U2 (tocan `cdad_packet.py`, sin solape de líneas con U1c); `U4` al final (toca texto generado); `U6` después de U1a–U5. Ninguna unidad empieza sin su RED declarado y sin la review de spec/plan hecha (PD-21).

U1a va antes que U1b porque la entrada **consume** la sección de configuración (PD-8/PD-9): sin ella `dispatch` no tiene de dónde resolver el runtime. U1c, U3 y U5 **comparten archivo** (`skills/cdad-cycle/scripts/cdad_packet.py`), así que la ejecución es secuencial: ninguna de ellas se declara `parallel` con otra (una `parallel` mutua con archivos compartidos es paralelismo inseguro y el CLI lo rechaza).

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1a** | Configuración de ejecución por runtime: `runtimes.json`, resolución del runtime, derivación, migración del exec-config heredado y plantilla del instalador | — | PD-8, PD-9 | **confirmación del owner** (O-5: modelo y credencial no viven en `runtimes.json`) **registrada antes del RED** + RED + focales GREEN + regresiones de instalador/config + `make validate` |
| **U1b** | Entrada única `cdad_dispatch.py` (`dispatch`/`record`/`capabilities`) y **registro único** (la interfaz deja de registrar; kind derivado en la vía nativa) | U1a | PD-1…PD-6, PD-23 (nativa) | RED + focales GREEN + regresiones de delegación/interfaz/entrega (A-1) + `make validate` |
| **U1c** | Agente en el paquete: `prepare` resuelve rol+`stack` y escribe `agent`; el conjunto cerrado del request lo admite; el render no cambia | — | PD-7 | RED + focales GREEN + regresiones de `prepare`/render + `make validate` |
| **U2** | Módulo de runtime OpenCode: credencial inyectada, agente del paquete, kind derivado, `capabilities`/`--observe`, correlación, fallo cerrado, sin polling | U1a, U1b, U1c (contrato) | PD-5, PD-10…PD-14, PD-23 (externa) | RED + focales con store descartable + **binario falso** + regresiones del módulo y de la tabla de materialización |
| **U3** | Temporal del test-writer: clase, política, propuesta, `git check-ignore` | — | PD-15…PD-18 | RED + focales de scope + regresiones de política/`prepare`/`receive` |
| **U4** | Entrada única en el mandato + secciones `delegation` + regeneración | U1a–U1c, U2, U3 | PD-20 | RED de texto + `make staging` determinista + `make validate` |
| **U5** | Camino mecánico a `failed` y desbloqueo verificado de `prepare` | — | PD-19 | **aprobación del owner** (O-1: enmienda de la consecuencia INV-9 de 005-012) **registrada antes del RED** + RED + focales + regresiones de transiciones/estado |
| **U6** | Recorrido de aceptación de §11 en proyecto descartable, con las dos vías | U1a–U1c, U2–U5 | PD-22 | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1a — Configuración por runtime, resolución y migración
- **Archivos:**
  - **nuevo** `skills/cdad-cycle/scripts/cdad_dispatch.py`: la **capa de configuración** —resolución del runtime (PD-8) y lectura/validación de la sección de `runtimes.json` con la derivación de la configuración interna del módulo bajo `.cdad/` (PD-9)— y el diagnóstico único de migración de §2.6 (el flag `--exec-config` en `argv` ⇒ rc≠0 antes de todo efecto; ninguna lectura ni sondeo de un archivo heredado). El resto de los verbos es de U1b.
  - `install.sh`: plantilla de `runtimes.json` con la disciplina de dato del usuario (`install_user_config`:1191-1201, precedente de plantilla `write_delegation_template`:1151-1166 — sólo si no existe, no se registra en el manifiesto, no se pisa).
  - `skills/cdad-cycle/references/cli-delegation.md`: la entrada nueva, la sección de config y la migración (el exec-config deja de ser dato del usuario; hoy lo describe en :31/:39/:89/:270/:345).
- **RED:** `tests/test_006_005_u1a_runtime_config.py` (nuevo) — PD-8 (flag / declaración sobre un **contexto v1 plano** / ninguno sobre un **contexto v2** con diagnóstico que nombra el flag y la ausencia de lugar / valor inválido) y PD-9 (documento derivado inspeccionado clave por clave; sin sección ⇒ el diagnóstico nombra `runtimes.json`, la sección y la **correspondencia clave por clave**; con `model` ⇒ rechazo que nombra `delegation.json`; con `--exec-config` en `argv`, en sus dos formas ⇒ rc≠0 antes de todo efecto y sin escritura; control negativo: `--exec-config` ausente de `--help`). Fixture: proyecto descartable con `XDG_CONFIG_HOME` redirigido (patrón ya usado por los tests de config de 006-003).
- **Regresiones:** `tests/test_006_003_u2_installer_without_profiles.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_006_003_u7_prune_obsolete.py`, `tests/test_install_review5_regressions.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`.
- **Nota (verificada):** el conjunto de archivos de config del usuario que `test_006_003_u7_prune_obsolete.py` fija (`CONFIG_REL_PATHS`:105-108) es **abierto** por construcción (`config_bytes` mapea sólo esas dos rutas y compara antes/después), así que la plantilla nueva no rompe esa aserción; la plantilla nueva **sí** debe quedar fuera del manifiesto (misma disciplina, se verifica en el RED).
- **Gate:** **confirmación del owner (O-5) registrada en `execution.md` antes del RED** (la corrección del fraseo de `execution.md`:250 es una decisión suya, fundada en ADR-033); RED declarado y failing por la razón correcta; GREEN focal; regresiones verdes; `make validate`.
- **Nota de diseño (sin abstracción nueva):** no se crea `cdad_runtime_<id>.py` (D-2); no se agrega lista de versiones (la declaración sigue siendo `binary_version`).

### U1b — Entrada única y registro único
- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_dispatch.py` (mismo archivo de U1a, zona de verbos): los tres verbos de §2.1, el cuerpo único de observación/registro/escenificación de `record` (PD-3…PD-6) con el **kind derivado** en su descriptor (PD-23, lados nativos) y la importación de los ayudantes de la interfaz (una sola implementación de cada uno).
  - `skills/cdad-cycle/scripts/cdad_delegate.py`: **se quita su registro** (`_observation`:288, `_register_dispatch`:311, su invocación :398) y se **relaya** el `attempt` del módulo; la interfaz conserva su CLI y su `--exec-config` (mecanismo interno, deuda declarada, §8 item 4).
- **RED:** `tests/test_006_005_u1b_dispatch_entry.py` (nuevo) — PD-1 (un intento por vía; la interfaz no registra), PD-2 (no es segundo escritor), PD-3 (`sha256` byte-exacto), PD-4 (sin texto no hay entrega ni `receive`), PD-5 (las cuatro llaves, una por caso, y el paquete sin `agent`), PD-6 (`session: null` + `provenance`), PD-23 lado nativo (el descriptor de `record` declara el kind derivado del rol y la subfase; **la tabla `_allowed_kinds` no se toca**).
- **Regresiones:** `tests/test_005_009_t1_interface.py`, `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_005_009_t4_acceptance.py`, `tests/test_005_010_t1_durable_signal.py`, `tests/test_005_010_t2_load_mode_invocation.py`, `tests/test_005_010_t4_integration.py`, `tests/test_005_010_reviewfix.py`, `tests/test_005_007_t5_delegation_dispatch.py`, `tests/test_004_002_t4_dispatch.py`, `tests/test_006_002_u5_transport_equivalence.py`, `tests/test_006_001_t1_selection.py`, `tests/test_006_003_u4_delegation_config.py`, `tests/test_006_003_u6_server_credential.py`, `tests/test_006_003_u8_acceptance.py`, `tests/test_packet_prepare.py`.
- **A-1 (tests acoplados, ver §4):** cuatro tests, con reemplazo declarado §4: `tests/test_005_009_t1_interface.py` (el destino de prueba del fixture registra **su propio** intento y la interfaz lo **relaya**), y los tres de la familia 005-010 T1/T4/reviewfix, que hoy cuentan **dos** registros y asertan `model_reported` nulo en el registro de la interfaz.
- **Gate:** RED declarado y failing por la razón correcta; GREEN focal; regresiones verdes (incluidos los cuatro reemplazos de A-1); `make validate`.

### U1c — El agente en el paquete
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py`, **dos zonas**:
  - la construcción del documento de `REQUEST.json` en `prepare` (:4455-4474, hoy sin el campo): resuelve el `stack` del estado y escribe `agent`;
  - el **conjunto cerrado de campos del request** de `validate_request` (:769-777, hoy `optional = {"plan_task"}`): se extiende con `agent` como propiedad opcional declarada, sin relajar el rechazo de claves desconocidas (el mismo patrón con que 005-003 sumó `plan_task`). `agent` **no** entra al render (`render_packet` usa su lista explícita de claves, :932), así que `PACKET.md` sigue byte-idéntico y `receive` —que recomputa el render y lo compara, `cdad_result.py`:563-566— no cambia.
- **RED:** `tests/test_006_005_u1c_packet_agent.py` (nuevo) — PD-7: `agent` = rol + `stack` en los tres casos (con `stack`, sin `stack`, con `stack` y agente no publicado — ese último se verifica en U2); el paquete con `agent` **pasa** `validate_request`; una clave desconocida **sigue** rechazándose; los bytes de `PACKET.md` son los mismos con y sin el campo; un paquete publicado antes de la feature (sin `agent`) sigue recibiendo (`receive` rc=0 sobre él).
- **Regresiones:** `tests/test_packet_prepare.py`, `tests/test_005_006_t2_intake.py`, `tests/test_role_packet_render.py`, `tests/test_005_013_t1_unit_projection.py`.
- **Gate:** RED + focales; regresiones verdes; `make validate`.

### U2 — Módulo de runtime OpenCode
- **Archivos:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`:
  - **PD-11:** inyección de la credencial resuelta en el entorno del cliente, sólo en `mode: server`, junto al `PWD` (`_invoke_destination`:426-427); nada en `standalone`/`service`.
  - **PD-14:** el agente sale de `REQUEST.json.agent` (`_entry_agent_name`:298 + `_check_derived_agent_published`:302 aplicados al agente del paquete), con la degradación declarada cuando el campo no está.
  - **PD-10/PD-12/PD-13:** `--capabilities` y `--observe` (una lectura `mode=ro`, acotada, sin polling), exigiendo las columnas de correlación (`parent_id`, `directory`, `time_created` además del subconjunto actual `SESSION_V2_COLUMNS`:182) y fallando cerrado nombrando las ausentes.
  - **PD-23 (lado externo):** el descriptor deja de escribir la constante `FINAL_TEXT_ARTIFACT_KIND` (`:127`, usado en `:1737`) y declara el kind derivado de rol y subfase según §2.8 (una sola fuente: la tabla de `cdad_result`, ya importado por el módulo, `:108`).
  - `attempt` declarado en el sobre (conserva su registro, PD-1).
- **Sonda antes del RED:** V-1/V-7 (cómo se obtiene la sesión hija y columnas reales de la versión instalada) y V-13 (el kind derivado contra la tabla real); el hallazgo se registra y se declara en `capabilities`.
- **RED:** `tests/test_006_005_u2_opencode_module.py` (nuevo) — **binario falso que exige `OPENCODE_PASSWORD`** y eco de si la vio (PD-11, con el centinela ausente de `argv`, stdout/stderr, registro I8 y recibo); PD-14 (`argv` con el agente del paquete; agente no publicado → fallo cerrado; sin campo → `cdad-<rol>` declarado); PD-5 (las cuatro llaves por caso) y PD-12/PD-13 con store SQLite descartable (receta de aislamiento, `cli-delegation.md`:239+); PD-10 (incluido el módulo sin la superficie nueva); PD-23 lado externo (entrega del reviewer en `plan-review` → `artifact_kind: plan-review` y `materialize` rc=0 con sha idéntico; architect en `draft` → `role-report` y `materialize` rc=0; scribe → sigue rechazado nombrando rol/subfase).
- **Regresiones:** `tests/test_cdad_adapters_opencode.py`, `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_006_001_t1b_service_mode.py`, `tests/test_006_001_t2_wait_recovery.py`, `tests/test_006_001_t3_concurrency.py`, `tests/test_006_003_u6_server_credential.py`, `tests/test_003_003_t2_preflight.py` y la **tabla cerrada de materialización**: `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t2_reviewfix.py`, `tests/test_003_002_t1_receive.py`.
- **Gate:** focales verdes con store descartable y binario falso; regresiones verdes (incluida la tabla, sin cambios respecto del HEAD); `make validate`.

### U3 — Temporal del test-writer
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — vocabulario de clases (`SCOPE_CLASSES`:67, hoy sin `temporary`), validador único de scopes (`_validate_scope`:694 y el conjunto de escritura del test-writer :728-729), pertenencia de un cambio observado (`_scope_contains`:739, usado por el manifiesto en `cdad_result.py`:370), propuesta (`propose_policy`:1088, hoy `temporary_roots: []` en :1100) y el paso `git check-ignore` en `prepare`. El detalle de forma es del implementer; el contrato son PD-15…PD-18.
- **RED:** `tests/test_006_005_u3_temporary_scope.py` (nuevo) — PD-15 (política vacía → rechazo nombrando `docs/cdad-policy.json`; con raíz declarada → acepta), PD-16 (`git check-ignore` negativo y positivo, y proyecto no-Git), PD-17 (recibo `scope_validation: passed` con test real + sonda temporal, y rechazo fuera de scope), PD-18 (raíz temporal solapada con producto → rechazo).
- **V-8 / regla A-1:** no se encontró test que fije el valor de la propuesta; si el RED encuentra uno, se cambia **en RED declarando el reemplazo**.
- **Regresiones:** `tests/test_004_002_t1_policy.py`, `tests/test_004_002_t1_reviewfix.py`, `tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t6_landing.py`, `tests/test_004_002_t7_acceptance.py`, `tests/test_004_002_t7_private_paths.py`, `tests/test_004_002_t7_limits_rule.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_packet_prepare.py`, `tests/test_005_005_t2_docs_policy.py`.
- **Gate:** RED + focales; regresiones de política y recepción verdes; `make validate`.

### U4 — Entrada única y secciones `delegation`
- **Archivos:** `sources/roles/orchestrator.md` (intake :22-57 con las cuatro entradas solapadas y la condición stale :24; disciplina de contexto :104-108), `sources/agents/adapters/opencode.md` (§`delegation` :60-94), `sources/agents/adapters/claude-code.md` (§`delegation` :80-116), `skills/cdad-cycle/references/re-entry.md` (si el paso mecánico de escenificación se nombra allí), `scripts/cdad-generate.py`:747 (etiqueta «## Delegation (adapter)», V-4) y **las salidas declaradas de `make agents`**: `agents/cdad-*.md` (11 archivos) y `agents/claude-code/cdad-*.md` (11 archivos), que son promociones de `build/staging/` y nunca se editan a mano (`Makefile`:1-24, objetivos `staging`/`agents`).
- **RED:** `tests/test_006_005_u4_single_entry.py` (nuevo) — PD-20: la fuente tiene el orden de cinco filas sin solapes, **sin** la condición `.cdad/execution.json` y **con** la regla de transporte (mismo runtime ⇒ nativa + `record`; otro ⇒ la entrada externa); el generado recomputado coincide byte a byte; las secciones `delegation` nombran la entrada nueva, el agente del paquete y la credencial del módulo.
- **Regresiones (todo test que lea orquestadores o agentes generados):** `tests/test_005_006_t2_intake.py`, `tests/test_006_002_u1_delegation_section.py`, `tests/test_006_002_u2_neutral_skill.py`, `tests/test_006_002_u3_runtime_references.py`, `tests/test_006_002_u6_context_discipline.py`, `tests/test_006_003_u3_texts_without_profiles.py`, `tests/test_cdad_generate.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_role_packet_render.py`.
- **Gate:** `make staging` determinista (dos corridas, mismos bytes), RED de texto verde, regresiones verdes, `make validate`.

### U5 — Camino mecánico a `failed`
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — efecto de la clase `disposition` (hoy `pass`:5584-5589) y la coherencia de `validate_state` (:546). No se toca `_dispatched_packet_ids`/`_missing_required_deliveries` (:4855/:4944): leen el **ledger de despachos**, así que el cierre sigue satisfaciendo PD-8(a) por la disposición registrada.
- **RED:** `tests/test_006_005_u5_disposition_failed.py` (nuevo) — PD-19: paquete activo sin recibo → `failed`; `validate-state` VALID; `prepare` bloqueado antes (:4336-4338) y desbloqueado después; con recibo durable ⇒ rechazo que nombra `receive` (:5207-5213); la disposición sigue sin aprobar nada (`approval_effect: false`, sin `approved_by`).
- **A-1 (declarado):** `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 afirma hoy que el paquete sigue `dispatched` tras la disposición. Reemplazo declarado: «`active_packet.status` pasa a `failed` (terminal); el resto del estado sigue intacto». Se revisa además que el flujo B1 (:835) siga avanzando.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
- **Gate:** **aprobación del owner de la enmienda de PD-19 registrada antes del RED** (la consecuencia INV-9 de 005-012 cambia: `docs/specs/005-012-transition-registration/spec.md`:243/:587; la aprobación está pedida y **no** se da por hecha); luego RED + focales; regresiones verdes; `make validate`.

### U6 — Recorrido de aceptación (no es unidad de código)
- **Escenario (PD-22):** proyecto **descartable** con layout anidado; el coordinador iniciado **desde otra carpeta**; agente **global** y configuración de **proyecto** declarados distintos (garantía menor declarada); un auxiliar temporal necesario; **un test real escrito y recibido** (recibo `pending`, `scope_validation: passed`); **una entrega por la vía externa** con la entrada nueva (con su intento = el del módulo y su kind derivado) y **una por la vía nativa** (`task` + `record`, con el mismo paquete y el mismo texto final esperado); **un intento interrumpido** registrado sin entrega y llevado a `failed` **por comando**; y la sonda V-11 (`--agent cdad-<rol>-odoo` con `stack: odoo`).
- **Evidencia:** los archivos de intento I8, los recibos, el estado resultante, los sobres de los dos verbos, la materialización de la entrega no-architect con su kind derivado y la versión/configuración observadas. Sin generalizar (spec §7). Se entrega como documento de evidencia en la carpeta de la spec (no en `tests/`).
- **Regla de bloqueo por ambiente:** si el ambiente no puede ejecutar el recorrido (runtime ausente, versión fuera de la declarada, store no disponible, agente `-odoo` no publicado), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado ni por «debería funcionar». Decide el dueño/orquestador (autorizar, re-scopear o re-rutear).

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo. Aplica a:

| Unidad | Test | Reemplazo declarado |
|---|---|---|
| U1b | `tests/test_005_009_t1_interface.py` (las aserciones donde la **interfaz** es quien registra) | la interfaz **relaya** el `attempt` del módulo y **no** registra; el destino de prueba del fixture registra **su propio** intento; el único registro del despacho es el del módulo (PD-1/D-ADP-2). El resto del contrato de la interfaz (transporte byte-idéntico, sobre, fallo cerrado) no cambia. |
| U1b | `tests/test_005_010_t1_durable_signal.py` (`:431-449` cuenta un registro del worker **además** del de la interfaz; `:536-543` aserta `model_reported` nulo en el registro de la interfaz) | **un solo registro por despacho**: la interfaz relaya el `attempt` del módulo, la distinción interfaz/worker dentro de la vía externa desaparece (D-14/PD-1) y el `model_reported` del único registro sale de la observación del módulo (la fila durable). Se conservan las aserciones del registro del worker; se retiran las del registro de la interfaz. |
| U1b | `tests/test_005_010_t4_integration.py` (`:480-486` y `:540-557`, mismo patrón) | idéntico reemplazo que el anterior (mismo acoplamiento verificado). |
| U1b | `tests/test_005_010_reviewfix.py` (`:489-500`: «el registro NUEVO que NO es el de la interfaz») | idéntico reemplazo: la localización del registro I8 del intento pasa a ser «el único registro nuevo del despacho»; las aserciones sobre `model_reported` desde la fila durable no cambian. |
| U3 | — (V-8: ningún test encontrado hoy que fije el valor de la propuesta) | si el RED encuentra uno, se declara aquí antes de tocarlo |
| U5 | `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 | `active_packet.status` pasa a `failed` (terminal); el resto del estado intacto |
| U2 | — (V-13: la tabla `_allowed_kinds` **no** se modifica; PD-23 sólo cambia el kind declarado por las entregas) | si el RED de U2 encuentra un test que fije la constante `role-report` del módulo, se declara aquí antes de tocarlo |

## 5. Cierre

Review independiente de spec/plan **antes** del RED (PD-21; `plan-review` sobre `draft-plan`, sin subfase nueva): esta entrega es la corrección del dictamen y va a una **re-review focal**; la aprobación es de la autoridad vigente y **no** la habilita el dictamen. Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada; se repite sólo si cambios o evidencia invalidada lo justifican). Review formal del resultado en sesión independiente; el recorrido real de U6 (AC-7) queda declarado con su estado, y no se acredita aceptación real por pruebas aisladas.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
 "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1a, U1b, U1c, U2, U3, U4 y U5; make staging determinista en U4. Los gates del dueno (confirmacion de la correccion de modelo/credencial para U1a; aprobacion de la enmienda de PD-19 para U5) se registran ANTES del RED de su unidad. La suite completa la corre una vez quien cierra (PD-21); se reutiliza evidencia equivalente con procedencia verificada (re-entry.md, Equivalence of a registered run).",
 "tasks": [
  {
   "id": "U1a",
   "objective": "Configuracion de ejecucion por runtime: runtimes.json (seccion por runtime), resolucion del runtime, derivacion de la configuracion interna, migracion del exec-config heredado como error de uso y plantilla del instalador.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_dispatch.py",
    "install.sh",
    "skills/cdad-cycle/references/cli-delegation.md"
   ],
   "focal_tests": [
    "tests/test_006_005_u1a_runtime_config.py"
   ],
   "regressions": [
    "tests/test_006_003_u2_installer_without_profiles.py",
    "tests/test_005_004_t2_installer_claims.py",
    "tests/test_006_003_u7_prune_obsolete.py",
    "tests/test_install_review5_regressions.py",
    "tests/test_006_003_rf_review_fixes.py",
    "tests/test_006_003_rf2_review_fixes.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U1b",
   "objective": "Entrada unica cdad_dispatch.py (dispatch/record/capabilities) con registro unico: la interfaz deja de registrar y relaya el attempt del modulo; record deriva el kind de la parte entregada.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1a"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_dispatch.py",
    "skills/cdad-cycle/scripts/cdad_delegate.py",
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_010_t4_integration.py",
    "tests/test_005_010_reviewfix.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u1b_dispatch_entry.py"
   ],
   "regressions": [
    "tests/test_005_009_t1_interface.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_005_009_t4_acceptance.py",
    "tests/test_005_010_t1_durable_signal.py",
    "tests/test_005_010_t2_load_mode_invocation.py",
    "tests/test_005_010_t4_integration.py",
    "tests/test_005_010_reviewfix.py",
    "tests/test_005_007_t5_delegation_dispatch.py",
    "tests/test_004_002_t4_dispatch.py",
    "tests/test_006_002_u5_transport_equivalence.py",
    "tests/test_006_001_t1_selection.py",
    "tests/test_006_003_u4_delegation_config.py",
    "tests/test_006_003_u6_server_credential.py",
    "tests/test_006_003_u8_acceptance.py",
    "tests/test_packet_prepare.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U1c",
   "objective": "El agente viaja en el paquete: prepare resuelve rol mas stack y escribe agent; el conjunto cerrado del request lo admite como propiedad opcional declarada; el render de PACKET.md no cambia.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u1c_packet_agent.py"
   ],
   "regressions": [
    "tests/test_packet_prepare.py",
    "tests/test_005_006_t2_intake.py",
    "tests/test_role_packet_render.py",
    "tests/test_005_013_t1_unit_projection.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U2",
   "objective": "Modulo de runtime OpenCode: credencial inyectada solo en el cliente en mode server, agente del paquete, kind derivado de la parte entregada, --capabilities/--observe, correlacion de cuatro llaves, fallo cerrado, sin polling.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1a",
    "U1b",
    "U1c"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_delegate_opencode.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u2_opencode_module.py"
   ],
   "regressions": [
    "tests/test_cdad_adapters_opencode.py",
    "tests/test_005_009_t2_opencode_adapter.py",
    "tests/test_006_001_t1b_service_mode.py",
    "tests/test_006_001_t2_wait_recovery.py",
    "tests/test_006_001_t3_concurrency.py",
    "tests/test_006_003_u6_server_credential.py",
    "tests/test_003_003_t2_preflight.py",
    "tests/test_005_007_t4_architect_report_materialization.py",
    "tests/test_003_002_t2_materialize.py",
    "tests/test_003_002_t2_reviewfix.py",
    "tests/test_003_002_t1_receive.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U3",
   "objective": "Temporal del test-writer: clase temporary, politica, propuesta y git check-ignore en prepare.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u3_temporary_scope.py"
   ],
   "regressions": [
    "tests/test_004_002_t1_policy.py",
    "tests/test_004_002_t1_reviewfix.py",
    "tests/test_004_002_t2_bootstrap.py",
    "tests/test_004_002_t6_landing.py",
    "tests/test_004_002_t7_acceptance.py",
    "tests/test_004_002_t7_private_paths.py",
    "tests/test_004_002_t7_limits_rule.py",
    "tests/test_003_002_t1_receive.py",
    "tests/test_003_002_t2_materialize.py",
    "tests/test_packet_prepare.py",
    "tests/test_005_005_t2_docs_policy.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U4",
   "objective": "Entrada unica en el mandato del orquestador + secciones delegation + regeneracion de los generados con make agents.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1a",
    "U1b",
    "U1c",
    "U2",
    "U3"
   ],
   "parallel": [],
   "files": [
    "sources/roles/orchestrator.md",
    "sources/agents/adapters/opencode.md",
    "sources/agents/adapters/claude-code.md",
    "skills/cdad-cycle/references/re-entry.md",
    "scripts/cdad-generate.py",
    "agents/cdad-*.md",
    "agents/claude-code/cdad-*.md"
   ],
   "focal_tests": [
    "tests/test_006_005_u4_single_entry.py"
   ],
   "regressions": [
    "tests/test_005_006_t2_intake.py",
    "tests/test_006_002_u1_delegation_section.py",
    "tests/test_006_002_u2_neutral_skill.py",
    "tests/test_006_002_u3_runtime_references.py",
    "tests/test_006_002_u6_context_discipline.py",
    "tests/test_006_003_u3_texts_without_profiles.py",
    "tests/test_cdad_generate.py",
    "tests/test_bash_policy_selection.py",
    "tests/test_opencode_read_map_and_steps.py",
    "tests/test_005_004_t2_installer_claims.py",
    "tests/test_role_packet_render.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U5",
   "objective": "Camino mecanico a failed por disposition sin recibo y desbloqueo verificado de prepare, con la aprobacion del dueno de la enmienda registrada antes del RED.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "tests/test_005_012_t3_closure_dispatch_resolution.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u5_disposition_failed.py"
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
   "id": "U6",
   "objective": "Recorrido de aceptacion de §11 en proyecto descartable con las dos vias (PD-22), incluida la sonda V-11 y la materializacion de una entrega no-architect con su kind derivado; no es unidad de codigo; regla de bloqueo por ambiente.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1a",
    "U1b",
    "U1c",
    "U2",
    "U3",
    "U4",
    "U5"
   ],
   "parallel": [],
   "files": [],
   "integration_gate": "@validation_strategy",
   "owner": "orquestador (recorrido real) con evidencia",
   "observable_checks": [
    "intento I8 por cada via (externa con la entrada nueva; nativa con task + record) en .cdad/executions/<exec>/dispatches/",
    "entrega no-architect por la via externa materializada con su kind derivado del rol y la subfase (descriptor con artifact_kind: plan-review; materialize rc=0 con sha identico)",
    "recibo pending con scope_validation: passed para un test real y una sonda temporal",
    "intento interrumpido llevado a failed por register-transition disposition, validate-state VALID",
    "sonda V-11: session_v2.agent == cdad-<rol>-odoo en proyecto descartable con stack: odoo, o BLOQUEADA con motivo"
   ],
   "regressions": []
  }
 ]
}
```
