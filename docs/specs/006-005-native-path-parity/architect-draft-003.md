He verificado el dictamen, el repo (HEAD medido) y las tres fuentes de instrucción del paquete antes de escribir. Entrego el texto final corregido.

===== BEGIN docs/specs/006-005-native-path-parity/spec.md (DRAFT — UNAPPROVED) =====
# 006-005-native-path-parity — SPEC (etapa 2, revisión draft-003)

Estado: **BORRADOR no aprobado.** No habilita RED, ni construcción, ni aprobación.
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §11 (enmienda 004) con el principio de §12; el recorrido es §13 (enmienda 006): la review independiente de spec y plan **precede** al RED.
Ejecución: `exec-006-005-native-path-parity-001`. Insumos: `discovery.md` (etapa 1), `architect-draft-001.md`, `architect-draft-002.md`, `plan-review.md` (dictamen independiente: 2 bloqueantes, 8 opcionales y la deuda declarada reconfirmada) y `docs/epics/epic-006-opencode-concurrency/execution.md` §«Uso real del adaptador por el orquestador» (**D-ADP-1..D-ADP-4**), §«Decisiones del owner sobre el despacho» y su última entrada, **«D-ADP-3 escalado a defecto real»** (2026-10-18).
Base medida: HEAD `b82e6a3`. El dictamen midió `357c461` y draft-002 midió `9d3b2ea`; `git diff 9d3b2ea..b82e6a3 --stat` es **docs-only** (state, `execution.md`, `plan-review.md` y los borradores), así que las citas de código siguen vigentes. Los números de línea son del HEAD medido y pueden correrse; por eso cada cita nombra además el símbolo.

Anonimización: rutas del repositorio, relativas; sin rutas del host, endpoints, ids de sesión, credenciales ni nombres de otros proyectos. El «proyecto consumidor» se nombra así.

## 0. Δ respecto de draft-001 (vigente) y Δ de la corrección draft-003

**Δ vigente de draft-002 respecto de draft-001:**

1. **Entrada externa y configuración del owner** (decisiones 1-2 de `execution.md`:249-250) entran a la feature: una sola entrada `cdad_dispatch.py --packet <id> [--runtime X]`, y la configuración de ejecución por runtime pasa a la config de usuario de CDAD (hoy un exec-config por argumento), con migración y tratamiento del heredado declarados (§2.1, §2.6, D-9…D-11).
2. **D-ADP-1** (`execution.md`:242): la credencial de `mode: server` la resuelve e inyecta **el módulo de runtime**, sólo en el entorno del proceso cliente (§2.5, D-12, PD-11).
3. **D-ADP-4** (`execution.md`:245, :251): el agente viaja en el paquete; `prepare` lo resuelve (rol + `stack`) y lo escribe en `REQUEST.json`; la llave «agente» de la correlación compara contra ese campo (§2.7, D-13, PD-7, PD-14).
4. **D-ADP-3** (`execution.md`:244) **escalado a defecto real** (`execution.md`:255): el kind de la parte entregada no puede ser fijo si la tabla cerrada rol/subfase admite otro; se fija desde rol y subfase del paquete **en las dos vías** (PD-23, §2.8). Sólo la **separación de `spec.md`/`plan.md` en partes propias del rol** queda en **deuda declarada** con el criterio de §12 (§8 item 3).
5. **Corrección de D-2 de draft-001.** draft-001 proponía un módulo nuevo por runtime (`cdad_runtime_<id>.py`) **además** del adaptador por destino. Serían dos módulos por runtime para el mismo trabajo: duplicación que puede divergir (§12). El contrato por runtime **ya existe y ya sabe lanzar, esperar y recoger**: `cdad_delegate_<id>.py` (ADR-023; `_invoke_destination`:381, `_await_durable_outcome`:680, `_store_state`:600). La integración **se extiende ahí** (§2.2, D-2).
6. **Quién registra el intento (PD-1).** D-ADP-2 pide «un solo registro por despacho, escrito por una sola capa, con la observación que el módulo de runtime ya produce». Entonces: en la vía externa registra **el módulo** (ya lo hace, con `model_reported` correcto desde `session_v2.model`, `_model_reported_from_row`:259) y la **interfaz común deja de registrar** (`cdad_delegate.py` `_observation`:288 + `_register_dispatch`:311 + su invocación :398); en la vía nativa registra el **núcleo**. `model_reported` sale en ambas vías de la observación del módulo (PD-1, PD-14).
7. **El instante del `begin` no es verificable en el repo** (V-10): la llave «momento» se mide contra un instante **declarado** por quien despacha (`--since`), no contra un timestamp que ninguna pieza registre.
8. **El runtime del proyecto no está declarado en ningún lugar verificable para un contexto v2** (V-9): la resolución «flag → configuración del proyecto → error claro» del owner se implementa con lo que el repo acredita y **falla cerrado** donde no hay declaración.
9. `capabilities` de draft-001 (`native_transport`) se renombra a claves con significado declarado (`native_observation`, `external_transport`, `session_correlation`): el transporte nativo no lo hace el módulo, lo hace la herramienta del runtime (§2.2).

**Δ de esta revisión (draft-003, corrección tras el plan-review):**

10. **B-1 — mecanismo del exec-config heredado (elegido: opción ii).** La entrada nueva **no declara `--exec-config`**: pasarlo (o pasar `--exec-config=<v>`) a cualquiera de sus verbos es **error de uso** (rc≠0 antes de todo efecto) con el diagnóstico de migración de §2.6, que nombra `runtimes.json`, la sección por runtime y la **correspondencia clave por clave**; la entrada **nunca sondea** ninguna ubicación heredada — no existe una declarada y el exec-config era un archivo cuya ruta pasaba el invocador. El fixture «con exec-config heredado» de PD-9 se redefine como «`--exec-config` en `argv`» (determinista y escribible). La interfaz común conserva su `--exec-config` como mecanismo **interno** (deuda declarada, §8 item 4).
11. **B-2 — tests acoplados al registro doble, movidos a A-1 con reemplazo declarado.** El dictamen verificó `tests/test_005_010_t1_durable_signal.py` (`:431-449` cuenta dos registros; `:536-543` aserta `model_reported` nulo en el registro de la interfaz). Con el mismo criterio —«el registro nuevo del ledger que NO es el del intento de la interfaz»— se verificó que **otros dos tests de la misma familia** tienen el mismo acoplamiento y ninguno estaba listado: `tests/test_005_010_t4_integration.py` (`:480-486`, `:540-557`) y `tests/test_005_010_reviewfix.py` (`:489-500`). Los tres van a **A-1 de la unidad de entrada+registro** con el reemplazo declarado (plan §4). Los demás usos de `dispatch_records`/`assert_attempt_is_in_ledger` de las listas de regresión (005-009 T1/T2, 005-010 T2, 006-001 T1b/T1/T2/T3, 006-003 U4/U6/U8) son **de pertenencia**: tras U1b el intento declarado es el del módulo y el registro existe, así que siguen verdes sin cambio (salvo el fixture de destinos de prueba de 005-009 T1, ya declarado en A-1).
12. **D-15 corregida (D-ADP-3 escalado a defecto real).** El defecto medido —el dictamen del reviewer llegó como `role-report` y `materialize` lo rechazó (`execution.md`:255)— **se corrige en 006-005**: el kind de la parte entregada se fija desde rol y subfase del paquete, en las dos vías (PD-23, §2.8, INV-14). Lo que queda en deuda es sólo la **separación en partes propias** (spec y plan como artefactos con el hash del rol), sin caso real medido que la exija (§12; §8 item 3).
13. **Gates del dueño declarados como pendientes, no dados por hechos.** (a) La confirmación del owner de que **el modelo y la credencial no viven en `runtimes.json`** (corrección del fraseo de `execution.md`:250, fundada en ADR-033) es **gate del RED de la unidad de configuración**. (b) La **aprobación del owner de la enmienda de PD-19** (cambia la consecuencia INV-9 de 005-012) es **gate del RED de U5**. Ninguna de las dos está registrada todavía; la spec no las presume (plan §2/§3).
14. **O-8 — citas corregidas contra el HEAD medido** (`_adapter_path` en `cdad_delegate.py`:91; la prohibición de `--replace-packet` sobre `dispatched` en `cdad_packet.py`:2094-2102; `temporary_roots: []` en `propose_policy`, `cdad_packet.py`:1100; `_load_observation_document` en :2410; `binary` leído en `cdad_delegate_opencode.py`:1999; el «Registro» de `runtime-adoption.md` es un párrafo dentro de «Qué emite por runtime», :21/:37).

## 1. Descripción funcional

La delegación **nativa** («herramienta del runtime», p. ej. `task` + `subagent_type: cdad-<rol>`) ejecuta el encargo pero **no traslada la preparación que el adaptador externo sí hace**: nadie registra el intento I8 —sin eso `receive` rechaza (`cdad_result.py`:576-580 «the active packet is not dispatched»)—; ningún encargo puede conceder un temporal al test-writer —el validador de scopes sólo admite `{tests, colocated-tests}` para su escritura, `cdad_packet.py`:728-729—; un intento que no vuelve no tiene camino mecánico a `failed` (la disposición registra la decisión y su efecto sobre el paquete es `pass`, `cdad_packet.py`:5584-5589). A esas tres brechas de §11 se suman, ya medidas en uso real (`execution.md`:242-245), la **entrada del orquestador sin config declarada** (el despacho externo se ejecuta con un exec-config local y un rodeo de entorno) y el **agente por stack** que nunca se resuelve; y del propio diagnóstico de §11 queda la sexta, **el orquestador que reconstruyó el protocolo a mano** (la cierra el registro mecánico de la vía nativa, PD-1/PD-2). **Seis brechas en total**, contadas una a una.

La feature cierra las seis con **una entrada operativa**, **una capa de configuración** y **una integración por runtime que ya existe**:

1. **Núcleo `skills/cdad-cycle/scripts/cdad_dispatch.py`** (runtime-neutral; capa `scripts` del principio de capas de §8 de §11/§12): la **entrada única del orquestador** en sus dos vías —`dispatch` (externa) y `record` (nativa)—, más `capabilities`. No reimplementa validaciones: importa `cdad_packet` (precedente: `cdad_result.py` lo importa) y los ayudantes de la interfaz común; escribe el ledger **sólo** por el comando que ya existe (`prepare --record-dispatch`, `cdad_packet.py`:2501) y **no agranda** `cdad_packet.py`.
2. **Configuración de ejecución por runtime** en la config de usuario de CDAD, junto a `delegation.json` (`cdad_delegate.py` `cdad_config_dir`:100): una sección por runtime con binario y versión, modo y URL, la superficie durable y la espera. Es la **única fuente** para la vía externa; el exec-config deja de ser dato del usuario (§2.6).
3. **Integración del runtime = el módulo por destino que ya existe** (`cdad_delegate_<id>.py`, ADR-023/ADR-032), extendido con: la credencial de `mode: server` (§2.5), el agente del paquete (§2.7), **el kind de la parte entregada derivado de la tabla rol/subfase** (§2.8) y una superficie de **observación** y **capacidades** para la vía nativa (§2.2). Fuera de su versión declarada o con esquema de store desconocido, falla cerrado.
4. **Registro del intento: uno por despacho.** La interfaz común deja de registrar; el módulo registra el suyo en la vía externa y el núcleo registra en la nativa (PD-1).
5. **Temporales del test-writer** como clase de scope `temporary` del vocabulario observable que ya existe (`classify_path_observable`, `cdad_packet.py`:303-322 nombra `"temporary"` desde `temporary_roots`), validada contra `temporary_roots` de la política y verificada con `git check-ignore` en `prepare`.
6. **Una sola entrada operativa del orquestador**, consumiendo el `entry`/`next` que el CLI ya calcula (`_entry_selection`:5828, `_next_route`:5847, `status_view`:5886) en vez de re-derivar la situación con cuatro entradas solapadas (`sources/roles/orchestrator.md`:22-57), y con la regla de transporte declarada: **mismo runtime que el orquestador ⇒ herramienta nativa + `record`; otro runtime ⇒ despacho externo** (`execution.md`:253). Cierra además la sexta brecha (la reconstrucción a mano del protocolo).
7. **Camino mecánico a `failed`** por la autoridad que ya existe (la disposición), para el intento interrumpido sin entrega.

## 2. Contrato

### 2.1 Superficie del núcleo (una CLI, tres verbos; `dispatch` es el verbo por defecto)

```
cdad_dispatch.py --project-root R --packet P [--runtime X] [--json]      # = dispatch (entrada del owner)
cdad_dispatch.py dispatch --project-root R --packet P [--runtime X] [--json]
cdad_dispatch.py record   --project-root R --packet P --attempt-id A
        [--native-result FILE|-] [--session S] [--parent S] [--since TS] [--runtime X]
cdad_dispatch.py capabilities --runtime X [--json]
```

- **`dispatch` (vía externa).** Resuelve el runtime (PD-8), lee su sección de config (PD-9) y **deriva** la configuración interna del módulo (§2.6); transporta el `PACKET.md` **byte-idéntico** al módulo del runtime, que lanza, espera, recoge y **registra su propio intento**; el núcleo **no** registra ni escenifica en esta vía (una sola capa escribe, PD-1) y devuelve el sobre del módulo con el `attempt` del módulo.
- **`record` (vía nativa).** Construye la observación con las claves cerradas I8 (`OBSERVATION_KEYS`, `cdad_packet.py`:2371; validación `_load_observation_document`, :2410); prioriza el **resultado nativo byte-exacto** y, sólo si no lo hay y hay motivo, **una** lectura acotada del store vía la superficie de observación del módulo (`--observe`, §2.2); verifica la correlación (§2.3); **registra** por `prepare --record-dispatch`; y, si recibió el texto final, lo **escenifica byte-exacto** bajo `.cdad/inbox` con su `RESULT.json` (paso mecánico del protocolo de re-entry, `skills/cdad-cycle/references/re-entry.md` §«Orchestrator materialization protocol»), declarando en ese descriptor el kind de §2.8. **No** ejecuta `receive`: el recibo es del protocolo de re-entry.
- **Convivencia sin duplicar lógica.** `record` es el **cuerpo único** de observación + registro + escenificación; `dispatch` no reimplementa nada de eso — delega en el módulo, que registra con la observación que él mismo produce (PD-1). Los dos verbos comparten el mismo constructor de observación, el mismo vocabulario y la misma ruta de escritura del ledger (el comando existente); ninguno de los dos valida por su cuenta lo que `cdad_packet` ya valida.
- **Sin `--exec-config`.** La entrada **no declara** esa opción: la configuración es la sección de `runtimes.json` (§2.6). Pasarla es error de uso (PD-9) y la entrada no sondea ningún archivo heredado.
- Sobre de salida de ambos verbos: exactamente las claves de `OUTPUT_KEYS` (`cdad_delegate.py`:52: `attempt`, `session`, `termination`, `delivery_ref`, `diagnosis`) y `termination` del vocabulario cerrado `TERMINATION_VOCABULARY` (:49). No se inventa un segundo idioma.
- `--json` es la forma estable legible por máquina; el texto libre sólo se suma cuando el dueño lo pida.

### 2.2 Contrato de la integración (el módulo por runtime; se extiende, no se duplica)

El módulo es `cdad_delegate_<id>.py`, resuelto por la convención de módulo que ya existe (`cdad_delegate.py` `_adapter_path`:91, ADR-023). Conserva su contrato actual (stdin byte-idéntico, envelope, preflight, espera acotada, terminación del grupo propio) y **suma**:

- **`--capabilities`**: documento `{native_observation, external_transport, session_correlation, version, reason}`. Significados declarados: `native_observation` = puede correlacionar un intento despachado por la herramienta nativa del runtime; `external_transport` = puede lanzar/esperar/recoger un proceso; `session_correlation` = el store expone las columnas de correlación (§2.3) en la versión observada; `version` = la versión **observada** del binario o `unknown` (nunca supuesta); `reason` = por qué una capacidad es falsa, **nombrando lo que falta**.
- **`--observe`**: una **única** lectura acotada del store que devuelve la observación del intento correlacionado o `null` (§2.3). Acceso sólo lectura (`mode=ro`, nunca `immutable`, nunca escritura — igual que `cdad_delegate_opencode.py`:619-621), sin polling.
- **`attempt` declarado** en su sobre (el intento que registró): quien lo invoca lo **relaya**, nunca lo reemplaza.
- **Kind de la parte entregada** derivado de la tabla rol/subfase (§2.8), nunca la constante fija de hoy (`FINAL_TEXT_ARTIFACT_KIND`, `cdad_delegate_opencode.py`:127).
- **Conducta ante un módulo sin la superficie nueva (ventana entre la entrada y esta unidad, O-6).** Si el módulo no implementa `--capabilities`/`--observe`, **no hay degradación silenciosa**: `capabilities` no puede acreditarse (el núcleo lo declara `native_observation: false` con `reason` que nombra la superficie ausente) y `record` sin resultado nativo byte-exacto **falla cerrado** con ese motivo — la observación nativa queda `unknown` y no hay entrega por esa vía (INV-4). Es una ventana transitoria, observable y declarada, no un fallback.

La **versión declarada** no es una abstracción nueva: sigue siendo `binary_version` de la configuración, con el gate ya existente del preflight (`_preflight_server`:1208, `_preflight_service`:1386) y su diagnóstico que nombra lo configurado y lo observado. No se agrega una lista de versiones (criterio §12: no introducir abstracciones que todavía no aportan utilidad).

### 2.3 Las cuatro llaves de correlación

Todas necesarias: **padre** (`session_v2.parent_id` == la sesión que despachó, declarada con `--parent`), **agente** (`session_v2.agent` == `REQUEST.json.agent`, §2.7), **proyecto** (`session_v2.directory` == la raíz autorizada del paquete) y **momento** (`session_v2.time_created` posterior al instante declarado con `--since`). Una llave no evaluable ⇒ `unknown`, y el diagnóstico **nombra la llave**. Nunca se compara contra un valor supuesto: si `REQUEST.json` no trae `agent` (paquete preparado antes de esta feature), la llave «agente» es **`unknown`**, no `cdad-<rol>`.

### 2.4 Observación y registro por vía

| Vía | Registra | Observación de la que sale `model_reported` |
|---|---|---|
| externa | el **módulo** (una vez) | la del módulo, leída de `session_v2.model` (`_model_reported_from_row`:259) |
| nativa | el **núcleo** (`record`, una vez) | la del módulo vía `--observe`, si la correlación se puede evaluar; si no, `null` con procedencia declarada |

En la vía nativa `model_configured` es `null` con procedencia declarada («el modelo de la delegación interna lo fija el runtime; CDAD no lo elige ni lo verifica», ADR-033 D2) — nunca un valor inventado. CDAD sigue **sin elegir modelo** (INV-9).

### 2.5 Credencial del servidor (D-ADP-1) — es del módulo OpenCode, no un contrato de entorno

En `mode: server`, el módulo resuelve la credencial con la precedencia **ya vigente** (entorno primero: `OPENCODE_PASSWORD`, luego `OPENCODE_SERVER_PASSWORD`, `_preflight_password`:949; y sólo si ninguna está, el archivo `credential_env_file` de `delegation.json` o el default `<config-dir>/cdad/opencode-server.env`, `_credential_file_path`:969, `_read_credential_file`:1008 con verificación de permisos sobre el fd abierto) y la **inyecta sólo en el entorno del proceso cliente que él lanza** (`OPENCODE_PASSWORD`), junto al `PWD` que ya pinea (`_invoke_destination`:426-427). Nunca en `argv`, ni en stdout/stderr, ni en el registro I8, ni en el recibo, ni en ningún artefacto versionado. En `standalone` y `service` **no se inyecta nada**. Ningún agente —orquestador ni rol— la carga, la ve ni la pasa: el rodeo de entorno que hoy hace el despachador (`set -a; . <env>; set +a`, `execution.md`:242) deja de ser necesario.

### 2.6 Configuración de ejecución por runtime y migración

Fuente única para la vía externa: la config de usuario de CDAD —`cdad_config_dir()`:100 (= `$XDG_CONFIG_HOME/cdad/` o `<base>/.config/cdad/`)—, archivo **`runtimes.json`** (`version: 1`), una sección por runtime:

```
{ "version": 1,
  "runtimes": {
    "<runtime-id>": { "binary": "<ruta>", "binary_version": "<versión verificada>",
                      "mode": "server|service|standalone", "server": "<url>",
                      "service": {"require": false}, "auto": true,
                      "sessions_db": "<store durable>",
                      "wait": {"timeout_seconds": N, ...} } } }
```

- Las claves de la sección son **las que el módulo ya lee** (`binary` —leído en `cdad_delegate_opencode.py`:1999—, `binary_version`, `mode`, `server`, `service`, `auto`, `sessions_db`, `wait`): se mueven de lugar, no se renombran (sin abstracción nueva).
- **`model` no vive aquí**: el modelo de la delegación externa es `delegation.json` por destino y rol (**ADR-033** D3). Una clave `model` en la sección se **rechaza nombrando `delegation.json`** (que el modelo se elija en un solo lugar se verifica por ausencia, ADR-033 «Reasons» 2).
- **La credencial tampoco se duplica aquí**: su ruta sigue donde ADR-033 punto 6 la puso (`delegation.json.credential_env_file`, default el hermano `opencode-server.env`). Se declara como corrección del fraseo «credencial si la usa» de `execution.md`:250 (evidencia: `cdad_delegate.py` `delegation_credential_env_file`:131). **Esta corrección no está confirmada por el dueño todavía** (gate de la unidad de configuración, PD-9; plan §2).
- **Derivación interna.** El núcleo **deriva** la configuración interna del módulo desde la sección y la entrega como archivo transitorio bajo el espacio de coordinación ya git-ignorado (`.cdad/`; verificado en este repo: `git check-ignore -v .cdad` → `.gitignore:11:.cdad/`), eliminándolo al terminar. Nunca contiene modelo ni valor de credencial.
- **Migración.** `install.sh` crea la plantilla de `runtimes.json` **sólo si no existe**, sin registrarla en el manifiesto y sin pisarla nunca: la misma disciplina de dato del usuario que ya aplica a `delegation.json` y `opencode-server.env.example` (`write_delegation_template`:1151-1166 y `install_user_config`:1191-1201, ADR-033 punto 5).
- **Exec-config heredado: error de uso accionable, no compatibilidad silenciosa** (B-1, opción ii del dictamen). La entrada **no declara `--exec-config`** en ninguno de sus verbos y **no lee ni sondea** ningún exec-config heredado: no hay ubicación convencional declarada donde encontrarlo (el archivo llegaba por argumento del invocador). Si el flag aparece en `argv` —en cualquiera de los verbos y en cualquiera de sus dos formas (`--exec-config <v>`, `--exec-config=<v>`)— la invocación **falla cerrado antes de todo efecto** (rc≠0, sin escritura, sin despacho) con **un solo diagnóstico de migración** que nombra (i) `runtimes.json` y su sección por runtime, (ii) la **correspondencia clave por clave** y (iii) la clave `model` que 006-003 D3 ya ignoraba y que ahora vive en `delegation.json`. Correspondencia declarada (es la que el diagnóstico nombra, y la misma que viaja en el diagnóstico del caso «sin sección»):

  | clave del exec-config retirado | dónde vive ahora |
  |---|---|
  | `runtime` | el **id de la sección** de `runtimes.json` (deja de ser una clave del documento) |
  | `binary`, `binary_version`, `mode`, `server`, `service`, `auto`, `sessions_db`, `wait` | las mismas claves, dentro de la sección del runtime |
  | `model` | `delegation.json` (ADR-033 D3; nunca en la sección) |
  | (credencial) | `delegation.json.credential_env_file` / el default `opencode-server.env` — nunca en `runtimes.json` |

  Razón declarada: admitirlo mantendría dos fuentes que pueden divergir (el propio criterio §12) y su efecto silencioso sería cambiar el binario, el store o el modo de un encargo ya preparado. La *interfaz* conserva su `--exec-config` como mecanismo **interno** (es el contrato que el módulo y sus tests usan); ningún texto del producto la nombra ya como camino del orquestador (U4) y queda como deuda declarada con su disparador (§8 item 4).

### 2.7 El agente viaja en el paquete (D-ADP-4)

`prepare` resuelve el agente con **rol + `stack` del estado** (`docs/.cdad-state.json.stack`; hoy **ningún** código del repo lo consume: grep de `stack` en `skills/cdad-cycle/scripts/` sólo devuelve usos ajenos, y `_derived_role`:2610-2621 clasifica nombres, no stacks) y lo escribe en `REQUEST.json` como campo **`agent`** (p. ej. `cdad-architect-odoo`). El campo es una **propiedad opcional declarada** del documento del request: el conjunto cerrado de `validate_request` (`cdad_packet.py`:769-777, hoy `required` + `optional = {"plan_task"}`) se **extiende** con `agent` y no se relaja — el mismo patrón con que 005-003 sumó `plan_task` (PD-10/INV-4). `agent` **no entra al render de `PACKET.md`** (`render_packet` usa su lista explícita de claves, `:932`), así que el paquete publicado sigue byte-idéntico y `receive` —que recomputa el render y lo compara, `cdad_result.py`:563-566— no cambia. El módulo lo traduce a su invocación (`--agent <agent>`) y **falla cerrado antes de despachar** si el agente no está publicado (reusa `_check_derived_agent_published`:302, hoy aplicado a `cdad-<rol>`, `_entry_agent_name`:298). Sin override de agente en `prepare` mientras no haya un caso real. Compatibilidad: un paquete sin `agent` sigue siendo despachable —el módulo usa `cdad-<rol>` y **declara la ausencia**— y la llave «agente» de la correlación queda `unknown` (§2.3). En la vía nativa el orquestador elige `subagent_type` al despachar: la divergencia no se previene, se **detecta** en la correlación de `record`.

### 2.8 Kind de la parte entregada (D-ADP-3 escalado a defecto real)

El `artifact_kind` de la parte que la entrega declara —en el descriptor `RESULT.json` que `receive` persiste— **se fija desde el rol y la subfase del paquete**, nunca se hardcodea, y **en las dos vías** (el módulo en la externa, `record` en la nativa):

1. Si la tabla cerrada `_allowed_kinds(rol, subfase)` (`cdad_result.py`:681-694) admite **exactamente un** kind, ése es el kind de la parte entregada: test-writer en `audit` → `test-audit`; test-writer en el resto de sus subfases → `test-writer-role-report`; implementer → `implementer-role-report`; reviewer en `review` → `review` y en `plan-review` → `plan-review` (su tabla es `{subfase}`).
2. Para el **architect** el kind es `role-report` (el informe del rol, la parte única que la entrega produce hoy), donde su tabla lo admite (`discovery`/`draft`). La tabla **no se amplía**: en `brainstorm` ese kind sigue rechazándose como hoy.
3. Cuando la tabla no determina uno —el **scribe**, con cuatro kinds (uno por archivo del Memory Bank) y sin destino elegible sin declararlo— la parte conserva `role-report` como hoy y `materialize` la rechaza nombrando rol, subfase y los kinds admisibles (`cdad_result.py`:917-919). No se adivina el destino del Memory Bank: límite declarado, con disparador (§8 item 3).

Evidencia medida que funda la decisión: el módulo escribe hoy la constante `FINAL_TEXT_ARTIFACT_KIND = "role-report"` (`cdad_delegate_opencode.py`:127) en `descriptor.parts[].artifact_kind` (`:1737`), y esa constante es el motivo por el que el dictamen del reviewer de esta misma feature no se pudo materializar (`execution.md`:255). La tabla no cambia: el kind deja de ser una constante y pasa a ser una derivación.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail. «Módulo» = `cdad_delegate_<id>.py` del runtime.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **Un solo intento I8 por despacho.** Vía externa: lo escribe el módulo (uno). Vía nativa: lo escribe `record` (uno). La interfaz común **no registra** (hoy sí: `cdad_delegate.py`:288/:311/:398) y el módulo tampoco registra dos veces. | conteo de `.cdad/executions/<exec>/dispatches/*.json` == 1 por intento en ambas vías; control negativo: el sobre del módulo y el registro coinciden en `attempt`; inspección de `cdad_delegate.py` sin `--record-dispatch` |
| **PD-2** | El núcleo **no es un segundo escritor**: no escribe `docs/.cdad-state.json`, no escribe el store, no escribe el ledger salvo por el comando existente; escribe sólo bajo `.cdad/`. | el estado sólo cambia por la transacción del comando; bytes del store idénticos (fixture); árbol de cambios acotado a `.cdad/` |
| **PD-3** | Con `--native-result`, la parte escenificada es **byte-exacta**: `sha256(parte) == sha256(entrada)`, sin retecleo, resumen ni regeneración; el descriptor apunta a ella y el recibo queda `semantic_status: pending`. | `sha256sum` de ambos; campo del recibo |
| **PD-4** | **Sin texto final o artefacto no hay entrega**: no se escenifica nada, no se escribe `RESULT.json`, no se invoca `receive`; el intento queda registrado y el sobre declara el hecho. (En la vía externa el módulo ya sólo persiste en `completed` con texto: `cdad_delegate_opencode.py`:2280-2300.) | `.cdad/inbox` sin cambios; ausencia de descriptor; existencia del intento |
| **PD-5** | Una sesión se acepta como del intento sólo si las cuatro llaves (§2.3) coinciden. Si falta o no coincide alguna: **no hay entrega por esa vía**, la observación lleva `session: null` y el diagnóstico **nombra la llave** fallida. Sin `agent` en el paquete ⇒ llave `unknown`, nunca `cdad-<rol>`. | fixtures con padre/agente/directorio/instante incorrectos y con paquete sin `agent`; el diagnóstico contiene el nombre de la llave |
| **PD-6** | **Garantía menor declarada:** con resultado nativo byte-exacto pero identidad no verificable (V-1), la entrega se persiste con `session: null` y `provenance` que declara que no se pudo verificar la identidad; nunca se inventa un valor de sesión. | observación con `session: null`; `provenance` sólo anota campos observados (`cdad_packet.py`:2371, `:2410`) |
| **PD-7** | `prepare` escribe `agent` = rol + `stack` del estado (p. ej. `cdad-architect-odoo`); sin `stack`, `cdad-<rol>`. El campo es una propiedad **opcional declarada** del request: el conjunto cerrado de `validate_request` lo admite y **sigue rechazando cualquier otra clave**; el render de `PACKET.md` **no cambia** (el paquete publicado sigue byte-idéntico para los mismos insumos) y un paquete publicado antes de la feature (sin `agent`) sigue siendo despachable y recibible. | `REQUEST.json` del paquete en los tres casos; `prepare` rc=0 en los tres; `receive` rc=0 sobre el paquete publicado; clave desconocida ⇒ rc≠0; bytes de `PACKET.md` idénticos con y sin `agent` |
| **PD-8** | **Resolución del runtime:** `--runtime X`; si no viene, el runtime declarado por el proyecto; si no hay ninguno, **error accionable** que nombra el flag y los lugares donde se declara; un valor declarado que no corresponde a un módulo de runtime disponible ⇒ rc≠0 **nombrando el valor**. **Alcance declarado (O-2):** el caso «declaración» sólo existe en un **contexto v1 plano** (el único documento que lleva `runtime`, `BINDING_FIELDS`:25-33); en un contexto v2 **no hay lugar de declaración verificado** (V-9: el contexto v2 no lleva `runtime` —`V2_EXECUTION_KEYS`:73-80, medido en el contexto de esta propia feature: `.cdad/executions/exec-006-005-native-path-parity-001/execution.json` es `schema_version: 2` y su `execution` no tiene la clave). El error de ese caso nombra el flag y **la ausencia de lugar de declaración**; no se nombra ni se inventa un lugar propuesto mientras el dueño no decida. | cuatro casos: flag / declaración (fixture de contexto **v1 plano** declarando un id con módulo) / ninguno (**contexto v2** ⇒ rc≠0, el diagnóstico nombra el flag y la ausencia) / valor inválido |
| **PD-9** | **Una sola fuente de configuración para la vía externa:** la sección del runtime en `runtimes.json`. Sin sección ⇒ falla cerrado con el diagnóstico que nombra el archivo, la sección y la **correspondencia clave por clave** de §2.6. La configuración derivada **no contiene `model`** (se rechaza nombrando `delegation.json`) **ni valor de credencial**. La entrada **no declara `--exec-config`** y no sondea ningún archivo heredado: el flag en `argv` (sus dos formas, en cualquiera de los verbos) ⇒ rc≠0 antes de todo efecto, con el **mismo** diagnóstico de migración. | documento derivado inspeccionado clave por clave; tres fixtures (sin sección con la correspondencia en el diagnóstico, con `model`, con `--exec-config` en `argv`) + control negativo (`--exec-config` ausente de `--help` y ninguna lectura de archivo heredado) |
| **PD-10** | `capabilities` responde las cinco claves de §2.2; con esquema de store desconocido ⇒ `session_correlation: false` **con `reason` que nombra lo que falta**; `version` es la observada o `unknown`, nunca supuesta; runtime id desconocido ⇒ rc≠0; módulo sin la superficie nueva ⇒ `native_observation: false` con `reason` que la nombra (§2.2). | fixture de esquema; el `reason` nombra el elemento faltante; fixture de módulo sin `--capabilities` |
| **PD-11** | **Credencial (D-ADP-1):** en `mode: server` la credencial resuelta (entorno → archivo 0600) se inyecta **sólo** en el entorno del proceso cliente; nunca en `argv`, stdout/stderr, el registro I8, el recibo ni ningún artefacto versionado; en `standalone`/`service` **no se inyecta nada**. El rodeo de entorno del despachador deja de ser necesario. | **binario falso que exige la variable** (sin ella falla; con ella completa) y eco de si la vio; centinela buscado en `argv`, salidas y registros; caso negativo en `standalone` |
| **PD-12** | La integración exige las columnas de correlación y **falla cerrado** nombrando las ausentes; nunca degrada a `timeout` ni a «ausente». | store descartable sin una columna → error específico |
| **PD-13** | **Sin bucle:** la lectura del store es única por invocación, `mode=ro`, con timeout acotado, y el intento declara `store_reads=<n>` con `n` ≤ el techo declarado; ninguna constante de intervalo ni bucle consulta el store. | conteo instrumentado del acceso; `store_reads` en el intento; ausencia de intervalo de polling en el módulo |
| **PD-14** | El agente del paquete llega a la invocación (`--agent <REQUEST.json.agent>`); si no está publicado, el módulo **falla cerrado antes de despachar** nombrando el agente; sin el campo, usa `cdad-<rol>` y declara la ausencia. `model_reported` del intento sale de la observación del módulo en las dos vías. | `argv` observado por el binario falso; caso de agente no publicado; ausencia de `agent` |
| **PD-15** | Un paquete puede declarar `{"class":"temporary","root":<selector>}`; se acepta **sólo si** el selector cae dentro de un `temporary_roots` de `docs/cdad-policy.json`. Con `temporary_roots: []` el encargo **se rechaza** nombrando el archivo y el campo. | `prepare` rc≠0 con el nombre del archivo; caso positivo rc=0 |
| **PD-16** | Con temporal declarado, `prepare` verifica con `git check-ignore` (read-only) que el selector está ignorado; si no lo está **o** el proyecto no es un árbol Git ⇒ falla cerrado nombrando las dos salidas legítimas (declararlo en `.gitignore`, o no pedir el temporal). | `prepare` rc≠0 + mensaje; caso positivo con raíz ignorada |
| **PD-17** | Con el temporal declarado e ignorado, un test real en `tests/` **más** una sonda dentro del temporal se reciben con `scope_validation: passed` y recibo `pending`; un cambio fuera de todo scope declarado sigue rechazándose. | campo `scope_validation` del recibo |
| **PD-18** | El temporal **no es producto**: sigue vigente el rechazo de `_validate_temporary_roots` (`cdad_packet.py`:414-430) cuando una raíz temporal se solapa con rutas de producto. | caso negativo de política |
| **PD-19** | **Camino mecánico a `failed`:** `register-transition --transition disposition --packet <activo> --resolution abandoned\|superseded`, **sin** recibo durable ⇒ `active_packet.status: failed` (terminal). No fabrica resultado, no fabrica recibo, no aprueba; `validate-state` (`cdad_packet.py`:546) VALID y `prepare` desbloqueado (hoy el bloqueo existe en :4336-4338). Si **hay** recibo durable ⇒ se rechaza nombrando `receive` (rechazo ya existente, :5207-5213). **Gate:** la enmienda de la consecuencia INV-9 de 005-012 (`docs/specs/005-012-transition-registration/spec.md`:243 y :587) **requiere aprobación explícita del dueño, todavía pendiente**, antes del RED de su unidad. | estado tras el comando; `validate-state`; `prepare` antes rc≠0 / después rc=0; la aprobación registrada como precondición |
| **PD-20** | **Entrada única:** el mandato conduce la decisión desde `status.entry`/`next` con el orden de cinco filas de §5 D-6, sin dos filas con la misma condición, y con la regla de transporte declarada (mismo runtime ⇒ nativa + `record`; otro ⇒ la entrada externa); **no existe** la condición stale de `.cdad/execution.json` (`sources/roles/orchestrator.md`:24) y el generado lleva el mismo texto. | test de texto sobre la fuente y sobre el generado recomputado (`make staging`); `status` del CLI como evidencia del insumo |
| **PD-21** | **Cierre:** la review independiente de spec/plan precede al RED (enmienda 006, procedimiento vigente `plan-review` sobre `draft-plan`: `cdad_packet.py`:52-53, :815-829, `cdad_result.py`:700); `make validate` y la suite completa **una vez** al cierre (política declarada; corre quien cierra). | salidas de los comandos; el dictamen en la carpeta de la spec |
| **PD-22** | **Recorrido de aceptación** (U6): en un proyecto **descartable** —nunca HOME, nunca el proyecto activo— un layout anidado, el coordinador iniciado desde otra carpeta, agente global y configuración de proyecto declarados con garantía menor, un auxiliar temporal, **un test real escrito y recibido**, **una entrega por la vía externa con la entrada nueva**, **una entrega por la vía nativa** (`task` + `record`) y **un intento interrumpido llevado a `failed` por comando**. Se declaran versión y configuración observadas y **no se generaliza** el resultado. | artefactos del recorrido: intento I8, recibo `pending`, estado `failed`, `scope_validation: passed`, sobre de `dispatch` con el `attempt` del módulo |
| **PD-23** | **El kind de la parte entregada se deriva de la tabla rol/subfase, en las dos vías** (§2.8): el módulo deja de declarar la constante fija (`FINAL_TEXT_ARTIFACT_KIND`) y `record` declara el mismo kind en el descriptor que escenifica. Nunca se declara un kind que la tabla no admita para el rol y la subfase; cuando la tabla no determina uno (scribe), la parte conserva `role-report` y `materialize` la rechaza nombrando rol/subfase (límite declarado). La tabla `_allowed_kinds` **no se modifica**. | entrega de un paquete del reviewer en `plan-review` → `artifact_kind: plan-review` en el descriptor y `materialize` rc=0 con sha idéntico (hoy rc≠0); entrega del architect en `draft` → `role-report` y `materialize` rc=0 (sin cambio); kind nombrado de otro rol → sigue rechazado; test-writer en `audit` → `test-audit`; scribe → sigue rechazado nombrando rol/subfase; tabla inspeccionada (sin cambios respecto del HEAD) |

**MAPEO AC → PD** (los AC del epic §4/§11 como origen, no como autoridad):

| AC (epic §4 / §11) | PD |
|---|---|
| AC-1 (selección comprensible; sin secretos; config incompatible ⇒ diagnóstico) | PD-8, PD-9, PD-10, PD-11 |
| AC-2 (mismo encargo y autoridad; identidad y entrega durable; una entrega no aprueba) | PD-1, PD-2, PD-3, PD-5, PD-7, PD-23 |
| AC-3 (concurrencia útil, prueba controlada) | PD-22 (el recorrido es contracara del escenario de §11; la prueba concurrente se hizo en 006-001) |
| AC-4 (fallo recuperable; sin éxito ni recibo fabricados) | PD-4, PD-6, PD-19 |
| AC-5 (espera proporcional; sin sondeo indefinido) | PD-13, PD-12 |
| AC-6 (versión estable; incompatibilidad con salida legítima) | PD-10, PD-16 |
| AC-7 (recepción real, una vez desplegado) | PD-22 (declarado con su estado; no se acredita por pruebas aisladas) |
| AC-8 / §11 «fuera de alcance» (producto portable; sin paths ni gestor de servicios impuesto) | PD-9, PD-20 |
| §11 aceptación (recorrido de cada integración) | PD-22 |
| Enmienda 006 / §13 | PD-21 |

## 4. Invariantes (INV-n)

- **INV-1.** Sin texto final o artefacto **no hay entrega**: nunca se fabrica recibo, `completed` ni resultado. El recibo nace `pending` y **no aprueba**.
- **INV-2.** La sesión **se correlaciona o se declara `unknown`**: nunca 0, nunca «ausente», nunca un valor no leído del store o no devuelto por el transporte.
- **INV-3.** El temporal está **ignorado por Git de verdad** (verificado con `git check-ignore`); un temporal ignorado nunca aparece como cambio observado (el manifiesto usa `git ls-files --cached --others --exclude-standard`, `cdad_result.py`:1305-1318).
- **INV-4.** Fuera de su versión declarada o con esquema desconocido, la integración responde **cerrado/`unknown`** con motivo; sin fallback silencioso (incluye un módulo sin la superficie nueva, §2.2).
- **INV-5.** **Un solo escritor por recurso:** del store (`mode=ro`, nunca `immutable`, nunca escritura), del estado y del ledger (sólo por los comandos existentes). El ledger recibe **un** intento por despacho (PD-1).
- **INV-6.** **Ninguna lectura del store en bucle**: sin polling, con techo de lecturas por invocación declarado y contado.
- **INV-7.** La política, `delegation.json` y `runtimes.json` son **datos del dueño**: ningún rol los edita; el instalador sólo crea plantillas cuando no existen; el default de temporal es **propuesta**.
- **INV-8.** La observación I8 conserva su **esquema cerrado** (`OBSERVATION_KEYS`); el `provenance` sólo anota campos observados y nunca transporta resultados, gates ni aprobaciones; en salidas versionadas no hay secretos, rutas del host ni ids de sesión.
- **INV-9.** CDAD **no elige modelo** (regla I8 vigente, ADR-033 D2, sin cambios).
- **INV-10.** El núcleo **no toca el producto**: escribe sólo bajo `.cdad/`.
- **INV-11.** **La credencial no sale del entorno del proceso cliente**: nunca en `argv`, logs, recibos, registros I8 ni artefactos versionados; y sólo en `mode: server`.
- **INV-12.** **Una fuente por camino:** el modelo de la delegación externa sólo en `delegation.json` (ADR-033 D3); la configuración de ejecución sólo en la sección del runtime; la credencial sólo donde ADR-033 punto 6 la puso. Ninguna clave se duplica entre archivos.
- **INV-13.** **La identidad del agente se detecta, no se supone:** la correlación compara contra el agente declarado en el paquete; sin ese campo es `unknown`; nunca hay degradación a un agente genérico no-Cdad (se conserva el rechazo ya vigente, `_check_derived_agent_published`:302).
- **INV-14.** **El kind de la parte entregada se deriva, no se hardcodea:** sale de la tabla cerrada rol/subfase (§2.8) en las dos vías; el producto no declara un kind que la tabla no admita para ese rol y esa subfase, y la tabla no se relaja para acomodar la entrega.

## 5. Decisiones (D-n) — adoptadas, con el criterio de §12

- **D-1 — Dónde vive el núcleo.** Módulo propio `cdad_dispatch.py` que **importa** `cdad_packet` y los ayudantes de la interfaz (read-only) y escribe el ledger por el comando existente. *General/específico:* el núcleo es general (entrada y transporte-neutral); **rechazadas** agrandar `cdad_packet.py` (§11 lo prohíbe) y meterlo en `cdad_result.py` (recepción es otra responsabilidad).
- **D-2 — Forma de la integración por runtime (corrige draft-001).** La integración **es** el módulo por destino que ya existe (`cdad_delegate_<id>.py`, ADR-023), extendido con credencial, agente, capacidades, observación y kind derivado. *Rechazadas:* (a) un segundo módulo nuevo por runtime (`cdad_runtime_<id>.py`, propuesta de draft-001) — dos módulos para el mismo trabajo, duplicación que puede divergir y dos lugares donde el store se lee; (b) un módulo con dict de runtimes — mezcla runtimes y contradice ADR-032; (c) clase base/plugin — abstracción sin segundo consumidor real todavía.
- **D-3 — Correlación.** Padre + agente + proyecto + momento (`time_created > --since`), con `null`/`unknown` cuando no se puede evaluar. *Rechazadas:* confiar sólo en el id del transporte (más débil y hoy `VERIFY` V-1) y «la hija más reciente del directorio» (ambigua bajo concurrencia: es el tema del epic). El **momento** se mide contra un instante **declarado** porque el repo no registra el instante del `begin` (V-10).
- **D-4 — Camino a `failed`.** El efecto del `disposition` mueve el paquete activo citado a `failed` (terminal, sin aprobar y sin recibo). *Rechazadas:* verbo nuevo `fail-packet` (admisible, más superficie), `--replace-packet` sobre `dispatched` (lo prohíbe PD-10, `cdad_packet.py`:2094-2102) y `reconcile` que escriba (es read-only por contrato). **Conflicto declarado y gate:** `docs/specs/005-012-transition-registration/spec.md`:243 y su INV-9 (`:587`) declaran que el `disposition` **no** cambia `active_packet`; PD-19 **enmienda** esa consecuencia y **requiere aprobación explícita del dueño, pedida y no registrada todavía** (gate del RED de su unidad); el test acoplado `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 se cambia **en RED declarando el reemplazo** (A-1).
- **D-5 — Temporal.** Clase `temporary` en el vocabulario de scopes, validada contra `temporary_roots` (autoridad del dueño), default **propuesto** `.cdad/tmp`, verificación `git check-ignore`. *Rechazadas:* declararla clase `tests` (miente sobre la clase), temporal fuera del proyecto (es el incidente de la espera larga) y ruta libre declarada por el paquete (PD-9 de 004-002). **Ubicación por defecto — justificación y condiciones:** (C1) es **propuesta**: la emite `propose_policy` (`cdad_packet.py`:1088, hoy con `temporary_roots: []` en :1100) y la acepta el dueño; en este repo la política vigente declara `[]`, así que **hoy** pedir un temporal falla cerrado — es lo correcto. (C2) `.cdad/tmp` es subdirectorio disjunto de los subárboles que el CLI escribe (`inbox/`, `packets/`, `executions/`, `runtime/`): nunca el `.cdad/` raíz. (C3) está ignorado de verdad: verificado en este repo, `git check-ignore -v .cdad/tmp` → `.gitignore:11:.cdad/`. (C4) si el proyecto no lo ignora, `prepare` falla cerrado nombrando las dos salidas (PD-16). (C5) el validador de política ya garantiza que una raíz temporal no se solape con producto (:414-430; PD-18). *Alternativa no elegida:* una raíz de primer nivel (p. ej. `.tmp/`), no ignorada por defecto.
- **D-6 — Entrada única.**

  | # | Condición (de la vista) | Acción única |
  |---|---|---|
  | 1 | `entry == diagnosis` | salida bloqueada: diagnóstico accionable; no se prepara ni despacha |
  | 2 | `continuity-reconcile` + paquete `dispatched` | reconciliar primero (`reconcile`, read-only); nunca re-despachar ni abrir un segundo worker |
  | 3 | `continuity-reconcile` + paquete `prepared` | validar → `begin` → **transportar**: mismo runtime ⇒ herramienta nativa + `record`; otro runtime ⇒ `cdad_dispatch.py --packet <id> [--runtime X]` → `receive` |
  | 4 | `continuity-reconcile` + sin paquete + ejecución activa | `resume` y continuar el trabajo activo |
  | 5 | `next-unit` | `open-unit` |

  «Legacy/handoff» pasa a **fallback de transporte**; «arranque en reposo» es el camino previo hacia `project-start.md`. *Rechazadas:* mantener la prosa con precedencia (el solape persiste) y un campo nuevo de estado (la vista ya lo calcula).
- **D-7 — Espera.** Detección post-hoc + a lo sumo una lectura acotada bajo demanda; prevención por D-5. *Rechazada:* vigilar el store.
- **D-8 — Alcance del transporte externo.** El adaptador externo **pierde su registro duplicado** y conserva su transporte; el producto deja de nombrar la interfaz común como camino del orquestador (U4). *Alternativa admisible:* dejarlo como está hasta una feature siguiente; se descarta por §12 (duplicación que puede divergir) y porque el consumidor real del núcleo es lo que justifica su forma.
- **D-9 — Una entrada para el orquestador.** `cdad_dispatch.py --packet <id> [--runtime X]` (verbo `dispatch` por defecto), **sin exec-config**, modelo, credencial ni modo: el orquestador no carga entornos. *Rechazadas:* dos entradas (una por vía) y que el orquestador siga pasando la configuración.
- **D-10 — Configuración por runtime en la config de usuario.** `runtimes.json`, una sección por runtime, junto a `delegation.json`, con las claves que el módulo ya lee. *Rechazadas:* (a) mantener el exec-config como dato del usuario (es el rodeo que el owner retira, `execution.md`:250); (b) una variable de entorno por clave (no es portable ni verificable); (c) **duplicar el modelo o la credencial en la sección** — el modelo es de `delegation.json` (ADR-033 D3) y la credencial también (ADR-033 punto 6); la sección se valida por ausencia de `model` (PD-9). **Pendiente declarado:** la confirmación del dueño de (c) es gate del RED de la unidad de configuración.
- **D-11 — Migración del exec-config heredado: error de uso accionable (B-1, opción ii).** La entrada **no declara** `--exec-config` y no lee ni sondea ningún archivo heredado (no hay ubicación convencional declarada); el flag en `argv` falla cerrado antes de todo efecto con el diagnóstico de migración que nombra `runtimes.json`, su sección por runtime, la correspondencia clave por clave y la clave `model`, que ya migró a `delegation.json`. *Rechazadas:* (i) «aceptarlo sólo para rechazarlo» — declara la opción y sugiere que existe una vía de paso; (iii) «una ubicación legada concreta sondeada» — inventa un lugar que el repo no acredita y hace el error dependiente de un archivo que puede no existir; y la compatibilidad con aviso, que cambia en silencio binario, store o modo de un encargo ya preparado y deja dos fuentes que pueden divergir. La interfaz conserva su `--exec-config` **interno** (deuda declarada con disparador, §8 item 4).
- **D-12 — La credencial es del módulo OpenCode.** Precedencia vigente (entorno → archivo 0600) e inyección sólo en el entorno del proceso cliente, sólo en `mode: server`; ningún agente la ve. *Rechazadas:* un contrato genérico de entorno del núcleo (mezclaría runtimes y expondría la credencial a la capa neutral) y exportarla en el proceso que despacha (el rodeo medido, `execution.md`:242).
- **D-13 — El agente viaja en el paquete.** `prepare` resuelve rol + `stack` y escribe `agent` (propiedad opcional declarada del request, sin tocar el render); el módulo traduce y falla cerrado si no está publicado; la correlación compara contra ese campo; sin override de agente mientras no haya caso real; compatibilidad con paquetes sin el campo. *Rechazadas:* que el módulo derive el stack por su cuenta (segunda resolución, puede divergir de `prepare`) y que el orquestador elija el agente en la vía externa (mete una decisión de dominio en el despacho).
- **D-14 — Quién registra.** El módulo en la vía externa, el núcleo en la nativa; la interfaz nunca. *Rechazadas:* que el núcleo registre también en la vía externa (tendría que recibir la observación interna del módulo y habría dos capas con el mismo dato) y que el núcleo no registre en la vía nativa (dejaría la vía nativa sin I8: la brecha que la feature cierra).
- **D-15 — D-ADP-3: el defecto se corrige; la separación en partes propias queda en deuda.** El defecto real medido (`execution.md`:255: el dictamen de un rol no-architect no se materializa porque el módulo declara una constante `role-report`) **entra a la feature** como PD-23 (§2.8, INV-14): el kind se deriva de la tabla rol/subfase, en las dos vías, sin tocar la tabla. La **separación de `spec.md`/`plan.md` en partes propias** del architect queda en **deuda declarada** con su disparador, por el criterio de §12: no hay caso real medido que la exija, y generalizarla costaría un campo nuevo en el contrato del paquete, un camino de separación en el núcleo y tocar `_allowed_kinds`/`receive` (§8 item 3).

## 6. Desconocidos (V-n) y su resolución

- **V-1 (riesgo principal) — cómo obtiene el padre la sesión hija por la vía nativa.** Resolución: **sonda real acotada** (un despacho nativo mínimo, declarado y con el resultado registrado) **antes o durante U2**; el hallazgo se declara en la integración (`capabilities`/`--observe`). Si la llave «padre» no es evaluable: (a) con resultado nativo byte-exacto hay entrega con **garantía menor declarada** (`session: null` + `provenance`, PD-6); (b) por la vía del store no hay entrega y la observación es `unknown` (PD-5). Nunca una entrega inventada.
- **V-2 — `time_idle`/`idle_outcome` en 0/null:** el fin de corrida **no** se exige en la vía nativa; la entrega depende del texto final del transporte.
- **V-3 — semántica de `external_directory` por versión:** la integración declara versión y falla cerrado fuera de ella (PD-10); la prevención es D-5.
- **V-4 — título «## Delegation (adapter)» con contenido nativo** (`scripts/cdad-generate.py`:747): se corrige en U4.
- **V-5 — si el `task` nativo bloquea al padre y la semántica exacta del permiso:** sonda declarada; si queda desconocido, la espera es post-hoc y se declara (PD-13).
- **V-6 — condición stale de `.cdad/execution.json` en el mandato** (`sources/roles/orchestrator.md`:24; el path v1 es `cdad_packet.py` `FLAT_EXECUTION_RELPATH`:88 y los contextos v2 viven en `.cdad/executions/<id>/execution.json`): se corrige en U4.
- **V-7 — columnas reales de correlación en la versión instalada:** sonda antes del RED de U2; la forma citada proviene de 005-002 y el módulo hoy exige un subconjunto menor (`SESSION_V2_COLUMNS`, `cdad_delegate_opencode.py`:182 = `id, agent, model, time_idle, idle_outcome`).
- **V-8 — la propuesta de temporal cambia bytes de `propose_policy`:** se buscaron tests que fijen ese valor y **no se encontró ninguno** (los hallados son fixtures: `tests/test_004_002_t1_policy.py`:204 no fija el valor; `tests/test_003_003_t2_preflight.py`:105 y `tests/test_004_002_t1_reviewfix.py`:125; `tests/test_004_002_t6_landing.py`:374 sólo parsea el JSON). Si el RED encuentra uno, se cambia **en RED declarando el reemplazo** (A-1).
- **V-9 — el runtime del proyecto no está declarado en ningún lugar verificable para un contexto v2.** Verificado: el contexto v2 **no** lleva `runtime` (`V2_EXECUTION_KEYS`, `cdad_packet.py`:73-80; comentario «runtime, model and session are dispatch observations, never part of the identity»), el estado no tiene clave de runtime, y el registro de activación sólo nombra `adopted_root` + rutas: «Registro:» es un **párrafo** dentro de «Qué emite por runtime» (`skills/cdad-cycle/references/runtime-adoption.md`:21 y :37), no un encabezado de sección. Medición directa del caso: el contexto de **esta** feature (`.cdad/executions/exec-006-005-native-path-parity-001/execution.json`) es `schema_version: 2` y su bloque `execution` **no** tiene `runtime`. *Consecuencia declarada:* en un contexto v2, sin `--runtime` la entrada **falla cerrado** con el error accionable de PD-8 (que es la salida legítima que el owner previó: «si no hay ninguno, error claro»), **nombrando el flag y la ausencia de lugar de declaración**; en un contexto v1 plano el valor **sí** existe (`BINDING_FIELDS` con `runtime`, :25-33) pero puede no ser un id de runtime disponible (en este repo, `.cdad/execution.json` declara `"multi-runtime"`), y PD-8 exige rc≠0 nombrando el valor. *Propuesta para el dueño (no decidida aquí y no inventada en la spec):* declarar el runtime en la config del proyecto. Hasta que el dueño decida, el error **no** nombra un lugar propuesto.
- **V-10 — el instante del `begin` no está registrado en ninguna pieza.** Verificado: los cuerpos de continuidad son deterministas por diseño («timestamps, so the same input in two different projects yields the same bytes», `skills/cdad-cycle/scripts/cdad_continuity.py`:36) y su esquema no tiene campo de tiempo (`attempt, authority, decisions, execution_id, goal, next_action, packet_id, record, references, schema_version, uncertainties`). *Consecuencia:* la llave «momento» usa el instante **declarado** por quien despacha (`--since`, PD-5); sin él ⇒ `unknown`; queda declarado en `provenance` que el instante es declarado, no medido.
- **V-11 — `opencode run --agent cdad-<rol>-odoo` de punta a punta (pendiente de verificar en el ciclo).** Es la decisión 6 del owner (`execution.md`:254). Sonda declarada: en un proyecto **descartable** con `stack: odoo`, un despacho externo real contra el binario instalado; se registran versión observada, la fila durable (`session_v2.agent`), el `attempt` y el recibo. Si no se puede ejecutar, la unidad queda **BLOQUEADA** con motivo y evidencia, sin sustituirla por una corrida simulada (regla de bloqueo, plan §3 U6).
- **V-12 — la paridad de las dos vías con la misma ejecución** (mismo paquete, misma entrega) sólo está medida para la vía externa (006-002/006-003); la vía nativa con `record` **nunca** se ejecutó. Sonda: el recorrido de PD-22 (U6), con el mismo escenario en las dos vías; un éxito es evidencia de ese recorrido, no prueba general.
- **V-13 — el kind derivado, medido contra la tabla real.** Verificado en el HEAD medido: `_allowed_kinds` (`cdad_result.py`:681-694) admite un solo kind para test-writer en `audit` (`test-audit`), para test-writer en el resto de sus subfases, para implementer y para reviewer por subfase; admite `role-report` para el architect sólo en `discovery`/`draft`; admite cuatro para el scribe. La derivación de §2.8 se prueba contra esa tabla; si el RED de U2 encuentra un caso donde la tabla no determina un kind y **sí** hay un caso real medido, se declara el reemplazo en RED (A-1) en vez de adivinar.

## 7. Medición de la aceptación

- Se mide lo observado (versión, configuración, intentos, lecturas del store, tiempos, terminaciones, modo solicitado/efectivo) y se registra; **desconocido no es cero**.
- **No** se fijan reducciones porcentuales de locks, tokens ni tiempo.
- Un éxito del recorrido de U6 es evidencia **de ese recorrido**, no de que la contención esté eliminada.
- La credencial no entra en ninguna medición ni salida: se mide **si hubo credencial y su procedencia** (`environment`/`file`), nunca su valor.

## 8. Fuera de alcance

1. La **integración Claude Code**: se deja la interfaz ya preparada (§2.2); su módulo, su sección de config y su guard quedan para después (plan §11).
2. El transporte externo **más allá de que consuma el núcleo**, los filtros de Bash, los ejecutores de acciones externas y la construcción incremental.
3. **La separación de las partes esperadas por el paquete en artefactos propios del rol** (el resto de D-ADP-3) **va a deuda declarada**; **el defecto de materialización se corrige en esta feature** (PD-23, §2.8). Criterio (§12): el único caso real medido es el informe del architect —parte única `role-report`, que su tabla admite en `discovery`/`draft` (`cdad_result.py`:681-694) y cuya materialización es el paso declarado del orquestador (ADR-003)— más el caso del dictamen no-architect, que ahora **sí** se materializa por el kind derivado; separar `spec.md`/`plan.md` en partes propias con hash del rol exigiría un campo nuevo en el contrato del paquete, un camino de separación en el núcleo **y** tocar `_allowed_kinds`/`receive`, sin un requisito declarado que lo pida. **Disparador declarado:** cuando un consumidor necesite los digests por parte **como artefactos propios del rol** (materialización automática por parte). **Disparador adicional del límite de §2.8.3:** el primer entregable del **scribe** por la vía del adaptador (hoy sigue rechazado nombrando rol y subfase: no hay destino de Memory Bank elegible sin declararlo).
4. La **retirada del `--exec-config` interno de la interfaz común** (`cdad_delegate.py`): la vía del producto ya no lo usa (D-11) y ningún texto lo nombra (U4); retirarlo del todo toca el contrato del módulo y sus tests y entra en la deuda **con disparador**: cuando no quede ningún despliegue con la interfaz como camino del orquestador.
5. La política del proyecto y `delegation.json`/`runtimes.json` (datos del dueño): esta feature sólo cambia la **propuesta** de política y crea **plantillas**.

## 9. Riesgos residuales

Contención del store (se mitiga, no se elimina aquí); deriva de esquema sin `schema_version` (detección por columnas → fallo cerrado); mapas `edit` no observados aplicados en la versión medida (por eso el temporal se declara, no se confía al mapa); V-1, que acota la garantía de identidad del recorrido nativo; V-9/V-10, que hacen que dos llaves de correlación dependan de datos **declarados** por el despachador; la ventana entre `prepare` (que ya escribe `agent`) y los paquetes publicados antes de la feature, que quedan con la llave «agente» `unknown` (declarado, PD-7/PD-5); y la ventana entre la entrada nueva y la superficie del módulo (§2.2): un módulo sin `--capabilities`/`--observe` **declara el hecho y falla cerrado** — no hay entrega nativa silenciosa en ese tramo.
===== END spec.md =====
===== BEGIN docs/specs/006-005-native-path-parity/plan.md (DRAFT — UNAPPROVED) =====
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
===== END plan.md =====

## Tabla hallazgo → corrección

| Hallazgo | Corrección aplicada |
|---|---|
| **B-1** | Opción **(ii)** declarada (spec §2.6 viñete «Exec-config heredado: error de uso accionable», D-11, PD-9; plan U1a). La entrada **no declara `--exec-config`** ni sondea archivo heredado alguno (no existe ubicación declarada: el archivo llegaba por argumento del invocador); el flag en `argv` (dos formas, cualquier verbo) ⇒ rc≠0 **antes de todo efecto**, con un diagnóstico único que nombra `runtimes.json`, su sección por runtime y la **correspondencia clave por clave** (tabla nueva en §2.6, la misma que viaja en el diagnóstico del caso «sin sección»). El fixture «exec-config heredado» de PD-9 se redefine como «`--exec-config` en `argv`» + control negativo (`--exec-config` ausente de `--help`). La interfaz conserva su `--exec-config` interno (§8 item 4). |
| **B-2** | Los tres tests acoplados al registro doble pasan a **A-1 de U1b** con reemplazo declarado: `tests/test_005_010_t1_durable_signal.py` (`:431-449` cuenta dos registros; `:536-543` aserta `model_reported` nulo en el de la interfaz) **más** `tests/test_005_010_t4_integration.py` (`:480-486`, `:540-557`) y `tests/test_005_010_reviewfix.py` (`:489-500`), que se verificaron con el mismo criterio y **no estaban listados en ninguna regresión**. Los tres se quitan de la lista de regresiones «simples» y quedan en `files` de U1b (plan §3/§4, plan-tasks U1b). |
| **D-15** (deuda sin sustento) | El defecto medido se corrige dentro de 006-005 con la forma más simple: **PD-23** (nueva) + **§2.8** + **INV-14** + unidad (**lado externo en U2, lado nativo en U1b**) + oráculo (entrega del reviewer en `plan-review` ⇒ `artifact_kind: plan-review` y `materialize` rc=0 con sha idéntico; architect en `draft` ⇒ `role-report` sin cambio; test-writer en `audit` ⇒ `test-audit`; scribe ⇒ sigue rechazado nombrando rol/subfase) + regresiones de la tabla `cdad_result.py` (`test_005_007_t4_architect_report_materialization.py`, `test_003_002_t2_materialize.py`, `test_003_002_t2_reviewfix.py`, `test_003_002_t1_receive.py`). La **separación de `spec.md`/`plan.md` en partes propias queda en deuda** decidida con §12 (sin caso real, coste: campo nuevo + camino de separación + tocar la tabla) con su disparador; §8 item 3 reescrito y V-13 (sonda del kind derivado). La tabla **no se modifica**. |
| **O-1** | Gate explícito en U5 (plan §2 y §3 U5, plan-tasks U5): «**aprobación del owner de la enmienda PD-19** (consecuencia INV-9 de 005-012, `docs/specs/005-012-transition-registration/spec.md`:243/:587) registrada **antes del RED**»; PD-19 lo declara como precondición y D-4 como «pedida y no registrada todavía». No se da por hecha. |
| **O-2** | PD-8 declara el alcance: el caso «declaración» se prueba sobre un **contexto v1 plano** (el único con `runtime`, `BINDING_FIELDS`:25-33) y en **v2** el error nombra el flag y **la ausencia de lugar de declaración**; V-9 se refuerza con la medición directa (el contexto v2 de esta feature no lleva `runtime`) y con la corrección del «Registro» (es un párrafo de «Qué emite por runtime», :21/:37). El lugar propuesto **no se inventa**. |
| **O-3** | U1 partida por los tres cortes del dictamen: **U1a** (config + migración, PD-8/PD-9), **U1b** (entrada + registro, PD-1…PD-6 y PD-23 nativa), **U1c** (agente en el paquete, PD-7). Dependencias ajustadas: U1a → U1b → U2; U1c independiente pero condiciona a U2; y la nota de que U1c/U3/U5 comparten `cdad_packet.py` ⇒ **sin `parallel` entre ellas**. RED y regresiones propios por unidad. |
| **O-4** | U4 (ficha §3 y plan-tasks) nombra las salidas de `make agents`: `agents/cdad-*.md` (11) y `agents/claude-code/cdad-*.md` (11), con la cita `Makefile`:1-24 (objetivos `staging`/`agents`) y la regla «nunca a mano». |
| **O-5** | La confirmación del owner (modelo y credencial **no** viven en `runtimes.json`) es **gate del RED de U1a** (plan §2 y §3 U1a, plan-tasks U1a, `validation_strategy`), declarada como pendiente en spec §2.6, D-10 y PD-9. |
| **O-6** | §2.2 suma la conducta declarada: un módulo sin la superficie nueva ⇒ `capabilities` no acredita (`native_observation: false` con `reason` que nombra la superficie ausente) y `record` sin resultado nativo byte-exacto **falla cerrado** (observación `unknown`, sin entrega por esa vía); PD-10 lo incluye como oráculo; §9 (riesgos) nombra la ventana. |
| **O-7** | §1 recontada: **seis** brechas, nombrándose la sexta (el orquestador que reconstruyó el protocolo a mano — §11 `plan.md`:289 —, cerrada por el registro mecánico, pieza 6). |
| **O-8** | Citas corregidas contra el HEAD medido `b82e6a3`: `_adapter_path` `cdad_delegate.py`**:91** (no :79); prohibición de `--replace-packet` sobre `dispatched` `cdad_packet.py`**:2094-2102** (no :2082-2083); `temporary_roots: []` en `propose_policy` **:1100**; `_load_observation_document` **:2410** y `OBSERVATION_KEYS` **:2371** (en vez del rango); `binary` leído en `cdad_delegate_opencode.py`**:1999** (§2.6 ya no atribuye el rango :1857-1900 a esa clave); «Registro» de `runtime-adoption.md` como **párrafo** de «Qué emite por runtime» (:21/:37). |
| **Propio (draft-003)** | **El agente del paquete no es implementable sólo con la zona de `prepare`**: `validate_request` impone un **conjunto cerrado** de campos del request (`cdad_packet.py`:769-777, `optional = {"plan_task"}`) y `receive` recomputa el render (`cdad_result.py`:563-566). PD-7 y la ficha U1c declaran las **dos zonas** (dict de `prepare` :4455-4474 + el conjunto cerrado :769-777), la propiedad opcional declarada, el render intacto (`render_packet` lista sus claves, :932) y las regresiones de `prepare`/render/`receive`. |

## Evidencia del rol

- **Rol:** architect, subfase `draft` (paquete `006-005-native-path-parity-architect-draft-003`), **read-only**: `write_scope: []` respetado.
- **HEAD medido:** `b82e6a3` (`git rev-parse HEAD`). `git diff 357c461..b82e6a3 --stat` → docs-only (state, `execution.md` +1 línea, `plan-review.md`); `git diff 9d3b2ea..b82e6a3 --stat` → docs-only (state, `execution.md`, `plan-review.md` y los dos borradores draft-002): **ninguna cita de código quedó invalidada por movimiento del árbol**.
- **Comandos exactos (resumen):** `git rev-parse HEAD`; `git log --oneline -6`; `git diff 357c461..b82e6a3 --stat`; `git diff 9d3b2ea..b82e6a3 --stat`; `git status --porcelain`; ~45 inspecciones `grep -n`/`sed -n`/`awk` de símbolo+línea sobre `skills/cdad-cycle/scripts/{cdad_packet,cdad_delegate,cdad_delegate_opencode,cdad_result}.py`, `install.sh`, `Makefile`, `scripts/cdad-generate.py`, `sources/roles/orchestrator.md`, `skills/cdad-cycle/references/{cli-delegation,runtime-adoption,re-entry}.md`, `skills/cdad-cycle/assets/artifact-policy.json`, `docs/specs/005-012-transition-registration/spec.md`, `tests/test_005_007_t4_architect_report_materialization.py`; lecturas dirigidas de `tests/test_005_009_t{1,2}*`, `tests/test_005_010_t1_durable_signal.py`, `tests/test_005_010_t4_integration.py`, `tests/test_005_010_reviewfix.py`, `tests/test_006_001_t1_selection.py`, `tests/test_006_003_u7_prune_obsolete.py`, `tests/test_006_003_u8_acceptance.py`; `python3 -c` para leer `docs/.cdad-state.json` (`stack: null`), `.cdad/execution.json` (`runtime: "multi-runtime"`) y `.cdad/executions/exec-006-005-native-path-parity-001/execution.json` (`schema_version: 2`, sin `runtime`).
- **Verificaciones nuevas que fundan las correcciones (símbolo + línea del HEAD medido):** `FINAL_TEXT_ARTIFACT_KIND = "role-report"` en `cdad_delegate_opencode.py`:127 y su uso en `descriptor.parts[].artifact_kind` :1737; `_allowed_kinds` `cdad_result.py`:681-694 (un solo kind para test-writer `audit`, implementer y reviewer por subfase; `role-report` para architect sólo en discovery/draft; cuatro para scribe) y el rechazo en :914-919; `artifact-policy.json` (`role-report` → `docs/specs/<feature>/`); `validate_request` con `required`/`optional = {"plan_task"}` en `cdad_packet.py`:769-777 y el render por claves explícitas en :932; `receive` recomputa el render en `cdad_result.py`:563-566; el dict de `REQUEST.json` en `cdad_packet.py`:4455-4474; `config.get("binary")` en `cdad_delegate_opencode.py`:1999; `def _adapter_path` en `cdad_delegate.py`:91; el bloque `dispatched` de `--replace-packet` en `cdad_packet.py`:2094-2102; `temporary_roots: []` en :1100; `OBSERVATION_KEYS` :2371 y `_load_observation_document` :2410; `SCOPE_CLASSES` :67, `_validate_scope` :694, escritura del test-writer :728-729, `_scope_contains` :739; `prepare` bloqueado :4336-4338 y rechazo que nombra `receive` :5207-5213; `disposition: pass` :5584-5589; `ACTIVE_PACKET_STATUSES` :115; `DISPOSITION_RESOLUTIONS` :4680; `_entry_selection`/:5828, `_next_route`/:5847, `status_view`/:5886; `install_user_config` :1191-1201 con `write_delegation_template` :1151-1166; `Makefile`:1-24 (`staging`/`agents`/`validate`); `orchestrator.md`:22-57 (intake), :24 (condición stale), :104-108 (contexto); `runtime-adoption.md`:21/:37; `005-012 spec.md`:243 y :587 (INV-9) y `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830/`:835`.
- **Acoplamientos verificados por lectura del código (no de memoria):** los tres tests de dos registros usan el mismo patrón `stem != out["attempt"]` + `assertEqual(len(worker_records), 1)` (`test_005_010_reviewfix.py`:495-500, `test_005_010_t1_durable_signal.py`:439-449, `test_005_010_t4_integration.py`:483-491) y dos de ellos asertan además `interface_record.get("model_reported") is None` (`t1_durable_signal`:534-538, `t4_integration`:553-557); `worker_records_with_marker` de `tests/test_006_001_t1_selection.py`:399-415 filtra por marcador de procedencia, no por la ausencia del registro de la interfaz, así que **no** rompe (sólo cambia la premisa de su docstring).
- **Archivos modificados:** ninguno (write_scope vacío; rol read-only cumplido). Los borradores no se materializan desde acá: los materializa el orquestador (ADR-003).
- **Commit:** ninguno (no corresponde a este rol; el orquestador commitea la corrección tras la re-review focal y la aprobación de la autoridad vigente).