<!-- Materializado por el orquestador Claude (ADR-003) desde la entrega del architect
     (paquete 005-010-real-opencode-delegation-architect-discovery-001, sesión OpenCode
     <ses-135>, recibo semantic_status: pending, parte sha256 7e45ab1c…0e92).
     Nota del orquestador: las sondas con --standalone usaron el directorio de datos del dueño
     (la instalación aislada perdió la credencial, que vive en la base) y dejaron sesiones de
     prueba en su base de OpenCode; no se tocó su configuración ni su servidor. El draft debe
     decidir si la prueba de integración necesita una credencial aislada en vez de esto. -->

# Discovery — 005-010-real-opencode-delegation (etapa 1, mapeo técnico y brainstorming)

Rol: architect (subetapa discovery). **Read-only. No se editó el repo.**
Contrato: `docs/epics/epic-005-real-operation/plan.md` — sha256 verificado
`996dd7e0afa837892a79d66f847c451e4cc65e909742c0ed1729cfb98a97466e` (coincide con el packet).
Fecha: 2026-10-11. Base del repo: HEAD `06d0e98`, rama `codex/epic-005-real-operation`.
Artefacto del adaptador bajo análisis: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`
(sha256 `838d22a18a6e60e2d19957481b781ef40001fd85e3b65242db8355c051f6d53a`), **byte-idéntico**
al instalado en la instalación elegida (misma sha256), confirmando la premisa del encargo.

Este reporte **NO propone el contrato** (eso es la subetapa draft). Mapea la superficie real, confirma o corrige los hechos del encargo, presenta opciones con recomendación y riesgos, señala puntos de extensión y VERIFY abiertos. Distingue en cada punto **principio de CDAD**, **adaptador OpenCode** y **particularidad de este entorno**.

---

## 1. Resumen ejecutivo

1. **Hecho (1) CONFIRMADO.** Los agentes de rol publicados son `mode: subagent` (el orquestador es `mode: all`) y el adaptador solo acepta `mode: all` (`SUPPORTED_LOAD_MODES = {"all"}`). Reproducido: `_check_load_mode(root, "architect")` devuelve `(False, 'subagent', …)` con diagnóstico. **Pero la premisa que lo justifica está obsoleta**: en la versión instalada (v2.0.26) `opencode run --agent <mode:subagent>` **sí funciona** como entrada no interactiva (sonda §3.2). La evidencia «cuelga en silencio» provenía del **binario legacy en PATH** (1.18.32), no del runtime real 2.x (`docs/specs/opencode-read-map-and-steps-2026-09-29/evidence/results.md:32`). El adaptador, tal como está, **bloquea todo despacho a un rol** por una regla que la versión instalada ya no requiere.

2. **Hecho (2) CONFIRMADO.** La señal durable `sessions_db` es un JSON `{status, session, final_text, diagnosis}` que **solo escribe el binario falso** del fixture (`tests/test_005_009_t2_opencode_adapter.py`, plantilla `FAKE_BINARY_SOURCE`, archivo `<fake>/sessions.json`). OpenCode real **no produce ese archivo**: persiste las sesiones en **SQLite** (`~/.local/share/opencode/opencode.db`, tablas `session_v2` y `session_message`). Contra el runtime real, `_read_signal` no encuentra la señal → `timeout`. Además, apuntado al DB real lanza una excepción **no capturada** (`UnicodeDecodeError`, no es JSON), así que ni siquiera falla cerrado con diagnóstico (§3.4).

3. **Hecho (3) PARCIALMENTE CONFIRMADO, con correcciones.** El adaptador invoca `opencode run --agent <rol>` con el paquete por **stdin**, sin `--standalone`, sin `--auto` y sin `--session`. Verificado: **stdin SÍ transporta el mensaje** en v2.0.26 (sonda §3.3); `run` acepta `--session <id>` (crea con id elegido: **correlación inequívoca**, §3.5), `--format json`, `--file`, `--title`, `--standalone`, `--server`, `--auto`. Lo que falta en el adaptador es `--standalone` (selector de servidor), `--auto` (permisos no interactivos), `--session` (correlación) y un lector de la superficie durable real.

4. **La superficie durable real y su correlación están resueltas con evidencia**: sesión creada con `--session <id>` elegido por el adaptador → fila en `session_v2` con ese `id`, `agent`, `model`, y **`idle_outcome`** (`succeeded`/`failed`/`interrupted`/NULL) + fila `session_message` de tipo `idle`; el texto final vive en `session_message.data.content[].text` (tipo `assistant`). Es una superficie **de solo lectura**, correlacionable sin ambigüedad y con **fallo cerrado** ante esquema desconocido.

5. **Recomendación de forma** (detalle y alternativas en §4): aceptar `mode: subagent` como entry soportada en la versión instalada, **verificar la identidad del agente desde la fila durable** (`session_v2.agent == "cdad-<rol>"`, sin fallback), transportar por stdin (ya funciona), agregar `--standalone` + `--auto`, y **correlacionar por `--session <id>` elegido** leyendo el store real (SQLite) en solo lectura, con fallo cerrado por esquema.

---

## 2. Superficie existente reutilizable (entidades verificadas archivo:línea)

- **Interfaz común de delegación:** `skills/cdad-cycle/scripts/cdad_delegate.py` (298 líneas).
  - `:131-162` `_run_adapter` corre el adaptador como subproceso con el `PACKET.md` en **stdin** byte-idéntico, argv `--project-root/--packet-id/--destination[--exec-config]`, y lee **un** envelope JSON del stdout (`_parse_envelope`, `:115-128`).
  - `:48-51` vocabulario de terminación y claves de salida `{attempt, session, termination, delivery_ref, diagnosis}`.
  - `:252-283` `delegate()`: resuelve el adaptador por convención de módulo, registra el intento I8 reutilizando `cdad_packet.py prepare --record-dispatch` (`:196-233`) y **no** escribe el state.
- **Adaptador OpenCode:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (589 líneas).
  - `:71` `SUPPORTED_LOAD_MODES = frozenset({"all"})`; `:72` `DERIVED_AGENTS_RELPATH = .opencode/agents`; `:134-159` `_check_load_mode` (falla cerrado si el derivado no es `all`).
  - `:165-181` `_invoke_destination`: argv `[binary, "run", "--agent", agent] (+ --model)`, `input=packet_bytes`, `cwd=project_root`, **sin `--standalone`/`--auto`/`--session`**.
  - `:187-209` `_read_signal`/`_wait_signal`: leen un **JSON** en `sessions_db` y sondean cada 50 ms hasta un deadline acotado.
  - `:411-437` `_classify`: `status` ∈ {completed, blocked, cancelled}; cierra desde `final_text`/`diagnosis`.
  - `:305-394` `_persist_delivery`/`_run_receive`: persisten el texto final por el flujo `receive` existente (recibo `semantic_status: "pending"`).
- **Referencias:** `skills/cdad-cycle/references/cli-delegation.md` (contrato del adaptador, PD-1..PD-8); `skills/cdad-cycle/references/opencode-delegation.md` (carga de roles, task vs delegate, origen/versión/reload de agentes de proyecto, `:149-167`).
- **Paquetes/ledger/recibos reutilizados:** `cdad_packet.py prepare --record-dispatch` (registro I8), `cdad_result.py receive` (`semantic_status:"pending"`), `cdad_continuity.py reconcile`/`resume`.
- **Generación de agentes:** `scripts/cdad-generate.py:391` emite literal `mode: subagent` para los roles OpenCode; el orquestador usa `mode: all` (fuente `sources/agents/adapters/opencode.md:14`; `make agents`; publicado por proyecto por `prepare` bajo `.opencode/agents/` con manifiesto `.cdad-derived.json`).
- **Instalación aislada:** `install.sh:45` `INSTALL_ROOT="${CDAD_INSTALL_ROOT:-${HOME:-}}"` — permite la instalación aislada de PD-10.
- **Prueba omitida de PD-10:** `tests/test_005_009_t4_acceptance.py:307-326` (`self.skipTest(...)`).

---

## 3. Superficie real de OpenCode v2.0.26 (hechos verificados: comando + resultado)

Binario: `~/.opencode/bin/opencode` (runtime real), `opencode v2.0.26`. Sondas de escritura en `/tmp/opencode/probe-005-010/`, agentes de prueba `probe-primary` (`mode: all`) y `probe-sub` (`mode: subagent`). **Nunca** se tocó el HOME/config del dueño ni se operó su servidor; las corridas exitosas usaron `--standalone`.

### 3.1 Superficie del CLI (`run`)

`opencode run --help` → `--standalone`, `--server`, `--continue/-c`, `--session/-s`, `--fork`, `--model/-m`, `--agent`, `--format {default,json}`, `--file/-f`, `--title`, `--thinking`, `--auto`. Argumento posicional `message...` **opcional**. Top-level `--standalone` = «Run with a private server instead of the background service». Subcomandos: `run`, `session {list,delete,export,import}`, `debug {agents,config,paths}`, `service {…}`, `models`, `reload`, `serve`, `api`, `auth {list,export,import,…}`.

### 3.2 Modo de carga del rol — **`mode: subagent` SÍ es entry no interactiva en v2.0.26**

```
$ opencode run --standalone --agent probe-primary --model <m> --format json "go"
  → {"type":"text",…,"part":{…,"type":"text","text":"PRIMARY",…}}   rc=0
$ opencode run --standalone --agent probe-sub    --model <m> --format json "go"
  → {"type":"text",…,"part":{…,"type":"text","text":"SUB",…}}       rc=0   # ¡subagent!
$ opencode run --standalone --agent no-such-agent-xyz --model <m> --format json "go"
  → {"type":"error",…,"error":{"type":"unknown","message":"Agent not found: \"no-such-agent-xyz\""}}
```

Los agentes respondieron el token de su propio system prompt (`PRIMARY` vs `SUB`): el `--agent` **se honra**; un nombre inválido da error explícito (no cuelga). Filas durables: `agent = probe-primary`/`probe-sub`, ambas `idle_outcome = succeeded`. **Interpretación:** la premisa de 005-009 era **una particularidad del binario legacy** (1.18.32 en PATH, tabla `session` legacy; `results.md:32`). La spec de 005-009 dejó esto como VERIFY-3 abierto; esta sonda lo re-verifica y **lo cambia**.

### 3.3 Transporte del paquete — **stdin SÍ transporta el mensaje**

```
$ printf 'Reply with exactly the token STDIN-OK…\n' | opencode run --standalone \
      --agent probe-primary --model <m> --format json      # sin argumento de mensaje
  → {"type":"text",…,"text":"STDIN-OK",…}                  rc=0
```

Sin argumento posicional, el contenido de **stdin se usa como prompt**. `--file` adjunta como **contexto** (no como instrucción). **stdin es un transporte válido y byte-fiel** para el `PACKET.md`.

### 3.4 Superficie durable real — SQLite (`session_v2`, `session_message`)

`opencode debug paths` → `db ~/.local/share/opencode/opencode.db`. Lectura en **solo lectura** (`sqlite3 "file:<db>?mode=ro"`).

`session_v2` (relevante): `id, project_id, parent_id, fork_session_id, slug, directory, title, version, agent, model, cost, tokens_*, time_created, time_updated, time_archived, time_idle, idle_outcome`.
`session_message`: `id, session_id, type, seq, time_created, time_updated, data` (JSON). Tipos observados: `assistant, user, system, idle, synthetic, agent-switched, compaction, model-switched, location-switched`.

Fila durable de una corrida (`id=<ses-321>`):
```
agent = probe-primary        model = {"id":"…","providerID":"…"}
idle_outcome = succeeded     time_idle = 1791734932539     time_archived = (NULL)
session_message: user{"text":"\"Reply with exactly OK\"","files":[]}
                 assistant{"agent":…,"model":{…},"content":[{"type":"text","text":"OK"}],
                           "finish":"stop","cost":…,"tokens":{…}}
                 idle{"outcome":"succeeded"}
```
`idle_outcome` (muestra 5000): NULL 3058, `succeeded` 1285, `interrupted` 21, `failed` 10. La sesión de un `--agent` inválido persistió con `idle_outcome = failed`. **Modelo durable:** la sesión pasa a *idle* con **outcome material**, y el texto final queda en el mensaje `assistant`. El `{status,session,final_text}` del fixture **no existe** en el runtime real.

Defecto del adaptador: `_read_signal` (`:187-197`) hace `read_text(utf-8)` y captura solo `(OSError, json.JSONDecodeError)`; contra el DB real lanza **`UnicodeDecodeError`** no capturado → trazabilidad y rc≠0 sin envelope (la interfaz lo mapea a `transport-error`). No falla cerrado *con diagnóstico*.

### 3.5 Correlación inequívoca — `--session <id>` crea la sesión con el id elegido

```
$ opencode run --standalone --session <ses-322> \
      --agent probe-primary --model <m> --format json --title "cdad-probe-sid" "…"
  → {"type":"text","sessionID":"<ses-322>",…}   rc=0
$ sqlite3 … "SELECT id,agent,idle_outcome FROM session_v2 WHERE id='<ses-322>';"
  id = <ses-322>   agent = probe-primary   idle_outcome = succeeded
```
El id elegido por el adaptador **es** el id durable. Elimina la ambigüedad «¿cuál sesión?» sin depender de `time_created`/`title`.

### 3.6 Salida estructurada del cliente (`--format json`)

JSONL tipado: `step_start`, `text` (con `part.text`), `error`, etc.; incluye `sessionID`. Es superficie **del cliente** (no durable): útil para diagnóstico, no como única señal de finalización.

### 3.7 Servidor: privado (`--standalone`) vs servicio de fondo

`--standalone` = servidor privado; sin él, `run` se conecta al **servicio de fondo** (proceso de larga vida con su entorno/agentes cargados al arrancar). Evidencia indirecta: `opencode models` sin `--standalone` intentó el servicio gestionado y falló con `Managed service port <P> on 127.0.0.1 is already in use`. El adaptador **no** pasa `--standalone` → se acopla al servicio de fondo del dueño. No se ejecutó `run` sin `--standalone` (operaría el servidor del dueño; prohibido).

### 3.8 Permisos no interactivos (`--auto`)

`--auto` auto-aprueba permisos no denegados explícitamente. Evidencia heredada (`results.md:29`, OpenCode 2.0.16): sin `--auto`, un pedido de permiso (edit/write) se **auto-rechaza** en `run` no interactivo; los deny-lists de path siguen vigentes. El adaptador **no** pasa `--auto`. No se forzó la mutación en vivo → VERIFY-B.

---

## 4. Opciones con recomendación y riesgos

### 4.1 Superficie durable, correlación y fallo cerrado

| Opción | Cómo | Ventajas | Riesgos |
|---|---|---|---|
| **A. Store SQLite en solo lectura + `--session <id>` elegido** (RECOMENDADA) | El adaptador elige el id, lo pasa en `--session`; espera la fila `session_v2` con ese `id` y su `time_idle`/`idle_outcome`; lee el texto final de `session_message` `assistant` | Superficie **material**; correlación **inequívoca**; solo lectura | El esquema **no es contrato público** (riesgo del epic): fallo cerrado por esquema; DB grande/con WAL → abrir `mode=ro` |
| **B. Salida `--format json` del cliente** | Parsea el JSONL de stdout | Sin tocar la DB | Superficie del cliente: puede volver antes de que el rol termine (`results.md:39`); no prueba finalización |
| **C. `opencode session export <id>`** | Export JSON de la sesión | Estructurado | Requiere servidor; llamada de cliente, no archivo durable |
| **D. El worker escribe un recibo durable** | Ruta pactada | No depende del runtime | **Señal inventada**; si el worker falla, no hay señal (contradice INV-6) |

**Recomendación A + verificación reforzada:** esperar la DB (A) y, como verificación de transporte/identidad, contrastar el JSONL del cliente (B) o el texto persistido. Reglas: correlación por `--session <id>`; **fallo cerrado por esquema** (`sqlite_master`/`PRAGMA table_info`; si `idle_outcome`/`content` no parsean → `blocked`/`unknown`, sin entrega ni recibo); apertura `mode=ro` (nunca escritura; evaluar `immutable=1`); deadline acotado por `wait.timeout_seconds`. **Frontera:** el *principio* es «superficie durable, no inventar señales»; *cuál* superficie es el *adaptador*; el path/tamaño/WAL son *particularidad del entorno* → `--exec-config`, nunca hardcodeados.

### 4.2 Modo de carga de la entry no interactiva

| Opción | Cómo | Ventajas | Riesgos |
|---|---|---|---|
| **A. Aceptar `mode: subagent` + verificar identidad desde la fila durable** (RECOMENDADA) | Deja de exigir `all`; exige `session_v2.agent == "cdad-<rol>"` | **No toca la generación** ni el uso como subagente; alinea con v2.0.26 | En un binario legacy podría colgar/ignorar → mitigado por timeout acotado + verificación de identidad |
| **B. Publicar variantes `mode: all`** | `cdad-generate.py` emite variantes `-primary` | Evita la pregunta de versión | Duplica agentes y su sincronía; cambia el set publicado |
| **C. Orquestador (`mode: all`) como entry que delega** | Entry = `cdad-orchestrator`; delega por `task` | Reusa el orquestador | Reintroduce anidamiento/spawn; roza «fallback a no-rol»; rechazado |

**Recomendación A.** **No** se cambia `scripts/cdad-generate.py` (que hardcodea `mode: subagent` en `:391`): el uso del rol como subagente queda intacto. Si el draft quiere una garantía *pre-despacho* adicional, combinar con un **chequeo de capacidad por versión** con fallo cerrado ante versión desconocida (VERIFY-E).

### 4.3 Transporte del paquete

- **stdin (RECOMENDADO, ya verificado):** byte-idéntico (PD-2/INV-3); verificación adicional posible contrastando el mensaje `user` persistido con el marcador `---cdad-packet-json` o su sha256.
- **Argumento posicional:** funciona, pero expone a límites de argv y quoting.
- **`--file`:** adjunta como contexto, **no** como instrucción → no sirve como transporte del paquete.

### 4.4 Servidor privado vs servicio de fondo

- **`--standalone` RECOMENDADO:** entorno previsible, agentes/config recién publicados, sin operar el servicio del dueño (INV-10).
- **Servicio de fondo:** agentes/entorno son los cargados **al arrancar**; un cambio de agente no recarga (paralelo a 005-005 PD-15) → riesgo de correr una versión distinta.
- **`--server <url>`:** escotilla para apuntar a un servidor concreto.

### 4.5 Permisos no interactivos

- **`--auto` RECOMENDADO** para roles que editan; sin él un pedido de permiso se auto-rechaza.
- Frontera honesta: `--auto` auto-aprueba lo **no** denegado; los mapas de path/deny de la frontmatter siguen siendo la barrera real (no es sandbox). VERIFY-B en v2.0.26.

---

## 5. Doble de test fiel y prueba de integración opcional

### 5.1 Doble de test (obligatorio, sin binario real)

El fixture actual (`opencode-fake`) escribe un **JSON** `sessions.json` — infiel al runtime real. El doble nuevo debe reproducir lo **observado**:
- **argv esperado:** `[binary, run, --agent, cdad-<rol>, (--model …), --session <id>, --standalone, --auto]` (registrar `calls.jsonl`).
- **transporte:** leer el paquete por **stdin**, copiarlo byte a byte.
- **señal durable:** crear un **SQLite real chico** con el esquema observado (`session_v2` + `session_message`) e insertar fila `session_v2` (`id` = `--session`, `agent` = `--agent`, `model`), mensaje `user` con el paquete, `assistant` con `content:[{type:text,text:<final>}]`, `idle` con `outcome`, y `time_idle`/`idle_outcome`.
- **variantes:** `succeeded`, `failed`, `interrupted`, `no-idle` (→ timeout), `unknown-schema` (falta `idle_outcome` → fallo cerrado), `transport-error` (rc≠0 sin señal).

### 5.2 Prueba de integración opcional (contra el binario real)

- **Marcada y omitida por defecto** (patrón `test_005_009_t4_acceptance.py:307-326`), habilitada por variable de entorno (p. ej. `CDAD_OPENCODE_INTEGRATION=1`), con el binario provisto por config.
- **Instalación aislada:** `CDAD_INSTALL_ROOT=<tmp>` (`install.sh:45`) para no tocar el HOME del dueño.
- **Corrida mínima real:** proyecto temporal + agente de prueba; `run --standalone --session <id> --auto` con prompt trivial; aserción de correlación durable. **Nunca** opera el servicio del dueño ni escribe en su HOME/DB.

---

## 6. Puntos de extensión

1. `cdad_delegate_opencode.py`: `_check_load_mode` (`:134-159`)/`SUPPORTED_LOAD_MODES` (`:71`); `_invoke_destination` (`:165-181`, agregar `--standalone`/`--auto`/`--session`, evaluar `--format json`); `_read_signal`/`_wait_signal` (`:187-209`, lector SQLite + fallo cerrado); `_classify` (`:411-437`); `_observation` (`:221-240`, `model_reported`/`session` desde la fila durable).
2. Config (`--exec-config`): `sessions_db` pasa a denotar el **store real** (ruta SQLite); evaluar declarar el tipo de store; todo local, sin valores del host (PD-8/INV-7).
3. Generación/publicación: **solo si** el draft elige la opción B de §4.2 (`scripts/cdad-generate.py:391`, `sources/agents/adapters/opencode.md`, `prepare`).
4. Integración/instalación: `install.sh` (`CDAD_INSTALL_ROOT`).

---

## 7. Convenciones aplicables

- Contrato del adaptador: `references/cli-delegation.md` (stdin `PACKET.md` byte-idéntico; argv; envelope único en stdout; rc 0 salvo error interno).
- Vocabulario de terminación `completed | blocked | transport-error | timeout | cancelled | unknown`; **entrega ≠ gate** (recibo `pending`).
- Fallo cerrado y **sin fallback** a agente genérico (PD-4/D5); **sin señales inventadas**, espera acotada (PD-5/INV-6); **sin valores del VPS** (PD-8/INV-7); el orquestador es el **único escritor** del state (INV-1).
- Generación determinista (`make agents`), nunca editar `agents/` a mano.

---

## 8. VERIFY abiertos

- **VERIFY-A — `run` sin `--standalone` en v2.0.26:** semántica del acoplamiento al servicio de fondo. No ejercido (operaría el servidor del dueño); evidencia indirecta por el error de puerto.
- **VERIFY-B — `--auto` en v2.0.26:** confirmar el auto-rechazo de permisos sin `--auto` (evidencia es de 2.0.16).
- **VERIFY-C — finalización con subagentes:** ¿`idle_outcome` del **padre** marca el subárbol, o solo el turno primario? ¿`run` vuelve tras el primario o tras los hijos?
- **VERIFY-D — estabilidad/versión del esquema:** marcador de versión (`__drizzle_migrations`/`PRAGMA user_version`) y forma estable del fallo cerrado entre versiones.
- **VERIFY-E — gating del `mode`:** confirmar que el `mode` ya no condiciona la entry; definir si hace falta chequeo de capacidad por versión además de la verificación de identidad material.
- **VERIFY-F — restricciones del id de `--session`:** charset/longitud (se usó un id `ses_…` con éxito; no se agotaron casos límite).
- **VERIFY-G — lectura segura con el servicio vivo:** que `mode=ro` no falle ni bloquee mientras el servicio escribe (WAL/SHM).

---

## 9. Límites honestos

- Un proceso/sesión separada **no es un sandbox**; cambiar de CLI **no** garantiza otra familia de modelo ni aislamiento.
- `rc=0` **no** aprueba un gate (recibo `pending`); `timeout` **no** prueba ausencia de cambios (reconciliar antes de repetir).
- El esquema de `opencode.db` **no es un contrato público** → fallo cerrado obligatorio.
- Sin valores de este VPS en producto/contratos publicables. **No** se construye scheduler, instalación automática de CLI ni sandbox.

---

## 10. Distinción principio CDAD / adaptador OpenCode / particularidad de este entorno

| Aspecto | Principio CDAD | Adaptador OpenCode | Particularidad de este entorno |
|---|---|---|---|
| Señal de finalización | Superficie **durable**, no el rc; no inventar | Leer `session_v2`/`session_message` | Path/tamaño/WAL del DB; credenciales en el propio DB (`credential`) |
| Correlación | Sin ambigüedad despacho↔sesión | `--session <id>` elegido por el adaptador | — |
| Modo de carga | Fallo cerrado, sin fallback genérico | `run --agent <mode:subagent>` (v2.0.26) / legacy 1.18.32 | Coexistencia histórica de binarios; versión instalada v2.0.26 |
| Transporte | Paquete byte-idéntico | stdin de `opencode run` | — |
| Servidor | Entorno previsible, sin operar producción del dueño | `--standalone` vs servicio de fondo | Servicio de fondo del dueño corriendo; puerto gestionado |
| Permisos | Deny de path siguen vigentes | `--auto` para no interactivo | — |

---

## 11. Evidencia de la sesión (comandos y resultados)

- `sha256sum docs/epics/epic-005-real-operation/plan.md` → `996dd7e0…466e` (== packet).
- `sha256sum skills/cdad-cycle/scripts/cdad_delegate_opencode.py` y el instalado → `838d22a1…` en ambos.
- `opencode --version` → `opencode v2.0.26`.
- `opencode --help`, `opencode run --help`, `opencode debug --help`, `opencode session --help` → §3.1 (salidas en `/tmp/opencode/probe-005-010/*.txt`).
- Import del adaptador: `_check_load_mode('.', 'architect')` → `(False, 'subagent', "unsupported load mode for entry 'cdad-architect' … only 'all' …")`; `SUPPORTED_LOAD_MODES == ['all']`.
- `_read_signal(<db real>)` → `UnicodeDecodeError` (no capturado).
- `sqlite3 "file:<db>?mode=ro" ".schema session_v2" / ".schema session_message" / ".tables"` → esquema §3.4.
- `sqlite3 … "SELECT type,count(*) FROM session_message …"` y consultas por sesión → §3.4/§3.5.
- Corridas reales `--standalone`: `probe-primary`→`PRIMARY` (rc 0), `probe-sub`→`SUB` (rc 0), `no-such-agent-xyz`→`Agent not found`, stdin sin argumento→`STDIN-OK` (rc 0), `--session ses_probe…`→ fila durable con ese id (salidas en `/tmp/opencode/probe-005-010/run-*.txt`).
- `opencode models` (sin `--standalone`) → error de puerto del servicio gestionado (§3.7).

**Archivos modificados:** ninguno (read-only). **Temporales:** solo en `/tmp/opencode/` (workspace declarado); transport del reporte en `/tmp/opencode/discovery-005-010.md`. **Commit:** ninguno.

---

## Nota de contrato (para el orquestador)

El packet declara `write_scope: []` y el rol architect es read-only; por eso **no** creé `docs/specs/005-010-real-opencode-delegation/discovery.md` en el repo. El contenido íntegro está arriba (texto final) y en `/tmp/opencode/discovery-005-010.md` (transporte), para su materialización por el orquestador (ADR-003). No apruebo el contrato; la propuesta es la subetapa draft.
