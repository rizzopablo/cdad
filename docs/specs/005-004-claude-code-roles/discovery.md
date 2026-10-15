# Discovery — 005-004-claude-code-roles

Rol: architect (etapa 1, subetapa discovery). Paquete `005-004-claude-code-roles-architect-discovery-001`,
execution `exec-005-004-claude-code-roles-001`. Contrato: `docs/epics/epic-005-real-operation/plan.md`
(fila 10, `:43`; sha256 `b22bc687…bec16`). Fecha de observación: 2026-10-13.
**No se propone contrato** (eso es la subetapa draft). Escritura en el repo: ninguna.

## 0. Método, alcance y honestidad

- Lectura y ejecución **read-only**. Ningún archivo del repo fue modificado por esta tarea: el único
  cambio en el árbol es `M docs/.cdad-state.json`, preexistente (`git status --porcelain`). No escribí
  en HOME: solo lo inspeccioné (el encargo §3 lo pide explícitamente); "no tocar HOME" es no cambiarlo.
- Temporales declarados: `/tmp/opencode/cc-check.out` (salida de `install.sh --check`) y este archivo
  `/tmp/opencode/discovery-005-004.md`.
- Versión observada: repo en `e74c0bc` (rama `codex/epic-005-real-operation`); instalación global
  `9d89a4b8ca139b1d589ba438860f08e94c03943a`. `git diff --stat 9d89a4b HEAD` = **1 archivo, docs**
  (`005-007/closure.md`, +9) ⇒ el **producto** instalado es idéntico al de HEAD.
- Todo dato no verificado está marcado **VERIFY**; toda incoherencia observada se declara **sin corregirla**.
- Lo que pertenece al dueño no se decide aquí: activar versiones en el repo real, cambios en HOME
  (`~/.claude`, `~/.agents`, `~/.config/opencode`), la confianza de carpeta de Claude Code
  (`docs/epics/epic-005-real-operation/execution.md:19-23`).

---

# (a) Entidades verificadas archivo:línea

## 1. Qué existe hoy para Claude Code en este producto

### 1.1 Agentes y layout

- Fuente canónica del adaptador: `sources/agents/adapters/claude-code.md` (52 líneas, secciones
  `frontmatter` `:9-26`, `permissions` `:28-43`, `tool-loading` `:45-50`).
- Layout declarado: `~/.claude/agents/cdad-<role>[-odoo].md` (`:10`).
- Derivados declarados en el repo: `agents/claude-code/cdad-*.md` — **11 archivos**
  (5 roles × base/odoo + orchestrator), generados por `scripts/cdad-generate.py`
  (`cc_frontmatter` `:489-507`) y promovidos por `make agents` (`Makefile:17-20`); `make staging`
  genera ambos runtimes (`Makefile:12-15`).
- Conteo declarado por el instalador: `install.sh:74` `EXPECTED_CDAD_AGENTS_CLAUDE_CODE=11`
  (comentario `:71-73`: mismo pase driven-by-staging).
- Herramientas por rol (verificado en los derivados, `:4` de cada archivo):
  `architect|architect-odoo|reviewer|reviewer-odoo|scribe|scribe-odoo` → `Read, Grep, Glob, Bash, Skill`;
  `implementer|-odoo|test-writer|-odoo` → `+ Edit, Write`; `orchestrator` → `+ Task, Skill`.
- **No hay bloque YAML de permisos**: el path-scoping se expresa con el hook, no con claves de permiso
  (`sources/agents/adapters/claude-code.md:24-25`).
- Hooks PreToolUse por rol (verificado en los derivados):
  - implementer / implementer-odoo → `matcher: Edit|Write` → `~/.claude/cdad-scripts/path-guard.sh <rol>`;
  - test-writer (`agents/claude-code/cdad-test-writer.md:6-17`) → **dos** matchers:
    `Read|Grep|Glob` → `path-guard.sh test-writer-read` y `Edit|Write` → `path-guard.sh test-writer-write`;
  - architect, reviewer, scribe, orchestrator → **sin hooks** (read-only por contrato, no por mecanismo).
- **Ningún agente CC lleva matcher `Bash`** (decisión del dueño 2026-09-29): verificado en producto por
  `tests/validate-consistency.sh:195-203`; la política permisiva de bash está en
  `scripts/claude-code-path-guard.sh:30-35`.
- Fail-open de rol desconocido: `scripts/claude-code-path-guard.sh:431-434`.

### 1.2 Qué hace `install.sh` para CC

- Destinos reales: `CLAUDE_CODE_AGENTS_DIR="$INSTALL_ROOT/.claude/agents"` (`install.sh:51`),
  `CLAUDE_CODE_SKILLS_DIR="$INSTALL_ROOT/.claude/skills"` (`:52`),
  `CLAUDE_CODE_SCRIPTS_DIR="$INSTALL_ROOT/.claude/cdad-scripts"` (`:53`);
  `INSTALL_ROOT="${CDAD_INSTALL_ROOT:-${HOME:-}}"` (`:45`).
- Agentes: el staging `agents/claude-code/*` se mapea a `<root>/.claude/agents/<name>`
  (`staged_destinations` `:696-700`) y el despliegue es `cp -p` de los bytes staged
  (`stage_one_destination` `:742-796`). **No hay post-proceso que quite el campo `model`** (ver §3.3).
- Skills: `install_skills()` `:1037-1045` sincroniza **cada** skill de `SKILLS` (`:62`:
  `cdad-cycle cdad-epic cdad-spec-and-test odoo-architect odoo-test-writer odoo-reviewer odoo-make-env
  odoo-expert`) a `~/.claude/skills/<s>`, archivo por archivo (`sync_skill_to` `:1012-1034`).
- Guard: `scripts/claude-code-path-guard.sh` → `~/.claude/cdad-scripts/path-guard.sh` con `+x`
  (`install_guard_script` `:1065-1078`).
- **Marcador de versión**: `<root>/version.txt` (`write_version_marker` `:638-641`, invocado `:1736-1737`;
  `INSTALL_VERSION` `:111`).
- **Manifiesto de propiedad**: `<root>/.cdad-install-manifest.json` (`OWNERSHIP_MANIFEST` `:104`,
  `write_ownership_manifest` `:869+`) con `manifest_version`, `installer`, **`source_version`**
  (PD-14/INV-7), `runtime`, `stack`, `profile`, `artifacts{rel→sha256+source}`, `pending_removal`,
  `conflicts`.
- `--check`: `main()` `:1660-1677` → `check_installed_staging()` `:1422+` compara **byte a byte** lo
  instalado contra el staging **local** vigente y reporta `OK` / `DRIFT` / `OBSOLETE` por artefacto.
  El staging no está versionado: `build/` está en `.gitignore:12` (`git ls-files build` = 0 archivos).

### 1.3 El guard de CC: dónde vive y qué necesita

- El archivo que citan los agentes instalados es `~/.claude/cdad-scripts/path-guard.sh`; su fuente en el
  repo es `scripts/claude-code-path-guard.sh`; instalado y repo son **byte-idénticos**
  (sha256 `e5ab39f45234…1e9` en ambos).
- v2 dinámico (`:16-28`): si el proyecto tiene `docs/cdad-policy.json`, clasifica cada ruta con el
  **clasificador instalado** (`cdad_packet.py validate-policy --classify`), con CLI por defecto
  `$HOME/.claude/skills/cdad-cycle/scripts/cdad_packet.py` y override `CDAD_PACKET_CLI` (`:134-138`);
  si falta el clasificador **bloquea sin fallback**.
- Usa `CLAUDE_PROJECT_DIR` que CC exporta a sus hooks como raíz del proyecto (`:50-53`).
- Requisitos: `jq` (presente: `/usr/bin/jq`, 1.7) y `python3`.
- Barreras retenidas (`:176-226`): nadie edita la política ni `.opencode/agents/**`; `private` se niega a
  todo rol; implementer no edita `test|colocated-test`; test-writer no lee `implementation` y solo edita
  `test|colocated-test`; Grep/Glob sin `path` acotado se bloquea (`:86-95`).
- Modo legacy sin política (globs globales `tests/**`, `**/*_test.go`, `**/test_*.py`, …): `:327-341`.

### 1.4 Skills y CLI en CC

- Instaladas en `~/.claude/skills/`: `cdad-cycle`, `cdad-epic`, `cdad-spec-and-test` y las 5 `odoo-*`.
  Verificado: `diff -r -x __pycache__` contra el repo → **sin diferencias** en las 8 skills declaradas.
- CLI disponible para una sesión CC: `~/.claude/skills/cdad-cycle/scripts/` contiene
  `cdad_packet.py`, `cdad_result.py`, `cdad_continuity.py`, `cdad_delegate.py`,
  `cdad_delegate_opencode.py`, `cdad_guard.py`, `cdad_context_meter.py`, `cdad-version-check.py`.
  **Esto cierra la deuda D-3 de 005-007** ("ruta del CLI en Claude Code para el ciclo real de 005-004",
  `docs/specs/005-007-progressive-planning/spec.md:147,180`): la ruta es la del árbol de skill instalado.
- Carga de skills: el adaptador declara el tool `Skill` (capital S) (`sources/agents/adapters/claude-code.md:46`)
  y los agentes CC incluyen `Skill` en `tools:`.

### 1.5 Qué roles existen, permisos, y qué **no** garantiza el perfil vigente

- Roles CC (11): architect/-odoo, test-writer/-odoo, implementer/-odoo, reviewer/-odoo, scribe/-odoo,
  orchestrator.
- Permisos efectivos: sin permission-block; solo los hooks de §1.1; bash permisivo; fail-open.
- **Perfil instalado = `basic`** (tres evidencias independientes: marcador
  `~/.config/opencode/agents/.cdad-models-profile` = `basic`; manifiesto `profile: basic`;
  `~/version.txt` = `9d89a4b…`). Con `basic`, `cdad_model_claude` devuelve vacío
  (`scripts/cdad-models.sh`, rama `[ "$perfil" = "basic" ] && return 0`) ⇒ **los 11 agentes CC
  instalados no llevan `model:`** (`grep -c '^model:' ~/.claude/agents/cdad-*.md` = 0 en los 11).
- Consecuencia verificada: **la invariante reviewer≠implementer NO queda garantizada por el instalador
  con el perfil vigente**. El guard anti-sesgo la **exime** explícitamente para `basic`
  (`scripts/validate-subagents.sh:249-257`: `ACTIVE_PROFILE != "basic"`), con el trade-off declarado en
  ADR-007. En el perfil `optimus` (perfil de diseño del repo) los derivados sí llevan
  `architect/test-writer/scribe=sonnet`, `implementer=haiku`, `reviewer/orchestrator=opus`
  (verificado en `build/staging/agents/claude-code/*.md` y `agents/claude-code/*.md`) ⇒ ahí
  reviewer(opus)≠implementer(haiku).
- Mecanismo alternativo **observado** (no garantía del instalador): la invocación nativa acepta `model`
  por llamada — en los transcripts de CC reales hay llamadas `Agent` con `"model": "opus"` explícito.
- **VERIFY**: si un subagente CC sin `model:` hereda el modelo de la sesión (`~/.claude/settings.json`
  declara `model: opus`, `effortLevel: low`) o un default del runtime. No se probó (implicaría escribir
  y consumir cuota).

### 1.6 Documentación de instalación/adopción sobre CC, y lo no verificado

- `README.md` (276 líneas) **no menciona Claude Code** (`grep -i claude README.md` = 0): la instalación
  CC no está documentada en el README.
- Sí está documentada en: `install.sh --help` (`:393-407`, destinos CC + "never touched" `:423`),
  `sources/agents/adapters/claude-code.md`, `skills/cdad-cycle/references/claude-code-delegation.md`
  (mecanismo `Agent`/`subagent_type` `:7-26`, hooks `:41-61`, profundidad 3 `:63-69`),
  `skills/cdad-cycle/references/runtime-adoption.md` (activación por proyecto para `claude-code`,
  `:26-33`), `skills/cdad-cycle/references/cli-delegation.md`.
- **Incoherencia observada 1 (declarada, sin corregir):** el adaptador declara en `:13-14`
  `tools: … Task for orchestrator` y en `:46-49` que la delegación usa el tool **`Agent`**
  (`subagent_type: cdad-<role>`); el derivado `agents/claude-code/cdad-orchestrator.md:4` declara
  `Task`. Los transcripts reales usan **`Agent`** con `subagent_type` (6 llamadas; ver §4).
- **Incoherencia observada 2 (declarada, sin corregir):** el adaptador afirma
  ("the installer STRIPS the model field at install time", `:15-17`). Verificado que el instalador **no**
  quita el campo: copia los bytes staged (`stage_one_destination` `:742-796`) y el staging del repo
  **tiene** `model:`. La observación de origen ("los archivos instalados son más chicos por la línea
  model") es cierta, pero su causa es el **perfil `basic`** (`cdad_model_claude` vacío), no un strip.
- **VERIFY (sin resolver):** (i) que CC honre `exit 2` de un hook en modo `-p` (print); (ii) que los hooks
  del frontmatter se apliquen a subagentes nativos; (iii) la herencia de modelo de un subagente sin
  `model:`; (iv) que el criterio "mapa de qué carga una sesión CC" se pueda cerrar sin una sesión viva.

---

## 2. Qué falta para un ciclo real despachado desde Claude Code

### 2.1 Lo entregado por 005-009/005-010 y su contrato

- **Interfaz común:** `skills/cdad-cycle/scripts/cdad_delegate.py` (298 líneas). Flags
  `--project-root/--packet/--destination/--exec-config`; vocabulario de terminación y claves de salida
  (`:48-51`); adaptador resuelto por convención `cdad_delegate_<id>.py` (`ADAPTER_PREFIX` `:54`,
  resolución `:88`, ayuda `:245`); `delegate()` `:252`.
- **Adaptador OpenCode:** `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (929 líneas).
  - elige el id de sesión y lo pasa en `--session <id>` (`:147`, `:259`, `:269`);
  - `--standalone` por defecto (servidor privado), `--server <url>` alternativa, `--auto` configurable
    (`:269-275`);
  - señal durable = store SQLite del runtime declarado por `sessions_db` de la config, abierto `mode=ro`;
    espera acotada por `wait.timeout_seconds` (`:805-862`);
  - clasificación desde `idle_outcome` (`:697`); fallo cerrado con diagnóstico nombrado (`:352`, `:420`,
    `:514-517`).
- **Transporte/contrato del adaptador** (documento canónico `references/cli-delegation.md`):
  `PACKET.md` **byte-idéntico por stdin** (`:85`), argv `--project-root/--packet-id/--destination
  [--exec-config]` (`:86-87`), un envelope JSON por stdout con las mismas claves (`:88-89`), exit 0 si
  el adaptador corrió (`:90`); "un adaptador por destino" (`:75-79`); límites honestos (`:172-183`).
- **Reutilización verificada en este repo (no solo en tests):**
  - `.cdad/local/exec-config-005-007-architect-discovery.json` + `.cdad/local/runs/005-007-discovery.delegate.json`
    → `{"attempt":"delegate-opencode-2ac2addcb404","termination":"completed","session":"ses_bd66a7…",
    "delivery_ref":"…/receipt.json"}`.
  - La aceptación PD-10 de 005-010 (paso a) corrió `cdad_delegate.py` **desde una sesión de Claude Code**
    (`docs/specs/005-010-real-opencode-delegation/evidence/pd10-acceptance.md:38-58`): coordinador = esa
    sesión CC, `PWD` ≠ proyecto, worker = OpenCode, salida `completed` + recibo `semantic_status: pending`
    + ledger I8 con dos registros (interfaz y worker).

### 2.2 Qué exigiría un adaptador Claude Code concreto

Reutilizable **tal cual**: el contrato stdin/argv/stdout/exit, la resolución por módulo, el transporte
byte-idéntico, el esquema de salida, el registro I8 con `provenance`, el recibo por `receive`, la
reconciliación y la configuración portable (`--exec-config`, local/git-ignored).

Del específico de CC (verificado contra `claude --help`, CC 2.1.296; el resto es **VERIFY**):

- **Entry no interactiva:** `claude -p` (print) con `--agent cdad-<rol>`; `--agents <json-o-archivo>`
  permite definir el agente sin depender del instalado. `--print` **omite el diálogo de confianza de
  carpeta** (help de `-p`: "The workspace trust dialog is skipped when Claude is run in non-interactive
  mode … Only use this in directories you trust").
- **Transporte:** stdin debe llevar el `PACKET.md` byte-idéntico. **VERIFY**: que `-p` tome el prompt de
  stdin en esta versión (no se ejecutó: escribiría en HOME y consumiría cuota).
- **Correlación:** `--session-id <uuid>` (help: *must be a valid UUID*) ⇒ a diferencia de OpenCode
  (`ses_…`), el id debe ser UUID y la ruta derivada depende del slug del cwd.
- **Señal durable candidata:** el transcript JSONL del runtime en `~/.claude/projects/<slug-cwd>/<session-id>.jsonl`.
  Existe y **persiste** (se observó un transcript con `entrypoint: sdk-cli`, es decir no interactivo;
  el flag `--no-session-persistence` "only works with `--print`" ⇒ por defecto persiste). Cada registro
  lleva `sessionId`, `version`, `timestamp`; los `assistant` llevan `message.model` y `message.usage`
  (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`); hay tipos
  `agent-name` y registros de subagente (`isSidechain`).
- **VERIFY crítico:** no se observó un hecho material de **fin de corrida** equivalente al `idle_outcome`
  de OpenCode (no hay tipo `result`; el último registro observado fue `cost-state` con `totalCostUSD`).
  Si no es inequívoco, el adaptador debe **fallar cerrado** (PD-2 de 005-010), no degradar a `completed`.
- **VERIFY crítico:** que la señal durable permita **verificar el agente** (registros `agent-name`/sidechain);
  si no, no puede cumplirse PD-3/INV-6 (identidad sin fallback a un agente genérico).
- **Permisos no interactivos:** `--permission-mode {acceptEdits|auto|bypassPermissions|manual|dontAsk|plan}`,
  `--allowedTools/--disallowedTools`, `--permission-prompts none`, `--dangerously-skip-permissions`.
  Documentar que **no es sandbox** (INV-8), igual que `--auto` en OpenCode.
- **Aislamiento del host:** `--setting-sources`, `--strict-mcp-config`, `--bare`/`--restricted` como
  superficie para no cargar/ni escribir configuración del dueño.
- **Modelo bajo `basic`:** el agente no lleva `model:` ⇒ el adaptador tendría que pasarlo por config
  (`--model`) y declarar `model_configured`/`model_reported` con provenance, como hoy.

### 2.3 Qué significa «despachado desde Claude Code» — lectura precisa

- **Coordinador** = la sesión de Claude Code (el rol `cdad-orchestrator` en CC, o la sesión CC que hace de
  orquestador). **Quién ejecuta el rol** admite dos mecanismos, y la fila 10 apunta al primero:
  1. **Nativo en CC** (lo que pide "roles CDAD activos en Claude Code para este proyecto"):
     subagente CC con `subagent_type: cdad-<rol>` vía el tool **`Agent`**
     (`skills/cdad-cycle/SKILL.md:501`; `references/claude-code-delegation.md:7-26`). El trabajo del rol
     corre **en CC**, con los agentes instalados.
  2. **Externo**: un adaptador despacha el rol a **otro** CLI. Hoy solo existe OpenCode
     (`cli-delegation.md:108-110`); es la dirección que ya probó 005-010 y **no** deja roles activos en CC.
- **Dónde vive el paquete:** `.cdad/packets/<packet_id>/{REQUEST.json,PACKET.md}`, publicado por
  `prepare` (en este repo: `.cdad/packets/005-004-claude-code-roles-architect-discovery-001/`).
- **Cómo se comporta el worker en CC no interactivo:** `claude -p --agent cdad-<rol>` (o el subagente
  nativo, que ya es no interactivo por diseño). El rol recibe el paquete como prompt/insumo y devuelve su
  texto final + evidencia referenciada (contrato PD-7).
- **Cómo se recibe:** `cdad_result.py receive` **exige** que el paquete activo esté `dispatched`
  (`skills/cdad-cycle/scripts/cdad_result.py:528-532`) y emite el recibo durable con
  `semantic_status: "pending"` (`:574`): la entrega **no** aprueba el gate. En el recorrido **nativo**, el
  texto final del subagente llega al coordinador por el retorno del tool `Agent`; el coordinador lo
  persiste como parte (`staged-file`) y llama a `receive` — exactamente el patrón que ya corrió en este
  repo **desde una sesión CC**: `.cdad/local/receive-005-003.sh` (reescribe el descriptor
  `.cdad/runtime/.<tag>.result.json` con `source.kind: staged-file` y `.cdad/inbox/<name>.md`, luego
  `receive`), con `runtime: opencode` en el intento. Para un ciclo CC el registro I8 debe declarar
  `runtime: claude-code` (esquema cerrado, `cdad_packet.py:2209-2213`).
- **Práctica actual del epic (para no confundirla con la interfaz):** los despachos se hicieron con
  **scripts por feature** — `.cdad/local/dispatch-005-010.sh` y `dispatch-005-003.sh`: `validate-packet`
  → `checkpoint` de continuidad → `attempt.json` con `provenance` → `prepare --record-dispatch` →
  `opencode run --standalone --agent … -m … --auto --title … -- "$(cat PACKET.md)"` en background con
  `timeout 5400` y captura `.out/.err/.rc`. Reutilizan ledger y recibo, pero **duplican el transporte**
  que la interfaz común ya resuelve (lección de 005-009/005-010: un adaptador por destino, no un script).

---

## 3. Estado real de la instalación en HOME y de ESTE proyecto

### 3.1 HOME (observado hoy, sin corregir)

- `~/.cdad-install-manifest.json`: `source_version 9d89a4b8ca139b1d589ba438860f08e94c03943a`,
  `runtime: claude-code`, `stack: odoo`, `profile: basic`, **364 artefactos**, `conflicts: 0`,
  `pending_removal: {}`; mtime 2026-10-13 08:59. Registra los 11 `.claude/agents/*`, el
  `.claude/cdad-scripts/path-guard.sh`, y las skills CC (`cdad-cycle` completa, `cdad-epic`,
  `cdad-spec-and-test`, `odoo-*`).
- `~/version.txt` = `9d89a4b8ca139b1d589ba438860f08e94c03943a`.
- Marcador de perfil: `~/.config/opencode/agents/.cdad-models-profile` = `basic`.
- `~/.claude/agents/`: 11 agentes, **sin `model:`**, mtimes 2026-10-09/10-11; `~/.claude/skills/`: las 8
  skills declaradas (idénticas al repo salvo `__pycache__`); `~/.claude/cdad-scripts/path-guard.sh`
  (idéntico al repo). `~/version.txt` es el **único** marcador; no hay `version.txt` por árbol.
- Coherencia byte a byte: `.claude/agents` vs el staging del repo difiere **solo** por el perfil — 1 línea
  en 10 agentes (`model: <alias>`) y 13 líneas en el orchestrator (`model: opus` **más** la columna de
  modelos de la tabla del contrato de roles). `git diff 9d89a4b HEAD -- agents/claude-code/` = **vacío**
  ⇒ el contenido instalado es el del repo actual, con el perfil `basic`.
- **Copias/artefactos viejos observados** (del dueño; no se tocan):
  `~/.claude/cdad-backup-2026-09-18/` (agentes+skills de septiembre),
  `~/.claude/cdad-scripts/path-guard.sh.bak-20260828`,
  `~/.claude/settings.json.bak-20261002-014433`, `~/.claude/backups/.claude.json.backup.*` (5).
  Además `~/.config/opencode/agents/` contiene agentes **no-Cdad** (`coder`, `general`, `ofap`,
  `ofap-plan`, `probe`, `researcher`, `reviewer`, `scribe`, `bootstrapper`): es el namespace donde
  PD-3/PD-4 de 005-009 **prohíben** caer. (En `~/.claude/agents/` no hay agentes no-Cdad.)
- **Confianza de carpeta:** `~/.claude.json` → `projects["<repo>"]
  .hasTrustDialogAccepted = false` (**este proyecto**); el padre
  `<repo>/..` = `true`. Evidencia de la práctica:
  `~/.claude/projects/<padre>/` tiene transcripts (2 `.jsonl`, uno de 40 MB
  actualizado hoy) y `…-cdad-cdad/` solo contiene `memory/` ⇒ **ninguna sesión CC corrió con cwd = este
  repo**; las sesiones CC de este epic corrieron desde el **padre** confiable.
- `~/.claude/settings.json`: `model: opus`, `effortLevel: low`,
  `permissions.allow: [Bash, Read, Edit, Write, Glob, Grep]`, hooks globales = nodeterm (no CDAD).
  `~/.claude/CLAUDE.md` es la identidad MOF del dueño (no menciona CDAD).

### 3.2 ESTE proyecto

- **Sin `.claude/`** (no hay agentes CC de proyecto) y **sin `.cdad/activation.json`** ⇒ la activación por
  proyecto para CC (`scripts/cdad-activate.py --runtime claude-code`,
  `references/runtime-adoption.md:26-33`) **no está emitida** aquí.
- Derivados de proyecto (OpenCode): `.opencode/agents/` (11) + `.opencode/agents/.cdad-derived.json` con
  `policy_sha256 f508ab1e…`, `source_dir <home>/.config/opencode/agents`,
  `source_version 9d89a4b8…`. Es el artefacto que fija la versión **para OpenCode**, no para CC.
- Comprobación de versión hoy (corrida hoy, read-only):
  - `python3 skills/cdad-cycle/scripts/cdad-version-check.py` (checkout) → `CLI: (no version.txt found)`,
    verdict `UNKNOWN`, rc 3 (el checkout no es raíz de instalación: comportamiento F2 del propio check).
  - `python3 ~/.claude/skills/cdad-cycle/scripts/cdad-version-check.py --project-root <repo>` →
    `project/agents/CLI = 9d89a4b8…`, verdict `COHERENT`, rc 0.
  - **Límite verificado:** la pata "agents" del check es la instalación de **OpenCode** (el `source_dir`
    del manifiesto derivado) y la pata "CLI" es el árbol de skill que aloja el script; **no hay pata
    para `~/.claude/agents`**. La coherencia del lado CC se verifica por `install.sh --check` (bytes) y el
    `source_version` del manifiesto de propiedad.
  - `bash install.sh --check` (read-only) → **rc 1**, 342 `OK` y drift en: los 11 agentes CC y los 11 de
    OpenCode (instalado `basic` vs staging local `optimus`) y los árboles `cdad-cycle` (los
    `__pycache__`: src 90 archivos vs instalado 85). **Explicación verificada:** es una condición **local**
    del staging no versionado (`build/` en `.gitignore`) más la deuda conocida de `__pycache__`, **no**
    una incoherencia de versión: el marcador y el `source_version` del manifiesto coinciden, y los bytes
    de contenido coinciden salvo la línea/columna del perfil. Se declara sin corregir.

### 3.3 Qué significaría «activos para este proyecto»

- **Hoy:** "activo" = la instalación **global** de HOME, que es lo que CC carga al arrancar una sesión en
  cualquier cwd. No existe artefacto de proyecto que fije la versión cargada por CC (el manifiesto
  `.opencode/agents/.cdad-derived.json` fija la de OpenCode).
- Vías posibles, con su costo y con quién decide:
  1. **Confiar la carpeta del proyecto** (`~/.claude.json`) → decisión **del dueño**; habilita cwd = repo,
     hooks/agentes con raíz correcta y la resolución de "copias viejas".
  2. **Activación por proyecto para CC** (`cdad-activate.py --runtime claude-code`): emite
     `.claude/agents/*.md` (copiados de una raíz adoptada, con el `command:` del hook reescrito a esa
     raíz vía `CDAD_PACKET_CLI`) y `.claude/skills/<s>` como enlaces, más `.cdad/activation.json`; **todo
     bajo el proyecto, git-ignored**, nunca HOME (`references/runtime-adoption.md:26-39,64-72`). Crea
     copias de proyecto (necesitan dueño explícito por la reserva "copias viejas"); la guía vigente
     pide no introducir raíces aisladas/activación solo para resolver derivados
     (`docs/runtime-adopted-version.md:40-45`).
  3. **Sin artefactos nuevos:** la sesión CC corre desde el **padre confiable** y pasa `--project-root`
     explícito (exigido por PD-3 de 005-009), que es la práctica **observada** en este epic.

---

## 4. Capacidades efectivas y acceso a las entregas (qué consumiría un ciclo en CC)

| Entrega | ¿La consume un ciclo en CC? | Evidencia / límite |
|---|---|---|
| 005-005 procedencia de la instalación | **Sí** | `~/version.txt` + `source_version` del manifiesto + derivados OpenCode; **falta pata CC** en el check (§3.2). Registro de activación: no emitido aquí. |
| 005-005 política única de tests | **Sí** (metodológica, neutral) | `references/stage-3-tdd.md` §Test evidence policy; el proyecto declara comandos. |
| 005-006 arranque guiado | **Sí** | `references/project-start.md`; mismo CLI; sin dependencia de runtime. |
| 005-008 rutas/permisos | **Sí** | El guard CC v2 + el clasificador instalado (§1.3); requiere `jq` (presente). |
| 005-009/005-010 delegación externa | **Parcial** | Como **coordinador** CC: probado (aceptación PD-10). Como **destino** CC: no existe. |
| 005-002 medidor de contexto | **No hoy** | Adaptador único = store SQLite de OpenCode (`cdad_context_meter.py:153`, `:451+`); CC guarda JSONL. |
| 005-003 vista compacta | **Sí** | `cdad_packet.py status` (`references/orientation.md:14-35`); neutral y read-only. |
| 005-007 planificación progresiva | **Sí** | Plantillas + regla de tamaño/unidad; neutral. Su D-3 queda cerrado por §1.4. |

**Evidencia de capacidades efectivas ya observada (y su límite declarado):**

- 005-010: la sesión CC **coordinó** y ejecutó `cdad_delegate.py` con `PWD` = padre del repo
  (`evidence/pd10-acceptance.md:38-58`) — el lado coordinador de CC funciona con la interfaz común.
- F2 de 005-003: la sesión CC despachó y recibió con scripts propios
  (`.cdad/local/dispatch-005-003.sh`, `receive-005-003.sh`), `runtime: opencode`.
- Delegación **nativa** CC a subagentes CDAD: **6** llamadas `Agent` con `subagent_type`
  `cdad-reviewer`/`cdad-test-writer` en la sesión CC histórica (`~/.claude/projects/<padre>/<sesión>.jsonl`;
  3 con `"model": "opus"` explícito), para features **003-001/003-005 (septiembre)**.
- **Límite de esa evidencia (se conserva):** (i) la delegación nativa es histórica, no de este epic;
  (ii) en 005-010 y F2 el **trabajo de rol** corrió en OpenCode, no en CC; (iii) los scripts por feature
  **no** son una delegación de paquete con la interfaz común y su recepción en un solo recorrido
  (el recibo sí existió, pero el transporte fue manual); (iv) ninguna sesión CC corrió con cwd = este repo.

---

## 5. Medición y evidencia disponibles para el lado CC

**Observable hoy**

- Transcripts JSONL de CC (`~/.claude/projects/<slug>/<session-id>.jsonl`): `sessionId`, `cwd`,
  `gitBranch`, `version`, `timestamp`, `entrypoint` (`cli`|`sdk-cli`), `isSidechain`, `agent-name`;
  `message.model`; `message.usage` (`input_tokens`, `cache_creation_input_tokens`,
  `cache_read_input_tokens`, `output_tokens`); `cost-state` (`totalCostUSD`, `totalDuration`).
- Vista compacta `cdad_packet.py status` (neutral, acotada por bytes).
- Registro de despacho I8 (`runtime`, `model_configured`, `model_reported`, `session`, `started_at`,
  `provenance`) y recibo durable (`semantic_status: pending`).
- `install.sh --check` + manifiesto de propiedad (coherencia de bytes del lado CC).
- `cdad-version-check.py` con su límite de §3.2 (invocado desde el árbol instalado da `COHERENT`).

**Desconocido declarado (se conserva; no se inventan cifras ni ahorros)**

- Medición por rol/contexto del lado CC con el instrumento entregado: **no hay adaptador CC** para el
  medidor de 005-002 ⇒ `unknown`, con la causa (el store que lee el medidor es el de OpenCode).
- Si un subagente sin `model:` hereda el modelo de sesión; cuál es el hecho material de fin de una corrida
  `claude -p`; si los hooks se aplican en `-p`.
- Atención humana, costo facturado y ventana real siguen no observables (heredado de
  `docs/specs/005-007-progressive-planning/discovery.md:409-410`).

---

## 6. Fronteras y no-objetivos

- **Sin tocar HOME** salvo decisión del dueño: no se cambian `~/.claude`, `~/.agents`,
  `~/.config/opencode` ni `~/.claude.json` (confianza de carpeta, copias viejas).
- **Sin WebUI** (ajuste del dueño 2026-10-11, `plan.md:77-78`), **sin CI**, **sin sandbox**, **sin push**.
- **Sin reabrir** 005-005, 005-009 ni 005-010 (sus contratos e invariantes se conservan).
- **Sin plataforma de jobs/scheduler**; **sin** implementar "todos los destinos".
- **No se propone contrato** en esta subetapa.

---

# (b) Recorrido de uso concreto

De la petición del dueño a un ciclo corto real despachado desde Claude Code **con recepción CDAD**.
`[D]` marca dónde hace falta una decisión del dueño; el resto es el mínimo que **no** la exige.

| # | Paso | Quién | Qué queda como evidencia | ¿Necesita al dueño? |
|---|---|---|---|---|
| R0 | El dueño pide: "usá CDAD en este proyecto para una unidad corta" (en una sesión de Claude Code) | dueño + sesión CC | la instrucción, en el transcript CC | — |
| R1 | La sesión CC arranca orientación con la **vista compacta** instalada: `python3 ~/.claude/skills/cdad-cycle/scripts/cdad_packet.py status --project-root <repo>` | coordinador CC | la salida JSON (bounded) | — |
| R2 | Comprueba la versión de lo que va a usar: `cdad-version-check.py` desde el árbol instalado → `COHERENT` | coordinador CC | verdict + rc | — |
| R3 | Elige el mecanismo (roles **en CC**: subagentes `cdad-*` con el tool `Agent`) y registra el intento: `prepare --record-dispatch <pkt> --input attempt.json` con `runtime: claude-code`, `model_configured`, `provenance` | coordinador CC | `.cdad/executions/<exec>/dispatches/<attempt>.json` (I8) | — |
| R4 | Invoca el rol con el **paquete canónico** como insumo: tool `Agent`, `subagent_type: cdad-<rol>`, con `model` explícito si el perfil `basic` deja los modelos sin declarar | coordinador CC | el retorno del subagente (texto final + evidencia) y los registros `isSidechain` del transcript CC | — |
| R5 | Persiste la entrega: escribe el texto final como parte y llama `cdad_result.py receive` (descriptor `staged-file`) | coordinador CC | `.cdad/runtime/results/<exec>/<packet>/receipt.json` (`semantic_status: pending`) | — |
| R6 | Re-entra: `reconcile`, verifica la entrega contra el contrato y decide el gate; único escritor del state | coordinador CC | transición en `docs/.cdad-state.json` + commit de docs | — |
| R7 | Cierre corto: el ciclo corre punta a punta con la versión instalada al empezar (`9d89a4b…`) | coordinador CC | `.cdad/local/runs/*` + receipt + I8 + re-entry | — |
| R8 | **(Opcional, si el dueño quiere cwd = repo)** confiar la carpeta del proyecto y/o emitir la activación de proyecto para CC | dueño | entrada en `~/.claude.json`; `.cdad/activation.json` + `.claude/` | **[D]** |
| R9 | **(Opcional)** desplegar una versión nueva / limpiar copias viejas de HOME | dueño | backup + `install.sh --check` PASS | **[D]** |

**Mínimo que no exige al dueño:** R1–R7 tal como están, corriendo la sesión CC desde un directorio ya
confiable con `--project-root` al repo (práctica ya observada), usando los agentes y las skills
**instalados** (no se necesita escribir nada en HOME).
**Lo que sí exige al dueño:** confiar la carpeta de **este** proyecto (interactivo con cwd = repo),
cualquier limpieza/despliegue en HOME, y activar versiones en el repo real.

---

# (c) Comparación breve y fundamentada de enfoques

| | A) Adaptador Claude Code sobre la interfaz común | B) Sólo activación y verificación de los roles CC (sin delegación externa) | C) Artefactos de proyecto para CC |
|---|---|---|---|
| Qué es | Nuevo `cdad_delegate_claude_code.py`; un coordinador (de cualquier CLI) despacha el rol a un worker CC no interactivo | El ciclo corre en la sesión CC (coordinador) con los roles CC nativos (`Agent`/`subagent_type`), usando I8 + `receive` existentes | `cdad-activate.py --runtime claude-code` → `.claude/agents` + `.claude/skills` + `.cdad/activation.json` bajo el proyecto |
| Evidencia a favor | Contrato y transporte ya probados (`cli-delegation.md:75-110`); resolución por módulo (`cdad_delegate.py:54,88`); coordinador CC ya ejercido (pd10-acceptance) | Es el mecanismo declarado para CC (`SKILL.md:501`); 11 agentes + skills ya **instalados y corriendo**; delegación nativa CC histórica (6 llamadas `Agent`); recepción ya corrida desde una sesión CC (`receive-005-003.sh`) | Ya entregado y documentado (`runtime-adoption.md:26-39`); no toca HOME; fija versión por proyecto; RU-1 ya resuelve el `CDAD_PACKET_CLI` del hook |
| Costo / riesgo | Adapter nuevo con **señal durable y hecho de fin no verificados** (JSONL de CC), identidad del rol a verificar, id UUID, hooks en `-p` sin probar; **no** demuestra roles activos en CC | Depende de la **confianza de carpeta** para cwd = repo (o del workaround del padre); el perfil `basic` no garantiza reviewer≠implementer (hay que declararlo por despacho); el nombre del tool (`Task` vs `Agent`) está mal declarado en la fuente | Crea **copias de proyecto** ("copias viejas" es reserva del dueño); la guía vigente pide no introducir activación sólo para resolver derivados (`runtime-adopted-version.md:40-45`) |
| Qué **no** demuestra | Que los roles estén activos en CC para este proyecto; el trabajo del rol correría en CC pero el entregable de la fila 10 es "roles activos **en Claude Code** para este proyecto" — que ya se cumple sin adapter | Nada por sí sola: hace falta un **ciclo corto real** que la cierre | Que un ciclo haya corrido; sin ciclo, es sólo un artefacto de configuración |

Nota de encaje: la fila 10 dice "**despachado desde Claude Code**" (el origen es CC) y "roles CDAD
activos en Claude Code **para este proyecto**" ⇒ el enfoque B es el que responde a la letra; A es una
capacidad **distinta** (CC como destino), útil después, y su contrato ya está preparado para admitirla
sin tocar la interfaz.

---

# (d) Propuesta mínima elegida

**Enfoque B como cuerpo, con el mínimo de verificación y sin tocar HOME:**

1. **Verificación de carga (lo que una sesión CC realmente carga en este proyecto):** rol + skills + hooks
   + versión, con las VERIFY de §1.6 resueltas por evidencia (sin escribir en HOME): que el agente CC
   `cdad-<rol>` es el que corre, que el guard bloquea lo que debe, y que la versión declarada es la
   instalada.
2. **Un ciclo corto real despachado desde Claude Code** con la versión instalada al empezar, con
   **recepción CDAD**: I8 con `runtime: claude-code` → rol en CC → `receive` (`semantic_status: pending`)
   → re-entry del coordinador. Reutilizar `prepare`, el ledger, `receive` y `reconcile`; **no** crear
   state ni ledger nuevos.
3. **Declarar (no ejecutar) los dos cruces que son del dueño:** confianza de carpeta de este proyecto y
   copias/despliegues en HOME.
4. **Cerrar D-3 de 005-007**: la ruta del CLI en CC es la del árbol de skill instalado (§1.4).

**Se descarta ahora:** el adaptador CC (enfoque A) como parte de esta feature — no es necesario para el
resultado de la fila 10, exige verificar una señal durable nueva y tiene riesgo de convertirse en scope
"plataforma de delegación"; queda **nombrado como incremento** con sus deltas concretos (§2.2).
También se descarta emitir artefactos de proyecto (C) sin decisión explícita del dueño.
Nada de esto se propone como contrato: el draft lo decidirá.

---

# (e) Plan legible por el humano

**Objetivo.** Que los roles CDAD estén **activos en Claude Code para este proyecto** y que un ciclo corto
**real**, despachado desde Claude Code con la versión instalada al empezar, cierre con entrega recibida por
el flujo CDAD — sin tocar HOME salvo decisión del dueño.

**Recorrido.** R1–R7 de la sección (b): orientación compacta → comprobación de versión → registro del
despacho (I8, `runtime: claude-code`) → rol CC (subagente `cdad-*`) → `receive` (recibo `pending`) →
re-entry y gate.

**Unidades y orden** (progresivo; detalle fino sólo para la próxima tanda):

1. **U1 — Reconocimiento de capacidades efectivas de CC (habilitadora).** Resultado: mapa verificado de
   qué carga una sesión CC en la versión instalada (rol, skills, hooks, modelo, confianza de carpeta,
   versión) con archivo:línea y VERIFY resueltos o declarados. Insumos: esta discovery (ya produjo el
   mapa), la instalación vigente, `sources/agents/adapters/claude-code.md`, el manifiesto de propiedad.
   Consumidor nombrado: U2. Aceptación: mapa + un rol CC arrancando y declarando su contrato sin fallback.
2. **U2 — Ciclo corto real en CC (porción integrada).** Resultado: una unidad pequeña corre punta a punta
   con la versión instalada, con I8 (`runtime: claude-code`), recibo durable y re-entry; imperfecciones
   registradas. Depende de U1. Incertidumbre: disponibilidad de cuenta/cuota; cwd confiable.
   Aceptación: el ciclo corre y se registra la evidencia; las ausencias se declaran.
3. **U3 — Cierre: roles activos + paridad declarada.** Resultado: la lista de roles activos en CC para
   este proyecto y la evidencia de paridad con el contrato de roles (permisos, invariante
   reviewer≠implementer declarada bajo `basic`, y los dos cruces del dueño declarados como BLOQUEO si
   aplican). Depende de U1 y U2.

**Decisiones a resolver en el draft y en los gates:**

- D-i: ¿el ciclo se corre desde un directorio ya confiable con `--project-root` (sin decisión del dueño) o
  se pide confiar la carpeta del proyecto? (Recomendación: lo primero para el ciclo; lo segundo, declarado.)
- D-ii: bajo `basic`, ¿el modelo por rol se declara por despacho (parámetro `model` del tool `Agent`) o se
  exime explícitamente la invariante? (No se puede dejar implícito: hoy no está garantizada.)
- D-iii: ¿se emite activación de proyecto para CC (`cdad-activate.py --runtime claude-code`)? Es del
  dueño; por defecto **no**.
- D-iv: ¿el adaptador CC (enfoque A) se registra como deuda/incremento nombrado? (Recomendación: sí.)

**Riesgos (con la evidencia que los sostiene):**

- **Confianza de carpeta** de este proyecto en `false` (§3.1): una sesión CC interactiva con cwd = repo
  pedirá decisión; workaround verificado = correr desde el padre y pasar `--project-root`.
- **Perfil `basic`**: sin modelos por rol, reviewer≠implementer **no** está garantizada y el guard la
  exime (§1.5). Debe declararse y resolverse por despacho o por perfil.
- **Drift de nombre del tool** (`Task` vs `Agent`) en la fuente del adaptador (§1.6): puede desorientar al
  coordinador CC; corrección de texto, no de arquitectura.
- **Señal durable de CC no verificada** para el enfoque A (§2.2): si se aborda, debe fallar cerrado.
- **`install.sh --check` hoy da rc 1** por la condición local del staging + deuda de `__pycache__`
  (§3.2): no leerlo como incoherencia de versión.
- **Cuota/cuenta** para una corrida real (heredado de `005-007/discovery.md:350-352`): si falta, se
  declara BLOQUEO, no verde.

---

# (f) Plan de aceptación proporcional

| Pregunta | Evidencia apropiada | Productor del insumo | Actor evaluador | Qué **no** permite afirmar sola |
|---|---|---|---|---|
| ¿Los roles CDAD están activos en CC para este proyecto? | Mapa de carga (rol/skills/hooks/versión) + una ejecución de rol CC que declare su contrato sin fallback | architect (mapa) / coordinador CC (ejecución) | orquestador + reviewer | Que funcione en otro perfil, otra máquina u otro proyecto |
| ¿Un ciclo corto real se despacha desde CC y se recibe por CDAD? | I8 con `runtime: claude-code` + `receipt.json` (`semantic_status: pending`) + re-entry registrado en el state | coordinador CC | orquestador (gate) [+ dueño si hay despliegue] | Que la entrega sea correcta (entrega ≠ gate); que sea repetible sin asistencia |
| ¿Se respetó la frontera de HOME? | `git status` del repo, huellas de la instalación (`~/version.txt`, manifiesto) sin cambios, y declaración de los cruces del dueño | coordinador CC | orquestador + dueño | Que no existan copias viejas (eso lo decide el dueño) |
| ¿La invariante reviewer≠implementer se sostiene? | Bajo `basic`: declaración explícita por despacho (parámetro `model` del tool `Agent`) o exención declarada; con `optimus`: los `model:` del artefacto | coordinador CC | reviewer (familia distinta) | Que el instalador la garantice con `basic` |
| ¿Es usable el recorrido por un consumidor? | Ciclo corrido en sesión fresca con la documentación del consumidor; fricciones y recuperación registradas | orquestador (prepara el punto de partida) | agente consumidor en sesión fresca (proxy declarado, no persona) | Usabilidad humana validada si solo participó un agente |

**Bloqueos declarados por defecto (no verdes por proximidad):** confianza de carpeta de este proyecto,
limpieza de copias viejas de HOME, despliegue de una versión nueva y cualquier cambio en el repo real.

**Proporcionalidad:** suite completa al cierre de la feature (la toca el instalador/adaptadores y docs),
regresión focal en los cambios; reutilización de evidencia registrada equivalente. Gate de tests del
proyecto: los comandos que declare el proyecto (política única de 005-005).

---

# (g) Medidas de seguimiento disponibles

- **Despacho y entrega:** ledger I8 (`.cdad/executions/<exec>/dispatches/<attempt>.json`) y recibo
  (`.cdad/runtime/results/<exec>/<packet>/receipt.json`) — sirven para el ciclo CC en cuanto el intento
  declare `runtime: claude-code`; ambos ya están entregados.
- **Orientación:** `cdad_packet.py status` (vista compacta acotada) — neutral, ya instalado en CC.
- **Versión:** `cdad-version-check.py` desde el árbol instalado (`COHERENT`) con su límite declarado
  (sin pata `~/.claude/agents`), + `install.sh --check` y el manifiesto de propiedad.
- **Contexto por rol en CC:** **desconocido** con el instrumento entregado (el medidor de 005-002 lee el
  store de OpenCode); los transcripts JSONL de CC tienen la materia prima (`usage`, `model`,
  `isSidechain`), pero **no hay adaptador** — se conserva como desconocido y **no** se promete ahorro.
- **Capacidades efectivas:** los transcripts CC del proyecto (con `entrypoint`, `version`, delegaciones
  `Agent`) permiten verificar qué corrió de verdad en una sesión.

---

# Evidencia de esta tarea

**Archivos modificados:** ninguno en el repo (`git status --porcelain` → solo ` M docs/.cdad-state.json`,
preexistente). Escritos sólo temporales declarados: `/tmp/opencode/cc-check.out`,
`/tmp/opencode/discovery-005-004.md`.

**Comandos exactos (read-only) y salida relevante:**

- `git log --oneline -3` → `e74c0bc docs(005-007): despliegue de 9d89a4b registrado` (HEAD);
  `git rev-parse --abbrev-ref HEAD` → `codex/epic-005-real-operation`;
  `git diff --stat 9d89a4b HEAD` → `1 file changed, 9 insertions(+)` (solo docs).
- `grep -n -i "claude" install.sh` → destinos `:51-53`, `SKILLS=…` `:62`, `EXPECTED_CDAD_AGENTS_CLAUDE_CODE=11` `:74`,
  staging CC `:696-700`, guard `:1069-1078`, marker `:638-641`, manifiesto `:104,869+`, `--check` `:1422+`.
- `sha256sum ~/.claude/cdad-scripts/path-guard.sh scripts/claude-code-path-guard.sh` →
  `e5ab39f45234…1e9` en ambos.
- `diff -r -x __pycache__ skills/cdad-cycle ~/.claude/skills/cdad-cycle` → sin diferencias;
  idem `cdad-epic`, `cdad-spec-and-test`, `odoo-architect|expert|make-env|reviewer|test-writer`.
- `for f in agents/claude-code/cdad-*.md; do diff ~/.claude/agents/<b> build/staging/…; done` →
  1 línea de diferencia en 10 agentes; 13 en `cdad-orchestrator.md` (model + columna de modelos).
- `python3 ~/.claude/skills/cdad-cycle/scripts/cdad-version-check.py --project-root "$PWD"` →
  `project/agents/CLI = 9d89a4b8…`, `verdict: COHERENT`, rc 0; desde el checkout → `UNKNOWN`, rc 3.
- `bash install.sh --check` → rc 1; 342 `OK`; drift: 11 agentes CC + 11 OpenCode (perfil) y
  `skills/cdad-cycle` (`__pycache__`, 90 vs 85 archivos).
- `cat ~/version.txt` → `9d89a4b8ca139b1d589ba438860f08e94c03943a`;
  `cat ~/.config/opencode/agents/.cdad-models-profile` → `basic`;
  manifiesto: `source_version 9d89a4b8… runtime claude-code stack odoo profile basic`,
  364 artefactos, 0 conflictos.
- `grep -c "^model:" ~/.claude/agents/cdad-*.md` → 0 en los 11.
- `~/.claude.json`: `projects["<repo>"].hasTrustDialogAccepted = false`
  (padre `…/projects/cdad` = true).
- Transcripts CC: `~/.claude/projects/<padre>/<sesión>.jsonl` → 6 tool_use `Agent` con
  `subagent_type` `cdad-reviewer`/`cdad-test-writer` (features 003-001/003-005), 3 con `"model": "opus"`.
- `claude --version` → `2.1.296`; flags relevantes de `claude --help`: `-p/--print`, `--agent`, `--agents`,
  `--session-id`, `--permission-mode`, `--allowedTools`, `--permission-prompts`, `--output-format`,
  `--bare`, `--restricted`, `--no-session-persistence`.
- `cat .cdad/local/runs/005-007-discovery.delegate.json` →
  `{"attempt":"delegate-opencode-2ac2addcb404","termination":"completed","session":"ses_bd66a7…", …}`;
  `cat .cdad/local/exec-config-005-007-architect-discovery.json` → config con `binary`, `model`,
  `sessions_db`, `wait.timeout_seconds`.

**Commit:** `null` (tarea read-only; no se commitea nada).
