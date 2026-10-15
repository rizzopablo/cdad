---
feature_id: 003-006-runtime-adoption
feature_name: Adopción y cableado de las herramientas CDAD por runtime
created_at: 2026-10-07
status: approved
approved_by: orchestrator (HITL delegation epic-003)
approved_at: 2026-10-07
---

# Spec: Adopción y cableado de las herramientas CDAD por runtime

## 1. Descripción funcional (Motivo)

Lo construido en 003-001/005 (`prepare`), 003-002 (`receive`), 003-003
(`cdad_guard`) y 003-004 (`cdad_continuity`) existe y está probado, pero **no se
descubre ni se usa** en el ciclo normal, y cada runtime (OpenCode, Claude Code,
Codex) carga **versiones distintas** de skills, agentes y guards. Esta feature
**cablea, activa y comprueba**: enlaza las herramientas en el ciclo, entrega un
generador de activación **por proyecto** que apunta a la raíz aislada adoptada,
adopta `receive` en el flujo de despacho, re-adopta la nueva versión operativa y
valida un recorrido breve por runtime. No agrega funcionalidad nueva; el
endurecimiento va a deuda.

## 2. Contrato

### 2.1 Cableado del ciclo
`skills/cdad-cycle/SKILL.md` y el cuerpo del orquestador (`sources/roles/orchestrator.md`
y sus agentes regenerados) nombran cada comando en su paso del ciclo, **sin
duplicar interfaces** (los contratos viven en `references/continuity.md`,
`references/progress-guards.md`, `references/re-entry.md` y las specs 002/003/004):

- `prepare` — Step 4 (ya cableado).
- `begin` — antes de despachar un paquete (write-ahead).
- `checkpoint` — al cerrar el límite de tarea/subfase.
- `receive` — re-entry: protocolo de materialización de rol read-only.
- `reconcile` — antes de todo retry o resume.
- `resume` — al iniciar una sesión nueva (Step 1).
- `trigger` — señal advisory antes de rotar.
- `classify` — declarado **fuera** (sin lector de sesiones).

La tabla "How to read the references" de `SKILL.md` enlaza `references/continuity.md`.

### 2.2 Activación por proyecto (nunca las configuraciones del HOME real)
`scripts/cdad-activate.py --project-root R --adopted-root A [--runtime RUNTIME]... [--dry-run]`
emite, por runtime, archivos de activación git-ignorados que apuntan a `A`:

- OpenCode: `.opencode/opencode.jsonc` (`skills: [A/.config/opencode/skills]`); los
  agentes de proyecto los sigue publicando `prepare` (I9).
- Claude Code: `.claude/{agents,skills}`. Los hooks viven en el **frontmatter de
  cada agente**, no en `settings.json`: la activación **reescribe de forma
  determinista** la línea
  `command: ~/.claude/cdad-scripts/path-guard.sh <rol>` →
  `command: <A>/.claude/cdad-scripts/path-guard.sh <rol>`.
  **No se emite `.claude/settings.json`.**
- Codex: `.agents/skills` → `A/.agents/skills` (VERIFY, V2); si el runtime no las
  descubre, se declara el límite y el camino es **paquete + prompt de rol**.

Garantías: determinista (mismo input → bytes idénticos); **cero escrituras en las
configuraciones del HOME real** (`~/.claude`, `~/.agents`, `~/.config/opencode`);
`--dry-run` sin efectos; `.gitignore` cubre `.opencode/`, `.claude/` y `.agents/`;
**no-clobber**: si un archivo destino existe y difiere de lo que el generador
emitiría, el generador **falla con error** (el `--dry-run` lo muestra) y nunca
sobrescribe en silencio.

### 2.3 `receive` en el flujo (reutiliza 002)
El orquestador **stagea** el FINAL TEXT del rol bajo `.cdad/inbox` (con
`RESULT.json`), ejecuta `receive`, valida el receipt y registra la **transición
única** de state. `receive` no aprueba (`semantic_status` = `pending`); el state
lo escribe solo el orquestador.

### 2.4 Continuidad en el ciclo
`begin`/`checkpoint`/`reconcile`/`resume` se usan en el ciclo; `trigger` es
advisory (casi siempre `unknown`); `classify` queda fuera.

### 2.5 Re-adopción de la versión operativa (v5)
El commit de cierre de T1–T3 se instala en una **raíz aislada versionada nueva**
bajo `~/.cache` (`CDAD_INSTALL_ROOT=$HOME/.cache/cdad-adopted-<rev> bash install.sh
--optimus`), se registra en `docs/runtime-adopted-version.md` (tabla vigente +
historial) con verificación de consumidor, y la activación de proyecto **repunta**
a esa raíz. La identidad de versión se comprueba contra el
`.cdad-install-manifest.json` que ya existe en `A` (sin herramienta nueva).
**Límite declarado:** la re-adopción escribe bajo `~/.cache` (raíz aislada
versionada), **nunca** en `~/.claude`, `~/.agents` ni `~/.config/opencode`.

## 3. Postcondiciones (verificables)

- **P1.** `skills/cdad-cycle/SKILL.md` enlaza `references/continuity.md` en su
  tabla de referencias, y el cuerpo del orquestador (`sources/roles/orchestrator.md`
  y sus agentes regenerados) nombra `receive`, `begin`, `checkpoint`, `reconcile`
  y `resume` en el paso correspondiente del ciclo, sin duplicar las interfaces;
  `trigger` se declara advisory y `classify` fuera.
- **P2.** El generador de activación es determinista: ejecutado dos veces con el
  mismo `(project_root, adopted_root)`, produce bytes idénticos.
- **P3.** Toda escritura de la activación está **fuera de las configuraciones del
  HOME real** y dentro de rutas git-ignoradas del proyecto; `git check-ignore`
  cubre `.opencode/`, `.claude/` y `.agents/`.
- **P4.** En OpenCode, con la versión v5 adoptada, una sesión/subagente nuevo
  reporta como base de `cdad-cycle` un directorio bajo la raíz adoptada y ve los
  4 scripts (`cdad_packet`, `cdad_result`, `cdad_guard`, `cdad_continuity`).
- **P5.** La activación de Claude Code emite agentes de proyecto con el hook
  reescrito a `<A>/.claude/cdad-scripts/path-guard.sh` y **ningún `command:`
  emitido contiene `~/.claude`** (verificación de unidad, T2); en runtime la
  activación resuelve y un hook ausente **no bloquea** herramientas (fail-open
  estructural, `exit 127 ≠ 2`) — evidencia solo en el rehearsal de T4.
- **P6.** El recorrido de Codex consume el paquete y el prompt de rol desde la
  raíz adoptada (o, si el runtime no descubre skills de proyecto, el límite queda
  declarado); sin adaptador de agentes Codex.
- **P7.** `receive` forma parte del flujo normal: la salida FINAL TEXT de un rol
  se stagea y se recibe (rc=0); un retry idéntico converge al mismo receipt byte
  a byte; el state registra una única transición.
- **P8.** Con `receive` en el flujo, `cdad_continuity reconcile` clasifica
  `received` en el recorrido de aceptación (deja de ser `dispatched-unknown`).
- **P9.** `begin` (write-ahead antes de despachar), `checkpoint` (límite de tarea)
  y `resume` (sesión nueva) se usan en el ciclo; `resume` reconstruye objetivo,
  decisiones con razón, autoridad y próxima acción sin re-preguntar.
- **P10.** `cdad_guard classify` se declara fuera de alcance por falta de lector
  de sesiones; `trigger` sigue siendo señal advisory (`unknown` sin contador).
- **P11.** El commit de cierre de T1–T3 queda adoptado como **v5**: instalado en
  una raíz aislada bajo `~/.cache`, registrado en `docs/runtime-adopted-version.md`
  (tabla vigente + historial) con verificación de consumidor, y la activación de
  proyecto repunta a esa raíz; ningún runtime del recorrido carga la versión
  anterior.
- **P12.** El recorrido real por runtime queda registrado en `adoption-ledger.md`
  **sin rutas absolutas locales** (marcadores `<adopted-root>`, `<project-root>`) y
  se entrega `closure-amendment-draft.md` al dueño.

## 4. Invariantes verificables

- **I1.** Ninguna activación escribe en las configuraciones del HOME real
  (`~/.claude`, `~/.agents`, `~/.config/opencode`); es por proyecto y apunta a la
  raíz aislada adoptada. La raíz adoptada versionada bajo `~/.cache` es la
  **excepción declarada** (la escribe la re-adopción, no la activación).
- **I2.** Una sola versión operativa por runtime (la raíz adoptada v5); ninguna
  copia global de HOME es fuente.
- **I3.** Los archivos de activación no se commitean; el producto entrega
  generador, procedimiento y tests.
- **I4.** No se endurecen permisos; sin push automático.
- **I5.** `receive` no aprueba; el state lo escribe solo el orquestador.
- **I6.** `classify` y la medición de contexto no se cablean (sin lector).

## 5. Criterios de aceptación

1. Suite completa verde y validadores del repo sin regresiones nuevas.
2. Recorrido real por runtime registrado en `adoption-ledger.md` (sin rutas
   absolutas locales) con evidencia `file:line`.
3. `reconcile` = `received` en el recorrido (no `dispatched-unknown`) y `resume`
   reconstruye sin re-preguntar al usuario.
4. v5 adoptada, registrada y cargada por los runtimes del recorrido.
5. Cero cambios en las configuraciones del HOME real.
6. Borrador de enmienda de cierre del epic entregado al dueño.

## 6. Fuera de alcance

Lector de sesiones para `classify`; medición de contexto; adaptador de agentes
Codex; `settings.json` de Claude Code de proyecto (deuda si V1 lo exigiera); guard
parametrizado en origen (`cdad-generate.py`; la reescritura en la activación basta
para el MVP); hooks de Claude Code más allá de `path-guard`; rotación automática de
sesión; anonimización retroactiva de docs existentes (la ruta absoluta
preadoptada en `docs/runtime-adopted-version.md` va a deuda de anonimización);
cualquier cambio en las configuraciones del HOME real; push.
