# Dictamen — plan-review sobre draft-plan (006-005-native-path-parity, draft-002)

## Veredicto: **CON BLOQUEANTES** (2)

La estructura general es sólida y la mayoría de las afirmaciones de código que sostienen las decisiones se verificaron correctas (detalle en la evidencia). Pero hay dos defectos observables: un paso no verificable tal como está declarado (B-1) y un test acoplado no listado en A-1 que rompería el GREEN de U1 (B-2). El dictamen no aprueba ni habilita RED: la aprobación es de la autoridad vigente.

---

## Hallazgos

### B-1 — El disparador del error por exec-config heredado no está declarado: el RED de PD-9 (fixture 3) no es escribible de forma determinista

- **Verdict:** BLOCKING · **Bucket:** m
- **Ubicación:** spec §2.6 (último viñete, `spec.md`:100), PD-9 (`spec.md`:120), D-11 (`spec.md`:188); plan §3 U1 RED.
- **Evidencia verificada:** la firma de §2.1 (`spec.md`:40-46) **no** incluye `--exec-config` en ningún verbo, y no se declara **ninguna ubicación convencional** donde la entrada pueda *encontrar* un exec-config heredado que no recibe por argumento (el exec-config era un archivo cuya ruta pasaba el invocador; el helper del rodeo es externo al repo; `opencode-server.env` es la credencial, otro artefacto — `install.sh`:1191-1201 verificado). Entonces: ¿cómo *se entera* la entrada de que existe un exec-config heredado como para fallar nombrando (i)-(ii)-(iii)? El oráculo de PD-9 exige «tres fixtures (sin sección, con `model`, con exec-config heredado)» — el tercero no tiene mecanismo de inyección declarado, así que el test-writer no puede escribirlo de forma determinista y el implementer tendría que **inventar** el mecanismo de detección (lo que puede divergir del intento). La segunda mitad de la pregunta del orquestador sí está respondida: el consumidor que hoy llama a la interfaz común con `--exec-config` sigue operativo como mecanismo interno (deuda con disparador, §8 item 4) — eso es coherente.
- **Corrección propuesta (elegir una y declararla):** (i) la entrada acepta `--exec-config` **sólo para rechazarlo** con el error de migración de §2.6; o (ii) la correspondencia de claves viaja en el diagnóstico del caso «sin sección» y el fixture 3 se elimina/redefine como «pasar `--exec-config` a la entrada es error de uso nombrando `runtimes.json`»; o (iii) declarar una ubicación legada concreta que la entrada sondea y nombra.

### B-2 — `tests/test_005_010_t1_durable_signal.py` está acoplado al registro que U1 elimina y está listado como regresión simple, no en A-1

- **Verdict:** BLOCKING · **Bucket:** m
- **Ubicación:** plan §3 U1 «Regresiones» (`plan.md`:31) y §4 A-1 (`plan.md`:78 — lista sólo `test_005_009_t1_interface.py`); spec PD-1/PD-14, D-14.
- **Evidencia verificada** (lectura del test): `tests/test_005_010_t1_durable_signal.py` maneja `cdad_delegate.py` (la interfaz) y en `:431-529` identifica el registro del worker como «el registro NUEVO del ledger que NO es el del intento de la interfaz — escrito por el adaptador» (supone **dos** registros: exactamente el comportamiento D-ADP-2 que la feature elimina); y en `:536-543` aserta `interface_record.get("model_reported") is None` («el registro del intento de la interfaz no mantiene model_reported honestamente null… la interfaz no lee el store»). Tras U1 la interfaz **relaya** el intento del módulo y deja de registrar: el registro del intento de la interfaz pasa a ser el del módulo, con `model_reported` **no nulo** → la regresión falla en GREEN sin reemplazo declarado, o tienta una edición no declarada (violando la regla A-1). El test **sí** está en la lista de regresiones de U1 — doblemente problemático: se anuncia que pasará sin cambios cuando se sabe que no puede.
- **Corrección propuesta:** moverlo a A-1 (U1) con reemplazo declarado: «un solo registro por despacho; la interfaz relaya el `attempt` del módulo; la distinción interfaz/worker dentro de la vía externa desaparece (D-14/PD-1)».

### O-1 — El gate de aprobación del dueño de la enmienda PD-19 (D-4) no llega al plan de U5

- **Verdict:** OPTIONAL · **Bucket:** m
- **Ubicación:** spec D-4 (`spec.md`:171) lo declara («requiere aprobación explícita del dueño»); plan §2 tabla (`plan.md`:18) y §3 U5 Gate (`plan.md`:65) no lo incluyen.
- **Evidencia:** las decisiones del owner de `execution.md`:249-254 cubren el despacho (1-6), no la enmienda de la consecuencia INV-9 de 005-012 (`spec.md` de 005-012 `:243`/`:587`, test `:745-830` verificado). Si U5 arranca sin esa aprobación, el trabajo se invalida.
- **Corrección:** añadir a la ficha U5 (y a la tabla §2) el gate explícito: «aprobación del dueño de la enmienda PD-19 antes del RED».

### O-2 — PD-8 no declara que el caso «declaración» sólo existe en contextos v1 planos

- **Verdict:** OPTIONAL · **Bucket:** m
- **Ubicación:** PD-8 (`spec.md`:119) vs V-9 (`spec.md`:204).
- **Evidencia verificada:** los contextos v2 no llevan runtime (`V2_EXECUTION_KEYS`, `cdad_packet.py`:73-80 ✓ sin runtime; `BINDING_FIELDS`:25-33 ✓ con runtime en v1; `.cdad/execution.json` declara `"multi-runtime"` ✓). El oráculo de PD-8 exige tres casos (flag / declaración / ninguno) y el error «nombra el flag y los lugares donde se declara»: en un contexto v2 **no hay** lugar declarado, así que el fixture del caso 2 sólo puede ser un contexto v1 plano, y el error no debe nombrar lugares inexistentes.
- **Corrección:** declarar en PD-8 (o en la ficha U1) que el caso «declaración» se prueba sobre un contexto v1 plano y que, en v2, el error nombra el flag y la ausencia de lugar de declaración (V-9), sin inventar el lugar propuesto mientras el dueño no decida.

### O-3 — Tamaño de U1: nueve PD y tres responsabilidades separables en una unidad

- **Verdict:** OPTIONAL · **Bucket:** m
- **Ubicación:** plan §2/§3 U1 (`plan.md`:14, :23-34).
- **Evidencia:** U1 acumula (a) entrada + registro único + correlación (PD-1..6), (b) config por runtime + migración (PD-8/9, `install.sh` + `cli-delegation.md`), (c) agente en el paquete (PD-7, zona `prepare` de `cdad_packet.py`:4456-4474 ✓). La regla vigente (`stage-2-specification.md`:144) manda «cut and split the task» cuando la unidad concentra demasiado. No es blocking: la ficha referencia PDs y no re-deriva implementación, y la secuencia es U1→U2→U4.
- **Corrección propuesta:** dividir (p. ej. U1a entrada+registro PD-1..6; U1b config+migración PD-8/9; PD-7 puede ir con cualquiera o aparte — es el corte natural porque toca otro archivo) o declarar en el plan por qué va en una sola unidad.

### O-4 — El bloque `plan-tasks` §6 omite los agentes regenerados que la ficha U4 de §3 declara

- **Verdict:** OPTIONAL · · **Bucket:** m
- **Ubicación:** plan §3 U4 (`plan.md`:55: «y los agentes regenerados por `make agents`») vs §6 `files` de U4 (`plan.md`:196-202).
- **Evidencia:** `agents/` es raíz de implementación según la política del paquete; `Makefile`:1-24 los declara salidas de `cdad-generate.py`. El propio §6 dice «si difiere de §3, manda §3 y el bloque se corrige».
- **Corrección:** añadir las salidas declaradas (o una anotación «salidas de `make agents`») al `files` de U4 en §6.

### O-5 — La spec corrige la letra de la decisión 2 del owner (modelo/credencial fuera de la sección) sin registro de confirmación del dueño

- **Verdict:** OPTIONAL · **Bucket:** m
- **Ubicación:** spec §2.6 (`spec.md`:96-97), D-10c (`spec.md`:187) vs `execution.md`:250 («modelo por rol y credencial si la usa» en la sección).
- **Evidencia verificada:** ADR-033 D3 (`docs/adr/ADR-033-...md`:96-101) pone el modelo en `delegation.json` y la credencial en `credential_env_file` — decisiones del dueño **previas y aprobadas**. La reconciliación está bien fundada y **declarada** («corrección del fraseo», evidencia `delegation_credential_env_file`:131 ✓), pero la letra de la decisión 2 dice lo contrario: la confirmación del dueño de esa corrección debe quedar registrada antes de que el RED de U1 fije el rechazo de `model` (PD-9).
- **Corrección:** pedir/régistrar la confirmación del owner (una línea en `execution.md`) antes del RED de U1.

### O-6 — Ventana U1→U2: no se declara cómo responde el núcleo ante un módulo que aún no implementa `--capabilities`/`--observe`

- **Verdict:** OPTIONAL · **Bucket:** l
- **Ubicación:** spec §2.2 (`spec.md`:54-62); plan §1 (U2 depende de U1).
- **Evidencia:** entre U1 y U2 el único módulo real (OpenCode) no tiene la superficie nueva; `capabilities`/`record --observe` contra él no tienen conducta declarada (fallo cerrado implícito, no escrito). Transitorio, pero observable si alguien usa la entrada en esa ventana.
- **Corrección:** una línea en §2.2: «un módulo que no implementa la superficie responde capacidad falsa con `reason` nombrándolo / fallo cerrado».

### O-7 — Conteo de brechas: «seis» contra cinco enumeradas

- **Verdict:** OPTIONAL · **Bucket:** l
- **Ubicación:** spec §1 (`spec.md`:24-26).
- **Evidencia:** se enumeran cinco (3 de §11 + entrada sin config + agente por stack); §11 (`epic plan.md`:289) nombra otros tres bloqueos (el tercero: el orquestador que reconstruyó el protocolo a mano — cerrado por `record`, no listado en el conteo). O bien el conteo es erróneo, o falta nombrar la sexta.
- **Corrección:** recontar o nombrar la sexta (la reconstrucción a mano del protocolo).

### O-8 — Citas de código con deriva menor (símbolos correctos, líneas no)

- **Verdict:** OPTIONAL · **Bucket:** l
- **Evidencia verificada (cada una, contra HEAD):** `_adapter_path` está en `cdad_delegate.py`:91 (citado :79; :79 es `_load_json`); la prohibición PD-10 de `--replace-packet` está en `cdad_packet.py`:2090-2098 (citado :2082-2083, que es el chequeo de paquete activo); `temporary_roots: []` en `propose_policy` está en :1100 (citado :1101); `_load_observation_document` def en :2410 (rango citado :2398-2440 lo contiene); `binary` se lee en :1999, fuera del rango citado :1857-1900; el «Registro» de `runtime-adoption.md` no es un encabezado de sección sino un párrafo dentro de «Qué emite por runtime» (el contenido citado — `adopted_root` + rutas — es correcto). Todos los símbolos existen y sostienen las decisiones; ninguna cambia un dictamen. El diff `9d3b2ea..HEAD` es docs-only (verificado), así que la deriva es del borrador, no del código.
- **Corrección:** ajustar los números de línea en una pasada de edición.

### Deuda declarada (confirmada, sin hallazgo nuevo)

- **D-ADP-3 a deuda** (D-15, §8 item 3): criterio y disparador declarados; `_allowed_kinds` verificado (`cdad_result.py`:681-694 ✓ admite `role-report` para architect en discovery/draft; `FINAL_TEXT_ARTIFACT_KIND` = `role-report` en :127 ✓). Conforme a §12.
- Retirada del `--exec-config` interno (§8 item 4): deuda con disparador declarado. Conforme.

---

## Abstenciones

- **Suite/build:** no ejecuté tests ni `make validate`/`make staging`: revisión read-only de plan; la suite completa corre una vez al cierre (política declarada, PD-21).
- **Sondas V-1/V-7/V-11:** juzgué su *declaración* en los borradores, no su factibilidad técnica (se ejecutan en U2/U6 según el plan).
- **V-8 (ningún test fija el valor de la propuesta):** verificado por grep acotado (sin resultados); no es una auditoría exhaustiva — lo cubre la regla A-1 residual que el plan ya declara.
- **Acoplamiento de `test_005_007_t5_delegation_dispatch.py`, `test_004_002_t4_dispatch.py` y `test_006_002_u5_transport_equivalence.py`:** lectura estática sugiere que no rompen con U1 (<80% de certeza de rotura), por eso no los afirmo; sólo `t1_durable_signal` pasa el umbral (B-2).
- **Confirmación previa del owner sobre la corrección §2.6 (O-5):** no la busqué en secciones anteriores de `execution.md`; si ya existe, O-5 cae.
- **Calidad semántica de `architect-draft-001.md`:** revisé los dos borradores como objetos declarados; no audité la fidelidad del Δ draft-001→draft-002 contra el informe del architect.

## Evidencia del rol

- **HEAD medido:** `357c461` (`2d1db9c` = sha256 del spec draft-002; plan `567ebcfe…` **coincide** con el sha256 del contrato del paquete). `git diff 9d3b2ea..HEAD --stat`: sólo docs (state + borradores) — las citas de código medidas en `9d3b2ea` siguen vigentes.
- **Comandos exactos (resumen):** `sha256sum` de ambos borradores; `git rev-parse HEAD`; `git log --oneline -3`; `git diff 9d3b2ea..HEAD --stat`; ~30 inspecciones `sed -n` de símbolo+línea en `cdad_packet.py`, `cdad_delegate.py`, `cdad_delegate_opencode.py`, `cdad_result.py`, `cdad_continuity.py`, `install.sh`, `Makefile`, `sources/roles/orchestrator.md`, `sources/agents/adapters/{opencode,claude-code}.md`, `skills/cdad-cycle/references/{cli-delegation,re-entry,runtime-adoption,stage-2-specification}.md`, `docs/adr/ADR-033-*.md`; `grep` de `OPENCODE_PASSWORD`/registro/`attempt` en los tests listados; verificación de existencia de los 45 tests de regresión (todos existen); lectura de `.cdad/execution.json` (`"runtime": "multi-runtime"` ✓) y de `docs/.cdad-state.json` (006-005 in-progress; 006-004 y 006-006 en cola, orden conforme a §11).
- **Verificaciones positivas que sostienen el plan:** `OBSERVATION_KEYS`:2371 ✓, `OUTPUT_KEYS`:52/`TERMINATION_VOCABULARY`:49 ✓, `_record_dispatch` :2500 ✓, `mode=ro` :619-621 ✓, `_invoke_destination`:381/`_await_durable_outcome`:680/`_store_state`:600 ✓, `_observation`:288/`_register_dispatch`:311/invocación :399 ✓, `ACTIVE_PACKET_STATUSES = {"prepared","dispatched"}` (:115) — `failed` no bloquea `prepare`, así que PD-19 no necesita tocar el chequeo de :4337 ✓, `VALID_PACKET_STATUSES` incluye `failed` (:44) ✓, `DISPOSITION_RESOLUTIONS = ("abandoned","superseded")` (:4680) coincide con el comando de PD-19 ✓, bloque de `prepare` :4337-4338 y rechazo con recibo :5207-5213 ✓, `_validate_temporary_roots` :414-430 ✓, `SCOPE_CLASSES` sin `temporary` (:67) ✓, `git check-ignore` → `.gitignore:11:.cdad/` ✓, `_entry_selection`/:5828 `_next_route`/:5847 `status_view`/:5886 ✓, cuatro entradas del intake (:22-57) y condición stale (:23-24) ✓, secciones `delegation` en :60/:80 ✓, encabezado «Orchestrator materialization protocol» en re-entry.md ✓, `install_user_config`/plantillas :1151-1201 ✓, maquinaria `plan-review` (`:52-53`, `:815-829`, `cdad_result.py`:700) ✓, test `test_005_012_t3_closure_dispatch_resolution.py`:745-830 y B1 :835 ✓, aserciones de registro de `test_005_009_t1_interface.py` ✓ (A-1 U1 bien fundado), `plan-tasks` §6 coincide con §3 en U1/U2/U3/U5/U6 (archivos, tests, dependencias) ✓, todas las PD 1-22 tienen unidad y oráculo ✓, y la spec cumple el resto de las decisiones del owner (entrada única D-9 ✓, config por runtime D-10 ✓, credencial del módulo D-12 ✓, agente en el paquete D-13 ✓, regla de transporte D-6 fila 3 con cita `execution.md`:253 ✓, sonda V-11 con regla de bloqueo ✓).
- **Archivos modificados:** ninguno (write_scope vacío; role read-only cumplido). **Commit:** ninguno (no corresponde; la materialización del dictamen es del orquestador, ADR-003).