# Discovery — `006-003-installer-single-profile-delegation-config`

**Rol:** architect (etapa 1). **Read-only.** Archivos modificados: **ninguno** (write_scope vacío). Contrato del epic verificado por hash.

**Verificación del contrato**
```
$ sha256sum docs/epics/epic-006-opencode-concurrency/plan.md
b6a59502ff18b6a2826e7cf672b790630d988a597cd6b24213442922ee4f2e63  docs/epics/epic-006-opencode-concurrency/plan.md
```
Coincide con `contract.sha256`. Leí `plan.md` completo (§8, §9, §10, principio de modelos por configuración) y `docs/epics/epic-006-opencode-concurrency/execution.md` (mandato, topología, despliegues, hallazgo de despliegue al final). No existe spec de esta feature y no la declaro existente.

**Estado del árbol al empezar (solo lectura):**
```
$ git log --oneline -2
192612a docs(state): 006-003 discovery despachado
f71a2e9 docs(state): 006-003 discovery preparado
$ git status --porcelain
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
$ python3 -c "import json;d=json.load(open('build/staging/manifest.json'));print(d.get('profile'))"
basic
```
Nota de contexto: el `build/staging` del checkout está hoy en `basic` (último `make staging PROFILE=basic`), mientras los `agents/` commiteados están en `optimus`. Esa divergencia es la que ya causó el fallo ambiental de `test_review5_b4_*` documentado en `execution.md:164`.

---

## 1. INVENTARIO — qué implementa o nombra perfiles y modelos hoy

### 1.1 `install.sh`

| Zona | Evidencia | Qué cambia al quedar siempre `basic` |
|---|---|---|
| Vars de estado | `install.sh:101-103` (`PROFILE_FLAG`, `MODEL_PROFILE`, `PROFILE_MARKER=.cdad-models-profile`) | Desaparecen las tres (ya no hay perfil que persistir). El marker instalado por versiones anteriores queda como `pending_removal` (§5). |
| Carga del mapa | `install.sh:126-133` (`source scripts/cdad-models.sh`, `die` si falta) | El `source` desaparece; `scripts/cdad-models.sh` deja de ser dependencia del instalador. |
| Ayuda | `install.sh:329-353` (bloques `--economical/--optimus/--premium/--basic`), `:362-369` (precedencia y default), `:371-380` (envs `CDAD_PREMIUM_MODEL_*`) | Se borra la sección de perfiles, la precedencia y las envs premium. |
| Parseo | `install.sh:441-444` (normaliza `-e/-o/-p/-b`), `:452` (`profile_count`), `:459-462`, `:471-472` (mutuamente excluyentes) | Se retira el parseo de flags de perfil. **Riesgo R2**: `--basic` es la receta de instalación aislada de ≥6 archivos de test (§1.6). |
| Resolución | `install.sh:978-1001` (`resolve_profile`, `validate_profile`) | Ambas funciones se retiran; no hay precedencia ni validación de perfil. |
| Marcador | `install.sh:1023-1034` (`write_profile_marker`, `record_owned`) | Se retira; dejar de escribirlo convierte el marker de instalaciones previas en `pending_removal`. |
| Check repo (legacy) | `install.sh:1283-1294` (espera el `model:` exacto del perfil), `:1344` (`want_model=$(cdad_model …)`) | El check deja de mirar `model:` por completo (deja de ser "la única desviación legítima"). |
| Check staging | `install.sh:1442-1497` (bytes vs staging), `:1499-1526` (`PENDING-REMOVAL` → `drift=1`) | El check ya no reporta marker obsoleto si §5 lo retira; sin §5, el marker viejo haría FAIL. |
| Mismatch | `install.sh:1722-1729` (`PROFILE MISMATCH`, gana el staged), `:1735` (`write_profile_marker`) | Se elimina: ya no hay dos perfiles que puedan discrepar (y desaparece el objeto del test review-5 B4). |
| Cabecera | `install.sh:20-31`, `:63-74` (mención a "fixed model per role") | Los comentarios sobre modelos fijos por rol (`-odoo`) dejan de ser ciertos. |

### 1.2 `scripts/cdad-models.sh` (el mapa único)

`cdad_model` en `scripts/cdad-models.sh:32`, `cdad_model_claude:112`, `cdad_valid_profile:172`. Devuelve vacío para **todos** los roles (incluidas las variantes `*-odoo`) cuando el perfil es `basic` (`:33-36`, `:113-115`).
**Qué cambia:** el archivo entero deja de tener sentido ("sin mapa de modelos"). Consumidores a actualizar: `install.sh:128-133`, `scripts/validate-subagents.sh:191-221`, `scripts/cdad-generate.py:183-214`, y los tests `test_cdad_generate.py:134`, `test_004_001_acceptance_matrix.py:72`, `test_004_001_t6.py:82`.

### 1.3 `Makefile`

`Makefile:7` `PROFILE ?= optimus`; `:13-14` pasan `--profile $(PROFILE)` a los dos `cdad-generate.py`.
**Qué cambia:** sin `PROFILE`, `make staging` genera siempre sin modelos. La aceptación del plan §9 lo pide literalmente ("sin perfiles en `install.sh` ni en `make staging`").

### 1.4 `scripts/cdad-generate.py`

| Zona | Evidencia | Cambio |
|---|---|---|
| Doc/uso | `:7`, `:22`, `:41` | Se retira `--profile` del uso y del manifiesto. |
| Validación | `:188-198` (`validate_profile` vía bash `cdad_valid_profile`) | Se retira. |
| Resolución | `:201-214` (`model_for(runtime, profile, role_key)`) | Se retira (o queda devolviendo `""` siempre). |
| Emisión `model:` | OC `:388-394` (`oc_frontmatter`), CC `:491-494` (`cc_frontmatter`) | Sin `model_for` no se emite la línea. |
| Nota de modelos | `:578-608` (`models_note`: perfiles economical/premium/basic + "Switch: install.sh --…") | Se reescribe: sin perfiles, sin nombres de modelo. |
| §2 del orquestador | `:755-812` (celdas de modelo por rol `:775-776`, `och_cell` `:778-779`, texto `:792-812`) | La tabla §2 deja de tener celdas de modelo resueltas por runtime×stack×perfil. |
| Manifiesto | `:954`, `:973`, `:990` (`"profile": profile`), `:996` (`regenerate`), `:1052` (`--profile required`), `:1057` | El manifiesto de staging pierde `profile` (o lo fija a `"basic"`). |
| Nota de honestidad | `:446` (comentario "absent `model:` under `basic`") | Ajustar redacción. |

### 1.5 Adaptadores fuente y agentes generados

- `sources/agents/adapters/opencode.md:15-18` (el `model:` se emite desde el mapa y el instalador lo reescribe por perfil), `:76-83` ("con perfil `basic` … write *invariant not guaranteed*").
- `sources/agents/adapters/claude-code.md:98-105` (idéntico).
- Agentes generados con `model:`: 10 OC (`agents/cdad-*.md:5`, todas menos el orquestador) + 11 CC (`agents/claude-code/*.md:5`, incluido `model: opus` del orquestador) = **21 líneas `model:`**. Al ser siempre `basic`, `make agents` las borra todas.
- `agents/cdad-orchestrator.md` / `agents/claude-code/cdad-orchestrator.md` (§2 compuesto + sección `delegation`) y el párrafo `models_note` embebido ("Models of the design … Profiles … Switch: install.sh --economical|…").
- **Consecuencia:** el repo deja de mostrar un diseño de modelos por rol. Es el objetivo declarado ("los modelos nunca los fija el orquestador ni los scripts"), pero es un diff visible y hay que decidirlo explícitamente en la spec.

### 1.6 Tests y validador acoplados a perfiles/modelos

| Archivo | Evidencia | Por qué se acopla |
|---|---|---|
| `tests/validate-consistency.sh` | `:463-471` (F008 recorre `economical optimus premium` con `cdad_model_claude`), `:531-535` (F011 corre `validate-subagents.sh`), `:303-361` (F001: frase de §2 + caveat `--basic` en los dos orquestadores) | Recorre perfiles y fija el texto de perfiles. |
| `tests/test_004_001_acceptance_matrix.py` | `:5-6`, `:85-88`, `:106-151`, `:289-327` (matriz 4 perfiles × roles, ejecuta `cdad-models.sh` como contrato de datos) | Es *el* test del mapa de modelos. |
| `tests/test_cdad_generate.py` | `:37` `PROFILE="optimus"`, `:46-58`, `:288-335` (caso `unknown-profile`), `:363-405` (PD-14 modelos por runtime) | Fija el flag `--profile` y los modelos. |
| `tests/test_004_001_t6.py` | `:82-83`, `:114` (`install.sh --basic`), `:218` | Modelos OC en §2. |
| `tests/test_005_004_t1_dispatch_tool_name.py` | `:93-96` `GENERATOR_PROFILE="optimus"` | Genera staging con perfil. |
| `tests/test_005_004_t2_installer_claims.py` | `:105` `MODELED_PROFILE="optimus"`, `:438` (exige "not guaranteed") | Reclamos del instalador sobre modelos. |
| `tests/test_005_006_t2_intake.py` | `:95` `PROFILE="optimus"` | Fixture de staging. |
| `tests/test_006_002_u4_skill_without_models.py` | `:153-180` (`PD11_SECTION2_CONCEPTS`, incluye conceptos **6/7 "cuando el perfil fija/no fija modelos" y 8 "profile/perfil"**), `:265-274` | Exige en §2 la redacción basada en perfiles → **se rompe** si §2 deja de hablar de perfiles. |
| `tests/test_006_002_u1_delegation_section.py` | `:121-127`, `:437-450` | Exige en cada orquestador `basic` + "familia no garantizada" (D-3). |
| `tests/test_install_review5_regressions.py` | `:401-480` (review-5 B4: `--basic` vs staging `optimus` debe informar el mismatch y publicar labels coherentes) | Sin perfiles, el caso pierde objeto. |
| `tests/test_install_ownership.py` | `:281-308` (manifiesto `profile` == staging `profile`) | Campo que desaparece. |
| Receta de instalación aislada | `tests/test_003_002_t4_integration.py:64`, `test_004_001_t6.py:114`, `test_004_001_t7_capacity.py:166`, `test_004_002_t6_landing.py:257`, `test_004_003_t2_plan_review.py:268`, `test_005_005_t4_integration.py:88`, `test_005_008_t3_acceptance.py:167` | Todos invocan `install.sh --basic`. |

### 1.7 ADR-007 y docs

- `docs/adr/ADR-007-perfiles-de-modelos.md` — **reemplazado por esta feature** (así lo dice `docs/adr/ADR-032…:121` y `:216`: "anticipa la sustitución de ADR-007 … instalador `basic` único, config de delegación y modelos por configuración"). Requiere ADR nuevo; ADR-008 (perfiles CC) queda afectado en su parte de perfiles.
- Memory Bank que ya lo anticipa: `docs/activeContext.md:156`, `:340`; `docs/systemPatterns.md:520`; `docs/progress.md:776`; `docs/runtime-adopted-version.md:164` (perfil `basic` desplegado).
- **`README.md`: cero menciones** de perfiles, `install.sh` o `make staging` (verificado: `grep -n "staging\|install.sh\|--basic\|perfil\|profile" README.md` → rc=1, sin salida). No hay docs *instalables* que nombren modelos: las superficies instalables son `skills/cdad-cycle/**` y los 8 skills; la §2 del skill ya declara que "no nombra modelos" (`skills/cdad-cycle/SKILL.md:77-82`).

---

## 2. Delegación externa: cómo toman hoy el modelo y cómo deberían tomarlo

### Hoy (evidencia)

- `skills/cdad-cycle/scripts/cdad_delegate.py`: `--exec-config` → `config.get("model")` (`:264-267`), que alimenta la observación I8 (`:177-190`, `model_configured` con procedencia "execution config") y se pasa al adaptador por `--exec-config` (`:132-145`).
- `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`: `model = _as_text(config.get("model"))` (`:1678`); `_invoke_destination` agrega `["--model", model]` (`:404-405`) y sólo si no está vacío; `model_reported` sale de la fila durable `session_v2.model` (`:245-265`, `:168`).
- Ejemplo portable: `skills/cdad-cycle/assets/opencode-exec-config.example.json` — clave **`"model": "<provider>/<model>"`** (una sola, lineal).
- Contrato: `skills/cdad-cycle/references/cli-delegation.md` sección *Configuration* — la prosa dice que "runtime, **model**, binary/version, logs, servers, timeouts y el modo viven en la execution configuration", pero la tabla de claves **no lista `model`** (sólo `mode`, `service.require`, `wait.*`). Esa prosa y el ejemplo son los dos lugares a corregir.
- Hecho del incidente (`execution.md:114-115`): el consumidor tenía **una exec-config por familia** (implementer / reviewer). Por eso la deriva: el modelo vive en un archivo por invocación, fuera de CDAD, y con `basic` no hay nada que fuerce familias distintas.
- `scripts/cdad_delegate.py` es sólo un wrapper del CLI instalable (sin lógica de modelo).

### Esquema mínimo propuesto (para la spec)

**Ubicación:** `$XDG_CONFIG_HOME/cdad/delegation.json`; si `XDG_CONFIG_HOME` no está definida, `<root>/.config/cdad/delegation.json` donde `<root>` es el `INSTALL_ROOT` del instalador (`install.sh:45`). Así se respeta el plan §9.5 *y* es redirigible en tests con `CDAD_INSTALL_ROOT` (hoy el instalador **no** lee `XDG_CONFIG_HOME` en ningún lado; el único XDG leído en el producto es `XDG_STATE_HOME` para el registro del servicio, `cdad_delegate_opencode.py:1167`).

**Contenido (versión 1):**
```json
{
  "version": 1,
  "models": {
    "<destination-id>": {
      "<role>": "<provider>/<model>"
    }
  },
  "credential_env_file": "<path>"
}
```
- `models` por **destino y rol** (`reviewer`, `implementer`, `test-writer`, `architect`, `scribe`) — es lo que pide el plan §9.2 ("modelo por rol y destino").
- `credential_env_file` opcional; por omisión `<config-dir>/cdad/opencode-server.env` (§4).

**Precedencia frente a la exec-config (compatibilidad):** el plan §9.3 es literal — "los scripts de delegación toman los modelos **solo** de ese archivo". Propuesta: la config de delegación es la **única** fuente de modelo del producto; una clave `model` heredada en la exec-config **no cambia el modelo efectivo** y produce un diagnóstico declarado de una línea (deprecado, con la ruta de la config de delegación y cómo migrar). Recomiendo **no** hacer fallback silencioso: un cambio de modelo efectivo no declarado es exactamente la deriva que la feature elimina. La alternativa (fallback a la exec-config cuando el rol no está en la config nueva) la dejo como decisión del dueño, marcada, porque cambia el comportamiento del consumidor actual.

**Si falta un rol:** no se pasa `--model`; el destino usa su propio modelo configurado; el intento se registra con `model_configured: null` y `model_reported` observado (o `unknown`); nunca se bloquea por eso; la verificación de familias (punto 3) reporta "no garantizado". El ejemplo `opencode-exec-config.example.json` pierde la clave `model` y la prosa de `cli-delegation.md` deja de nombrar el modelo como parte de la exec-config.

---

## 3. Verificación de familias (plan §9.4)

### Dónde se obtiene el modelo efectivo en cada ruta

| Ruta | Modelo efectivo | Evidencia |
|---|---|---|
| **Nativa OpenCode** (`task` + `subagent_type`) | Lo resuelve el runtime: config `agent.<name>.model` / `model` global y, si no, el frontmatter del agente. Bajo `basic` el agente no declara `model:` | `sources/agents/adapters/opencode.md:60-75` (mecanismo y prohibición intra-runtime); `agents/cdad-orchestrator.md` §2; `installation` del runtime: **UNKNOWN** — `execution.md:200` registra que un `opencode.json` de proyecto con `agent.cdad-reviewer.model` dejó la lista de agentes vacía ("observación, no investigada"). |
| **Nativa Claude Code** (`Agent` + `subagent_type`) | Frontmatter `model:` de `agents/claude-code/cdad-<role>.md:5` (hoy `sonnet/haiku/opus`) | `sources/agents/adapters/claude-code.md:82-97`; hoy con `basic` quedaría sin `model:`. |
| **Externa (adaptador OpenCode)** | `model_configured` desde la config (hoy exec-config, `:1678`); `model_reported` desde `session_v2.model` (`:245-265`) | `cdad_delegate_opencode.py`; contrato del adaptador punto 4 (cli-delegation.md, "report `runtime`, `model_configured`, `model_reported`, `session` … `null`/`unknown` cuando no se observa"). |

**Observación clave:** en la ruta **nativa**, CDAD no puede leer el modelo *antes* del despacho (el runtime es dueño de la resolución). Lo único observable es **post-hoc** desde la fila durable (`session_v2.model`), que es el mismo mecanismo que ya usa el adaptador externo. El "modelo efectivo del reviewer y del implementer" para la verificación es, por tanto: config de delegación (externo, pre) + fila durable (cualquier ruta, post) + frontmatter (CC, pre).

### Cómo determinar la «familia» sin lista de proveedores

Hechos verificables del mapa (`scripts/cdad-models.sh`): el **proveedor no es la familia** — un mismo gateway sirve `deepseek-v4-pro/flash`, `glm-5.2`, `qwen3.7-plus/max`, `minimax-m3` bajo el mismo prefijo `mofgw/`. La convención ya establecida en el repo es **comparación de strings exacta sin inferir familia** (`ADR-007`, y `scripts/validate-subagents.sh:234-242`: "Exact string comparison — detects misconfigured envs … without needing to infer model family"), incluido el guard de Claude Code (`:244-258`, con `basic` exento).

Propuesta (determinista, sin tabla de proveedores):
1. **Chequeo duro = igualdad exacta** de los dos modelos efectivos: si son iguales → misma familia, aviso inequívoco (conserva la convención existente y no inventa taxonomía).
2. **Aviso de familia = token derivado del *stem* alfabético inicial del id del modelo** (después del último `/`): `deepseek-v4-pro`→`deepseek`, `glm-5.2`→`glm`, `qwen3.7-plus`→`qwen`, `minimax-m3`→`minimax`, `claude-sonnet-4-5`→`claude`; si difieren, la familia se declara **garantizada por configuración**; si coinciden con ids distintos, aviso de misma familia.
3. **Límite honesto declarado (fail-open conocido):** con alias de Claude Code (`sonnet` vs `opus`) el stem no identifica la familia real (todo Anthropic). El script **no** debe prometer lo que no sabe: con alias conocidos (lista corta de alias del runtime CC, no un inventario de proveedores) debe reportar **"no verificable"**, nunca "garantizada".
4. Si un rol no tiene modelo (falta la entrada, o no se observó fila) → **"invariante no garantizado"**, siempre, nunca silencio.

### Dónde registra el gate «invariante no garantizado»

- La **declaración** ya existe en la capa de agente: `sources/agents/adapters/opencode.md:76-83` y `claude-code.md:98-105` ("write *invariant not guaranteed* at the review gate instead of omitting it"), compuestas a `agents/cdad-orchestrator.md:199` y `agents/claude-code/cdad-orchestrator.md:204`; la §2 del skill declara el invariante como "garantizado por configuración … y declarado cuando no" (`SKILL.md:77-82`) y los invariantes de rol en `SKILL.md:168`.
- El **gate** es la 3→4/4→5 de la review: `review.md` existe y los bloqueantes están resueltos (`SKILL.md:363`, `:538`; `references/stage-4-review.md:72` referencia el verdict-tuple). Recomendación: la declaración vive en el **texto de `review.md`** (artefacto del reviewer, materializado por el orquestador — ADR-003) y se registra en el intento (`runtime`/`model_configured`/`model_reported`/`session`) con los campos ya cerrados (I8, `cdad_delegate.py:177-190`), sin inventar un campo nuevo de estado.
- **Brecha a cubrir por la spec:** hoy el chequeo de familia **no existe como script**; sólo el mapa por perfil (`validate-subagents.sh:216-242`) y el guard de igualdad estática. Con el instalador siempre `basic` el guard del validador pasa **vacuamente** (`:226` `continue` con expected vacío; `:240`/`:252` con `-n`), es decir: deja de proteger. El script de comparación (runtime-independiente) es nuevo y su lugar natural es `skills/cdad-cycle/scripts/` (junto a `cdad_delegate.py`), porque el gate corre desde el proyecto y el principio de capas pone los scripts como capa independiente del runtime (`plan.md` §8).

---

## 4. Credencial del servidor OpenCode (plan §9.5)

**Estado actual (verificado):** el adaptador **no carga ningún `.env`**. `_preflight_password()` sólo lee `os.environ` (`cdad_delegate_opencode.py:935-945`): `OPENCODE_PASSWORD` y si no `OPENCODE_SERVER_PASSWORD` (el primero presente gana, aunque sea incorrecto). El preflight hace `GET <server>/api/info` con Basic auth `opencode:<password>` (`:970-1023`) y clasifica `401/403` como `unauthorized` (`:1010`). El diagnóstico actual (`:1056-1060`) nombra **las dos variables** y aclara "(never its value)", pero **no nombra ruta ni archivo** y no menciona permisos. El dueño cargó la credencial en el entorno del proceso que despacha a mano (`execution.md:185`).

**Qué falta y dónde va:**
1. **Carga del `.env`:** en el adaptador OpenCode, **sólo en modo `server`** (el preflight del servidor es el único punto que usa la credencial: `_preflight_server` `:1026-1067`). Orden propuesto: variables de entorno explícitas primero (permiten override del operador) y, si ninguna está presente, el archivo: `credential_env_file` de la config de delegación, o el default `<config-dir>/cdad/opencode-server.env`. Claves aceptadas: `OPENCODE_PASSWORD` y/o `OPENCODE_SERVER_PASSWORD`. Sin valor en el archivo ⇒ se trata como ausente (nunca se manda un header vacío, criterio ya fijado en `:939-941`).
2. **Verificación de permisos:** rechazar si el modo tiene cualquier bit de grupo u otros (`S_IMODE(st.st_mode) & 0o077 != 0`), es decir aceptar 600 (y 400, más estricto). Verificar sobre el **fd abierto** (`os.fstat`) y no con un `stat` previo, reutilizando el patrón inode/TOCTOU que ya existe en `skills/cdad-cycle/scripts/cdad_packet.py:1275-1320`. Diagnóstico cuando está más abierto que 600: nombrar la ruta, el modo encontrado y el comando de arreglo, sin el valor.
3. **Texto del diagnóstico de 401/403** (reescritura del de `:1056-1060`). Debe nombrar, sin exponer el valor:
   - variables: `OPENCODE_PASSWORD`, luego `OPENCODE_SERVER_PASSWORD`;
   - ruta: el `credential_env_file` resuelto, o el default `<config-dir>/cdad/opencode-server.env`;
   - de dónde sale el valor: la contraseña del `opencode serve` que se use (con OpenChamber, su configuración) — texto del plan §9.5; y que debe estar en el entorno del proceso que despacha;
   - caso permisos: "el archivo existe pero su modo (NNN) es más abierto que 600".
4. **Instalador:** crea el dir de config y dos archivos — `delegation.json` (plantilla) y `opencode-server.env.example` **sin valor**, con la explicación de dónde sale la contraseña y la instrucción de copiarlo a `opencode-server.env` con 600. Idempotente: no debe pisar un archivo que ya existe (política de conflicto del instalador, `install.sh:790-857`, `:1013-1020`).

**Desconocidos declarados:** la relación exacta OpenChamber↔`opencode serve` (contraseña) la afirma el plan y **no la pude verificar en el repo** → queda como afirmación documental a confirmar por el dueño; y el formato del `.env` (¿admite `export`, comillas, comentarios?) lo decide la spec (propongo el subconjunto `KEY=value` + `#`).

---

## 5. Hallazgo del despliegue — ¿entra en esta feature?

**Hecho (evidencia):** `execution.md:213-214` — al desplegar 006-002, las dos referencias retiradas (`opencode-delegation.md`, `claude-code-delegation.md`) quedaron en HOME como `pending_removal`; sólo `install.sh --uninstall` las borró. Mecánica verificada: el manifiesto las **conserva** al reinstalar (`install.sh:917-946`, `:958`), `--check` las **reporta y falla** (`:1499-1526`), y sólo `--uninstall` las retira (`:1150-1211`, `:1170`). El archivo retirado sigue físicamente en el árbol instalado y un orquestador puede seguir leyéndolo (hoy existen, no instalables, en `docs/evidence/runtime-delegation/`; el árbol instalable los declara ausentes en `tests/validate-consistency.sh:260` y `:586`).

**Evaluación:** sí, el instalador debería retirar en la instalación lo que él mismo instaló y ya no despliega — y el mecanismo **ya existe**: `uninstall_by_manifest` compara el sha256 registrado con los bytes actuales y **preserva** lo modificado localmente (`:1196-1207`). Es decir, la semántica pedida ("sin tocar archivos ajenos ni modificados localmente") está implementada; sólo está atada a `--uninstall`. La instalación podría aplicar esa misma regla al conjunto que hoy calcula como `pending_removal` (`:938-946`): retirar los que (a) están en el manifiesto anterior, (b) **no** se redespliegan en esta corrida, (c) **no** están en conflicto, y (d) tienen sha256 igual al registrado; dejar intacto todo lo demás.

**¿Cabe en esta feature?** Recomiendo **sí, como unidad propia y pequeña**, porque: (i) 006-003 ya toca `install.sh` y su aceptación es "`install.sh --check` pasa"; (ii) sin esto, cada instalación normal deja el `pending_removal` del marker de perfil (§1.1) y el `--check` seguiría fallando; (iii) el cierre de 006-002 ya trasladó el hallazgo a 006-003 (`execution.md:214`). Alternativa conservadora (marcada para el dueño): dejarlo afuera y abrir una feature aparte, si se prefiere no mezclar borrado en HOME con el cambio de perfiles. Detalles a resolver en la spec: `--dry-run` muestra las bajas; opt-out explícito; el python del manifiesto **no recibe hoy `INSTALL_ROOT`** y las rutas del manifiesto pueden ser absolutas (`install.sh:1447-1449`, `:1506-1509`) → hay que pasarlo para resolver rutas correctamente.

---

## 6. DECISIONES, CRITERIOS DE ACEPTACIÓN y RIESGOS

### Decisiones (con recomendación y evidencia)

- **D1 — Alcance del cambio de perfil.** El instalador y el generador dejan de tener perfiles y mapa de modelos. *Recomendación:* sí, y **conservar `--basic` como alias aceptado y sin efecto** por un ciclo, o actualizar los ≥6 tests que lo usan en la misma feature (elegir una, no ambas). *Evidencia:* `plan.md` §9.1; `install.sh:459-472`; receta de tests en §1.6. *Por qué:* quitar el flag a secas rompe la receta de "instalación aislada" de toda la suite.
- **D2 — Modelo de la ruta nativa.** CDAD no lo fija ni lo adivina: lo toma de la config del runtime (frontmatter/`agent.<name>.model`) y, cuando no puede observarlo, lo **declara** no garantizado. *Evidencia:* `plan.md` §9 principio; `sources/agents/adapters/opencode.md:76-83`; `execution.md:200` (observación no investigada). *Recomendación:* la verificación de familia consume el modelo **observado** (fila durable) y el **configurado** (config de delegación / frontmatter), y reporta "no verificable" cuando falta.
- **D3 — Fuente única del modelo en la delegación externa.** La config de delegación, y sólo ella. *Recomendación:* estricta con diagnóstico de deprecación para la clave `model` de la exec-config; sin fallback silencioso. *Evidencia:* `plan.md` §9.3; `cdad_delegate_opencode.py:1678`.
- **D4 — Forma de la verificación de familia.** Igualdad exacta de strings como chequeo duro + token de stem como aviso, sin tabla de proveedores, con límite honesto para alias. *Evidencia:* `cdad-models.sh` (un gateway, varias familias); `validate-subagents.sh:234-242`; `ADR-007` (no inferir familia).
- **D5 — Credencial.** Env vars → `.env` (default o `credential_env_file`), sólo modo `server`, permisos sobre el fd, diagnóstico que nombra variables/ruta/procedencia. *Evidencia:* `cdad_delegate_opencode.py:935-945`, `:970-1060`.
- **D6 — Retiro de obsoletos en instalar (punto 5).** Sí, reutilizando la regla owned+sha256 de `uninstall_by_manifest`. *Evidencia:* `install.sh:1150-1211`, `:917-946`, `:1499-1526`; `execution.md:213-214`.
- **D7 — `SKILL.md` §2.** La frase "garantizada por configuración cuando el perfil fija modelos / declarada cuando no" se reescribe **sin perfiles**: la familia pasa a ser una **verificación de configuración** con declaración cuando no es verificable. *Evidencia:* `SKILL.md:77-82`; el test que la fija, `test_006_002_u4_skill_without_models.py:153-180` (conceptos 6/7/8 dependen de la palabra "perfil").

### Criterios de aceptación (verificables; incluyen los del plan §9)

- **AC-1 (plan §9.1).** `grep -nE -- '--(economical|optimus|premium)' install.sh` → vacío; `Makefile` sin `PROFILE`; `make staging` corre sin `--profile` y `build/staging/manifest.json` no declara perfil (o declara `basic` constante); ningún `agents/**/*.md` tiene `^model:` (21 líneas menos). Control negativo: `install.sh --check` PASS.
- **AC-2 (plan §9.2).** En una raíz redirigida, la instalación crea `<cfg>/cdad/delegation.json` (plantilla) y `<cfg>/cdad/opencode-server.env.example` **sin valor**, con la explicación; con `XDG_CONFIG_HOME` fijada los usa; una segunda instalación **no** pisa un archivo ya editado por el usuario.
- **AC-3 (plan §9.3).** `skills/cdad-cycle/assets/opencode-exec-config.example.json` sin clave `model`; con una exec-config que declara `model`, el modelo efectivo **no** cambia y aparece el diagnóstico de deprecación; con un rol sin entrada en la config de delegación, el argv del destino **no** lleva `--model` y el intento registra `model_configured: null`.
- **AC-4 (plan §9.4).** Con fixtures: (a) reviewer e implementer con el mismo modelo → aviso de misma familia; (b) modelos distintos y conocidos → "garantizada por configuración"; (c) falta uno o alias no interpretable → "no verificado / **invariante no garantizado**"; y el texto de `review.md`/orquestador registra la declaración en (c).
- **AC-5 (plan §9.5).** Con un fixture de servidor que exige credencial: sin credencial el diagnóstico permite resolverlo **sin otra documentación** (nombra variables, ruta y procedencia); un `.env` con modo 0644 se **rechaza** con diagnóstico claro; el valor **nunca** aparece en stdout/stderr/argv ni en el registro I8 (oráculo de ausencia con centinela).
- **AC-6 (plan §9).** `install.sh --check`, `make validate` y la suite pasan.
- **AC-7 (plan §9).** El orquestador y los scripts no nombran modelos: `grep -rE 'deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/' skills/ agents/cdad-orchestrator.md agents/claude-code/cdad-orchestrator.md` → vacío.
- **AC-8 (punto 5, si entra).** Instalar sobre una raíz con `pending_removal` de archivos propios **no modificados** los retira y `--check` no los reporta; un archivo propio **modificado localmente** se preserva, se reporta como CONFLICT y sigue registrado; ningún archivo no registrado se toca.

### Riesgos

- **R1 — Tests acoplados a perfiles** (tabla §1.6): la matriz de 4 perfiles (`test_004_001_acceptance_matrix.py`), `PD-14` (`test_cdad_generate.py:363-405`), `F008` (`validate-consistency.sh:463-471`), `u4` (`test_006_002_u4…:153-180`), `u1` (`test_006_002_u1…:121-127`), review-5 B4 (`test_install_review5_regressions.py:401-480`) y `test_install_ownership.py:281-308`. Mitigación: reescribir el oráculo a la vez que el producto, declarando el reemplazo (no borrar el assert, reformularlo — convención ya usada en `validate-consistency.sh:293-309`).
- **R2 — Consumidores que usan flags de perfil.** `install.sh --basic|--economical|--optimus|--premium` está en recetas locales y en `execution.md:110` (`make staging PROFILE=basic && bash install.sh --force --basic && …`). Mitigación: aceptar `--basic` como alias deprecado o migrar la receta en la misma feature.
- **R3 — Compatibilidad de exec-configs existentes.** El consumidor tiene exec-configs con `model`. Sin fallback silencioso, su modelo efectivo cambia (pasa al default del destino). Mitigación: diagnóstico explícito + guía de migración en `cli-delegation.md`; decisión del dueño entre estricto y fallback.
- **R4 — Diff grande en `agents/`**: 21 líneas `model:` + el párrafo `models_note` + la §2 de los orquestadores. Intencional, pero hay que declararlo para que no se lea como pérdida accidental del diseño.
- **R5 — Estado del staging.** Un checkout con `build/staging` de `optimus` (o al revés) deja de tener un caso de mismatch con sentido; el test review-5 B4 pierde objeto y hay que retirarlo/reformularlo declarándolo.
- **R6 — DT-8 (`__pycache__`) e interacción con el retiro.** El prune del punto 5 retiraría el `.pyc` registrado, pero el uso vuelve a crearlo y el staging lo sigue incluyendo (deuda DT-8 declarada, `execution.md:103`, `:181`). Mitigación: no mezclar; DT-8 sigue aparte y el prune no debe prometer que el árbol queda "limpio".
- **R7 — Familia heurística (fail-open).** `sonnet` vs `opus` es la misma familia real; el stem no lo sabe. Mitigación: declarar el límite, reportar "no verificable" con alias, y no convertir el aviso en gate duro.
- **R8 — Nueva superficie de lectura de credencial.** Leer un `.env` por una ruta de config añade un camino que puede apuntar a cualquier archivo. Mitigación: no imprimir valores ni eco del archivo, verificar permisos sobre el fd abierto, y que el diagnóstico nombre la ruta sin el contenido.
- **R9 — `model_reported` vs `model_configured`.** Al sacar el modelo del orquestador, la divergencia destino↔config es más probable y debe **registrarse**, no interpretarse como éxito.

### Desconocidos (marcados, no cero)

- Si el runtime OpenCode honra `agent.<name>.model` sobre el frontmatter de un agente markdown custom (`ADR-007` enmienda 2 lo deja "verificar en runtime"; `execution.md:200` observó una anomalía no investigada).
- La relación exacta de contraseña con OpenChamber (`plan.md` §9.5 lo afirma; no verificable desde el repo).
- Si el manifiesto de staging puede quedar sin `profile` sin romper consumidores no auditados (p. ej. scripts locales del dueño).

---

**Resumen de evidencia (comandos de solo lectura ejecutados):** `sha256sum docs/epics/…/plan.md`; `ls -R`, `wc -l`, `head`, `sed -n` sobre `install.sh`, `Makefile`, `scripts/cdad-models.sh`, `scripts/cdad-generate.py`, `scripts/validate-subagents.sh`, `skills/cdad-cycle/**`, `sources/agents/adapters/*`, `agents/**`, `tests/*`; `grep -n/-rn/-rc` por perfiles, `model`, `cdad_model`, `pending_removal`, `XDG_CONFIG_HOME`, `OPENCODE_PASSWORD`, `not guaranteed`; `git log/status/diff --stat`; `python3 -c` sobre `build/staging/manifest.json`. **Ningún archivo fue modificado, ningún test corrido, ninguna instalación ni escritura en HOME.**
