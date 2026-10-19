# 006-005-native-path-parity — SPEC (etapa 2, revisión draft-002)

Estado: **BORRADOR no aprobado.** No habilita RED, ni construcción, ni aprobación.
Contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §11 (enmienda 004) con el principio de §12; el recorrido es §13 (enmienda 006): la review independiente de spec y plan **precede** al RED.
Ejecución: `exec-006-005-native-path-parity-001`. Insumos: `discovery.md` (etapa 1), `architect-draft-001.md`, `docs/epics/epic-006-opencode-concurrency/execution.md` §«Uso real del adaptador por el orquestador» (**D-ADP-1..D-ADP-4** y §«Decisiones del owner sobre el despacho», 2026-10-18).
Base medida: HEAD `9d3b2ea`. draft-001 midió `1e508ec` y el discovery `af0e0b5`: los números de línea son del HEAD medido y pueden correrse; por eso cada cita nombra además el símbolo.

Anonimización: rutas del repositorio, relativas; sin rutas del host, endpoints, ids de sesión, credenciales ni nombres de otros proyectos. El «proyecto consumidor» se nombra así.

## 0. Δ respecto de draft-001 (lo que cambia y por qué)

1. **Entrada externa y configuración del owner** (decisiones 1-2 de `execution.md`:249-250) entran a la feature: una sola entrada `cdad_dispatch.py --packet <id> [--runtime X]`, y la configuración de ejecución por runtime pasa a la config de usuario de CDAD (hoy un exec-config por argumento), con migración y tratamiento del heredado declarados (§2.1, §2.6, D-9…D-11).
2. **D-ADP-1** (`execution.md`:242): la credencial de `mode: server` la resuelve e inyecta **el módulo de runtime**, sólo en el entorno del proceso cliente (§2.5, D-12, PD-11).
3. **D-ADP-4** (`execution.md`:245, :251): el agente viaja en el paquete; `prepare` lo resuelve (rol + `stack`) y lo escribe en `REQUEST.json`; la llave «agente» de la correlación compara contra ese campo (§2.7, D-13, PD-7, PD-14).
4. **D-ADP-3** (`execution.md`:244): partes esperadas declaradas por el paquete → **deuda declarada**, con el criterio de §12 (§8 item 3).
5. **Corrección de D-2 de draft-001.** draft-001 proponía un módulo nuevo por runtime (`cdad_runtime_<id>.py`) **además** del adaptador por destino. Serían dos módulos por runtime para el mismo trabajo: duplicación que puede divergir (§12). El contrato por runtime **ya existe y ya sabe lanzar, esperar y recoger**: `cdad_delegate_<id>.py` (ADR-023; `_invoke_destination`:381, `_await_durable_outcome`:680, `_store_state`:600). La integración **se extiende ahí** (§2.2, D-2).
6. **Quién registra el intento (PD-1).** D-ADP-2 pide «un solo registro por despacho, escrito por una sola capa, con la observación que el módulo de runtime ya produce». Entonces: en la vía externa registra **el módulo** (ya lo hace, con `model_reported` correcto desde `session_v2.model`, `_model_reported_from_row`:259) y la **interfaz común deja de registrar** (`cdad_delegate.py` `_observation`:288 + `_register_dispatch`:311 + su invocación :399, hoy con `model_reported: null`); en la vía nativa registra el **núcleo**. `model_reported` sale en ambas vías de la observación del módulo (PD-1, PD-14).
7. **El instante del `begin` no es verificable en el repo** (V-10): la llave «momento» se mide contra un instante **declarado** por quien despacha (`--since`), no contra un timestamp que ninguna pieza registre.
8. **El runtime del proyecto no está declarado en ningún lugar verificable para un contexto v2** (V-9): la resolución «flag → configuración del proyecto → error claro» del owner se implementa con lo que el repo acredita y **falla cerrado** donde no hay declaración.
9. `capabilities` de draft-001 (`native_transport`) se renombra a claves con significado declarado (`native_observation`, `external_transport`, `session_correlation`): el transporte nativo no lo hace el módulo, lo hace la herramienta del runtime (§2.2).

## 1. Descripción funcional

La delegación **nativa** («herramienta del runtime», p. ej. `task` + `subagent_type: cdad-<rol>`) ejecuta el encargo pero **no traslada la preparación que el adaptador externo sí hace**: nadie registra el intento I8 —sin eso `receive` rechaza (`cdad_result.py`:578-581 «the active packet is not dispatched»)—; ningún encargo puede conceder un temporal al test-writer —el validador de scopes sólo admite `{tests, colocated-tests}` para escritura, `cdad_packet.py`:727-729—; un intento que no vuelve no tiene camino mecánico a `failed` (la disposición registra la decisión y su efecto sobre el paquete es `pass`, `cdad_packet.py`:5584-5589). A esas tres brechas de §11 se suman, ya medidas en uso real (`execution.md`:242-245), la **entrada del orquestador sin config declarada** (el despacho externo se ejecuta con un exec-config local y un rodeo de entorno) y el **agente por stack** que nunca se resuelve.

La feature cierra las seis brechas con **una entrada operativa**, **una capa de configuración** y **una integración por runtime que ya existe**:

1. **Núcleo `skills/cdad-cycle/scripts/cdad_dispatch.py`** (runtime-neutral; capa `scripts` del principio de capas de §8 de §11/§12): la **entrada única del orquestador** en sus dos vías —`dispatch` (externa) y `record` (nativa)—, más `capabilities`. No reimplementa validaciones: importa `cdad_packet` (precedente: `cdad_result.py` lo importa) y los ayudantes de la interfaz común; escribe el ledger **sólo** por el comando que ya existe (`prepare --record-dispatch`, `cdad_packet.py`:2501) y **no agranda** `cdad_packet.py`.
2. **Configuración de ejecución por runtime** en la config de usuario de CDAD, junto a `delegation.json` (`cdad_delegate.py` `cdad_config_dir`:100): una sección por runtime con binario y versión, modo y URL, la superficie durable y la espera. Es la **única fuente** para la vía externa; el exec-config deja de ser dato del usuario (§2.6).
3. **Integración del runtime = el módulo por destino que ya existe** (`cdad_delegate_<id>.py`, ADR-023/ADR-032), extendido con: la credencial de `mode: server` (§2.5), el agente del paquete (§2.7), y una superficie de **observación** y **capacidades** para la vía nativa (§2.2). Fuera de su versión declarada o con esquema de store desconocido, falla cerrado.
4. **Registro del intento: uno por despacho.** La interfaz común deja de registrar; el módulo registra el suyo en la vía externa y el núcleo registra en la nativa (PD-1).
5. **Temporales del test-writer** como clase de scope `temporary` del vocabulario observable que ya existe (`classify_path_observable`, `cdad_packet.py`:303-322 nombra `"temporary"` desde `temporary_roots`), validada contra `temporary_roots` de la política y verificada con `git check-ignore` en `prepare`.
6. **Una sola entrada operativa del orquestador**, consumiendo el `entry`/`next` que el CLI ya calcula (`_entry_selection`:5828, `_next_route`:5847, `status_view`:5886) en vez de re-derivar la situación con cuatro entradas solapadas (`sources/roles/orchestrator.md`:22-57), y con la regla de transporte declarada: **mismo runtime que el orquestador ⇒ herramienta nativa + `record`; otro runtime ⇒ despacho externo** (`execution.md`:253).
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
- **`record` (vía nativa).** Construye la observación con las claves cerradas I8 (`OBSERVATION_KEYS`, `cdad_packet.py`:2371; validación `_load_observation_document`, :2398-2440); prioriza el **resultado nativo byte-exacto** y, sólo si no lo hay y hay motivo, **una** lectura acotada del store vía la superficie de observación del módulo (`--observe`, §2.2); verifica la correlación (§2.3); **registra** por `prepare --record-dispatch`; y, si recibió el texto final, lo **escenifica byte-exacto** bajo `.cdad/inbox` con su `RESULT.json` (paso mecánico del protocolo de re-entry, `skills/cdad-cycle/references/re-entry.md` §«Orchestrator materialization protocol»). **No** ejecuta `receive`: el recibo es del protocolo de re-entry.
- **Convivencia sin duplicar lógica.** `record` es el **cuerpo único** de observación + registro + escenificación; `dispatch` no reimplementa nada de eso — delega en el módulo, que registra con la observación que él mismo produce (PD-1). Los dos verbos comparten el mismo constructor de observación, el mismo vocabulario y la misma ruta de escritura del ledger (el comando existente); ninguno de los dos valida por su cuenta lo que `cdad_packet` ya valida.
- Sobre de salida de ambos verbos: exactamente las claves de `OUTPUT_KEYS` (`cdad_delegate.py`:52: `attempt`, `session`, `termination`, `delivery_ref`, `diagnosis`) y `termination` del vocabulario cerrado `TERMINATION_VOCABULARY` (:49). No se inventa un segundo idioma.
- `--json` es la forma estable legible por máquina; el texto libre sólo se suma cuando el dueño lo pida.

### 2.2 Contrato de la integración (el módulo por runtime; se extiende, no se duplica)

El módulo es `cdad_delegate_<id>.py`, resuelto por la convención de módulo que ya existe (`cdad_delegate.py` `_adapter_path`:79, ADR-023). Conserva su contrato actual (stdin byte-idéntico, envelope, preflight, espera acotada, terminación del grupo propio) y **suma**:

- **`--capabilities`**: documento `{native_observation, external_transport, session_correlation, version, reason}`. Significados declarados: `native_observation` = puede correlacionar un intento despachado por la herramienta nativa del runtime; `external_transport` = puede lanzar/esperar/recoger un proceso; `session_correlation` = el store expone las columnas de correlación (§2.3) en la versión observada; `version` = la versión **observada** del binario o `unknown` (nunca supuesta); `reason` = por qué una capacidad es falsa, **nombrando lo que falta**.
- **`--observe`**: una **única** lectura acotada del store que devuelve la observación del intento correlacionado o `null` (§2.3). Acceso sólo lectura (`mode=ro`, nunca `immutable`, nunca escritura — igual que `cdad_delegate_opencode.py`:619-621), sin polling.
- **`attempt` declarado** en su sobre (el intento que registró): quien lo invoca lo **relaya**, nunca lo reemplaza.

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

- Las claves son **las que el módulo ya lee** (`binary`, `binary_version`, `mode`, `server`, `service`, `auto`, `sessions_db`, `wait`, `cdad_delegate_opencode.py`:1857-1900): se mueven de lugar, no se renombran (sin abstracción nueva).
- **`model` no vive aquí**: el modelo de la delegación externa es `delegation.json` por destino y rol (**ADR-033** D3). Una clave `model` en la sección se **rechaza nombrando `delegation.json`** (que el modelo se elija en un solo lugar se verifica por ausencia, ADR-033 «Reasons» 2).
- **La credencial tampoco se duplica aquí**: su ruta sigue donde ADR-033 punto 6 la puso (`delegation.json.credential_env_file`, default el hermano `opencode-server.env`). Se declara como corrección del fraseo «credencial si la usa» de `execution.md`:250 (evidencia: `cdad_delegate.py` `delegation_credential_env_file`:131).
- **Derivación interna.** El núcleo **deriva** la configuración interna del módulo desde la sección y la entrega como archivo transitorio bajo el espacio de coordinación ya git-ignorado (`.cdad/`; verificado en este repo: `git check-ignore -v .cdad` → `.gitignore:11:.cdad/`), eliminándolo al terminar. Nunca contiene modelo ni valor de credencial.
- **Migración.** `install.sh` crea la plantilla de `runtimes.json` **sólo si no existe**, sin registrarla en el manifiesto y sin pisarla nunca: la misma disciplina de dato del usuario que ya aplica a `delegation.json` y `opencode-server.env.example` (`install.sh`:1151-1201, ADR-033 punto 5).
- **Exec-config heredado: error accionable, no compatibilidad silenciosa.** Un exec-config existente **no se lee**: la entrada falla cerrado nombrando (i) el archivo y la sección nuevos, (ii) la correspondencia clave por clave y (iii) la clave `model` que 006-003 D3 ya ignoraba. Razón declarada: admitirlo mantendría dos fuentes que pueden divergir (el propio criterio §12) y su efecto silencioso sería cambiar el binario, el store o el modo de un encargo ya preparado. La *interfaz* conserva su `--exec-config` como mecanismo **interno** (es el contrato que el módulo y sus tests usan); ningún texto del producto la nombra ya como camino del orquestador (U4) y queda como deuda declarada con su disparador (§8 item 4).

### 2.7 El agente viaja en el paquete (D-ADP-4)

`prepare` resuelve el agente con **rol + `stack` del estado** (`docs/.cdad-state.json.stack`; hoy **ningún** código del repo lo consume: grep de `stack` en `skills/cdad-cycle/scripts/` sólo devuelve `_derived_role`:2610-2621 y textos ajenos) y lo escribe en `REQUEST.json` como campo **`agent`** (p. ej. `cdad-architect-odoo`). El módulo lo traduce a su invocación (`--agent <agent>`) y **falla cerrado antes de despachar** si el agente no está publicado (reusa `_check_derived_agent_published`:302, hoy aplicado a `cdad-<rol>`, `_entry_agent_name`:298). Sin override de agente en `prepare` mientras no haya un caso real. Compatibilidad: un paquete sin `agent` sigue siendo despachable —el módulo usa `cdad-<rol>` y **declara la ausencia**— y la llave «agente» de la correlación queda `unknown` (§2.3). En la vía nativa el orquestador elige `subagent_type` al despachar: la divergencia no se previene, se **detecta** en la correlación de `record`.

## 3. Postcondiciones (PD-n, observables y testeables)

Convención: «oráculo» = el artefacto o comando que decide el pass/fail. «Módulo» = `cdad_delegate_<id>.py` del runtime.

| # | Postcondición | Oráculo |
|---|---|---|
| **PD-1** | **Un solo intento I8 por despacho.** Vía externa: lo escribe el módulo (uno). Vía nativa: lo escribe `record` (uno). La interfaz común **no registra** (hoy sí: `cdad_delegate.py`:288/:311/:399) y el módulo tampoco registra dos veces. | conteo de `.cdad/executions/<exec>/dispatches/*.json` == 1 por intento en ambas vías; control negativo: el sobre del módulo y el registro coinciden en `attempt`; inspección de `cdad_delegate.py` sin `--record-dispatch` |
| **PD-2** | El núcleo **no es un segundo escritor**: no escribe `docs/.cdad-state.json`, no escribe el store, no escribe el ledger salvo por el comando existente; escribe sólo bajo `.cdad/`. | el estado sólo cambia por la transacción del comando; bytes del store idénticos (fixture); árbol de cambios acotado a `.cdad/` |
| **PD-3** | Con `--native-result`, la parte escenificada es **byte-exacta**: `sha256(parte) == sha256(entrada)`, sin retecleo, resumen ni regeneración; el descriptor apunta a ella y el recibo queda `semantic_status: pending`. | `sha256sum` de ambos; campo del recibo |
| **PD-4** | **Sin texto final o artefacto no hay entrega**: no se escenifica nada, no se escribe `RESULT.json`, no se invoca `receive`; el intento queda registrado y el sobre declara el hecho. (En la vía externa el módulo ya sólo persiste en `completed` con texto: `cdad_delegate_opencode.py`:2280-2300.) | `.cdad/inbox` sin cambios; ausencia de descriptor; existencia del intento |
| **PD-5** | Una sesión se acepta como del intento sólo si las cuatro llaves (§2.3) coinciden. Si falta o no coincide alguna: **no hay entrega por esa vía**, la observación lleva `session: null` y el diagnóstico **nombra la llave** fallida. Sin `agent` en el paquete ⇒ llave `unknown`, nunca `cdad-<rol>`. | fixtures con padre/agente/directorio/instante incorrectos y con paquete sin `agent`; el diagnóstico contiene el nombre de la llave |
| **PD-6** | **Garantía menor declarada:** con resultado nativo byte-exacto pero identidad no verificable (V-1), la entrega se persiste con `session: null` y `provenance` que declara que no se pudo verificar la identidad; nunca se inventa un valor de sesión. | observación con `session: null`; `provenance` sólo anota campos observados (`cdad_packet.py`:2398-2440) |
| **PD-7** | `prepare` escribe `agent` = rol + `stack` del estado (p. ej. `cdad-architect-odoo`); sin `stack`, `cdad-<rol>`. Un paquete publicado antes de la feature (sin `agent`) sigue siendo despachable. | `REQUEST.json` del paquete en los tres casos; `prepare` rc=0 en los tres |
| **PD-8** | **Resolución del runtime:** `--runtime X`; si no viene, el runtime declarado por el proyecto; si no hay ninguno, **error accionable** que nombra el flag y los lugares donde se declara; un valor declarado que no corresponde a un módulo de runtime disponible ⇒ rc≠0 **nombrando el valor**. | tres casos (flag / declaración / ninguno) + un valor inválido |
| **PD-9** | **Una sola fuente de configuración para la vía externa:** la sección del runtime. Sin sección ⇒ falla cerrado nombrando el archivo y las claves; la configuración derivada **no contiene `model`** (se rechaza nombrando `delegation.json`) **ni valor de credencial**; un exec-config heredado ⇒ el error accionable de §2.6 con la correspondencia de claves. | documento derivado inspeccionado clave por clave; tres fixtures (sin sección, con `model`, con exec-config heredado) |
| **PD-10** | `capabilities` responde las cinco claves de §2.2; con esquema de store desconocido ⇒ `session_correlation: false` **con `reason` que nombra lo que falta**; `version` es la observada o `unknown`, nunca supuesta; runtime id desconocido ⇒ rc≠0. | fixture de esquema; el `reason` nombra el elemento faltante |
| **PD-11** | **Credencial (D-ADP-1):** en `mode: server` la credencial resuelta (entorno → archivo 0600) se inyecta **sólo** en el entorno del proceso cliente; nunca en `argv`, stdout/stderr, el registro I8, el recibo ni ningún artefacto versionado; en `standalone`/`service` **no se inyecta nada**. El rodeo de entorno del despachador deja de ser necesario. | **binario falso que exige la variable** (sin ella falla; con ella completa) y eco de si la vio; centinela buscado en `argv`, salidas y registros; caso negativo en `standalone` |
| **PD-12** | La integración exige las columnas de correlación y **falla cerrado** nombrando las ausentes; nunca degrada a `timeout` ni a «ausente». | store descartable sin una columna → error específico |
| **PD-13** | **Sin bucle:** la lectura del store es única por invocación, `mode=ro`, con timeout acotado, y el intento declara `store_reads=<n>` con `n` ≤ el techo declarado; ninguna constante de intervalo ni bucle consulta el store. | conteo instrumentado del acceso; `store_reads` en el intento; ausencia de intervalo de polling en el módulo |
| **PD-14** | El agente del paquete llega a la invocación (`--agent <REQUEST.json.agent>`); si no está publicado, el módulo **falla cerrado antes de despachar** nombrando el agente; sin el campo, usa `cdad-<rol>` y declara la ausencia. `model_reported` del intento sale de la observación del módulo en las dos vías. | `argv` observado por el binario falso; caso de agente no publicado; ausencia de `agent` |
| **PD-15** | Un paquete puede declarar `{"class":"temporary","root":<selector>}`; se acepta **sólo si** el selector cae dentro de un `temporary_roots` de `docs/cdad-policy.json`. Con `temporary_roots: []` el encargo **se rechaza** nombrando el archivo y el campo. | `prepare` rc≠0 con el nombre del archivo; caso positivo rc=0 |
| **PD-16** | Con temporal declarado, `prepare` verifica con `git check-ignore` (read-only) que el selector está ignorado; si no lo está **o** el proyecto no es un árbol Git ⇒ falla cerrado nombrando las dos salidas legítimas (declararlo en `.gitignore`, o no pedir el temporal). | `prepare` rc≠0 + mensaje; caso positivo con raíz ignorada |
| **PD-17** | Con el temporal declarado e ignorado, un test real en `tests/` **más** una sonda dentro del temporal se reciben con `scope_validation: passed` y recibo `pending`; un cambio fuera de todo scope declarado sigue rechazándose. | campo `scope_validation` del recibo |
| **PD-18** | El temporal **no es producto**: sigue vigente el rechazo de `_validate_temporary_roots` (`cdad_packet.py`:414-430) cuando una raíz temporal se solapa con rutas de producto. | caso negativo de política |
| **PD-19** | **Camino mecánico a `failed`:** `register-transition --transition disposition --packet <activo> --resolution abandoned\|superseded`, **sin** recibo durable ⇒ `active_packet.status: failed` (terminal). No fabrica resultado, no fabrica recibo, no aprueba; `validate-state` (`cdad_packet.py`:546) VALID y `prepare` desbloqueado (hoy el bloqueo existe en :4337-4338). Si **hay** recibo durable ⇒ se rechaza nombrando `receive` (rechazo ya existente, :5207-5213). | estado tras el comando; `validate-state`; `prepare` antes rc≠0 / después rc=0 |
| **PD-20** | **Entrada única:** el mandato conduce la decisión desde `status.entry`/`next` con el orden de cinco filas de §5 D-6, sin dos filas con la misma condición, y con la regla de transporte declarada (mismo runtime ⇒ nativa + `record`; otro ⇒ la entrada externa); **no existe** la condición stale de `.cdad/execution.json` (`sources/roles/orchestrator.md`:24) y el generado lleva el mismo texto. | test de texto sobre la fuente y sobre el generado recomputado (`make staging`); `status` del CLI como evidencia del insumo |
| **PD-21** | **Cierre:** la review independiente de spec/plan precede al RED (enmienda 006, procedimiento vigente `plan-review` sobre `draft-plan`: `cdad_packet.py`:52-53, :815-829, `cdad_result.py`:700); `make validate` y la suite completa **una vez** al cierre (política declarada; corre quien cierra). | salidas de los comandos; el dictamen en la carpeta de la spec |
| **PD-22** | **Recorrido de aceptación** (U6): en un proyecto **descartable** —nunca HOME, nunca el proyecto activo— un layout anidado, el coordinador iniciado desde otra carpeta, agente global y configuración de proyecto declarados con garantía menor, un auxiliar temporal, **un test real escrito y recibido**, **una entrega por la vía externa con la entrada nueva**, **una entrega por la vía nativa** (`task` + `record`) y **un intento interrumpido llevado a `failed` por comando**. Se declaran versión y configuración observadas y **no se generaliza** el resultado. | artefactos del recorrido: intento I8, recibo `pending`, estado `failed`, `scope_validation: passed`, sobre de `dispatch` con el `attempt` del módulo |

**MAPEO AC → PD** (los AC del epic §4/§11 como origen, no como autoridad):

| AC (epic §4 / §11) | PD |
|---|---|
| AC-1 (selección comprensible; sin secretos; config incompatible ⇒ diagnóstico) | PD-8, PD-9, PD-10, PD-11 |
| AC-2 (mismo encargo y autoridad; identidad y entrega durable; una entrega no aprueba) | PD-1, PD-2, PD-3, PD-5, PD-7 |
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
- **INV-4.** Fuera de su versión declarada o con esquema desconocido, la integración responde **cerrado/`unknown`** con motivo; sin fallback silencioso.
- **INV-5.** **Un solo escritor por recurso:** del store (`mode=ro`, nunca `immutable`, nunca escritura), del estado y del ledger (sólo por los comandos existentes). El ledger recibe **un** intento por despacho (PD-1).
- **INV-6.** **Ninguna lectura del store en bucle**: sin polling, con techo de lecturas por invocación declarado y contado.
- **INV-7.** La política, `delegation.json` y `runtimes.json` son **datos del dueño**: ningún rol los edita; el instalador sólo crea plantillas cuando no existen; el default de temporal es **propuesta**.
- **INV-8.** La observación I8 conserva su **esquema cerrado** (`OBSERVATION_KEYS`); el `provenance` sólo anota campos observados y nunca transporta resultados, gates ni aprobaciones; en salidas versionadas no hay secretos, rutas del host ni ids de sesión.
- **INV-9.** CDAD **no elige modelo** (regla I8 vigente, ADR-033 D2, sin cambios).
- **INV-10.** El núcleo **no toca el producto**: escribe sólo bajo `.cdad/`.
- **INV-11.** **La credencial no sale del entorno del proceso cliente**: nunca en `argv`, logs, recibos, registros I8 ni artefactos versionados; y sólo en `mode: server`.
- **INV-12.** **Una fuente por camino:** el modelo de la delegación externa sólo en `delegation.json` (ADR-033 D3); la configuración de ejecución sólo en la sección del runtime; la credencial sólo donde ADR-033 punto 6 la puso. Ninguna clave se duplica entre archivos.
- **INV-13.** **La identidad del agente se detecta, no se supone:** la correlación compara contra el agente declarado en el paquete; sin ese campo es `unknown`; nunca hay degradación a un agente genérico no-Cdad (se conserva el rechazo ya vigente, `_check_derived_agent_published`:302).

## 5. Decisiones (D-n) — adoptadas, con el criterio de §12

- **D-1 — Dónde vive el núcleo.** Módulo propio `cdad_dispatch.py` que **importa** `cdad_packet` y los ayudantes de la interfaz (read-only) y escribe el ledger por el comando existente. *General/específico:* el núcleo es general (entrada y transporte-neutral); **rechazadas** agrandar `cdad_packet.py` (§11 lo prohíbe) y meterlo en `cdad_result.py` (recepción es otra responsabilidad).
- **D-2 — Forma de la integración por runtime (corrige draft-001).** La integración **es** el módulo por destino que ya existe (`cdad_delegate_<id>.py`, ADR-023), extendido con credencial, agente, capacidades y observación. *Rechazadas:* (a) un segundo módulo nuevo por runtime (`cdad_runtime_<id>.py`, propuesta de draft-001) — dos módulos para el mismo trabajo, duplicación que puede divergir y dos lugares donde el store se lee; (b) un módulo con dict de runtimes — mezcla runtimes y contradice ADR-032; (c) clase base/plugin — abstracción sin segundo consumidor real todavía.
- **D-3 — Correlación.** Padre + agente + proyecto + momento (`time_created > --since`), con `null`/`unknown` cuando no se puede evaluar. *Rechazadas:* confiar sólo en el id del transporte (más débil y hoy `VERIFY` V-1) y «la hija más reciente del directorio» (ambigua bajo concurrencia: es el tema del epic). El **momento** se mide contra un instante **declarado** porque el repo no registra el instante del `begin` (V-10).
- **D-4 — Camino a `failed`.** El efecto del `disposition` mueve el paquete activo citado a `failed` (terminal, sin aprobar y sin recibo). *Rechazadas:* verbo nuevo `fail-packet` (admisible, más superficie), `--replace-packet` sobre `dispatched` (lo prohíbe PD-10, :2082-2083) y `reconcile` que escriba (es read-only por contrato). **Conflicto declarado:** `docs/specs/005-012-transition-registration/spec.md`:243 y su INV-9 (`:587`) declaran que el `disposition` **no** cambia `active_packet`; PD-19 **enmienda** esa consecuencia y requiere aprobación explícita del dueño; el test acoplado `tests/test_005_012_t3_closure_dispatch_resolution.py`:745-830 se cambia **en RED declarando el reemplazo** (A-1).
- **D-5 — Temporal.** Clase `temporary` en el vocabulario de scopes, validada contra `temporary_roots` (autoridad del dueño), default **propuesto** `.cdad/tmp`, verificación `git check-ignore`. *Rechazadas:* declararla clase `tests` (miente sobre la clase), temporal fuera del proyecto (es el incidente de la espera larga) y ruta libre declarada por el paquete (PD-9 de 004-002). **Ubicación por defecto — justificación y condiciones:** (C1) es **propuesta**: la emite `propose_policy` (`cdad_packet.py`:1088, hoy `temporary_roots: []` en :1101) y la acepta el dueño; en este repo la política vigente declara `[]`, así que **hoy** pedir un temporal falla cerrado — es lo correcto. (C2) `.cdad/tmp` es subdirectorio disjunto de los subárboles que el CLI escribe (`inbox/`, `packets/`, `executions/`, `runtime/`): nunca el `.cdad/` raíz. (C3) está ignorado de verdad: verificado en este repo, `git check-ignore -v .cdad/tmp` → `.gitignore:11:.cdad/`. (C4) si el proyecto no lo ignora, `prepare` falla cerrado nombrando las dos salidas (PD-16). (C5) el validador de política ya garantiza que una raíz temporal no se solape con producto (:414-430; PD-18). *Alternativa no elegida:* una raíz de primer nivel (p. ej. `.tmp/`), no ignorada por defecto.
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
- **D-9 — Una entrada para el orquestador.** `cdad_dispatch.py --packet <id> [--runtime X]` (verbo `dispatch` por defecto), sin exec-config, modelo, credencial ni modo: el orquestador no carga entornos. *Rechazadas:* dos entradas (una por vía) y que el orquestador siga pasando la configuración.
- **D-10 — Configuración por runtime en la config de usuario.** `runtimes.json`, una sección por runtime, junto a `delegation.json`, con las claves que el módulo ya lee. *Rechazadas:* (a) mantener el exec-config como dato del usuario (es el rodeo que el owner retira, `execution.md`:250); (b) una variable de entorno por clave (no es portable ni verificable); (c) **duplicar el modelo o la credencial en la sección** — el modelo es de `delegation.json` (ADR-033 D3) y la credencial también (ADR-033 punto 6); la sección se valida por ausencia de `model` (PD-9).
- **D-11 — Migración del exec-config heredado: error accionable.** No se lee; el diagnóstico nombra archivo, sección, correspondencia de claves y la clave `model` ya ignorada por 006-003. *Rechazada:* compatibilidad con aviso, porque un exec-config heredado cambia en silencio binario, store o modo de un encargo ya preparado y deja dos fuentes que pueden divergir. La interfaz conserva su `--exec-config` **interno** (deuda declarada con disparador, §8 item 4).
- **D-12 — La credencial es del módulo OpenCode.** Precedencia vigente (entorno → archivo 0600) e inyección sólo en el entorno del proceso cliente, sólo en `mode: server`; ningún agente la ve. *Rechazadas:* un contrato genérico de entorno del núcleo (mezclaría runtimes y expondría la credencial a la capa neutral) y exportarla en el proceso que despacha (el rodeo medido, `execution.md`:242).
- **D-13 — El agente viaja en el paquete.** `prepare` resuelve rol + `stack` y escribe `agent`; el módulo traduce y falla cerrado si no está publicado; la correlación compara contra ese campo; sin override de agente mientras no haya caso real; compatibilidad con paquetes sin el campo. *Rechazadas:* que el módulo derive el stack por su cuenta (segunda resolución, puede divergir de `prepare`) y que el orquestador elija el agente en la vía externa (mete una decisión de dominio en el despacho).
- **D-14 — Quién registra.** El módulo en la vía externa, el núcleo en la nativa; la interfaz nunca. *Rechazadas:* que el núcleo registre también en la vía externa (tendría que recibir la observación interna del módulo y habría dos capas con el mismo dato) y que el núcleo no registre en la vía nativa (dejaría la vía nativa sin I8: la brecha que la feature cierra).
- **D-15 — D-ADP-3 (partes esperadas) va a deuda.** Ver §8 item 3, con el criterio y el disparador declarados.

## 6. Desconocidos (V-n) y su resolución

- **V-1 (riesgo principal) — cómo obtiene el padre la sesión hija por la vía nativa.** Resolución: **sonda real acotada** (un despacho nativo mínimo, declarado y con el resultado registrado) **antes o durante U2**; el hallazgo se declara en la integración (`capabilities`/`--observe`). Si la llave «padre» no es evaluable: (a) con resultado nativo byte-exacto hay entrega con **garantía menor declarada** (`session: null` + `provenance`, PD-6); (b) por la vía del store no hay entrega y la observación es `unknown` (PD-5). Nunca una entrega inventada.
- **V-2 — `time_idle`/`idle_outcome` en 0/null:** el fin de corrida **no** se exige en la vía nativa; la entrega depende del texto final del transporte.
- **V-3 — semántica de `external_directory` por versión:** la integración declara versión y falla cerrado fuera de ella (PD-10); la prevención es D-5.
- **V-4 — título «## Delegation (adapter)» con contenido nativo** (`scripts/cdad-generate.py`:747): se corrige en U4.
- **V-5 — si el `task` nativo bloquea al padre y la semántica exacta del permiso:** sonda declarada; si queda desconocido, la espera es post-hoc y se declara (PD-13).
- **V-6 — condición stale de `.cdad/execution.json` en el mandato** (`sources/roles/orchestrator.md`:24; el path v1 es `cdad_packet.py` `FLAT_EXECUTION_RELPATH`:88 y los contextos v2 viven en `.cdad/executions/<id>/execution.json`): se corrige en U4.
- **V-7 — columnas reales de correlación en la versión instalada:** sonda antes del RED de U2; la forma citada proviene de 005-002 y el módulo hoy exige un subconjunto menor (`SESSION_V2_COLUMNS`, `cdad_delegate_opencode.py`:182).
- **V-8 — la propuesta de temporal cambia bytes de `propose_policy`:** se buscaron tests que fijen ese valor y **no se encontró ninguno** (los hallados son fixtures: `tests/test_004_002_t1_policy.py`:204 no fija el valor; `tests/test_003_003_t2_preflight.py`:105 y `tests/test_004_002_t1_reviewfix.py`:125; `tests/test_004_002_t6_landing.py`:374 sólo parsea el JSON). Si el RED encuentra uno, se cambia **en RED declarando el reemplazo** (A-1).
- **V-9 — el runtime del proyecto no está declarado en ningún lugar verificable para un contexto v2.** Verificado: el contexto v2 **no** lleva `runtime` (`V2_EXECUTION_KEYS`, `cdad_packet.py`:73-80; comentario «runtime, model and session are dispatch observations, never part of the identity»), el estado no tiene clave de runtime (claves de `docs/.cdad-state.json`) y el registro de activación sólo nombra `adopted_root` + rutas (`skills/cdad-cycle/references/runtime-adoption.md` §«Registro»). *Consecuencia declarada:* en un contexto v2, sin `--runtime` la entrada **falla cerrado** con el error accionable de PD-8 (que es la salida legítima que el owner previó: «si no hay ninguno, error claro»); en un contexto v1 plano el valor **sí** existe (`BINDING_FIELDS` con `runtime`, :25-33) pero puede no ser un id de runtime disponible (en este repo, `.cdad/execution.json` declara `"multi-runtime"`), y PD-8 exige rc≠0 nombrando el valor. *Propuesta para el dueño (no decidida aquí):* declarar el runtime en la config del proyecto; hoy no se inventa.
- **V-10 — el instante del `begin` no está registrado en ninguna pieza.** Verificado: los cuerpos de continuidad son deterministas por diseño («timestamps, so the same input in two different projects yields the same bytes», `skills/cdad-cycle/scripts/cdad_continuity.py`:36) y su esquema no tiene campo de tiempo (`attempt, authority, decisions, execution_id, goal, next_action, packet_id, record, references, schema_version, uncertainties`). *Consecuencia:* la llave «momento» usa el instante **declarado** por quien despacha (`--since`, PD-5); sin él ⇒ `unknown`; queda declarado en `provenance` que el instante es declarado, no medido.
- **V-11 — `opencode run --agent cdad-<rol>-odoo` de punta a punta (pendiente de verificar en el ciclo).** Es la decisión 6 del owner (`execution.md`:254). Sonda declarada: en un proyecto **descartable** con `stack: odoo`, un despacho externo real contra el binario instalado; se registran versión observada, la fila durable (`session_v2.agent`), el `attempt` y el recibo. Si no se puede ejecutar, la unidad queda **BLOQUEADA** con motivo y evidencia, sin sustituirla por una corrida simulada (regla de bloqueo, plan §3 U6).
- **V-12 — la paridad de las dos vías con la misma ejecución** (mismo paquete, misma entrega) sólo está medida para la vía externa (006-002/006-003); la vía nativa con `record` **nunca** se ejecutó. Sonda: el recorrido de PD-22 (U6), con el mismo escenario en las dos vías; un éxito es evidencia de ese recorrido, no prueba general.

## 7. Medición de la aceptación

- Se mide lo observado (versión, configuración, intentos, lecturas del store, tiempos, terminaciones, modo solicitado/efectivo) y se registra; **desconocido no es cero**.
- **No** se fijan reducciones porcentuales de locks, tokens ni tiempo.
- Un éxito del recorrido de U6 es evidencia **de ese recorrido**, no de que la contención esté eliminada.
- La credencial no entra en ninguna medición ni salida: se mide **si hubo credencial y su procedencia** (`environment`/`file`), nunca su valor.

## 8. Fuera de alcance

1. La **integración Claude Code**: se deja la interfaz ya preparada (§2.2); su módulo, su sección de config y su guard quedan para después (plan §11).
2. El transporte externo **más allá de que consuma el núcleo**, los filtros de Bash, los ejecutores de acciones externas y la construcción incremental.
3. **D-ADP-3 (partes esperadas declaradas por el paquete, separadas por el núcleo en las dos vías) va a deuda declarada.** Criterio (§12): el único caso medido es el informe del architect, donde la parte única `role-report` es **admisible por contrato** (`cdad_result.py` `_allowed_kinds`:681-694 la admite para architect en `discovery`/`draft`) y la materialización de `spec.md`/`plan.md` es el paso declarado del orquestador (ADR-003) — no se pierde ninguna capacidad. Generalizar exigiría un campo nuevo en el contrato del paquete, un camino de separación en el núcleo **y** tocar `_allowed_kinds`/`receive`, sin un requisito declarado que lo pida. **Disparador declarado:** cuando un consumidor necesite los digests por parte **como artefactos propios del rol** (materialización automática por parte).
4. La **retirada del `--exec-config` interno de la interfaz común** (`cdad_delegate.py`): la vía del producto ya no lo usa (D-11) y ningún texto lo nombra (U4); retirarlo del todo toca el contrato del módulo y sus tests y entra en la deuda **con disparador**: cuando no quede ningún despliegue con la interfaz como camino del orquestador.
5. La política del proyecto y `delegation.json`/`runtimes.json` (datos del dueño): esta feature sólo cambia la **propuesta** de política y crea **plantillas**.

## 9. Riesgos residuales

Contención del store (se mitiga, no se elimina aquí); deriva de esquema sin `schema_version` (detección por columnas → fallo cerrado); mapas `edit` no observados aplicados en la versión medida (por eso el temporal se declara, no se confía al mapa); V-1, que acota la garantía de identidad del recorrido nativo; V-9/V-10, que hacen que dos llaves de correlación dependan de datos **declarados** por el despachador; y la ventana entre `prepare` (que ya escribe `agent`) y los paquetes publicados antes de la feature, que quedan con la llave «agente» `unknown` (declarado, PD-7/PD-5).

