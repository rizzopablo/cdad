# 006-006-spec-plan-review — PLAN (etapa 2, borrador draft-004)

Estado: **BORRADOR — SIN APROBAR**. Habilita el RED por unidad **sólo** después de la aprobación de la spec y de la revisión independiente de este par (PD-21 del plan de 006-005, y §13.3 de la enmienda 006: la revisión del borrador precede al RED).
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §13 (sha256 `d6da11db…9809`). Spec: la de esta carpeta (misma entrega). Decisiones: `docs/epics/epic-006-opencode-concurrency/execution.md`:379-388.
Correcciones de draft-003 (dictamen `docs/specs/006-006-spec-plan-review/plan-review-002.md`, 1 bloqueante — **B-3**; conservadas en draft-004): la exención entra en el payload de identidad **sólo cuando se declara** (spec §2.7 R-11/R-12/R-13, PD-9, INV-12/INV-13, D-13/D-14, V-7) → toca §3 U5 (la zona del payload pasa a **condicional**; el RED gana el **recorrido de dos revisiones** en `gate`, `closure` y `disposition`; las regresiones ganan `tests/test_005_014_closure_replay.py` y `tests/test_006_005_u5_disposition_failed.py`) y §4 (la fila «la identidad de la transición» reescrita: el análisis de draft-002 estaba equivocado, y por qué).
Correcciones de draft-004 (dictamen `docs/specs/006-006-spec-plan-review/plan-review-003.md`, 1 bloqueante — **B-4**; B-3 queda **cerrado en el diseño**): la rama de no-op se **qualifica** —el **replay histórico** (la entrada nombrada **es** la vigente, o no hay vigente que compita) **sigue siendo no-op**, y la invocación que colisiona con una entrada histórica que **NO** es la vigente deja de ser un no-op exitoso: con `--supersedes` ⇒ **rechazo explícito de colisión** (nombra la clave que colisiona, que no es la vigente, la clave de la vigente y las dos salidas); sin `--supersedes` ⇒ el **rechazo vigente** de una sola aprobación (spec §2.7 R-14, PD-9, INV-12, D-15, V-8) → toca §3 U5 (la zona de la decisión de no-op gana la calificación y el rechazo de colisión, y el RED gana el **recorrido A→B→A** con sus dos ramas, el replay de la vigente y el registro con valor distinguible) y §4 (la fila «la identidad de la transición» y la A-1, con la evidencia de que ningún oráculo vigente cambia). **Sin** cambio en la fórmula de la identidad (R-11/R-12/R-13 intactas) y **sin** cambio en las claves históricas. Todo lo demás de draft-003 se conserva.
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
| **U5** | **La exención registrada **e incluida en la identidad de la transición, pero sólo cuando se declara:** tres banderas opcionales (+ un interruptor) en la clase `gate` de `register-transition`, con `exempted_by`, `delegated`, `requested_by` y `reason` en la entrada, y un **bloque `exemption` condicional** en el payload de identidad (repetición idéntica = no-op; repetición que cambia la exención = registrada por `--supersedes` o rechazada, nunca éxito sin registrar) **y el replay histórico distinguido del intento de sustituir la aprobación vigente** (la colisión con una entrada histórica que **NO** es la vigente se **rechaza explícitamente**, nunca un no-op que deje la anterior vigente) **sin** cambiar la identidad de ninguna transición ya registrada | U1 | PD-9, PD-1 (forja) | RED + focales GREEN + regresiones de transiciones/estado (incluidas las dos de O-1 y las dos nuevas de B-3) + `make validate` |
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

- **Archivos:** `skills/cdad-cycle/scripts/cdad_packet.py` — **cuatro** zonas:
  1. el parser de `register-transition` (~:6425-6480): tres banderas opcionales y un interruptor — `--exempted-by`, `--exemption-reason`, `--requested-by`, `--delegated`; admisibles **sólo** con `--transition gate` (fuera de esa clase ⇒ rc≠0 nombrando la clase);
  2. la construcción de la entrada de la clase `gate` (~:5849-5856): la entrada suma `exempted_by`, `reason`, `requested_by` y `delegated` **sólo** cuando las banderas están presentes (planos, en la entrada);
  3. **el payload canónico de identidad** (`_transition_identity_payload`, :5015-5063) — **zona cambiada por B-3**: el payload se construye **exactamente como hoy** (16 claves) y **sólo** cuando la invocación **declara** la exención (alguna de las cuatro banderas) se le añade **una** clave, `exemption`, con **exactamente** los campos declarados (R-11/R-12). **Sin** exención declarada: **ni una clave cambia** ⇒ la serialización canónica (:5077-5079) y la `transition_key` son **byte-idénticas** a las del producto vigente (R-13) ⇒ las entradas ya registradas siguen reconociéndose como la misma transición, y la repetición idéntica de una transición registrada por la revisión anterior del producto sigue siendo un **no-op**;
  4. **la rama de no-op** (:5767-5770) y **la regla de una sola aprobación vigente** (:5789-5829) — **zona cambiada por B-4**: la rama de no-op se **qualifica** (R-14). Si la entrada que la clave nombra **es** la aprobación vigente de esta invocación (o no hay vigente que compita con ella) ⇒ **no-op**, como hoy (PD-11, PD-23, PD-19(b)). Si **no** es la vigente y hay una vigente que compita ⇒ **nunca** un no-op: con `--supersedes` ⇒ **rechazo explícito de colisión** (rc≠0, marcador `state incoherent`, nombrando la clave que colisiona y que **no** es la vigente, la clave de la vigente y las **dos salidas**: registrar el cambio con un **valor distinguible**, o **reconciliar**); sin `--supersedes` ⇒ el rechazo vigente de :5821-5829 (que nombra la entrada vigente y la vía). El rechazo de colisión se evalúa **antes** de la rama de no-op y **no** sustituye la regla vigente de PD-14: sin `--supersedes`, el rechazo sigue siendo el de :5821-5829.
- **Lo que se toca y lo que no:** se **qualifica** la decisión de no-op (:5767-5770) — su **resultado** no cambia cuando la entrada nombrada es la vigente (PD-11) ni en las clases sin aprobación vigente (PD-23, PD-19(b)), ni en las invocaciones sin pin de contrato; lo que se **añade** es el rechazo de colisión. **No se toca** la fórmula de la clave ni el payload de las 16 claves (R-11/R-12/R-13), ni el pin de la aprobación, ni el texto del rechazo vigente de PD-14.
- **RED:** `tests/test_006_006_u5_exemption_record.py` (nuevo) — **PD-9**:
  - la invocación con las cuatro banderas escribe una entrada de `stage_history` con `exempted_by`, `reason`, `requested_by` y `delegated`;
  - la invocación **sin** ellas escribe una entrada **sin** esos campos (control negativo);
  - las banderas fuera de la clase `gate` ⇒ rc≠0 nombrando la clase;
  - la entrada de exención **no habilita construcción** (un `prepare` de un rol de construcción sigue rechazando sin la aprobación con su pin);
  - **V-4**: la aprobación con exención sigue siendo **vigente** para el cierre (PD-8(b)) y una segunda aprobación sin `--supersedes` **sigue** rechazándose;
  - **identidad, los dos casos (B-2):** (a) **repetición idéntica** (misma exención) ⇒ rc=0, **no-op**, **sin** segunda entrada, state byte a byte idéntico y salida que nombra la entrada existente; (b) **repetición que cambia la exención** ⇒ **no** es no-op: se **registra** por `--supersedes <transition_key>` (la entrada previa sigue en el historial y la nueva la marca) **o** se **rechaza explícitamente** nombrando la entrada vigente y la vía permitida — **en ningún caso** rc=0 sin registrar; el `transition_key_payload` de la entrada lleva el bloque `exemption` con **exactamente** los campos declarados (y **sin** bloque cuando la invocación no declara exención) y la `transition_key` se **recomputa** desde él.
  - **el recorrido A→B→A (B-4) — retirada y restauración de un valor anterior, con sus cinco pasos:** (i) **A**: `register-transition --transition gate --stage specification --contract-path <spec> --approve-by <autoridad>` (sin exención) ⇒ rc=0 y una entrada, con su `transition_key`; (ii) **B**: la misma orden **con** las cuatro banderas de exención y `--supersedes <key_de_A>` ⇒ rc=0 y una **segunda** entrada, cuya clave es **distinta** (el bloque `exemption` entra en el payload); (iii) **A de nuevo, sin `--supersedes`**: la orden de (i) ⇒ **rc≠0** y **no** un no-op: el **rechazo vigente** de PD-14, que nombra la entrada vigente; (iv) **A de nuevo, con `--supersedes <key_de_B>`** ⇒ **rc≠0** con el **rechazo de colisión**: el mensaje nombra la **clave que colisiona** (la de A) y dice que **no** es la vigente, nombra la **clave de la vigente** (la de B) y nombra las **dos salidas**; en **ambos** rechazos el estado queda **byte-idéntico** y **B sigue vigente** (el lector del producto lo dice: la entrada que habilita sigue siendo la de B); (v) **el replay de la vigente**: repetir la orden de (ii) (B) ⇒ **rc=0**, **no-op**, sin segunda entrada, estado byte-idéntico y salida que nombra la entrada existente. **El RED comprueba la vigencia con el lector** (`prepare` de un rol de construcción: habilitado por la entrada vigente, bloqueado por la sustituida), no sólo con el conteo de entradas.
  - **el registro con valor distinguible (la salida que nombra el rechazo de colisión):** repetir (i) **citando evidencia** (`--artifact <archivo-de-decisión-del-owner>`; su digest entra en la identidad, :5028-5031) ⇒ la clave **difiere** de la de A ⇒ **rc=0** y una **tercera** entrada, **vigente** (su clave no está en el conjunto de claves sustituidas) y **sin** bloque `exemption` ⇒ la exención queda **retirada** de verdad y la vigente anterior deja de habilitar. **Si esta salida no se puede materializar, el RED falla** (es la parte del contrato que el rechazo declara).
  - **recorrido de dos revisiones (B-3) — los tres casos**, `gate`, `closure` y `disposition`: (i) se registra la transición con el CLI real; (ii) se comprueba que el `transition_key_payload` escrito es **byte-idéntico** al que produce la **fórmula de identidad anterior** — congelada en el propio test, como copia literal de `_transition_identity_payload` y de la serialización canónica, en la forma que tenía al abrirse este RED; y que la `transition_key` es la misma; (iii) se **repite la misma orden** (sin exención) ⇒ rc=0, la salida nombra la entrada existente (su `transition_key`, la histórica), **no** hay segunda entrada y el estado queda **byte-idéntico** (sha256 antes = después). **El recorrido no es una simulación del binario anterior**: el producto anterior queda representado por **su fórmula de identidad**, que es la única parte que determina el reconocimiento entre revisiones (`_registered_transition` compara el `transition_key` exacto, :5098-5108); el resto de la entrada y los efectos sobre el estado los produce el **CLI real**. **Declarado en el propio RED**: estos tres casos son **controles de no-regresión** —pasan con el producto vigente y **deben** seguir pasando con el producto nuevo—, mientras que los casos de la exención son los que **fallan** al abrir el RED. **El recorrido A→B→A es, en cambio, un caso que falla al abrir el RED** (hoy devuelve un no-op exitoso).
- **Regresiones:** `tests/test_005_012_t1_register_transition_base.py`, `tests/test_005_012_t2_gate_authority.py` **(O-1)**, `tests/test_005_012_t3_closure_dispatch_resolution.py`, `tests/test_005_012_t4_late_delivery.py`, `tests/test_005_012_t5_approval_vigency.py` **(O-1)**, `tests/test_005_014_closure_replay.py` **(B-3)**, `tests/test_006_005_u5_disposition_failed.py` **(B-3)**, `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_001_t3_idle.py`, `tests/test_006_003_rf_review_fixes.py`, `tests/test_006_003_rf2_review_fixes.py`, `tests/test_packet_prepare.py`.
  - **Por qué estas dos (O-1):** `tests/test_005_012_t2_gate_authority.py` cubre precisamente **autoridad, campos e idempotencia** del `gate` (incluido `test_pd11_identical_gate_repetition_is_noop_byte_identical`, :630 — el no-op que la identidad debe conservar) y `tests/test_005_012_t5_approval_vigency.py` la **vigencia** que U5 promete conservar (incluido `test_pd14_second_vigente_without_supersedes_fails_closed`, :341, y `test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop`, :622). Son la **regresión focal** del acoplamiento que B-2.questiona; la suite del cierre reduce el riesgo pero no la sustituye.
  - **Por qué estas dos (B-3):** `tests/test_005_014_closure_replay.py` fija el **replay de cierre** de 005-014 (PD-23: `test_pd23_identical_closure_replay_is_noop_naming_the_registered_entry`, :220 — repetir la misma orden de cierre ⇒ rc=0, no-op que nombra la entrada, estado byte-idéntico y **una sola** entrada `closure`) y `tests/test_006_005_u5_disposition_failed.py` fija la **idempotencia de la disposición** de 006-005 (PD-19(b): `test_pd19_b_identical_disposition_is_a_byte_identical_noop`, :376 — repetir la misma disposición ⇒ rc=0, **sin** segunda entrada, estado byte-idéntico). Son los dos oráculos que **se rompen** si el payload de identidad cambia para las invocaciones sin exención: el replay de cierre pasó a ser **rechazo** (rama de feature cerrada, :5622-5633) y la disposición pasó a escribir una **segunda entrada** (con el estado reescrito). Con la forma condicional de R-11/R-12 siguen verdes **sin cambio de oráculo**.
  - **Por qué las tres de B-4 no se tocan (y por qué siguen verdes):** la calificación de B-4 afecta a la rama de no-op **sólo** cuando hay una aprobación vigente que compita (la misma condición de la regla vigente, :5789-5790). (i) `test_pd11_identical_gate_repetition_is_noop_byte_identical` (`tests/test_005_012_t2_gate_authority.py`:630) repite la invocación idéntica de la **única** aprobación, en un `gate` de `--stage tdd-review` **sin** pin de contrato ⇒ la entrada nombrada **es** la vigente ⇒ no-op, sin cambio; (ii) `test_pd14_second_vigente_without_supersedes_fails_closed` (`tests/test_005_012_t5_approval_vigency.py`:341) registra la segunda aprobación con un `--substage` **distinto** ⇒ payload distinto ⇒ **no** hay colisión ⇒ el rechazo vigente (:5821-5829) sigue siendo el que se produce, sin cambio; (iii) `test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop` (:622) registra la segunda con `--supersedes` y un payload **distinto** (substage y bytes del contrato) ⇒ **no** hay colisión, y su repetición es la de la **vigente** ⇒ no-op, sin cambio. El RED de U5 **añade** el recorrido A→B→A y **no toca** estos tres oráculos.
- **A-1:** **ninguna** (§4) — los oráculos vigentes de estos archivos **recomputan** la clave desde el payload escrito y comprueban campos sueltos; no fijan el conjunto de claves del payload ni un digest literal (verificado sobre el código, §4). Los dos ficheros nuevos de B-3 **tampoco** se tocan: se **ejecutan**.
- **Gate:** RED + focales; los **tres** casos del recorrido de dos revisiones verdes; el **recorrido A→B→A** completo verde (los tres rc, el texto del rechazo de colisión, la vigencia antes/después y el registro con valor distinguible); regresiones de transiciones verdes (con las dos de O-1 y las dos de B-3); `make validate`.

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
- **Evidencia:** los tres paquetes y sus `REQUEST.json` (digests y forma), los tres recibos, los tres dictámenes materializados con su carpeta destino, el estado antes/después (sin aprobación), la comparación de digests del caso E4, el texto del dictamen del caso E6, la **salida real de la corrida de dos fases del caso E7** (los rc de las dos recepciones y el texto del diagnóstico) y la **salida real del recorrido de dos revisiones** de U5 (PD-9: los tres rc de no-op, las tres salidas que nombran la entrada, los tres conteos de entradas y los tres sha256 del estado antes/después) y la **salida real del recorrido A→B→A** de U5 (PD-9, B-4: los tres rc, el texto del rechazo de colisión con sus dos salidas, el conteo de entradas, el sha256 del estado antes/después y la entrada vigente antes/después, observada por el lector). Se entrega como **documento de evidencia** en la carpeta de la spec (no en `tests/`). Sin generalizar (spec §7).
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
| **El replay histórico frente al intento de sustituir la aprobación vigente (B-4)** | `tests/test_005_012_t2_gate_authority.py`:630 (`test_pd11_identical_gate_repetition_is_noop_byte_identical`), `tests/test_005_012_t5_approval_vigency.py`:341 (`test_pd14_second_vigente_without_supersedes_fails_closed`) y :622 (`test_pd10_pd11_gate_with_supersedes_carries_key_and_repeat_is_noop`) | **NO APLICA — ninguno se reemplaza; los tres siguen verdes sin cambio de oráculo.** Comprobado sobre el código y los tests: (a) el oráculo de PD-11 repite la invocación **idéntica** de la **única** aprobación, en un `gate` de `--stage tdd-review` **sin** pin de contrato ⇒ no hay aprobación vigente que compita ⇒ R-14(a) ⇒ no-op, sin cambio; (b) el oráculo de PD-14 registra la segunda aprobación con un `--substage` **distinto** ⇒ payload distinto ⇒ **no** hay colisión ⇒ el rechazo vigente (:5821-5829) sigue siendo el que se produce, sin cambio; (c) el oráculo de :622 registra la segunda con `--supersedes` y un payload **distinto** (substage y bytes del contrato) ⇒ **no** hay colisión, y su repetición es la de la **vigente** ⇒ no-op, sin cambio. El RED de U5 **añade** el recorrido A→B→A (las dos ramas de rechazo, el replay de la vigente y el registro con valor distinguible) y **no toca** estos tres oráculos. |

**Regla de la regla A-1 aplicada a esta feature:** el RED de U1 declara, de forma explícita, que **no** reemplaza ningún oráculo y **sí** añade casos; si el RED encontrara un test que fije la puerta `plan-tasks` **para un borrador de forma `spec`** (es decir, que exija que una spec sea rechazada por no traer `plan-tasks`), ese test se declararía aquí como reemplazo antes de tocarlo — con la razón y la postcondición nueva. El RED de U5 declara lo mismo respecto del payload de identidad, y además declara que sus tres casos de **recorrido de dos revisiones** son **controles de no-regresión** (pasan con el producto vigente y deben seguir pasando con el nuevo), no aserciones que deban fallar al abrir el RED; y que el **recorrido A→B→A** es, en cambio, un caso que **falla** al abrir el RED (hoy devuelve un no-op exitoso que deja vigente la aprobación anterior).

## 5. Cierre

- **Revisión independiente de spec/plan antes del RED** (epic §13.3, y la ilustración de 006-005: esta misma spec y este mismo plan son la **primera recepción posible** de la capacidad que la feature introduce — con la diferencia declarada de que el paquete que se revisa aquí es un `draft-plan` sobre un **borrador de plan**, que es exactamente la superficie que ya existe). La revisión que esta feature habilita para las specs (E1) **no** está disponible hasta que U1 esté en verde: se declara esta dependencia, no se la disimula.
- **La declaración de la política de compatibilidad (PD-16(b)) está en `re-entry.md` antes del recorrido (U6)**: el recorrido demuestra el comportamiento; la salida que el orquestador aplica está declarada antes de que el recorrido la use.
- **El recorrido de dos revisiones de U5 (PD-9) forma parte de la evidencia de cierre**: su salida real (los rc, la salida del no-op, el conteo de entradas y el sha256 del estado antes/después, en las tres clases) se adjunta a la evidencia de U6; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con el motivo y la evidencia del intento (misma regla de bloqueo que U6).
- **El recorrido A→B→A de U5 (PD-9, B-4) forma parte de la evidencia de cierre**: su salida real (los tres rc, el texto del rechazo de colisión con sus dos salidas, el conteo de entradas, el sha256 del estado antes/después y la entrada vigente antes/después, observada por el lector) se adjunta a la evidencia de U6; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con el motivo y la evidencia del intento (misma regla de bloqueo que U6).
- Al cerrar el código: `make validate` y la **suite completa una vez**, corrida por quien cierra (política declarada en el paquete; se repite sólo si un cambio o una evidencia invalidada lo justifican).
- **Review formal del resultado** en sesión independiente (etapa 4, sin cambios por esta feature).
- El recorrido real de U6 (PD-13) queda **declarado con su estado**; no se acredita aceptación real por pruebas aisladas.
- **Cierre de la feature**: la spec y el plan de 006-006 pasan por la revisión independiente que la propia feature introduce (o, si el gate 2→3 de esta feature no está aún en verde, por la superficie vigente `plan-review`/`draft-plan` sobre este plan), y la aprobación es de la autoridad vigente.

## 6. Tareas declaradas (`plan-tasks`)

Derivado de las fichas de §3 (archivos, RED, regresiones y A-1) para que el CLI admita el plan como `draft-plan`. Si difiere de §3, manda §3 y el bloque se corrige.

```plan-tasks
{
  "validation_strategy": "Por unidad: RED declarado y failing por la razon correcta, focales GREEN y las regresiones listadas en su ficha; make validate en U1, U2, U3, U4 y U5; make staging determinista en U4. La suite completa la corre UNA VEZ quien cierra (politica declarada en el paquete). A-1: esta feature NO reemplaza ningun oraculo vigente (ver plan §4): el oraculo de tests/test_004_003_t4_validation_fields.py:427 se conserva porque la forma por omision es plan, los 11 archivos que comparten el fixture DRAFT_PLAN_RELPATH no se tocan, y los oraculos de identidad de transicion recomputan la clave desde el payload escrito sin fijar su conjunto de claves; los REDs nuevos anaden casos, no cambian oraculos. Compatibilidad (B-1): la garantia de render byte-identico vale DENTRO de una misma revision del producto; entre revisiones no se promete compatibilidad y la politica (terminarlo bajo la revision con la que se publico, o preparar uno nuevo) queda declarada en re-entry.md, con su caso demonstrativo en U6. Exencion (B-2, corregido por B-3): sus cuatro campos entran en el payload de identidad de la transicion SOLO cuando la invocacion los declara, como un bloque exemption condicional; sin exencion declarada el payload y la transition_key quedan byte-identicos a los del producto vigente, de modo que las identidades historicas se conservan y NO hay enmienda de 005-014 PD-23 ni de 006-005 PD-19(b) (D-14); la repeticion identica es no-op y la repeticion que cambia la exencion (incluido el paso de sin exencion a con exencion) se registra por --supersedes o se rechaza explicitamente, nunca exito sin registrar. El RED de U5 incluye el recorrido de dos revisiones en gate, closure y disposition (control de no-regresion: el payload escrito debe ser byte-identico al de la formula de identidad anterior, congelada, y la repeticion de la misma orden sin exencion debe ser no-op, con la misma entrada y el estado byte-identico). Sustitucion de la aprobacion vigente (B-4): la rama de no-op se califica sin cambiar la formula de la identidad ni las claves historicas; el replay historico (la entrada nombrada es la vigente, o no hay vigente que compita) sigue siendo no-op y los replays historicos de B-3 se conservan; una invocacion con --supersedes cuyo payload colisiona con una entrada historica que NO es la vigente se rechaza explicitamente, nombrando la clave que colisiona, la clave de la vigente y las dos salidas (registrar con un valor distinguible, o reconciliar); sin --supersedes se conserva el rechazo vigente de una sola aprobacion. El RED de U5 incluye el recorrido A->B->A completo (las dos ramas de rechazo, el replay de la vigente y el registro con valor distinguible): registro valido o rechazo explicito, nunca un no-op exitoso que deje vigente la aprobacion anterior. Los gates del dueno que estaban pendientes YA ESTAN REGISTRADOS (execution.md:260 PD-19 aprobada; execution.md:262 modelo y credencial fuera de runtimes.json): no hay gate del dueno que esperar antes de un RED, y las unidades lo citan como precondicio cumplida.",
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
      "objective": "La exencion registrada e incluida en la identidad de la transicion SOLO cuando se declara: tres banderas opcionales y un interruptor en la clase gate de register-transition (--exempted-by, --exemption-reason, --requested-by, --delegated), admisibles solo en esa clase; la entrada suma exempted_by, reason, requested_by y delegated solo cuando las banderas estan; el payload canonico de identidad se construye exactamente como hoy y, solo cuando la invocacion declara la exencion, gana una clave nueva exemption con exactamente los campos declarados; sin exencion declarada el payload y la transition_key quedan byte-identicos a los del producto vigente, de modo que las identidades historicas se conservan; ademas, la rama de no-op se califica (B-4) sin cambiar la formula de la identidad ni las claves historicas: el replay historico (la entrada nombrada es la vigente, o no hay vigente que compita) sigue siendo no-op, y una invocacion que colisiona con una entrada historica que NO es la vigente deja de ser un no-op (con --supersedes, rechazo explicito de colision que nombra la clave que colisiona, la clave de la vigente y las dos salidas; sin --supersedes, el rechazo vigente de una sola aprobacion); la exencion viaja en la MISMA entrada que la aprobacion, sin alterar el pin ni la regla de una sola aprobacion vigente.",
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
       "recorrido de dos revisiones (B-3), en gate, closure y disposition: el payload escrito es byte-identico al de la formula de identidad anterior (congelada) y la repeticion de la misma orden sin exencion es no-op, con la misma entrada nombrada, sin segunda entrada y con el state byte-identico (PD-9, R-13, D-14)",
       "replay frente a sustitucion (B-4, R-14): repetir la entrada vigente es no-op (rc=0, sin segunda entrada, state byte-identico, salida que nombra la entrada) y no cambia el comportamiento de las clases sin aprobacion vigente (PD-9, PD-23, PD-19b)",
       "recorrido A->B->A (B-4): con --supersedes, la invocacion que vuelve al payload anterior se rechaza con el rechazo de colision (nombra la clave que colisiona, dice que no es la vigente, nombra la clave de la vigente y nombra las dos salidas); sin --supersedes, se rechaza por la regla de una sola aprobacion; en ambos casos el estado queda byte-identico y la aprobacion vigente sigue en vigor, comprobado con el lector (PD-9, R-14, D-15)",
       "el registro con valor distinguible (la salida que nombra el rechazo de colision): repetir la orden anterior citando evidencia con --artifact deja una entrada nueva, vigente y sin bloque exemption; si esa salida no se puede materializar, el RED falla (PD-9, R-14, D-15)"
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
       "la salida real del recorrido A->B->A de U5 (PD-9, B-4) queda adjunta: los tres rc, el texto del rechazo de colision con sus dos salidas, el conteo de entradas, el sha256 del estado antes/despues y la entrada vigente antes/despues, observada por el lector (PD-9, R-14, D-15)",
       "las versiones y configuraciones observadas quedan declaradas y el resultado no se generaliza (spec 7)"
      ],
      "regressions": [],
      "integration_gate": "recorrido con evidencia declarada; si el ambiente no permite ejecutarlo, la unidad se declara BLOQUEADA con motivo y evidencia del intento, sin corrida simulada",
      "owner": "orchestrator con el reviewer; evidencia en la carpeta de la spec"
    }
  ]
}
```
