# 006-005-native-path-parity — PLAN (etapa 2, revisión draft-005)

Estado: **APROBADO** (draft-005, tras cuatro reviews independientes; ver la marca al final). Habilita el RED por unidad.
Contrato: epic `plan.md` §11/§12/§13. Spec: la de esta carpeta (misma entrega). Base medida: HEAD `6cbff30a` (draft-004 midió `b235d497`, la review por escenarios `a8865e0c`, draft-003 `b82e6a3` y el dictamen `357c461`; `git diff b235d497..HEAD --stat` es docs-only —5 archivos, todos `docs/`—, las citas de código siguen vigentes y se re-midieron). Anonimización como en la spec. Es un plan de feature: unidades, archivos, RED y gates.
Corrección de esta revisión (draft-005): (1) **B-1** — U6/PD-22 ya no pide dos recepciones del mismo paquete: el mismo escenario en las dos vías **sobre dos paquetes de la misma ejecución** (elegido y declarado; la transición `delivery` del primero lo deja `completed` y el segundo `prepare` queda desbloqueado), con la evidencia y los `observable_checks` ajustados; (2) **O-2** — la sonda V-14 registra **qué copia del agente** cargó el hijo nativo además de si aplicó el mapa, con la atribución declarada; (3) **O-3** — la acreditación «verificada» exige **al menos una llave discriminante**; con sólo «agente» el resultado es `unknown` (entrega sólo por PD-6) y el oráculo incluye dos despachos nativos concurrentes del mismo rol; (4) **O-4** — el RED de U3b suma fixtures de raíz temporal que solapan una ruta privada y el directorio de derivados, donde `deny` gana; (5) **O-5** — D-9 alineado con la superficie de §2.1 (`--project-root`); (6) **fila del scribe adoptada** (§12): `_allowed_kinds` admite `role-report` para el scribe, con **U7** (RED + regresiones de la tabla), **PD-26** y **E3 sin excepción**.
Corrección de la revisión anterior (draft-004): decisiones del owner registradas como tomadas (PD-19 aprobada; runtime explícito —O-9 cerrado, V-9 resuelta—; modelo y credencial fuera de `runtimes.json` confirmados); correlación por transporte en U2; permiso del agente derivado en U3 (PD-24); paso de migración `migrate` en U1a (E5, PD-25); O-10 (barrido previo al parseo del verbo); escenarios E1..E5 en la spec §3.1 y en el recorrido de U6 (PD-22).

## 1. Orden y dependencias

`U1a (config + migración) → U1b (entrada + registro) → U2`; `U1c` (agente en el paquete) es independiente de U1a/U1b y sólo condiciona a U2; `U3` y `U5` son independientes de U2 (tocan `cdad_packet.py`, sin solape de líneas con U1c); `U7` (fila del scribe en `cdad_result.py`) es independiente de todas y sólo la necesita `U6` para materializar el informe del scribe; `U4` al final (toca texto generado); `U6` después de U1a–U5 y U7. Ninguna unidad empieza sin su RED declarado y sin la review de spec/plan hecha (PD-21).

U1a va antes que U1b porque la entrada **consume** la sección de configuración (PD-8/PD-9): sin ella `dispatch` no tiene de dónde resolver el runtime, y el paso de migración (PD-25) es la vía declarada para que la sección exista. U1c, U3 y U5 **comparten archivo** (`skills/cdad-cycle/scripts/cdad_packet.py`), así que la ejecución es secuencial: ninguna de ellas se declara `parallel` con otra (una `parallel` mutua con archivos compartidos es paralelismo inseguro y el CLI lo rechaza). U7 toca **otro** archivo (`skills/cdad-cycle/scripts/cdad_result.py`) y ninguna otra unidad lo toca.

## 2. Unidades

| Unidad | Resultado | Depende de | PD | Gate |
|---|---|---|---|---|
| **U1a** | Configuración de ejecución por runtime: `runtimes.json`, resolución **explícita** del runtime, derivación, rechazo del exec-config como error de uso, **paso acotado de migración** y plantilla del instalador | — | PD-8, PD-9, PD-25 | RED + focales GREEN + regresiones de instalador/config + `make validate` (la confirmación del dueño de modelo/credencial **ya está registrada**: `execution.md`:262) |
| **U1b** | Entrada única `cdad_dispatch.py` (`dispatch`/`record`/`capabilities`) y **registro único** (la interfaz deja de registrar; kind derivado en la vía nativa) | U1a | PD-1…PD-6, PD-23 (nativa) | RED + focales GREEN + regresiones de delegación/interfaz/entrega (A-1) + `make validate` |
| **U1c** | Agente en el paquete: `prepare` resuelve rol+`stack` y escribe `agent`; el conjunto cerrado del request lo admite; el render no cambia | — | PD-7 | RED + focales GREEN + regresiones de `prepare`/render + `make validate` |
| **U2** | Módulo de runtime OpenCode: credencial inyectada, agente del paquete, kind derivado, `capabilities`/`--observe`, **correlación por la evidencia de su vía** (con el umbral de §2.3), fallo cerrado, sin polling | U1a, U1b, U1c (contrato) | PD-5, PD-10…PD-14, PD-23 (externa) | RED + focales con store descartable + **binario falso** + regresiones del módulo y de la tabla de materialización |
| **U3** | Temporal del test-writer: clase, política, propuesta, `git check-ignore` en `prepare` **y permiso de edición del agente derivado** para las raíces declaradas (con la precedencia probada) | — | PD-15…PD-18, PD-24 | RED + focales de scope y de derivados + regresiones de política/`prepare`/`receive`/derivados |
| **U4** | Entrada única en el mandato + secciones `delegation` + **borde de adopción de la migración** + regeneración | U1a–U1c, U2, U3 | PD-20 | RED de texto + `make staging` determinista + `make validate` |
| **U5** | Camino mecánico a `failed` con las condiciones aprobadas y desbloqueo verificado de `prepare` | — | PD-19 | RED + focales + regresiones de transiciones/estado (la aprobación del dueño **ya está registrada**: `execution.md`:260) |
| **U7** | Fila del scribe en la tabla cerrada: `_allowed_kinds("scribe", …)` admite `role-report`, con la materialización dentro de la carpeta de la spec y el Memory Bank fuera de su alcance | — | PD-26 (y PD-23, tabla) | RED + focales + regresiones de la tabla de materialización + `make validate` |
| **U6** | Recorrido de aceptación de §11 contra los escenarios E1..E5 (§3.1), en proyecto descartable, **sobre dos paquetes de la misma ejecución**, con las dos vías y el informe del scribe | U1a–U1c, U2–U5, U7 | PD-22, PD-26 (recorrido) | recorrido con evidencia; regla de bloqueo (§3 U6) |

## 3. Fichas por unidad

### U1a — Configuración por runtime, resolución, migración y plantilla
- **Archivos:**
  - **nuevo** `skills/cdad-cycle/scripts/cdad_dispatch.py`: la **capa de configuración** —resolución explícita del runtime (PD-8) y lectura/validación de la sección de `runtimes.json` con la derivación de la configuración interna del módulo bajo `.cdad/` (PD-9)—, el **barrido de `argv` por token exacto, previo al parseo del verbo**, con el diagnóstico único de migración (§2.6), el **paso acotado de migración** (PD-25, §2.6.1) y nada más: el resto de los verbos es de U1b.
  - `install.sh`: plantilla de `runtimes.json` con la disciplina de dato del usuario (`install_user_config`:1191-1200, precedente de plantilla `write_delegation_template`:1151 — sólo si no existe, no se registra en el manifiesto, no se pisa).
  - `skills/cdad-cycle/references/cli-delegation.md`: la entrada nueva, la sección de config, el paso de migración y su **borde de adopción** (el exec-config deja de ser dato del usuario; hoy lo describe en :31/:39/:89/:270/:345).
- **RED:** `tests/test_006_005_u1a_runtime_config.py` (nuevo) — **PD-8** (sin `--runtime` ⇒ rc≠0 nombrando el flag, en el verbo por defecto y en uno explícito; valor sin módulo ⇒ rc≠0 nombrando el valor; valor válido ⇒ procede; inspección: la entrada no lee `runtime` de ningún documento, ni del contexto v1 que lo declara). **PD-9** (documento derivado inspeccionado clave por clave; sin sección ⇒ el diagnóstico nombra `runtimes.json`, la sección y la **correspondencia clave por clave**; con `model` ⇒ rechazo que nombra `delegation.json`; `--exec-config` en `argv` en sus dos formas ⇒ rc≠0 antes de todo efecto y sin escritura; control negativo: `--exec-config` ausente de `--help` y **ninguna** lectura de archivo heredado fuera del paso de migración). **PD-25** (sin sección ⇒ escribe la sección clave por clave y sin `model`/credencial; con sección ⇒ rc≠0 y bytes de `runtimes.json` idénticos antes/después; `--dry-run` ⇒ sin escritura; archivo ausente ⇒ rc≠0 nombrando la ruta; la verificación es `capabilities`). Fixture: proyecto descartable con `XDG_CONFIG_HOME` redirigido (patrón ya usado por los tests de config de 006-003).
- **Regresiones:** `tests/test_006_003_u2_installer_without_profiles.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_006_003_u7_prune_obsolete.py`, `tests/test_install_review5_regressions.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`.
- **Nota (verificada):** el conjunto de archivos de config del usuario que `test_006_003_u7_prune_obsolete.py` fija (`CONFIG_REL_PATHS`:105-108) es **abierto** por construcción (`config_bytes` mapea sólo esas dos rutas y compara antes/después), así que la plantilla nueva no rompe esa aserción; la plantilla nueva **sí** debe quedar fuera del manifiesto (misma disciplina, se verifica en el RED).
- **Gate:** RED declarado y failing por la razón correcta; GREEN focal; regresiones verdes; `make validate`. La confirmación del dueño sobre modelo y credencial **ya está registrada** (`execution.md`:262) y no vuelve a pedirse; el RED la cita como precondición cumplida.
- **Nota de diseño (sin abstracción nueva):** no se crea `cdad_runtime_<id>.py` (D-2); no se agrega lista de versiones (la declaración sigue siendo `binary_version`); el paso de migración **no** reutiliza el nombre `--exec-config` (D-11) y escribe la sección **sólo si no existe** (INV-7).

### U1b — Entrada única y registro único
- **Archivos:**
  - `skills/cdad-cycle/scripts/cdad_dispatch.py` (mismo archivo de U1a, zona de verbos): los verbos `dispatch`/`record`/`capabilities` de §2.1, el cuerpo único de observación/registro/escenificación de `record` (PD-3…PD-6) con el **kind derivado** en su descriptor (PD-23, lado nativo) y la importación de los ayudantes de la interfaz (una sola implementación de cada uno).
  - `skills/cdad-cycle/scripts/cdad_delegate.py`: **se quita su registro** (`_observation`:288, `_register_dispatch`:311, su invocación :398) y se **relaya** el `attempt` del módulo; la interfaz conserva su CLI y su `--exec-config` (mecanismo interno, deuda declarada, §8 item 4).
- **RED:** `tests/test_006_005_u1b_dispatch_entry.py` (nuevo) — PD-1 (un intento por vía; la interfaz no registra), PD-2 (no es segundo escritor), PD-3 (`sha256` byte-exacto), PD-4 (sin texto no hay entrega ni `receive`), PD-5 (la correlación vía nativa por columnas: verificada / no verificable / **verificada e incorrecta** ⇒ rechazo; el paquete sin `agent`; **con sólo «agente» evaluable ⇒ `unknown`, y con dos despachos nativos concurrentes del mismo rol ninguna sesión se acredita**, O-3), PD-6 (`session: null` + `provenance`), PD-23 lado nativo (el descriptor de `record` declara el kind derivado del rol y la subfase —`role-report` incluido para el scribe, que su fila admite tras PD-26—; **la tabla `_allowed_kinds` no se toca en esta unidad**), **y PD-9 sobre los verbos que U1b agrega**: el token `--exec-config` (sus dos formas) rechazado en `dispatch` explícito, `record` y `capabilities` —observable porque el barrido es previo al parseo del verbo (O-10; el RED de U1a sólo ve el verbo por defecto).
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
  - **PD-10/PD-12/PD-13:** `--capabilities` y `--observe` (una lectura `mode=ro`, acotada, sin polling), exigiendo **las llaves que esta vía evalúa** y fallando cerrado nombrando las ausentes; `session_correlation` declara las llaves que la versión observada expone **y si alcanza el umbral de §2.3** (hoy: sólo `agent`, que no discrimina ⇒ `false` con `reason`).
  - **PD-5 (lado externo):** la correlación es **el id de sesión que el módulo elige** (`_choose_session_id`:242) corroborado contra `session_v2.agent` vs el agente del paquete (`_check_durable_identity`:327); **no** se compara un padre y **no** se exige `directory == raíz` (§2.3, INV-15). Una **contradicción evaluable** ⇒ rechazo que nombra la llave.
  - **PD-23 (lado externo):** el descriptor deja de escribir la constante `FINAL_TEXT_ARTIFACT_KIND` (`:127`, usado en `:1737`) y declara el kind derivado de rol y subfase según §2.8 (una sola fuente: la tabla de `cdad_result`, ya importado por el módulo, `:108`).
  - `attempt` declarado en el sobre (conserva su registro, PD-1).
- **Sonda antes del RED:** V-1/V-7 (cómo se obtiene la sesión hija y **columnas reales de la versión instalada**, para declarar en `capabilities.session_correlation` cuáles expone y si alguna discrimina) y V-13 (el kind derivado contra la tabla real); el hallazgo se registra y se declara en `capabilities`.
- **RED:** `tests/test_006_005_u2_opencode_module.py` (nuevo) — **binario falso que exige `OPENCODE_PASSWORD`** y eco de si la vio (PD-11, con el centinela ausente de `argv`, stdout/stderr, registro I8 y recibo); PD-14 (`argv` con el agente del paquete; agente no publicado → fallo cerrado; sin campo → `cdad-<rol>` declarado); PD-5 lado externo (el id del transporte como asociación; **acepta** un `directory` de subdirectorio del proyecto y de un coordinador iniciado en otra carpeta; **rechaza** un `agent` de otro rol); PD-12/PD-13 con store SQLite descartable (receta de aislamiento, `cli-delegation.md`:239+); PD-10 (incluido el módulo sin la superficie nueva **y el store que sólo expone `agent`**: `session_correlation: false` con `reason` que nombra la llave discriminante ausente); PD-23 lado externo (entrega del reviewer en `plan-review` → `artifact_kind: plan-review` y `materialize` rc=0 con sha idéntico; architect en `draft` → `role-report` y `materialize` rc=0; **scribe → el descriptor declara `role-report`** —el kind que su fila admite tras PD-26; la materialización de esa fila es el oráculo de U7).
- **Regresiones:** `tests/test_cdad_adapters_opencode.py`, `tests/test_005_009_t2_opencode_adapter.py`, `tests/test_006_001_t1b_service_mode.py`, `tests/test_006_001_t2_wait_recovery.py`, `tests/test_006_001_t3_concurrency.py`, `tests/test_006_003_u6_server_credential.py`, `tests/test_003_003_t2_preflight.py` y la **tabla cerrada de materialización**: `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t2_reviewfix.py`, `tests/test_003_002_t1_receive.py`.
- **Gate:** focales verdes con store descartable y binario falso; regresiones verdes (incluida la tabla, que **no cambia en esta unidad**); `make validate`.

### U3 — Temporal del test-writer (autorizado **y escribible**)
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — **cuatro zonas**:
  1. vocabulario de clases (`SCOPE_CLASSES`:67, hoy sin `temporary`), validador único de scopes (`_validate_scope`:694 y el conjunto de escritura del test-writer :728-729) y pertenencia de un cambio observado (`_scope_contains`:739, usado por el manifiesto en `cdad_result.py`:370; sólo si debe clasificar el temporal — un cambio ignorado nunca entra al manifiesto, INV-3);
  2. propuesta (`propose_policy`:1088, hoy `temporary_roots: []` en :1100) y el paso `git check-ignore` en `prepare`;
  3. **el permiso del agente derivado (PD-24, §2.9):** `_derived_maps`:2783 para el test-writer emite como `allow`, **junto a las reglas de permiso del rol y antes de la política, los derivados y las rutas privadas**, las **raíces temporales declaradas**; su llamada en `_build_derived_payloads`:2968/:2996 (`_rewrite_derived_agent`:2854) recibe esas raíces;
  4. la **fuente** de esas raíces: la política aceptada que el contexto ya pina y cuyo sha gobierna el manifiesto (`policy_sha = execution_document["execution"]["policy_sha256"]`, :2990) — en v2 el `policy.snapshot` verificado contra `policy_sha256` (:630-637; hoy `temporary_roots: []`, medido), en v1 plano el archivo de política validado por `_validate_policy_document` (:432).
  El detalle de forma es del implementer; el contrato son PD-15…PD-18 y PD-24.
- **RED:** `tests/test_006_005_u3_temporary_scope.py` (nuevo) — PD-15 (política vacía → rechazo nombrando `docs/cdad-policy.json`; con raíz declarada → acepta), PD-16 (`git check-ignore` negativo y positivo, y proyecto no-Git), PD-17 (recibo `scope_validation: passed` con test real + sonda temporal, y rechazo fuera de scope; la nota de alcance: `passed` no prueba la escritura). **`tests/test_006_005_u3b_derived_temporary_permission.py`** (nuevo) — PD-24: con una raíz temporal declarada, el derivado publicado la lista en `edit` como `allow` y **ninguna otra ruta gana permiso** (producto, política, derivados y privados siguen `deny`); con `temporary_roots: []` el mapa es **byte-idéntico** al de hoy; se publica por el mismo camino y con el mismo manifiesto; **y la precedencia se prueba con dos fixtures de colisión (O-4):** (a) una raíz temporal que **solapa una ruta privada** declarada por la política del fixture **fuera de las regiones de producto** —así `_validate_temporary_roots`:414-430, que sólo garantiza disjunción con producto, la admite— ⇒ el `deny` privado gana; (b) una raíz temporal que **solapa el directorio de derivados** (`.opencode/agents/`, `DERIVED_RELPATH`:98) ⇒ el `deny` de derivados gana. Sin estos dos casos un `allow` emitido **después** de las barreras (que invertiría la precedencia) pasaría inadvertido.
- **V-8 / regla A-1:** no se encontró test que fije el valor de la propuesta; si el RED encuentra uno, se cambia **en RED declarando el reemplazo**.
- **Regresiones:** `tests/test_004_002_t1_policy.py`, `tests/test_004_002_t1_reviewfix.py`, `tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t6_landing.py`, `tests/test_004_002_t7_acceptance.py`, `tests/test_004_002_t7_private_paths.py`, `tests/test_004_002_t7_limits_rule.py`, `tests/test_004_002_t5_runtime.py`, `tests/test_004_002_t5_reviewfix.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_packet_prepare.py`, `tests/test_005_005_t2_docs_policy.py`.
- **Gate:** RED + focales; regresiones de política, recepción y **derivados** verdes; `make validate`. La prueba de que el temporal es **escribible de verdad** no está en esta unidad: es la escritura real del recorrido de U6 (V-14).

### U4 — Entrada única, secciones `delegation` y borde de adopción
- **Archivos:** `sources/roles/orchestrator.md` (intake :22-57 con las cuatro entradas solapadas y la condición stale :24; disciplina de contexto :104-108), `sources/agents/adapters/opencode.md` (§`delegation` :60-94), `sources/agents/adapters/claude-code.md` (§`delegation` :80-116), `skills/cdad-cycle/references/re-entry.md` (si el paso mecánico de escenificación se nombra allí), `skills/cdad-cycle/references/cli-delegation.md` (el **borde de adopción** de §2.6.1: orden migrar → `capabilities` → despachar; una sola fuente vigente), `scripts/cdad-generate.py`:747 (etiqueta «## Delegation (adapter)», V-4) y **las salidas declaradas de `make agents`**: `agents/cdad-*.md` (11 archivos) y `agents/claude-code/cdad-*.md` (11 archivos), que son promociones de `build/staging/` y nunca se editan a mano (`Makefile`:1-24, objetivos `staging`/`agents`).
- **RED:** `tests/test_006_005_u4_single_entry.py` (nuevo) — PD-20: la fuente tiene el orden de cinco filas sin solapes, **sin** la condición `.cdad/execution.json` y **con** la regla de transporte (mismo runtime ⇒ nativa + `record`; otro ⇒ la entrada externa); el generado recomputado coincide byte a byte; las secciones `delegation` nombran la entrada nueva (con `--runtime`), el agente del paquete y la credencial del módulo; y el texto del **borde de adopción** de la migración está presente y no sugiere que el producto lea el exec-config.
- **Regresiones (todo test que lea orquestadores o agentes generados):** `tests/test_005_006_t2_intake.py`, `tests/test_006_002_u1_delegation_section.py`, `tests/test_006_002_u2_neutral_skill.py`, `tests/test_006_002_u3_runtime_references.py`, `tests/test_006_002_u6_context_discipline.py`, `tests/test_006_003_u3_texts_without_profiles.py`, `tests/test_cdad_generate.py`, `tests/test_bash_policy_selection.py`, `tests/test_opencode_read_map_and_steps.py`, `tests/test_005_004_t2_installer_claims.py`, `tests/test_role_packet_render.py`.
- **Gate:** `make staging` determinista (dos corridas, mismos bytes), RED de texto verde, regresiones verdes, `make validate`.

### U5 — Camino mecánico a `failed`
- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — efecto de la clase `disposition` (hoy `pass`:5586) y la coherencia de `validate_state` (:546). No se toca `_dispatched_packet_ids`/`_missing_required_deliveries` (:4855/:4944): leen el **ledger de despachos**, así que el cierre sigue satisfaciendo PD-8(a) por la disposición registrada.
- **RED:** `tests/test_006_005_u5_disposition_failed.py` (nuevo) — PD-19: paquete activo sin recibo → `failed`; **sólo** `active_packet` cambia y **es idempotente** (segunda invocación idéntica ⇒ no-op con estado byte-idéntico); `validate-state` VALID; `prepare` bloqueado antes (:4336-4338; `ACTIVE_PACKET_STATUSES`:115) y desbloqueado después; la ruta `late-delivery` sigue registrable sobre el mismo paquete (fixture de feature cerrada con recibo durable, :5233-5249); con recibo durable ⇒ rechazo que nombra `receive` (:5207-5213); la disposición sigue sin aprobar nada (`approval_effect: false`, sin `approved_by`).
- **A-1 (declarado):** `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 afirma hoy que el paquete sigue `dispatched` tras la disposición. Reemplazo declarado: «`active_packet.status` pasa a `failed` (terminal); el resto del estado sigue intacto». La enmienda de esa consecuencia INV-9 está **aprobada por el dueño** (`execution.md`:260). Se revisa además que el flujo B1 (:835) siga avanzando.
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
- **Gate:** RED + focales; regresiones verdes; `make validate`. La aprobación del dueño **ya está registrada** (`execution.md`:260) y no vuelve a pedirse: PD-19 la cita como precondición cumplida.

### U7 — Fila del scribe en la tabla cerrada (informe del rol)
- **Archivos:** `skills/cdad-cycle/scripts/cdad_result.py` — **una sola zona**: la fila del scribe de `_allowed_kinds` (:701-703) pasa a admitir `role-report` además de los cuatro `scribe-*`, con su comentario. **No** se toca `_allowed_target`/`_artifact_policy` ni `skills/cdad-cycle/assets/artifact-policy.json` (el kind `role-report` ya existe con raíz `docs/specs/<feature>/`, `:672-678`). Ninguna otra fila de la tabla cambia. Decisión D-17; contrato: PD-26 (§2.8.3).
- **RED:** `tests/test_006_005_u7_scribe_role_report.py` (nuevo) — PD-26: recibo de rol `scribe`/subfase `memory` con la **parte única `role-report`** ⇒ `materialize` rc=0 hacia un target dentro de `docs/specs/<feature>/` con **sha idéntico** al de la parte (hoy rc≠0 por la tabla); **caso negativo del destino**: un target de Memory Bank (`docs/projectbrief.md`, y el mismo criterio para `docs/systemPatterns.md`, `docs/activeContext.md`, `docs/progress.md`) con ese kind ⇒ rc≠0 nombrando la raíz permitida (el Memory Bank no es alcanzable por el informe); **regresión R5**: los cuatro `scribe-*` siguen materializando sus raíces-archivo; **eje rol**: `role-report` de un rol que no lo admite (test-writer, implementer, reviewer) ⇒ sigue rechazado, y los cuatro cruces de R3 siguen rechazados; `artifact-policy.json` inspeccionado (sin cambios); recibo `pending`, `approval_effect: false`.
- **A-1 (declarado):** ningún test del repo afirma hoy que el scribe con `role-report` se rechace (verificado: R2 cubre sólo los kinds de auditoría y R3 cruza `("scribe","memory","test-audit")`; las clases R5 usan los cuatro `scribe-*`). Si el RED encuentra un test que fije la fila del scribe **incluyendo la ausencia de `role-report`**, se declara el reemplazo aquí antes de tocarlo.
- **Regresiones (la tabla de materialización, `cdad_result.py`):** `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t2_reviewfix.py` (R2/R3/R5), `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t1_reviewfix.py`, `tests/test_003_002_t4_integration.py`, `tests/test_005_007_t4_architect_report_materialization.py`.
- **Gate:** RED + focales; regresiones verdes; `make validate`. La fila **no** cambia el resto de la tabla; la prueba de recorrido real del informe del scribe es de U6 (E3).

### U6 — Recorrido de aceptación (no es unidad de código)
- **Escenario (PD-22, contra los escenarios E1..E5 de §3.1 de la spec):** proyecto **descartable** con **layout anidado** y el coordinador iniciado **desde otra carpeta**, y **dos paquetes de la misma ejecución** (nunca dos recepciones del mismo paquete: el recibo durable admite una sola finalización por par ejecución/paquete, `_final_dir` `cdad_result.py`:212, y la convergencia exige el mismo conjunto de partes, `_require_identical_result`:440). (E3) **un despacho por la vía externa** con la entrada nueva y **sólo paquete y `--runtime`** (con su intento = el del módulo y su kind derivado del rol y la subfase, materializado con `materialize` rc=0), **más un segundo despacho externo del rol scribe** cuya parte única `role-report` se materializa dentro de `docs/specs/<feature>/` (PD-26); `receive` y la transición `delivery` del protocolo de re-entry (el paquete queda `completed`, `cdad_packet.py`:5560, y `ACTIVE_PACKET_STATUSES`:115 no lo incluye ⇒ el `prepare` del siguiente queda desbloqueado); (E1) **un despacho por la vía nativa** (`task` + `record`) del **otro paquete de la misma ejecución**, con su intento I8 registrado **una vez** y su entrega recibida; (E2) un auxiliar **escrito con la herramienta del rol** dentro del temporal declarado (sonda V-14) **más un test real escrito y recibido** (recibo `pending`, `scope_validation: passed`, **y el auxiliar escrito**); (E4) un intento interrumpido registrado sin entrega y llevado a `failed` **por comando**, con el siguiente paquete preparable y `reconcile` limpio antes de repetir; (E5) la migración de un **exec-config heredado** a la sección y su verificación con `capabilities`; y la sonda V-11 (`--agent cdad-<rol>-odoo` con `stack: odoo`).
- **Evidencia:** los archivos de intento I8 (uno por despacho y por paquete), **los recibos de los dos paquetes**, el estado resultante, los sobres de los dos verbos, la materialización de la entrega no-architect con su kind derivado, **el informe del scribe materializado dentro de la carpeta de la spec**, el auxiliar escrito en el temporal **con la copia del agente en efecto y el directorio efectivo del hijo** (O-2), la sección migrada y su salida de `capabilities`, y la versión/configuración observadas. Sin generalizar (spec §7). Se entrega como documento de evidencia en la carpeta de la spec (no en `tests/`).
- **Regla de bloqueo por ambiente (con la atribución de V-14):** si el ambiente no puede ejecutar el recorrido (runtime ausente, versión fuera de la declarada, store no disponible, agente `-odoo` no publicado, **o el runtime bloquea la escritura del auxiliar con la copia derivada en efecto — V-14**), la unidad se declara **BLOQUEADA** con el motivo y la evidencia del intento; **no** se sustituye por una corrida simulada, por un éxito inventado, por «debería funcionar» ni por `scope_validation: passed`. **Caso distinto y declarado (O-2):** si la escritura se bloquea **y la observación registrada muestra que la copia en efecto es la global instalada** (coordinador fuera de la raíz), el bloqueo **se atribuye a esa causa**, se registra como límite declarado del recorrido nativo con su disparador (spec §9), **no** invalida U3, y la escritura temporal queda cubierta por la vía externa (que pinea `PWD` a la raíz). Decide el dueño/orquestador (autorizar, re-scopear o re-rutear) en cualquiera de los dos casos.

## 4. Regla A-1 (tests acoplados)

Un test acoplado a la superficie que cambia se modifica **sólo en el RED de su unidad**, declarando en el propio RED: (1) el test que se reemplaza, (2) la postcondición nueva que lo reemplaza, (3) la razón. Nunca en GREEN, nunca por invisibilizar un fallo. Aplica a:

| Unidad | Test | Reemplazo declarado |
|---|---|---|
| U1b | `tests/test_005_009_t1_interface.py` (las aserciones donde la **interfaz** es quien registra) | la interfaz **relaya** el `attempt` del módulo y **no** registra; el destino de prueba del fixture registra **su propio** intento; el único registro del despacho es el del módulo (PD-1/D-ADP-2). El resto del contrato de la interfaz (transporte byte-idéntico, sobre, fallo cerrado) no cambia. |
| U1b | `tests/test_005_010_t1_durable_signal.py` (`:431-449` cuenta un registro del worker **además** del de la interfaz; `:536-543` aserta `model_reported` nulo en el registro de la interfaz) | **un solo registro por despacho**: la interfaz relaya el `attempt` del módulo, la distinción interfaz/worker dentro de la vía externa desaparece (D-14/PD-1) y el `model_reported` del único registro sale de la observación del módulo (la fila durable). Se conservan las aserciones del registro del worker; se retiran las del registro de la interfaz. |
| U1b | `tests/test_005_010_t4_integration.py` (`:480-486` y `:540-557`, mismo patrón) | idéntico reemplazo que el anterior (mismo acoplamiento verificado). |
| U1b | `tests/test_005_010_reviewfix.py` (`:489-500`: «el registro NUEVO que NO es el de la interfaz») | idéntico reemplazo: la localización del registro I8 del intento pasa a ser «el único registro nuevo del despacho»; las aserciones sobre `model_reported` desde la fila durable no cambian. |
| U3 | — (V-8: ningún test encontrado hoy que fije el valor de la propuesta) | si el RED encuentra uno, se declara aquí antes de tocarlo |
| U3 | — (PD-24: la política vigente de este repo declara `temporary_roots: []`, así que el mapa derivado es byte-idéntico al de hoy y `tests/test_004_002_t5_runtime.py` no cambia) | si el RED encuentra un test que fije el mapa `edit` del test-writer derivado incluyendo los probes usados, se declara aquí antes de tocarlo |
| U5 | `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 | `active_packet.status` pasa a `failed` (terminal); el resto del estado intacto (enmienda **aprobada** por el dueño, `execution.md`:260) |
| U2 | — (V-13: la tabla `_allowed_kinds` **no** se modifica en esta unidad; PD-23 sólo cambia el kind declarado por las entregas) | si el RED de U2 encuentra un test que fije la constante `role-report` del módulo, se declara aquí antes de tocarlo |
| U7 | — (verificado: ningún test afirma hoy que el scribe con `role-report` se rechace; R2 cubre los kinds de auditoría, R3 cruza `("scribe","memory","test-audit")` y las clases R5 usan los cuatro `scribe-*`) | si el RED encuentra un test que fije la fila del scribe incluyendo la **ausencia** de `role-report`, se declara aquí antes de tocarlo (PD-26/D-17) |

## 5. Cierre

Review independiente de spec/plan **antes** del RED (PD-21; `plan-review` sobre `draft-plan`, sin subfase nueva): esta entrega es la corrección del dictamen por escenarios (B-1) y de sus cuatro opcionales, más la fila declarada del scribe; va a una **re-review focal**; la aprobación es de la autoridad vigente y **no** la habilita el dictamen. Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada; se repite sólo si cambios o evidencia invalidada lo justifican). Review formal del resultado en sesión independiente; el recorrido real de U6 (AC-7) queda declarado con su estado, y no se acredita aceptación real por pruebas aisladas.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
 "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1a, U1b, U1c, U2, U3, U4, U5 y U7; make staging determinista en U4. Los gates del dueno que estaban pendientes YA ESTAN REGISTRADOS (execution.md:260 PD-19 aprobada con sus condiciones; execution.md:262 modelo y credencial fuera de runtimes.json): no hay gate del dueno que esperar antes de un RED, y las unidades los citan como precondicion cumplida. La suite completa la corre una vez quien cierra (PD-21); se reutiliza evidencia equivalente con procedencia verificada (re-entry.md, Equivalence of a registered run).",
 "tasks": [
  {
   "id": "U1a",
   "objective": "Configuracion de ejecucion por runtime: runtimes.json (seccion por runtime), resolucion explicita del runtime por flag, derivacion de la configuracion interna, rechazo del exec-config heredado como error de uso con barrido previo al parseo del verbo, paso acotado de migracion y plantilla del instalador.",
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
   "objective": "Entrada unica cdad_dispatch.py (dispatch/record/capabilities) con registro unico: la interfaz deja de registrar y relaya el attempt del modulo; record deriva el kind de la parte entregada y la correlacion nativa exige al menos una llave discriminante (con solo agente el resultado es unknown); el rechazo del token --exec-config se observa tambien en cada verbo nuevo.",
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
   "objective": "Modulo de runtime OpenCode: credencial inyectada solo en el cliente en mode server, agente del paquete, kind derivado de la parte entregada (role-report tambien para el scribe), --capabilities/--observe con session_correlation que declara el umbral de discriminacion, correlacion por la evidencia de la via externa (id de sesion que el modulo elige, sin igualdad directory == raiz), fallo cerrado, sin polling.",
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
   "objective": "Temporal del test-writer autorizado Y escribible: clase temporary, politica, propuesta, git check-ignore en prepare, y permiso de edicion del agente derivado acotado a las raices temporales declaradas (sin abrir producto), con la precedencia probada por colisiones con una ruta privada y con el directorio de derivados.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u3_temporary_scope.py",
    "tests/test_006_005_u3b_derived_temporary_permission.py"
   ],
   "regressions": [
    "tests/test_004_002_t1_policy.py",
    "tests/test_004_002_t1_reviewfix.py",
    "tests/test_004_002_t2_bootstrap.py",
    "tests/test_004_002_t6_landing.py",
    "tests/test_004_002_t7_acceptance.py",
    "tests/test_004_002_t7_private_paths.py",
    "tests/test_004_002_t7_limits_rule.py",
    "tests/test_004_002_t5_runtime.py",
    "tests/test_004_002_t5_reviewfix.py",
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
   "objective": "Entrada unica en el mandato del orquestador + secciones delegation + borde de adopcion de la migracion + regeneracion de los generados con make agents.",
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
    "skills/cdad-cycle/references/cli-delegation.md",
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
   "objective": "Camino mecanico a failed por disposition sin recibo, con las condiciones aprobadas por el dueno (solo el paquete identificado, idempotente, entregas tardias intactas, reconcile antes de repetir) y desbloqueo verificado de prepare.",
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
   "id": "U7",
   "objective": "Fila declarada del scribe en la tabla cerrada: _allowed_kinds admite role-report para el scribe (el informe del rol se materializa dentro de docs/specs/<feature>/), el Memory Bank queda fuera de su alcance y ninguna otra fila de la tabla cambia.",
   "produce": [],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_result.py"
   ],
   "focal_tests": [
    "tests/test_006_005_u7_scribe_role_report.py"
   ],
   "regressions": [
    "tests/test_003_002_t2_materialize.py",
    "tests/test_003_002_t2_reviewfix.py",
    "tests/test_003_002_t1_receive.py",
    "tests/test_003_002_t1_reviewfix.py",
    "tests/test_003_002_t4_integration.py",
    "tests/test_005_007_t4_architect_report_materialization.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "U6",
   "objective": "Recorrido de aceptacion de los escenarios E1..E5 (PD-22) en proyecto descartable con layout anidado y el coordinador iniciado desde otra carpeta, sobre DOS paquetes de la misma ejecucion (nunca dos recepciones del mismo paquete): entrega externa con solo paquete y runtime materializada por kind derivado; informe del scribe materializado como role-report dentro de la carpeta de la spec (PD-26); entrega nativa con task + record del otro paquete registrada una vez y recibida; escritura real del auxiliar temporal con la herramienta del rol mas test real, registrando que copia del agente cargo el hijo; intento interrumpido a failed por comando con el siguiente paquete preparable; migracion de un exec-config heredado verificada con capabilities; y la sonda V-11; no es unidad de codigo; regla de bloqueo por ambiente con atribucion por copia.",
   "produce": [],
   "consume": [],
   "depends_on": [
    "U1a",
    "U1b",
    "U1c",
    "U2",
    "U3",
    "U4",
    "U5",
    "U7"
   ],
   "parallel": [],
   "files": [],
   "integration_gate": "@validation_strategy",
   "owner": "orquestador (recorrido real) con evidencia",
   "observable_checks": [
    "intento I8 por cada via y por paquete (externa con la entrada nueva y --runtime; nativa con task + record) en .cdad/executions/<exec>/dispatches/, uno por despacho; los dos paquetes de la misma ejecucion, nunca dos recepciones del mismo paquete",
    "entrega no-architect por la via externa materializada con su kind derivado del rol y la subfase (descriptor con artifact_kind: plan-review; materialize rc=0 con sha identico)",
    "informe del scribe por la via externa materializado como role-report dentro de docs/specs/<feature>/ (materialize rc=0, sha identico) y el destino del Memory Bank rechazado por esa raiz (PD-26)",
    "auxiliar escrito con la herramienta del rol dentro del temporal declarado (sonda V-14) y recibo pending con scope_validation: passed para un test real; el recibo no prueba la escritura, la escritura si",
    "sonda V-14 con atribucion: resultado de la escritura, directorio efectivo del hijo nativo y copia del agente en efecto (derivada project-local vs global instalada, resuelta con opencode debug agents en ese directorio); si la copia es la global el bloqueo se atribuye a esa causa y queda como limite declarado con disparador; si es la derivada y la escritura se bloquea, la unidad se declara BLOQUEADA",
    "intento interrumpido llevado a failed por register-transition disposition, validate-state VALID, siguiente paquete preparable y reconcile limpio antes de repetir",
    "seccion de runtimes.json escrita por el paso de migracion (sin pisar la existente) y verificada con capabilities --runtime X",
    "sonda V-11: session_v2.agent == cdad-<rol>-odoo en proyecto descartable con stack: odoo, o BLOQUEADA con motivo"
   ],
   "regressions": []
  }
 ]
}
```


---

Erratas de letra aceptadas en la aprobación (`plan-review-004.md`, opcionales sin efecto en contrato): **O-6**, el recorrido de U6/PD-22 usa un paquete distinto por cada entrega (tres despachos con entrega más el de repetición de E4), nunca dos recepciones del mismo paquete; donde dice «dos paquetes», rige ese invariante. **O-7**, el caso `--exec-config` en `argv` sobre `migrate` del oráculo de PD-9 lo declara el RED de U1a. N-1 (base medida) sin efecto.

Status: Approved by orquestador Claude (HITL delegada por Pablo, epic-006) on 2026-10-18; enmienda PD-19 y las decisiones de runtime, modelo y credencial approved by Pablo on 2026-10-18 (`execution.md`, «Decisiones del owner sobre los gates de 006-005»).
