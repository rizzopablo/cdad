# cdad-010: Permisos OpenCode — clasificación task-able, fail-fast sin ask, allowlists derivadas del stack

> Fecha: 2026-09-12 · Origen: probes empíricos del 2026-09-12 (sesión primaria)
> y hallazgo de delegación rota (delegate timeout, findings del workspace
> 2026-09-08). Estado: DRAFT — sin marca de aprobación.

## Descripción funcional

La delegación a los agentes `cdad-*` en OpenCode está rota por interacción de
tres capas verificadas empíricamente:

1. **Clasificador del plugin** (`~/.config/opencode/plugins/background-agents.ts:326-361`,
   fuera del repo): un agente es read-only si y solo si `edit`, `write` y
   `bash` tienen TODOS catch-all deny. Ignora allows específicas. Los
   sub-agentes cdad (que tienen `write: {"*": deny, "tests/**": allow}`) son
   clasificados read-only → el orquestador es forzado a `delegate`, canal
   muerto en este deploy (modelo default global sin crédito). Probe: `task` a
   cdad-test-writer → RECHAZADO ("read-only, use delegate").
2. **Matcher del core** (1.18.18): `merge()` concatena `[global..., agente...]`
   y `findLast` hace ganar a la última regla que matchea. La fuga del
   2026-09-12 (`write src/__cdad_probe__.ts` PERMITIDO en cdad-test-writer-local)
   se explica porque esa variante live (fuera del repo) tiene `edit:` sin
   catch-all deny → el global `edit: {"*": "allow"}` llena el hueco.
3. **Huecos de allowlist + wrapper rtk**: las allowlists hardcodean
   Python/Node (o legacy Go); los modelos envuelven comandos en `rtk`
   (convención del workspace) y `pytest*` no matchea `rtk pytest*`.

Además, descubrimiento clave: la clave `write:` del frontmatter NO se evalúa
en runtime (el tool write pide `"edit"`; cero evaluaciones `permission=write`
en 124MB de logs), pero el clasificador del plugin SÍ la lee → `write: ask`
es una palanca de clasificación sin efecto en runtime.

Esta feature hace: (i) task-ables los sub-agentes vía `write: ask`
(documentado como hack con regla de vigilancia), (ii) bloques de permisos
autocontenidos con catch-all explícito y orden findLast-correcto, (iii) cero
`ask` en runtime (fail-fast deny), (iv) allowlists bash por rol con pares
`X*`/`rtk X*` (política formalizada en ADR-009), (v) install.sh deriva las
allowlists del stack detectado, (vi) actualización del mapa de delegación.

**Decisiones de scope tomadas por el usuario (Pablo, 2026-09-12):**
- Las 5 variantes `-odoo` entran en scope (misma falla de clasificación y
  allowlists hardcodeadas) → total **10 agentes** (5 base + 5 odoo). El
  orquestador queda fuera por diseño (mode: all, permission: allow, nunca
  task-spawneado).
- El plugin `background-agents.ts` NO se modifica (vive fuera del repo);
  `write: ask` es el workaround elegido, no un fix del clasificador.

## Contrato (postcondiciones numeradas)

**P1 — Clasificación write-capable (task-able).** Los 10 sub-agentes OpenCode
(`cdad-{architect,test-writer,implementer,reviewer,scribe}` + sus 5 variantes
`-odoo`) declaran en su frontmatter la clave `write: "ask"` (valor simple,
literal), y ninguna otra clave de permisos con catch-all deny cambia su
clasificación. Verificación:
- (estático) `frontmatter` de cada agente contiene `write: "ask"`.
- (empírico, probe) `task` con `subagent_type: cdad-<rol>` para cada uno →
  aceptado (sin rechazo "read-only... use delegate").
`cdad-orchestrator` queda fuera (mode: all, permission: allow, nunca
task-spawneado).

**P2 — Bloques autocontenidos y scoping de edición por path.** Para cada uno
de los 10 sub-agentes, cada clave de permisos con reglas (`edit`, `bash`,
`read` donde exista) abre con catch-all explícito EN EL AGENTE (nunca heredado
del global) y coloca las reglas específicas DESPUÉS del catch-all (semántica
findLast). En particular:
- `cdad-test-writer` (+ `-odoo`): `edit` = `{"*": deny, "tests/**": allow,
  "**/tests/**": allow, ...tests colocados}` donde "tests colocados" son los
  mismos patrones del fix path-guard 2026-09-04: `**/*_test.go`,
  `**/*.test.{js,ts,mjs,cjs}`, `**/*.spec.{ts,js}`, `**/test_*.py` (VERIFICAR
  soporte de estos globs en el matcher 1.18.x con probe antes de GREEN; si no
  soporta braces `{}`, el generador expande variantes). `read` agrega las
  mismas excepciones de lectura para tests colocados bajo `src/**`/`lib/**`.
- `cdad-implementer` (+ `-odoo`): `edit` = `{"*": allow, "tests/**": deny,
  ...tests colocados deny}` — la blocklist incluye los patrones de tests
  colocados.
- Los read-only (`architect`, `reviewer`, `scribe` + `-odoo`): `edit: deny`
  (simple).
Verificación empírica (probes, tras restart):
- test-writer: write `tests/<probe>` PERMITIDO; write `src/<probe>.ts`
  DENEGADO; write `<paquete>/<probe>_test.go` PERMITIDO (sujeto al VERIFICAR).
- implementer: write `tests/<probe>` DENEGADO; write `src/<probe>.ts`
  PERMITIDO; write `<paquete>/<probe>_test.go` DENEGADO.
- read-only: write `<cualquier path>` DENEGADO.

**P3 — Cero `ask` en runtime (fail-fast).** Ninguna regla de permiso
evaluable en runtime (claves `bash`, `edit`, `read` de los 10 agentes) resuelve
a "ask"; todo default es deny explícito en el catch-all del agente. Única
excepción: la palanca de clasificación `write: "ask"` (P1), no evaluable en
runtime. Verificación:
- (estático) ninguna acción `ask` en las claves `bash`/`edit`/`read` de los
  10 frontmatters; prohibido un catch-all `allow` en `bash` de cualquier rol
  cdad.
- (empírico) comando no-allowlistado en un sub-agente (p.ej. `python3 -c` en
  test-writer) → DENIED sin prompt visible; durante toda la batería de probes,
  cero prompts de permiso y cero evaluaciones `permission=write` en los logs
  del runtime (regla de vigilancia).

**P4 — Allowlist bash por rol + política rtk (núcleo verificable).**
- Prohibido en TODOS los roles cdad: catch-all `"rtk *": allow` (fuga total).
- Denegados explícitamente en TODOS los roles: `"rtk err*"`, `"rtk summary*"`
  (ejecución arbitraria).
- Denegados explícitamente en los roles cuyo scope de lectura los prohíbe
  (test-writer genérico + odoo): `"rtk read*"`, `"rtk grep*"`, `"rtk find*"`,
  `"rtk diff*"` (fuga de lectura hacia `src/**`). En roles lectores
  (architect/reviewer/scribe + odoo) los pares `rtk read*`/`rtk grep*`/
  `rtk find*` están permitidos (leyendo, que es su trabajo).
- Cada rol declara pares `X*` + `rtk X*` para los comandos de suite legítimos
  del stack detectado (P5 define el set; ejemplo Go: `go test*` + `rtk go
  test*`; Python: `pytest*` + `rtk pytest*`).
- Los read-only conservan allowlist de SOLO lectura (sin `sed -i`, `tee`,
  redirecciones de escritura): sin backdoor bash de escritura.
Verificación: estático (pares presentes, denies presentes, orden
catch-all-primero vía awk line-order) + empírico (probes):
- test-writer: `rtk pytest --version` PERMITIDO (si pytest en el stack
  detectado); `rtk read src/x.go` DENEGADO; `rtk summary x` DENEGADO.
- implementer: `rtk pytest --version` PERMITIDO; `sed -i` sobre tests
  DENEGADO.
- read-only: `rtk read docs/x.md` PERMITIDO; `rtk err` DENEGADO.

**P5 — install.sh deriva allowlists del stack detectado.** La allowlist bash
por rol deja de estar hardcodeada en los `.md` del repo para los comandos de
suite: una fuente única (patrón `scripts/cdad-models.sh`: nuevo
`scripts/cdad-bash-allowlist.sh`, generador rol×stack) produce las entradas;
`install.sh` aplica el resultado SOLO en la copia instalada (mismo patrón que
la línea `model:`), detectando los toolchains disponibles en la máquina destino
(`command -v`: go, python/pytest, node/npm, deno, cargo, ruby, make...). El
repo conserva un default agnóstico (`make *` + navegación git/ls, tal como
F009 exige). Verificación:
- (estático) el generador existe y `install.sh` lo invoca (grep).
- (empírico) `install.sh --dry-run` lista la allowlist derivada para el stack
  actual; después de instalar, el agente copiado contiene los pares del stack
  detectado y NO contiene entradas de stacks ausentes; `install.sh --check`
  sigue en PASS (compara contra la expectativa DERIVADA, no contra bytes del
  repo); segunda corrida de install = idempotente (sin cambios).
- Las asserts F009 de `validate-consistency.sh` siguen en PASS (o se ajustan
  con justificación registrada en este spec, regla AUDIT).

**P6 — Documentación actualizada (mapa de delegación + hack documentado).**
- `references/opencode-delegation.md`: tabla actualizada — los roles son
  task-ables vía `write: ask`; `delegate` documentado como fallback no-viable
  en este deploy (con la evidencia citada y el mitigation de regla de cierre
  intacto); la distinción task/delegate queda explicada por clasificación del
  plugin, no por rol CDAD.
- `SKILL.md` §4 y `agents/cdad-orchestrator.md`: misma corrección (o cita).
- `docs/projectbrief.md`: restricción delegación corregida.
- `docs/systemPatterns.md`: convención nueva — "palanca `write: ask`"
  documentada con fecha (2026-09-12), motivo (clasificación del plugin lee
  `write`; runtime no la evalúa — evidencia logs), y REGLA DE VIGILANCIA: si
  una versión futura de opencode evalúa la clave `write` en runtime, la
  palanca empieza a generar prompts y debe revisarse (checklist al migrar
  versión).
Verificación: estático (grep por sección en cada archivo).

**Limpieza fuera del repo (ejecuta el orquestador, no install.sh):** eliminar
`~/.config/opencode/agents/cdad-test-writer-local.md` (variante huérfana del
spike de debugging; contamina probes futuros y es la que filtra a `src/`).

## Invariantes

- **No se modifica el plugin** `background-agents.ts` ni la config global del
  usuario (`opencode.jsonc`): el fix vive íntegro en el repo (agents +
  install.sh) y sus copias instaladas.
- **Orden de reglas**: catch-all primero, específicas después (semántica
  findLast). Cualquier regla específica antes del catch-all es un bug de
  config, no una preferencia.
- **Autocontención**: el catch-all de cada clave vive en el agente; el global
  llena huecos solo por diseño explícito (implementer-edit usa `"*": allow`
  propio, no heredado).
- **Fail-fast**: default deny explícito, nunca `ask` (única excepción
  documentada: la palanca `write: ask`).
- **Repo = fuente de verdad**: las copias instaladas derivan (model +
  allowlist); nunca se edita una copia a mano.
- **Claude Code sin cambios**: los agentes `agents/claude-code/` no llevan
  diff (el hack es OpenCode-specific; el path-guard CC ya cubre tests
  colocados desde 2026-09-04).
- **Scope de archivos cerrado**: 10 agentes OpenCode (5 base + 5 odoo),
  `install.sh`, `scripts/cdad-bash-allowlist.sh` (nuevo),
  `tests/validate-consistency.sh` (solo asserts F009 si aplica), 4 archivos
  de doc (P6), `docs/specs/cdad-010-opencode-permissions/` (spec,
  VALIDATION.md, run-checks.sh), `docs/adr/ADR-009-*` (nuevo).

## Desviación registrada (proceso de verificación)

- Los "tests" de comportamiento de esta feature son **PROBES ejecutables solo
  desde una sesión primaria** de opencode (la guardia anti-spawn prohíbe
  sub-subagentes — no se puede verificar permisos de cdad-* desde dentro de un
  cdad-*).
- Entre escribir la config y verificar hay **restart de opencode**
  obligatorio (los agentes se leen al boot).
- El **RED ya existe**: los probes del 2026-09-12 (task rechazado, `go
  version` denegado, fuga `src/__cdad_probe__.ts`, `rtk pytest` denegado) son
  la evidencia de fallo; se registran como baseline en VALIDATION.md. La capa
  estática (run-checks.sh) sí sigue el RED convencional: asserts definidos
  antes de editar y fallando sobre el estado actual.

## Criterios de aceptación (verificables)

1. `run-checks.sh` de la feature: todos los asserts en PASS, definidos en RED
   antes de editar (evidencia: output pegado).
2. Matriz de probes de VALIDATION.md ejecutada desde sesión primaria tras
   restart: 100% de resultados esperados de P1-P4, output pegado (no
   descrito).
3. Durante los probes: cero prompts de permiso `ask` y cero evaluaciones
   `permission=write` (grep de logs pegado como evidencia).
4. Suite completa del repo en PASS simultáneo: `validate-subagents.sh`,
   `validate-odoo-specialization.sh`, `validate-consistency.sh` (F009 intacto
   o ajustado con justificación en este spec).
5. `install.sh --dry-run` muestra allowlist derivada; `--check` PASS post-
   install; install idempotente (segunda corrida sin diff).
6. Cero diff en `agents/claude-code/` (excepto lo que el AUDIT justifique).
7. Los 4 archivos de doc de P6 contienen las correcciones (checks grep por
   sección) y `docs/adr/ADR-009-*` existe con la matriz completa de la
   política rtk.
