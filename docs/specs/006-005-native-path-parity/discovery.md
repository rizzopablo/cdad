He terminado el discovery. Reporte (texto final, read-only) a continuación.

---

# 006-005-native-path-parity — DISCOVERY (etapa 1)

Rol: architect · substage: discovery · ejecución `exec-006-005-native-path-parity-001` · contrato: `docs/epics/epic-006-opencode-concurrency/plan.md` §11 (enmienda 004), con el principio de §12. Evidencia: `docs/epics/epic-006-opencode-concurrency/execution.md` §«006-003: paquete despachado sin entrega» (:217-219), ADR-032, ADR-033.

Sin cambios en el repo: **archivos modificados: ninguno** (write scope vacío). **Commit: ninguno.** Comandos y salidas en §9.

No afirmo que exista spec de feature: `docs/specs/006-005-native-path-parity/` **no existe** (verificado). Este documento es el insumo del borrador de spec/plan.

**Anonimización:** el «otro proyecto activo» se nombra así; las rutas del host, el store, los ids de sesión y las configs locales del dueño no se reproducen.

---

## 0. Método y límites

- Sólo lectura sobre el repo, HEAD `af0e0b5`. `git status --porcelain` sólo muestra sin-trackear `docs/planning/` y `findings/…` de otro agente: no fueron usados como fuente.
- No leí `tests/.sensitive-patterns.local`; no toqué `~/.claude`, `~/.config`, servicios ni la base de sesiones; no ejecuté `git stash`.
- Datos del otro proyecto (a)–(f) se toman como **reportados**; cuando el repo no los puede acreditar, se marcan `VERIFY`.
- El store vivo no se consultó: la forma de `session_v2` se cita del repo (`docs/specs/005-002-session-context-meter/discovery.md`), no de una sonda nueva (ver V-7).

---

## 1. Inventario del estado actual (archivo:línea)

### 1.1 Qué hace hoy el adaptador externo

**Antes de despachar** (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py`, `delegate()` :1845-2160):

| # | Paso | Línea |
|---|---|---|
| 1 | resuelve `--project-root` absoluto y exige directorio | :1846-1850 |
| 2 | carga `--exec-config` y **bloquea antes de leer el paquete** si `wait`/`mode`/`service` son inválidos | :1866-1884 |
| 3 | lee `REQUEST.json` del paquete publicado (rol, `execution_id`) | :1891-1896 |
| 4 | lee el paquete **byte a byte** desde stdin | :1898 |
| 5 | elige `attempt_id` (`opencode-<uuid12>`) | :1901 |
| 6 | modelo **sólo** de `delegation.json` (D3 de 006-003) | :1990-1997 |
| 7 | **comprueba el agente derivado publicado** antes de despachar | :1995 → `_check_derived_agent_published` :302-325 |
| 8 | exige `binary` y `sessions_db` en la config (falla cerrado) | :2000-2010 |
| 9 | exige `wait.timeout_seconds` positivo y > reserva | :2016-2036 |
| 10 | `mode: server` sin URL válida → `blocked` | :2040-2046 |
| 11 | calcula gracia/presupuesto internos | :2049-2057 |
| 12 | **chequeo de intento previo** contra el store (vivo ⇒ `blocked`) | :2059-2085 → `_prior_attempt_check` :741 |
| 13 | preflight de servidor (`--version` + `/api/info`) o de servicio (`service status` + gate de versión) | :2095-2131 |
| 14 | elige el id de sesión | :2134 |
| 15 | invoca el destino con `--session`, `--agent cdad-<rol>`, `--auto`, y **fija `PWD` al proyecto autorizado** | :2146-2155 → `_invoke_destination` :381-460 (PWD :427) |

**Después de despachar**: espera la señal durable **después** de que el cliente sale (`_await_durable_outcome` :2170-2181), clasifica terminación (:2184-2260), verifica la **identidad del rol en la fila durable** (`session_v2.agent == cdad-<rol>`, :2276 → `_check_durable_identity` :327-346), y **persiste la entrega**: registra su propio intento I8 (:1715), escenifica el texto final en `.cadad/inbox` + descriptor y corre `receive` (:1724-1753) → recibo `semantic_status: pending`. Emite el sobre `{attempt, session, termination, delivery_ref, diagnosis}` (:1762-1771).

La interfaz común (`cdad_delegate.py`) **registra su propio intento I8** después de que el adaptador retorna, con la sesión del sobre (:390-399 → `_register_dispatch` :311-348). Es decir, hoy **hay dos registros I8 por despacho externo** (interfaz + adaptador), ambos por el mismo `prepare --record-dispatch`.

### 1.2 Qué es neutral y qué es de OpenCode

**Neutral (debería ser el núcleo):** raíz de proyecto explícita e independiente del cwd del coordinador (PD-3); paquete byte-idéntico; verificación del agente derivado publicado antes de despachar; **señal durable declarada por configuración**, nunca por `rc`; espera acotada; clasificación de terminación con vocabulario cerrado; registro del intento en el **mismo ledger I8**; persistencia de la entrega por `receive` (recibo `pending`, que no aprueba); nunca escribir el store ni `docs/.cadad-state.json`; sobre de salida.

**Específico de OpenCode:** el store SQLite y su esquema (`session_v2`/`session_message`, columnas requeridas en `SESSION_V2_COLUMNS` :182); la invocación `opencode run` y sus flags (`--server`/`--standalone`/`--session`/`--auto`) :409-460; el pinneo de `PWD` como fuente del directorio de proyecto en v2.0.26 (:420-427, evidencia histórica en `docs/evidence/runtime-delegation/opencode-delegation.md`:80-87); el preflight de servicio y el gate de versión D-11 (`_preflight_service` :1386); `/api/info` y la credencial (:1152-1289); la semántica `idle_outcome` (`succeeded/failed/interrupted`).

### 1.3 Qué hace hoy la vía nativa

- El **mecanismo** está declarado en `sources/agents/adapters/opencode.md` §`delegation` (:60-94): `task` con `subagent_type: cdad-<rol>`, pase byte-idéntico del paquete, prohibición del adaptador intra-runtime, procedencia del modelo y «recibo» (que **delega** los pasos a re-entry).
- El **mandato del orquestador** tiene cuatro entradas solapadas: ejecución preparada (`sources/roles/orchestrator.md`:22-40), legacy (:41-44), arranque en reposo (:45-51) y salida bloqueada (:52-57); más la disciplina de contexto (:104-108, con `:105` «nunca volcar el state/ledger/skill») y el wiring de re-entry (:141-148).
- **Nada** de la vía nativa nombra `begin`, `--record-dispatch` ni el chequeo del agente derivado; el wiring de re-entry sólo nombra `receive` (`sources/roles/orchestrator.md`:141-148; `skills/cdad-cycle/references/re-entry.md`:14-68 — el grep de `record-dispatch` no devuelve ninguna línea de `re-entry.md`).
- Sección compuesta como `## Delegation (adapter)` en el agente generado (`scripts/cdad-generate.py`:747; `agents/cdad-orchestrator.md`:181) aunque su contenido es el mecanismo **nativo** — es O-1, deuda declarada en ADR-032:184.

### 1.4 Comandos del CLI por paso (existen hoy)

| Paso | Comando | Evidencia |
|---|---|---|
| publicar paquete | `cdad_packet.py prepare --project-root R --role … --substage … --objective …` | `orientation.md`:66-71; parser :6037-6075 |
| write-ahead | `cdad_continuity.py begin --project-root R --execution-context E --update U` | `orientation.md`:59-61; parser `cdad_continuity.py`:1300-1309; `project-start.md`:121 |
| **registrar el intento (I8)** | `cdad_packet.py prepare --record-dispatch P --attempt-id A --input obs.json` | `orientation.md`:72; `project-execution.md`:130-141; parser :6054-6061; implementación `_record_dispatch` :2501-2583 |
| recibir entrega | `cdad_result.py receive --project-root R --execution-context E --packet PACKET.md --request REQUEST.json --descriptor RESULT.json` | `re-entry.md`:25-45; parser `cdad_result.py`:1517-1531; `receive()` :531-655 |
| validar recibo / materializar | `cdad_result.py validate-receipt` / `materialize` | `re-entry.md`:46-56; parser :1533-1548 |
| disposición del despacho | `cdad_packet.py register-transition --transition disposition --packet P --resolution abandoned\|superseded [--replaced-by Q]` | parser :6090-6138; `TRANSITION_CLASSES`/`DISPOSITION_RESOLUTIONS` :4665-4680 |
| vista compacta | `cdad_packet.py status` (`entry`+`next`) | `orientation.md`:15-35; `_entry_selection` :5828, `_next_route` :5847, `status_view` :5886 |

### 1.5 La brecha, punto por punto

- **(a) recibo imposible.** `receive` exige `active_packet.status == "dispatched"` (`cdad_result.py`:578-581). `prepare` publica `prepared` (:4483) y sólo `--record-dispatch` mueve `prepared → dispatched` (`cdad_packet.py`:2562-2571). La vía nativa nunca corre `--record-dispatch` (§1.3) ⇒ **todo despacho nativo termina en ese rechazo**. El comando existe y está documentado en `orientation.md`:72 y `cli-delegation.md`:15, pero no en la sección `delegation` ni en `re-entry.md`.
- **(b) temporal del test-writer.** El validador de scopes sólo admite, para escritura, `{"tests","colocated-tests"}` (`cdad_packet.py`:728-729). La política declara `temporary_roots` (`docs/specs/004-002-project-execution-bootstrap/spec.md`:98, PD-9: «la lista vacía no autoriza temporales»), pero `propose_policy` los emite vacíos (`cdad_packet.py`:1101) y **ningún camino del encargo puede conceder un subconjunto**. `classify_path` (:239-259) **no conoce** temporales; sólo `classify_path_observable` (:303-322) los nombra y **sólo** para `validate-policy --classify` (:6297). Escribir fuera del proyecto dispara la aprobación propia del runtime (`external_directory`), que el bloque `permission:` generado **no declara** (`agents/cdad-test-writer.md`:5-56 declara `read/edit/bash/grep/write`), y por eso la sesión hija queda esperando a alguien que no ve.
- **(c) espera indistinguible.** El `task` nativo bloquea al padre (reportado); el repo no lo puede acreditar ⇒ `VERIFY` (V-5).
- **(d) entradas solapadas.** Las cuatro entradas de `sources/roles/orchestrator.md`:22-57 **no son mutuamente excluyentes** y ninguna consume el `entry` que el CLI ya publica (`_entry_selection` :5828-5844). Además la condición de la primera entrada nombra `.cadad/execution.json` (v1, `FLAT_EXECUTION_RELPATH` :85), mientras los contextos v2 viven en `.cadad/executions/<id>/execution.json` (`EXECUTIONS_DIR` :83; `_find_prior_context` :1710-1727).
- **(e) paquete despachado sin entrega.** `register-transition --transition disposition` registra la decisión pero su efecto sobre el state es `pass`: **no toca `active_packet`** (`cdad_packet.py`:5584-5589). Nada escribe `"failed"`: el estado es válido (`VALID_PACKET_STATUSES` :44) y está previsto como terminal en el propio código (`_record_dispatch`:2565 usa `not in {"completed","failed","dispatched"}`), pero **ningún comando lo produce**. Consecuencia: `prepare` bloquea mientras el activo sea `prepared/dispatched` (:4323-4335), `--replace-packet` sólo acepta `prepared` (:2094-2103) y `reconcile` es read-only ⇒ el cambio a mano fue obligatorio. Es exactamente el caso «intento interrumpido sin entrega» de §11.
- **(f) preparación que falta en la vía nativa.** El adaptador ya hace: comprobar el agente derivado (`cdad_delegate_opencode.py`:302, llamado en :1995), fijar el directorio del proceso (:427) y leer la observación de `session_v2` (:600-659, :515-523).

---

## 2. Diseño de las tres piezas de la enmienda 004

### 2.1 Núcleo común (módulo propio; no agranda `cdad_packet.py`)

**Módulo nuevo:** `skills/cdad-cycle/scripts/cdad_dispatch.py` (runtime-neutral; capa `scripts` del principio de §8). No reimplementa validaciones: **importa** `cdad_packet` como módulo (precedente: `cdad_result.py` importa `cdad_packet`, p. ej. `validate_request` invocado desde `receive`) y **escribe en el ledger por el comando existente** `prepare --record-dispatch`, en subproceso (precedente idéntico en `cdad_delegate.py`:336-348 y `cdad_delegate_opencode.py`:1600-1616). Así el escritor del ledger sigue siendo uno.

Operaciones del núcleo (una CLI, dos verbos):

1. `cdad_dispatch.py record --project-root R --packet P --attempt-id A [--native-result FILE|-] [--since TS] [--parent SESSION] [--runtime auto|<id>]`
   - resuelve la **integración de runtime** (§2.2);
   - construye el documento de observación con las **claves cerradas** I8 (`OBSERVATION_KEYS` :2369-2375; validación :2411-2448);
   - prioridad: **resultado nativo byte-exacto** (texto final del transporte) y, sólo si no lo hay, **una lectura acotada del store** vía la integración;
   - verifica correspondencia de sesión (§2.3);
   - invoca `prepare --record-dispatch` (idempotente por bytes, :2549-2560);
   - escenifica el texto final **byte-exacto** en `.cadad/inbox` + `RESULT.json` y **deja el `receive` al orquestador** (el protocolo de re-entry sigue siendo el único dueño del recibo).
2. `cdad_dispatch.py capabilities --runtime <id> [--json]`
   - responde qué puede hacer la integración en la versión detectada (transporte nativo sí/no, transporte externo disponible, columnas de correlación presentes, versión declarada) → es lo que el orquestador consulta para decidir el transporte sin volcar el store.

Salida: un sobre JSON con el **mismo vocabulario** de terminación (`TERMINATION_VOCABULARY`, `cdad_delegate.py`:49-51) para no inventar un segundo idioma.

### 2.2 Integración del runtime (contrato con una implementación por runtime)

Contrato mínimo, resuelto por convención de módulo junto al núcleo (`cdad_runtime_<id>.py`, espejo de `cdad_delegate_<id>.py`, ADR-023/ADR-032):

```
NAME: str                          # id del runtime ("opencode")
VERIFIED_VERSIONS: tuple[str, ...]  # declarada, observada — nunca un supuesto
def capabilities() -> dict          # {"native_transport": bool, "external_adapter": bool,
                                    #  "session_correlation": bool, "reason": str}
def resolve_context(project_root) -> dict
    # {"runtime": id, "version": str|None, "agent_prefix": "cdad-",
    #  "directory": <raíz autorizada>, "session": <id|None>, "source": <declarado>}
def observe_session(project_root, *, parent, agent, since, candidate=None) -> dict|None
    # {"session","agent","directory","time_created","model_reported","idle_outcome"} | None
```

Reglas:
- **Dentro de las versiones declaradas**: lectura del store en **solo lectura** (URI `mode=ro`, nunca `immutable` ni escritura — igual que el adaptador, `cli-delegation.md`:118-120), acotada por tiempo y sin polling.
- **Fuera de ellas o esquema desconocido** (faltan columnas requeridas): falla cerrado con diagnóstico accionable que **nombra lo que falta**; los campos no observados quedan `null`/`unknown`, nunca inventados (PD-8 de 005-009, ADR-033 punto 3). Si el resultado nativo es byte-exacto, **la entrega puede persistirse** con sesión `null` y `provenance` que declare que no se pudo verificar la identidad.
- **OpenCode**: columnas de correlación `session_v2.id/agent/model/directory/parent_id/time_created` (+`time_idle`/`idle_outcome` cuando existan) — evidencia de esquema: `docs/specs/005-002-session-context-meter/discovery.md`:63-73 y :118-134 (los subagentes CDAD son sesiones separadas con `parent_id` no nulo). El adaptador hoy exige un subconjunto menor (`session_v2` = id, agent, model, time_idle, idle_outcome; `SESSION_V2_COLUMNS` :182): la integración **debe** requerir además las columnas de correlación y fallar cerrado si no están.
- **Qué responde fuera de la versión declarada**: `capabilities()["native_transport"]=false` + `reason`; el núcleo no marca identidad y el orquestador ve el motivo. No hay fallback silencioso.

### 2.3 Cómo se verifica que una sesión corresponde al intento

Cuatro llaves, todas **necesarias**; si una no es evaluable, la observación es `unknown` y **no hay entrega**:

1. **padre** — `session_v2.parent_id` == la sesión del orquestador que despachó;
2. **agente** — `session_v2.agent` == `cdad-<rol>` (barrier ya vigente del adaptador, `_check_durable_identity` :327);
3. **proyecto** — `session_v2.directory` == la raíz autorizada del paquete (no el cwd del coordinador; espejo de PD-3 y del pinneo de `PWD`);
4. **momento** — `session_v2.time_created` **posterior al instante del `begin`** del intento (`cdad_continuity.py begin`, `orientation.md`:59-61).

**Pregunta abierta V-1:** cómo obtiene el padre la sesión hija por la vía nativa (si el resultado de `task` la expone, si hay variable de entorno, o si hay que resolverla del store por `parent`). Debe confirmarse sobre la versión instalada **antes** del RED y declararse en la integración.

### 2.4 Sin texto final (intento interrumpido sin entrega)

- Si no hay texto final ni artefacto ⇒ **no hay entrega**: el intento se registra como tal (observación) y el núcleo **no** fabrica recibo (`receive` sólo se invoca con bytes escenificados).
- **Camino mecánico a `failed`:** la autoridad es la disposición que el orquestador ya registra (§1.5e, y `execution.md`:219 «con la disposición como autoridad»). Recomiendo dar al efecto de `--transition disposition` la consecuencia operativa que hoy le falta: cuando cita el **paquete activo**, sin recibo durable y con `--resolution` en el vocabulario cerrado, mover `active_packet.status` a `failed` (terminal, no aprueba nada, no fabrica resultado). `prepare` queda desbloqueado por la propia definición de `ACTIVE_PACKET_STATUSES` (:115) y `_pending_work` (:5800-5804). `validate-state` debe aceptarlo. Ver **D-4** y la alternativa.

---

## 3. Temporales del test-writer

1. **El encargo concede el subconjunto explícito.** El paquete declara en `write_scope` una entrada de clase nueva `temporary` (nombre ya existente en el vocabulario observable, `classify_path_observable`:317-321 — se reutiliza, no se inventa): `{"class":"temporary","root":"<subconjunto>"}`. El validador único de scopes (`_validate_scope` :694-735, `_scope_contains` :739-753) la acepta **sólo si** el selector cae dentro de un `temporary_roots` **declarado por la política** (`_validate_temporary_roots`:414-430, que ya rechaza solapamiento con producto).
2. **La política es la fuente.** `temporary_roots` es dato del dueño (004-002 spec :98). Lista vacía ⇒ **no autoriza nada**: el encargo falla cerrado con diagnóstico que **nombra `docs/cdad-policy.json`** y cómo declararlo (nada silencioso).
3. **Ubicación por defecto adaptable al layout.** `propose_policy` (:1088-1104) hoy emite `[]`; la propuesta pasa a incluir un temporal por defecto **fuera de los roots de producto** y dentro de la coordinación: `.cadad/tmp` (el repo ya ignora `.cadad/`, `.gitignore`:11). Es **propuesta**: la acepta el dueño, ningún rol edita la política.
4. **Git lo ignora de verdad.** En `prepare`, cuando el paquete declara un temporal, se verifica con `git check-ignore` (comando read-only) que el selector está ignorado; si no lo está, falla cerrado con diagnóstico accionable (declararlo en `.gitignore` o no pedir el temporal). Verificado en este repo: `git check-ignore -v .cadad/tmp` → `.gitignore:11:.cadad/`. Evidencia de por qué importa: el snapshot de `receive` usa `git ls-files --others --exclude-standard` (`cdad_result.py`:1301-1324) con fallback a la aproximación de `.gitignore` (:1225-1252); un temporal ignorado **nunca** aparece como cambio observado, y si apareciera, `_validate_scope` (:340-384) lo aceptaría **sólo** porque el encargo lo declaró.
5. **Efecto operativo:** con el temporal **dentro del proyecto**, la sesión hija deja de necesitar `external_directory` ⇒ el bloqueo de (b) desaparece por construcción, sin depender de que un humano apruebe.

Nota honesta: en OpenCode 2.0.16 los mapas `edit` **no se observaron aplicados** (`project-execution.md`:158-166); la respuesta operativa es declarar el temporal, no confiar en el mapa.

---

## 4. Una sola entrada operativa del orquestador

Recomiendo que el mandato **no re-derive** la situación: consume `status.entry`/`status.next` (`_entry_selection` :5828-5844; `_next_route` :5847-5867) y sigue **un único orden de decisión sin solapes**:

| # | Condición (de la vista) | Acción única |
|---|---|---|
| 1 | `entry == diagnosis` | salida bloqueada: diagnóstico accionable; **no** se prepara ni despacha nada |
| 2 | `entry == continuity-reconcile` + `packet.status == dispatched` | **reconciliar** primero (`reconcile` read-only); nunca re-despachar ni abrir un segundo worker |
| 3 | `entry == continuity-reconcile` + `packet.status == prepared` | validar → `begin` → **transportar** (§2.2) → `cdad_dispatch record` → `receive` (re-entry) |
| 4 | `entry == continuity-reconcile` + sin paquete + ejecución activa | `resume` (read-only) y continuar el trabajo activo |
| 5 | `entry == next-unit` | `open-unit` |

Las otras dos entradas del mandato dejan de competir: **legacy/handoff** pasa a ser *fallback de transporte* (runtime sin delegación nativa y sin adaptador), no una entrada del orden; **arranque en reposo** es el camino *previo* (sin ejecución) hacia `project-start.md`. Se corrige además la condición obsoleta de `.cadad/execution.json` (§1.5d) y se acota `:105`: no volcar el state/ledger/**skill completo**; cargar la metodología es la excepción declarada de los caminos legacy/reposo. Ver **D-6**.

---

## 5. Espera observable (sin sondeos frecuentes)

Qué se puede detectar **después**, y se declara:

- **Transporte nativo en error/abortado**: el resultado de `task` lo entrega al padre; es el primer observable.
- **Permiso rechazado o pendiente**: en OpenCode, la parte de mensaje `tool` trae `state.status`/`state.error` (forma verificada en 005-002 discovery §1.4:102-110) y el store tiene la tabla `permission` (005-002 discovery §1.2:57-68). Es una **lectura única bajo demanda** de la integración (`observe_session`), nunca un bucle; y sólo si el orquestador tiene motivo.
- **Prevención > detección**: declarar el temporal dentro del proyecto (§3) elimina la necesidad de aprobación externa.
- **Prohibido**: polling al store. El adaptador mantiene su espera proporcional declarada (`cli-delegation.md`:324-335); la vía nativa **no** hace polling: registra al final.
- Lo no observado se declara `unknown` (nunca 0 ni «ausente», INV-9 del adaptador).

`VERIFY` (V-5): que el `task` nativo bloquee al padre, y la semántica exacta de la aprobación `external_directory` en la versión instalada.

---

## 6. Decisiones (D-n), criterios de aceptación, riesgos, Claude Code

### Decisiones con recomendación y alternativa

- **D-1 — Dónde vive el núcleo.** *Recomendado:* módulo nuevo `cdad_dispatch.py` que importa `cdad_packet` (read-only) y escribe el ledger por el comando existente. *Alternativas:* (a) sumar verbos a `cdad_packet.py` — **rechazada** por §11 («sin agrandarlo»); (b) meterlo en `cdad_result.py` — **rechazada**: ése es recepción/recibo, otra responsabilidad (§12).
- **D-2 — Forma de la integración de runtime.** *Recomendado:* un módulo por runtime resuelto por convención, con la interfaz mínima de §2.2 y `VERIFIED_VERSIONS` declarada. *Alternativas:* (a) un módulo con un dict de runtimes — **rechazada**: mezcla runtimes y contradice el principio de capas (ADR-032); (b) clase base/plugin genérico — **rechazada** por §12: abstracción sin segundo consumidor real todavía; (c) que el orquestador lo resuelva a mano — **rechazada**: es exactamente la paridad que falta.
- **D-3 — Correlación de la sesión.** *Recomendado:* padre + agente + proyecto + `time_created > begin` (§2.3), con `null`/`unknown` cuando no se puede evaluar. *Alternativas:* (a) confiar sólo en el id que devuelva el transporte — más débil y hoy `VERIFY` (V-1); (b) «la hija más reciente del directorio» — **rechazada**: ambigua bajo concurrencia (el epic entero es sobre concurrencia).
- **D-4 — Camino mecánico a `failed`.** *Recomendado:* el efecto del `disposition` mueve el paquete activo citado a `failed` (terminal, sin aprobar, sin recibo) — reutiliza el vocabulario y la autoridad ya existentes (§1.5e). *Alternativas:* (a) verbo nuevo `fail-packet` en el núcleo — admisible, más explícito, más superficie; (b) admitir `--replace-packet` sobre un `dispatched` — **rechazada** por PD-10 (:2094-2103); (c) `reconcile` que escriba — **rechazada**: `reconcile` es read-only por contrato.
- **D-5 — Temporal del test-writer.** *Recomendado:* clase `temporary` en el vocabulario de scopes, validada contra `temporary_roots` de la política, default propuesto `.cadad/tmp`, verificación `git check-ignore` en `prepare`. *Alternativas:* (a) declarar el temporal como clase `tests` — **rechazada**: miente sobre la clase y rompe el clasificador; (b) temporal fuera del proyecto — **rechazada**: es el incidente de 53 minutos; (c) ruta libre declarada por el paquete — **rechazada** por PD-9 (004-002 :98).
- **D-6 — Entrada única.** *Recomendado:* consumir `status.entry`/`next` con la tabla de §4. *Alternativas:* (a) mantener la prosa con precedencia — **rechazada**: el solape persiste; (b) un campo nuevo de state — **rechazada**: la vista ya lo calcula (005-003 T1).
- **D-7 — Espera.** *Recomendado:* detección post-hoc + a lo sumo una lectura única bajo demanda; prevención por D-5. *Alternativa:* vigilar el store — **rechazada** por §11.5 y AC-5 del epic.
- **D-8 — Alcance del transporte externo.** *Recomendado:* el adaptador externo **consume el núcleo** y pierde su duplicación (dos I8 hoy); nada más. *Alternativa:* dejarlo como está hasta una feature siguiente — admisible, pero deja dos caminos que pueden divergir (§12: duplicación que diverge).

### Criterios de aceptación verificables

- **AC-1 (paridad antes/después).** Con la misma ejecución, un despacho **nativo** registra I8 y `receive` acepta (recibo `semantic_status: pending`). Oráculo: existe `.cadad/executions/<exec>/dispatches/<attempt>.json` y el recibo queda `pending`.
- **AC-2 (identidad).** Una sesión con otro padre, otro agente, otro directorio o creada **antes** del `begin` **no** produce entrega; diagnóstico que nombra la llave fallida.
- **AC-3 (intento interrumpido).** Sin texto final: el intento queda registrado sin entrega y el paquete llega a `failed` **por comando**, sin edición a mano; `validate-state` VALID y `prepare` desbloqueado.
- **AC-4 (temporal).** Con `temporary_roots` vacío, el encargo que pide temporal **se rechaza** con diagnóstico que nombra la política; con el temporal declarado e ignorado por Git, un test real en `tests/` **más** una sonda en el temporal se reciben con `scope_validation: passed`; con un temporal **no** ignorado, `prepare` falla cerrado.
- **AC-5 (entrada única).** El mandato compuesto conduce la decisión desde `status.entry`/`next`; la sección stale de `.cadad/execution.json` no existe; no quedan dos caminos con la misma condición.
- **AC-6 (espera).** Un permiso rechazado/pendiente se reporta en el re-entry; **no** hay ninguna ruta que consulte el store en bucle (verificable por inspección del intervalo y por el `store_reads` del intento).
- **AC-7 (escenario de la enmienda).** Layout anidado; coordinador iniciado **desde otra carpeta**; agente global y configuración de proyecto **distintos** (y declarado con garantía menor); auxiliar temporal necesario; un test real escrito y **recibido**; un intento interrumpido registrado sin entrega. Cada integración demuestra su propio recorrido; se comparten escenarios y expectativas, no la corrida (§11).
- **AC-8 (cierre).** `make validate` y la suite completa una vez al cierre (política declarada); la review independiente de spec/plan precede al RED (enmienda 006).

### Riesgos

1. **V-1 (alto):** cómo se obtiene la sesión hija por la vía nativa. Sin respuesta, la llave «padre» no es evaluable y la correlación cae a `unknown`.
2. **V-2:** `time_idle`/`idle_outcome` valen 0/null en toda la base observada (005-002 discovery V4:267) ⇒ el «fin de corrida» **no** debe exigirse en la vía nativa; la entrega depende del texto final del transporte y, opcionalmente, de la observación.
3. **V-3:** el comportamiento de `external_directory` por versión; la integración debe declarar versión y fallar cerrado fuera de ella.
4. **Store vivo:** la lectura debe ser acotada, read-only, `busy → unknown`; nunca un segundo escritor (INV-3 del adaptador).
5. **Mapas `edit` no aplicados** en OpenCode (medido): no prometer protección por mapa.
6. **Deriva de esquema del store** (sin `schema_version`; detección por columnas — 005-002 discovery §5:278-282): fallar cerrado, nunca degradar a `timeout`.
7. **Alcance:** no tocar `install.sh`, el transporte externo más allá de que consuma el núcleo, ni la config del consumidor (§11 «Fuera de alcance»).
8. **Ownership:** la política y `delegation.json` son datos del usuario; el default de temporal es **propuesta**.

### Qué queda para la integración Claude Code (después, sobre la misma interfaz)

- Implementar `cdad_runtime_claude-code.py` con la misma interfaz de §2.2 (contexto efectivo, agente, observación de sesión) sobre el mecanismo nativo de CC (`Agent`, ADR-026) y su guard `PreToolUse` (`sources/agents/adapters/claude-code.md`:55-70), resolviendo la observación de la sesión hija por la superficie que CC exponga (a verificar en su momento).
- Cambiar su sección `delegation` (`sources/agents/adapters/claude-code.md`:73-110) igual que la de OpenCode: nombrar el paso de registro del intento y el de entrega, que hoy tampoco nombra.
- No bloquea lo urgente: la interfaz y el núcleo se construyen una vez; CC sólo agrega una implementación.

---

## 7. Partes en unidades (si el alcance se confirma grande)

| Unidad | Resultado | Validación proporcional |
|---|---|---|
| **U1** | Núcleo `cdad_dispatch.py` (`record` + `capabilities`), reusando `--record-dispatch`; resultado nativo byte-exacto | focales: observación con claves cerradas; idempotencia; error accionable |
| **U2** | Integración OpenCode: resolución de contexto/agente/observación; correlación §2.3; fallo cerrado fuera de versión/esquema | focales con store disposable (patrón de `cli-delegation.md` §Isolation recipe) |
| **U3** | Temporal del test-writer: clase `temporary`, política, default de `propose_policy`, `git check-ignore` en `prepare` | focales de scope (positivo/negativo), política vacía, no-ignorado |
| **U4** | Entrada única del orquestador + secciones `delegation` de los adaptadores fuente + regeneración | test de texto + `make validate`; el generador sigue determinista |
| **U5** | Camino mecánico a `failed` (efecto del `disposition`) y desbloqueo verificado de `prepare` | focal: `prepare` antes/después; `validate-state` VALID |
| **U6** | Escenario de aceptación de §11 (nested layout, cwd distinto, agente global vs proyecto, auxiliar temporal, test real recibido, intento interrumpido) | recorrido real aislado; no es unidad de código |

Secuencia sugerida: **U1 → U2**; **U3** y **U5** son independientes de U2; **U4** al final (toca texto generado); **U6** después de U1–U5. Claude Code (arriba) queda fuera de esta feature: sólo consume la interfaz ya congelada por U2.

---

## 8. VERIFY / deuda declarada

- **V-1** obtención de la sesión hija por la vía nativa (bloqueante para la llave «padre»).
- **V-4** alias del test-writer con `task`: el título de la sección generada dice «(adapter)» con contenido nativo (`cdad-generate.py`:747) — deuda O-1 de ADR-032:184; se corrige con U4.
- **V-5** que el `task` nativo bloquee al padre y la semántica de `external_directory` en la versión instalada.
- **V-6** la condición stale de `.cadad/execution.json` en el mandato (§1.5d) — se corrige con U4.
- **V-7** confirmar las columnas reales de correlación en la versión instalada antes del RED (la forma citada es de 005-002; el adaptador exige hoy un subconjunto menor).
- **V-8** la propuesta de temporal por defecto cambia bytes de `propose_policy`; los tests que fijen esa salida deben reformularse **declarando el reemplazo** (regla D7/A-1 de 006-003).

---

## 9. Evidencia de este rol (comandos, salidas, archivos, commit)

**Archivos modificados: ninguno.** **Commit: ninguno.** Nada escrito en el repo (write scope vacío); la CLI `status` se corrió read-only (el state queda byte-idéntico).

Comandos ejecutados (extracto literal, salida resumida):

```
$ git rev-parse HEAD
af0e0b5b17dd14b0cdf46c5b2ca3f8336ebec069

$ git status --porcelain
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md

$ grep -n 'role == "test-writer"' skills/cdad-cycle/scripts/cdad_packet.py
728:    if role == "test-writer":
729:        allowed = {"contract", "docs", "tests", "colocated-tests"} if not write else {"tests", "colocated-tests"}

$ grep -rn "record-dispatch" skills/cdad-cycle/references/{re-entry,orientation,cli-delegation}.md
skills/cdad-cycle/references/orientation.md:34   (route text)
skills/cdad-cycle/references/orientation.md:72   (table row: "Record a dispatch attempt")
skills/cdad-cycle/references/cli-delegation.md:15
# re-entry.md: sin coincidencias

$ grep -n "the active packet is not dispatched" skills/cdad-cycle/scripts/cdad_result.py
579:                "the active packet is not dispatched: reception requires the I8 dispatch "

$ grep -n "def propose_policy" -A14 skills/cdad-cycle/scripts/cdad_packet.py | grep temporary_roots
1101:        "temporary_roots": [],

$ git check-ignore -v .cdad .cdad/tmp .cdad/local
.cdad       -> .gitignore:11:.cdad/   .cdad
.cdad/tmp   -> .gitignore:11:.cdad/   .cdad/tmp
.cdad/local -> .gitignore:11:.cdad/   .cdad/local

$ python3 skills/cdad-cycle/scripts/cdad_packet.py status --project-root .   # read-only
{"entry":"continuity-reconcile","next":{"route":"reconcile the dispatched packet before repeating (resume)",
 "source":"docs/.cdad-state.json:active_packet.status"},
 "packet":{"id":"006-005-native-path-parity-architect-discovery-001","role":"architect","status":"dispatched",
 "substage":"discovery"}, "feature":{"active_feature":"006-005-native-path-parity","current_stage":"discovery"}}
```

Sondas apoyadas en evidencia del repo (no en supuestos): esquema `session_v2`/`session_message` y `parent_id` de subagentes (`docs/specs/005-002-session-context-meter/discovery.md`:63-73, :118-134; DDL espejo en `tests/test_005_002_t1_neutral_record.py`:120-138); `PWD` como fuente del directorio y límites de activación (`docs/evidence/runtime-delegation/opencode-delegation.md`:80-87, :200-218); límite de los mapas `edit` (`skills/cdad-cycle/references/project-execution.md`:158-166).

Sin conflictos entre el contrato (§11/§12) y lo observado en el repo. Las únicas incógnitas que impiden cerrar el diseño antes de RED son V-1 y V-7; V-2, V-3 y V-5 condicionan la integración, no el núcleo. Quedo a la espera del brainstorm y del reviewer (`plan-review`) antes de redactar la spec y el plan.
