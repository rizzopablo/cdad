He leído y ejecutado el encargo en modo solo-lectura. Verifiqué rama/HEAD (`codex/epic-003-context-efficiency` @ `7436a38`), el árbol real y los runtimes de la máquina. No modifiqué nada (no corrí `install.sh`; solo `--help`, `--dry-run` no fue necesario).

---

# 1. Discovery (puntos 1–5)

## 1.1 Inventario por runtime — qué carga hoy, desde dónde, cómo se activaría por proyecto

| Runtime | Skills | Agentes | Hooks / guards | Fuente real hoy | ¿Activación por proyecto? |
|---|---|---|---|---|---|
| **OpenCode** | `.opencode/opencode.jsonc` → `skills: ["<home>/.cache/cdad-adopted-818f12a/.config/opencode/skills"]` (git-ignorado) | `.opencode/agents/cdad-*.md` + `.cdad-derived.json` (publicados por `prepare` I9, git-ignorados) | `permission` derivado en frontmatter (path maps); sin hooks externos | raíz aislada `818f12a` | **Sí, ya activa y verificada** (`docs/runtime-adopted-version.md:29-41,45-59`) |
| **Claude Code** | `~/.claude/skills/cdad-cycle` — **stale**: `scripts/` solo tiene `cdad_packet.py` | `~/.claude/agents/cdad-*.md` (mtime Sep 29, ~15.0 KB) | `~/.claude/cdad-scripts/path-guard.sh` sha `18197266…` ≠ repo `e5ab39f4…` | **HOME global, desactualizado** | **No**: no existe `.claude/` de proyecto |
| **Codex** | `~/.agents/skills/cdad-cycle` — **stale**: `scripts/` solo tiene `cdad_packet.py` | **Ninguno**: CDAD no genera adaptador de agentes (`scripts/cdad-generate.py:1060` → `choices=("opencode","claude-code")`) | hooks de nodeterm (`~/.codex/hooks.json`), no CDAD | **HOME global, desactualizado** | **VERIFY**: `.agents/skills` de proyecto sin verificar; el descubrimiento de skills por Codex es inestable (ver V2) |

**Raíz aislada adoptada** (`<home>/.cache/cdad-adopted-818f12a`) — verificada: contiene `.config/opencode/{skills,agents}`, `.claude/{agents,skills,cdad-scripts/path-guard.sh}`, `.agents/skills` y `.cdad-install-manifest.json` (72 KB). Sus tres copias de `skills/cdad-cycle/scripts/` contienen **los 4 scripts** (`cdad_packet`, `cdad_result`, `cdad_guard`, `cdad_continuity`). Su `path-guard.sh` = `e5ab39f4…` (igual al repo, distinto del global). **Pero su `SKILL.md` no menciona `cdad_result`/`cdad_guard`/`cdad_continuity` ni `continuity.md`** (`grep -c` = 0).

## 1.2 Hallazgos verificados (con cita)

1. **Descubrimiento roto (confirmado).**
   - La tabla "How to read the references" de `skills/cdad-cycle/SKILL.md:441-456` **no incluye `continuity.md`** (sí incluye `progress-guards.md:450`, pero solo "if you dispatch roles as external processes").
   - `cdad_result` **no aparece** en `SKILL.md` ni en `agents/cdad-orchestrator.md`; solo en `skills/cdad-cycle/references/re-entry.md:19`. Igual para `cdad_guard`/`cdad_continuity` (solo sus propias referencias).
   - `agents/cdad-orchestrator.md:56-59` dice "materialize the read-only roles' artifacts from their FINAL TEXT output" **sin nombrar el CLI de `receive`**.
2. **Recepción sin usar (RU-2a confirmado).** El protocolo de 4 pasos **existe** en `re-entry.md:14-63` (RECEIVE→RECONCILE→MATERIALIZE→STATE), y `SKILL.md:275-278` (Step 6) manda cargar `re-entry.md`; pero el cuerpo operativo del orquestador no lo ejecuta, por eso `reconcile` queda en `dispatched-unknown` (`continuity-ledger.md:7`, `debt.md:28`).
3. **Versión por runtime divergente (confirmado con shas):**
   - OpenCode → `818f12a` (correcto).
   - Claude Code global: skills/agents/guard viejos; `path-guard.sh` global ≠ repo y ≠ adoptado.
   - Codex global: `~/.agents/skills/cdad-cycle/scripts/` solo `cdad_packet.py`; sin adaptador.
4. **La raíz adoptada tiene todo el material**, solo falta que se descubra/enlace.
5. **Inconsistencia documental (flag):** `docs/runtime-adopted-version.md:10-16` declara vigente `818f12a`, pero su tabla de historial `:122` declara v3 = `939f501`. Hay que fijar cuál es la versión operativa (V6).

## 1.3 Puntos de cableado mínimos (dónde y en qué paso)

| Comando | Paso del ciclo donde se cablea | Estado hoy |
|---|---|---|
| `cdad_packet prepare` | Step 4 — delegar (`SKILL.md:256-263`; `agents/cdad-orchestrator.md:14-30`) | ✅ cableado |
| `cdad_continuity begin` | Step 4 — **antes de despachar** el paquete | ❌ |
| `cdad_continuity checkpoint` | Step 6 — al **cerrar el límite de tarea/subfase** | ❌ |
| `cdad_result receive` | Step 6 — protocolo de materialización (staging + receive + transición de state) | ⚠️ en referencia (`re-entry.md`), no en el cuerpo operativo |
| `cdad_continuity reconcile` | Step 6 / antes de todo retry o resume | ⚠️ en referencia, no ejecutado |
| `cdad_continuity resume` | Step 1 — **sesión nueva**: reconstruir antes de detectar estado | ❌ |
| `cdad_continuity trigger` | antes de rotar sesión (señal advisory) | ❌ |
| `cdad_guard classify` | — | **FUERA** (sin lector de sesiones; `progress-guards.md:17`) |
| `cdad_guard preflight`/`record`/`budget` | opcional si se despacha como proceso externo | fuera del flujo nativo |

## 1.4 Recorrido de aceptación breve por runtime (no un desarrollo entero)

Mismo guion para OpenCode / Claude Code / Codex, en un proyecto desechable (rehearsal) y luego en el repo:

1. **Identidad de versión** — sesión/subagente nuevo reporta la **base** desde la que cargó `cdad-cycle` y lista `scripts/` (esperado: los 4 archivos). Evidencia: la ruta base reportada + `ls`.
2. **Consumo de paquete** — `prepare` un paquete de rol real → despacho. Evidencia: stdout/PACKET.md.
3. **`receive` del resultado** — el orquestador **stagea** el FINAL TEXT del rol bajo `.cdad/inbox` (+`RESULT.json`) y corre `receive`; `validate-receipt` pasa. Evidencia: rc + receipt.
4. **Checkpoint + reconcile** — `begin` (write-ahead) antes del despacho, `checkpoint` al límite; `reconcile --packet` → **`received`** (ya no `dispatched-unknown`). Evidencia: JSON.
5. **Reconstrucción** — sesión nueva, solo `resume` → reconstruye objetivo/decisiones/autoridad/next_action sin re-preguntar.

**Evidencia suficiente:** (a) la base cargada reportada por la sesión; (b) stdout de cada comando con rc; (c) la fila del ledger con `file:line`; (d) que `reconcile` clasifique `received`.

## 1.5 Riesgos

- **Hook roto en Claude Code bloquea herramientas.** Mitigación: hook *fail-open* (si el script no existe, `cat >/dev/null; exit 0`) y **rehearsal en una raíz desechable antes** de tocar el proyecto real; nunca `~/.claude`.
- **Mezcla de versiones** (agentes nuevos + guard viejo). Mitigación: una sola raíz adoptada por runtime + chequeo de identidad; el guard de proyecto resuelve a `A/.claude/cdad-scripts/path-guard.sh`.
- **Codex sin adaptador de agentes / descubrimiento inestable.** MVP: paquete + prompt de rol desde la raíz adoptada; adaptador de agentes → deuda.
- **HOME prohibido.** Activación por proyecto; `.claude/` y `.agents/` hoy **NO** están git-ignorados (`.gitignore:13` solo tiene `.opencode/`).
- **Inconsistencia de versión** en el doc (V6).

## 1.6 Qué entra y qué va a deuda

**Entra:** cableado en SKILL/orquestador/referencias; generador de activación por proyecto; adopción de `receive`; recorrido real por runtime + enmienda de cierre del epic (borrador).
**Deuda explícita:** lector de sesiones para `classify`; medición de contexto (`trigger` seguirá `unknown`); adaptador de agentes Codex; hooks de CC más allá de `path-guard`; rotación automática.

---

# 2. Decisiones D1..Dn (con VERIFY)

- **D1 — Alcance MVP:** cablear/activar/comprobar; **sin funcionalidad nueva**; endurecimiento a deuda. (Encargo.)
- **D2 — Activación por proyecto, nunca HOME:** destino = raíz aislada adoptada; el archivo concreto queda git-ignorado como `.opencode/`. **Agregar `/.claude/` y `/.agents/` a `.gitignore`** (hoy ausentes; `.gitignore:13` solo tiene `.opencode/`).
- **D3 — Generador determinista** (propuesto `scripts/cdad-activate.py`; nombre a fijar con el dueño) desde `(project_root, adopted_root)`; `--dry-run` sin efectos; consumible por tests. El producto entrega **generador + procedimiento + tests**, no las rutas locales.
- **D4 — Claude Code:** activación de proyecto vía `.claude/{agents,skills,settings.json}`; hook `path-guard.sh` **fail-open** apuntando a la raíz adoptada; **rehearsal en raíz desechable** antes de aplicar. Nunca tocar `~/.claude`. VERIFY V1.
- **D5 — OpenCode:** mantener y **generar** el shape ya verificado (`.opencode/opencode.jsonc` + `.opencode/agents/` de `prepare`); no cambiar el mecanismo.
- **D6 — Codex MVP:** skills de la raíz adoptada vía `.agents/skills` de proyecto **si** el runtime las descubre (VERIFY V2); si no, camino **paquete + prompt de rol** y límite declarado; **sin adaptador de agentes Codex** (deuda). No tocar `~/.agents`.
- **D7 — `receive` en el flujo (cierra RU-2a):** el orquestador **stagea** el FINAL TEXT y ejecuta `receive`; transición única de state; retry idéntico converge. **Reutiliza** `cdad_result.py` de 002 (sin CLI nuevo).
- **D8 — Continuidad en el ciclo:** `begin` antes de despachar; `checkpoint` en límites; `reconcile` antes de retry/resume; `resume` al iniciar sesión nueva; `trigger` advisory. **`classify` fuera** (sin lector) → deuda.
- **D9 — Identidad de versión:** la activación registra commit/raíz adoptada; el recorrido exige que una sesión nueva **reporte qué cargó**; un mismatch se detecta con chequeo.
- **D10 — Enmienda de cierre del epic:** la última tarea entrega un **borrador** de enmienda (criterio 3 del plan del epic: reconstrucción automática en un límite natural) para aprobación del dueño; no se autoprueba.

**VERIFY (no comprobado, no inventar):**
- **V1** — Descubrimiento CC por proyecto (`.claude/agents`, `.claude/skills`, `.claude/settings.json`) y **semántica de merge/trust de hooks** proyecto↔usuario; precedencia vs `~/.claude`.
- **V2** — Descubrimiento de skills de Codex por proyecto (`.agents/skills` vs `~/.codex/skills` vs `.codex/skills`); hay reportes de regresión de descubrimiento (community.openai.com, 2026-04). No asumir.
- **V3** — Shape exacto aceptado por OpenCode 2.0.16 para la entrada `skills` (re-confirmar; hoy verificado empíricamente en `docs/runtime-adopted-version.md:33-41`).
- **V4** — Esquema exacto del `RESULT.json` de staging (spec 002 §3/§4); no duplicar la interfaz.
- **V5** — `resume --role` requiere `docs/cdad-policy.json` (existe, `461 B`) — confirmar en el recorrido.
- **V6** — Versión operativa a fijar: `818f12a` (tabla vigente) vs `939f501` (historial, `runtime-adopted-version.md:122`). Decisión del dueño/orquestador.

---

# 3. Borrador `spec.md`

```markdown
---
feature_id: 003-006-runtime-adoption
feature_name: Adopción y cableado de las herramientas CDAD por runtime
created_at: 2026-10-07
status: draft
---

# Spec: Adopción y cableado de las herramientas CDAD por runtime

## 1. Descripción funcional (Motivo)

Lo construido en 003-001/005 (`prepare`), 003-002 (`receive`), 003-003
(`cdad_guard`) y 003-004 (`cdad_continuity`) existe y está probado, pero **no se
descubre ni se usa** en el ciclo normal, y cada runtime (OpenCode, Claude Code,
Codex) carga **versiones distintas** de skills, agentes y guards. Esta feature
**cablea, activa y comprueba**: enlaza las herramientas en el ciclo, entrega un
generador de activación **por proyecto** que apunta a la raíz aislada adoptada,
adopta `receive` en el flujo de despacho y valida un recorrido breve por runtime.
No agrega funcionalidad nueva; el endurecimiento va a deuda.

## 2. Contrato

### 2.1 Cableado del ciclo
`skills/cdad-cycle/SKILL.md` y el cuerpo del orquestador nombran cada comando en
su paso del ciclo, **sin duplicar interfaces** (los contratos viven en
`references/continuity.md`, `references/progress-guards.md`,
`references/re-entry.md` y las specs 002/003/004):

- `prepare` — Step 4 (ya cableado).
- `begin` — antes de despachar un paquete (write-ahead).
- `checkpoint` — al cerrar el límite de tarea/subfase.
- `receive` — re-entry: protocolo de materialización de rol read-only.
- `reconcile` — antes de todo retry o resume.
- `resume` — al iniciar una sesión nueva (Step 1).
- `trigger` — señal advisory antes de rotar.
- `classify` — declarado **fuera** (sin lector de sesiones).

La tabla "How to read the references" de `SKILL.md` enlaza `references/continuity.md`.

### 2.2 Activación por proyecto (nunca HOME)
`scripts/cdad-activate.py --project-root R --adopted-root A [--runtime RUNTIME]... [--dry-run]`
emite, por runtime, archivos de activación git-ignorados que apuntan a `A`:

- OpenCode: `.opencode/opencode.jsonc` (`skills: [A/.config/opencode/skills]`); los
  agentes de proyecto los sigue publicando `prepare` (I9).
- Claude Code: `.claude/{agents,skills,settings.json}`; hooks `path-guard.sh`
  resueltos a `A/.claude/cdad-scripts/path-guard.sh`, **fail-open**.
- Codex: `.agents/skills` → `A/.agents/skills` (VERIFY, V2); si el runtime no las
  descubre, se declara el límite y el camino es **paquete + prompt de rol**.

Garantías: determinista (mismo input → bytes idénticos); **cero escrituras bajo
HOME**; `--dry-run` sin efectos; `.gitignore` cubre `.opencode/`, `.claude/` y
`.agents/`.

### 2.3 `receive` en el flujo (reutiliza 002)
El orquestador **stagea** el FINAL TEXT del rol bajo `.cdad/inbox` (con
`RESULT.json`), ejecuta `receive`, valida el receipt y registra la **transición
única** de state. `receive` no aprueba (`semantic_status` = `pending`); el state
lo escribe solo el orquestador.

### 2.4 Continuidad en el ciclo
`begin`/`checkpoint`/`reconcile`/`resume` se usan en el ciclo; `trigger` es
advisory (casi siempre `unknown`); `classify` queda fuera.

## 3. Postcondiciones (verificables)

- **P1.** `skills/cdad-cycle/SKILL.md` enlaza `references/continuity.md` en su
  tabla de referencias y nombra `receive`, `begin`, `checkpoint`, `reconcile`,
  `resume` y `trigger` en el paso correspondiente del ciclo, sin duplicar las
  interfaces; `classify` queda declarado fuera.
- **P2.** El generador de activación es determinista: ejecutado dos veces con el
  mismo `(project_root, adopted_root)`, produce bytes idénticos.
- **P3.** Toda escritura del generador está **fuera de HOME** y dentro de rutas
  git-ignoradas del proyecto; `.gitignore` cubre `.opencode/`, `.claude/` y
  `.agents/` (verificado con `git check-ignore`).
- **P4.** En OpenCode, una sesión/subagente nuevo reporta como base de
  `cdad-cycle` un directorio bajo la raíz adoptada y ve los 4 scripts
  (`cdad_packet`, `cdad_result`, `cdad_guard`, `cdad_continuity`).
- **P5.** En Claude Code con activación de proyecto, los agentes/skills resuelven
  a la raíz adoptada y el hook `path-guard.sh` resuelve a
  `A/.claude/cdad-scripts/path-guard.sh`; un hook ausente **no bloquea**
  herramientas (fail-open), probado en raíz desechable antes del proyecto real.
- **P6.** El recorrido de Codex consume el paquete y el prompt de rol desde la
  raíz adoptada (o, si el runtime no descubre skills de proyecto, el límite
  queda declarado); sin adaptador de agentes Codex.
- **P7.** `receive` forma parte del flujo normal: la salida FINAL TEXT de un rol
  se stagea y se recibe (rc=0); un retry idéntico converge al mismo receipt
  byte a byte; el state registra una única transición.
- **P8.** Con `receive` en el flujo, `cdad_continuity reconcile` clasifica
  `received` en el recorrido de aceptación (deja de ser `dispatched-unknown`).
- **P9.** `begin` (write-ahead antes de despachar), `checkpoint` (límite de
  tarea) y `resume` (sesión nueva) se usan en el ciclo; `resume` reconstruye
  objetivo, decisiones con razón, autoridad y próxima acción sin re-preguntar.
- **P10.** `cdad_guard classify` se declara fuera de alcance por falta de lector
  de sesiones; `trigger` sigue siendo señal advisory (`unknown` sin contador).

## 4. Invariantes verificables

- **I1.** Ninguna activación escribe bajo HOME; es por proyecto y apunta a la
  raíz aislada adoptada.
- **I2.** Una sola versión operativa por runtime (la raíz adoptada); ninguna
  copia global de HOME es fuente.
- **I3.** Los archivos de activación no se commitean; el producto entrega
  generador, procedimiento y tests.
- **I4.** No se endurecen permisos; sin push automático.
- **I5.** `receive` no aprueba; el state lo escribe solo el orquestador.
- **I6.** `classify` y la medición de contexto no se cablean (sin lector).

## 5. Criterios de aceptación

1. Suite completa verde y validadores del repo sin regresiones nuevas.
2. Recorrido real por runtime registrado en un ledger con evidencia `file:line`.
3. `reconcile` = `received` en el recorrido (no `dispatched-unknown`).
4. Reconstrucción con `resume` en sesión nueva sin re-preguntar al usuario.
5. Sin cambios fuera de la raíz adoptada y del proyecto (nada en HOME).
6. Borrador de enmienda de cierre del epic entregado al dueño.

## 6. Fuera de alcance

Lector de sesiones para `classify`; medición de contexto; adaptador de agentes
Codex; hooks de Claude Code más allá de `path-guard`; rotación automática de
sesión; cualquier cambio en HOME; push.

---
Status: draft — pendiente de aprobación del dueño.
```

---

# 4. Borrador `plan.md`

```markdown
---
feature_id: 003-006-runtime-adoption
feature_name: Adopción y cableado de las herramientas CDAD por runtime
created_at: 2026-10-07
status: draft
approved_by: (pendiente — dueño)
---

# Plan — 003-006-runtime-adoption

> Borrador del architect. El plan define el **contrato**, nunca el código
> (`stage-2-specification.md:115-119`); usa el bloque canónico `plan-tasks`
> (`planning-contract-draft.md` §4.1). 4 tareas (máximo del encargo).

## Restricciones globales (copia de la spec)

- Repo en español. Tooling Python **stdlib-only**.
- Nunca instalar/modificar CDAD en HOME real; activación **por proyecto** hacia
  la raíz aislada adoptada. Configs de activación **git-ignoradas**.
- No endurecer permisos; sin push automático. OpenCode 2.0.16 (referencia).
- `receive` no aprueba; el state lo escribe solo el orquestador. Reutilizar
  `cdad_result.py`/`cdad_continuity.py` (sin CLI nuevo).

## 1. Tareas

### T1 — Cableado del descubrimiento en SKILL y referencias
- **Postcondiciones:** P1 (y parte de P9/P10).
- **Alcance incluido:** enlazar `references/continuity.md` en la tabla de
  referencias; nombrar `receive`/`begin`/`checkpoint`/`reconcile`/`resume`/
  `trigger` en su paso del ciclo; `classify` declarado fuera. Sin duplicar
  interfaces.
- **Excluido:** el cuerpo operativo del orquestador (T3) y la activación (T2).
- **Archivos:** Modify `skills/cdad-cycle/SKILL.md`;
  Modify `skills/cdad-cycle/references/progress-guards.md` (nota de paso);
  Test `tests/test_003_006_t1_wiring.py`.
- **Dependencias:** ninguna.
- **Owner:** RED test-writer; GREEN implementer.

### T2 — Generador de activación por proyecto (determinista, sin HOME)
- **Postcondiciones:** P2, P3 (y aporta a P4/P5/P6).
- **Alcance incluido:** `scripts/cdad-activate.py` desde
  `(project_root, adopted_root)`; emisión OpenCode / Claude Code / Codex;
  `--dry-run`; fail-open del hook CC; `.gitignore` para `.claude/` y `.agents/`;
  chequeo de identidad de versión (D9).
- **Excluido:** adaptador de agentes Codex; hooks CC adicionales.
- **Archivos:** Create `scripts/cdad-activate.py`;
  Create `skills/cdad-cycle/references/runtime-adoption.md`;
  Modify `.gitignore`; Test `tests/test_003_006_t2_activation.py`.
- **Validación focal:** dos corridas → bytes idénticos; cero escrituras bajo HOME
  (HOME temporal en el test); `git check-ignore` sobre los 3 directorios; shape
  OpenCode igual al verificado.
- **Detener si:** V2 (descubrimiento Codex) no se puede fijar → declarar límite,
  no inventar.
- **Owner:** RED test-writer; GREEN implementer.

### T3 — Adopción de `receive` + continuidad en el cuerpo del orquestador
- **Postcondiciones:** P7, P8 (y parte de P9).
- **Alcance incluido:** reglas operativas del orquestador (staging + `receive` +
  transición única; `begin`/`checkpoint`/`reconcile`/`resume`); regenerar los
  agentes (OpenCode + Claude Code) desde `sources/`.
- **Excluido:** cambios a `cdad_result.py`/`cdad_continuity.py` (se reutilizan);
  el recorrido real (T4).
- **Archivos:** Modify `sources/roles/orchestrator.md`;
  Regenerate `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md`
  (`make agents`); Test `tests/test_003_006_t3_receive_wiring.py`.
- **Dependencias:** ninguna (T1 es docs, no toca `sources/roles/`).
- **Owner:** RED test-writer; GREEN implementer.

### T4 — Recorrido real por runtime + enmienda de cierre del epic (borrador)
- **Postcondiciones:** P4, P5, P6, P9 (evidencia), P10.
- **Alcance incluido:** guion de aceptación (§1.4) en OpenCode, Claude Code y
  Codex; un `receive` real con `reconcile = received`; una reconstrucción con
  `resume`; borrador de enmienda de cierre del epic para el dueño.
- **Excluido:** benchmark; comparación A/B; forzar la feature para repetirla.
- **Archivos:** Create `docs/specs/003-006-runtime-adoption/adoption-ledger.md`;
  Create `docs/epics/epic-003-context-efficiency/closure-amendment-draft.md`.
- **Registro obligatorio del ledger:** `runtime | base cargada (file:line) |
  receive rc/receipt | reconcile | resume | límites | pendiente`.
- **Validación (observable):** la sesión nueva reporta la base adoptada y los 4
  scripts; `reconcile = received`; `resume` no re-pregunta.
- **Dependencias:** T1, T2, T3 verdes.
- **Owner:** orquestador.

## 2. Estimaciones (rango, método, incertidumbre)

- Rango: **bajo–medio** (T1, T3), **medio** (T2), **medio** (T4).
  Método: comparación cualitativa con 003-002/003-004. Incertidumbre **alta**
  por V1/V2 (descubrimiento CC/Codex).

## 3. Incertidumbres / replanificación

- Si V1/V2 no se resuelven, reacotar con el dueño antes de expandir
  infraestructura; no asumir APIs (V1–V6).
- Si T2 crece más allá de su mini-ciclo, dividir (OpenCode/CC vs Codex).

```plan-tasks
{
  "validation_strategy": "focales por unidad (pytest, env -u TMPDIR) con HOME temporal en los tests de activación; suite completa y validadores del repo al cierre; recorrido real por runtime en el repo con ledger; sin tocar la sesión orquestadora ni HOME",
  "tasks": [
    {"id": "T1", "produce": [{"artifact": "wiring-ciclo", "contract": "n/a (documentación)"}], "consume": [], "depends_on": [], "parallel": [], "files": ["skills/cdad-cycle/SKILL.md", "skills/cdad-cycle/references/progress-guards.md", "tests/test_003_006_t1_wiring.py"], "focal_tests": ["tests/test_003_006_t1_wiring.py"], "regressions": [], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T2", "produce": [{"artifact": "cdad-activate", "contract": "activación-por-proyecto-v1"}], "consume": [], "depends_on": [], "parallel": [], "files": ["scripts/cdad-activate.py", "skills/cdad-cycle/references/runtime-adoption.md", ".gitignore", "tests/test_003_006_t2_activation.py"], "focal_tests": ["tests/test_003_006_t2_activation.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T3", "produce": [{"artifact": "orquestador-receive-continuidad", "contract": "n/a (reglas operativas)"}], "consume": [{"artifact": "wiring-ciclo", "contract": "n/a (documentación)", "producer": "T1"}], "depends_on": [], "parallel": [], "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md", "agents/claude-code/cdad-orchestrator.md", "tests/test_003_006_t3_receive_wiring.py"], "focal_tests": ["tests/test_003_006_t3_receive_wiring.py"], "regressions": ["tests/validate-consistency.sh"], "integration_gate": "@validation_strategy", "owner": "RED: test-writer; GREEN: implementer"},
    {"id": "T4", "produce": [{"artifact": "adoption-ledger", "contract": "n/a"}, {"artifact": "closure-amendment-draft", "contract": "n/a"}], "consume": [{"artifact": "cdad-activate", "contract": "activación-por-proyecto-v1", "producer": "T2"}, {"artifact": "orquestador-receive-continuidad", "contract": "n/a (reglas operativas)", "producer": "T3"}], "depends_on": ["T1", "T2", "T3"], "parallel": [], "files": ["docs/specs/003-006-runtime-adoption/adoption-ledger.md", "docs/epics/epic-003-context-efficiency/closure-amendment-draft.md"], "observable_checks": ["una sesión/subagente nuevo por runtime reporta la base adoptada y los 4 scripts", "un receive real produce receipt y reconcile clasifica received", "resume en sesión nueva reconstruye objetivo/decisiones/autoridad/next_action sin re-preguntar"], "regressions": ["tests/validate-consistency.sh", "tests/validate-odoo-specialization.sh"], "integration_gate": "@validation_strategy", "owner": "orquestador"}
  ]
}
```

---

Status: draft — pendiente de aprobación del dueño.

---

## Notas de honestidad (PD-15)

- No verifiqué **V1** (descubrimiento/hook-merge de Claude Code por proyecto) ni **V2** (descubrimiento Codex por proyecto): por eso van como VERIFY y con fallback declarado, no como contrato cerrado.
- No ejecuté `install.sh` (más allá de `--help`) ni escribí nada; el repo quedó intacto.
- La inconsistencia `818f12a` vs `939f501` en `docs/runtime-adopted-version.md` es real y hay que resolverla (V6) antes de fijar la activación.
