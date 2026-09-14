# VALIDATION — cdad-010-opencode-permissions

> Fecha: 2026-09-12 · Evidencia empírica pegada, no descrita (Regla de Oro).

## Baseline RED (pre-implementación)

### 1. Probes de runtime del 2026-09-12 (sesión primaria, pre-fix)

Estos probes SON el RED de la capa empírica (fallas verificadas del estado
actual). Output pegado de la sesión:

```
task → cdad-test-writer:
❌ Agent 'cdad-test-writer' is read-only and should use the delegate tool
   for async background execution.

task → cdad-test-writer-local (probe de permisos):
PROBE-1 go version: DENEGADO permiso
PROBE-2 gofmt --help: PERMITIDO con output
PROBE-3 rtk go version: DENEGADO permiso
PROBE-4 pwd: PERMITIDO con output
PROBE-5 write tests/__cdad_probe__.md: PERMITIDO
PROBE-6 write src/__cdad_probe__.ts: PERMITIDO   ← FUGA (P2 violada hoy)

task → cdad-implementer (probe de permisos):
PROBE-A write tests/__cdad_probe2__.md: DENEGADO  (correcto — regla del agente gana)
PROBE-B go version: DENEGADO permiso              (allowlist sin go)
PROBE-C pytest --version: DENEGADO permiso        (el modelo corrió 'rtk pytest --version')
```

Evidencia de log (runtime, `~/.local/share/opencode/log/opencode.log`):
- `evaluated permission=edit pattern=src/__cdad_probe__.ts action.pattern=* action.action=allow`
  → el hueco lo llenó el `edit: {"*": "allow"}` GLOBAL de `opencode.jsonc`.
- `evaluated permission=edit pattern=tests/__cdad_probe2__.md action.pattern=tests/** action.action=deny`
  → la regla del agente GANA sobre el global (findLast, merge [global..., agente...]).
- `evaluated permission=bash pattern="rtk pytest --version" action.pattern=* action.action=deny`
  → el wrapper rtk no matchea `pytest*` (P4 violada hoy).
- Cero evaluaciones `permission=write` en 124MB de logs → la clave `write:`
  es solo de clasificación (base de la palanca P1).

### 2. Capa estática: run-checks.sh en RED

```
$ bash docs/specs/cdad-010-opencode-permissions/run-checks.sh
RESULTADO: 42 PASS, 132 FAIL
```

Fallas esperadas: A1 (write: ask ausente), A2 (catch-all ausente/ask),
A3/A4/A5/A6 (pares rtk, denies, globs), A7 (generador inexistente),
A8 (docs sin actualizar), A10 (2 validadores en FAIL preexistente).

### 3. Fallas PREEXISTENTES (no de cdad-010, corregidas post-audit)

- `scripts/validate-subagents.sh` → FAIL: `install.sh --check` rechaza
  `~/.config/opencode/agents/cdad-architect.md` — las copias instaladas
  driftaron del repo (enmiendas 02-09/09-08 aplicadas a mano en las copias).
- `tests/validate-consistency.sh` → 1 FAIL (F011, hereda del anterior).
- Corrección registrada en test-audit.md §"Corrección post-RED".
- Implicancia: GREEN debe dejar ambos en PASS (criterio de aceptación 4).

## Matriz de probes GREEN (a ejecutar tras implementar + RESTART de opencode)

Ejecución: SOLO sesión primaria (guardia anti-spawn). Cada celda = comando →
resultado esperado. Evidencia: output pegado abajo de cada fila al ejecutar.

| # | Agente (task) | Probe | Esperado | Postcond |
|---|---------------|-------|----------|----------|
| G1 | cdad-test-writer | `task` aceptado | sin rechazo "read-only" | P1 |
| G2 | cdad-test-writer | write `tests/__probe_g2__.md` | PERMITIDO | P2 |
| G3 | cdad-test-writer | write `src/__probe_g3__.ts` | DENEGADO | P2 |
| G4 | cdad-test-writer | bash `rtk pytest --version` (si pytest en stack) | PERMITIDO | P4 |
| G5 | cdad-test-writer | bash `rtk read docs/x.md` | DENEGADO | P4 |
| G6 | cdad-test-writer | bash `python3 -c "print(1)"` | DENEGADO sin prompt | P3 |
| G7 | cdad-implementer | write `tests/__probe_g7__.md` | DENEGADO | P2 |
| G8 | cdad-implementer | write `src/__probe_g8__.ts` | PERMITIDO | P2 |
| G9 | cdad-implementer | bash `go version` | DENEGADO (enmienda: no es comando de suite; ver abajo) + G9b `rtk pytest --version` PERMITIDO | P4 |
| G10 | cdad-architect | `task` aceptado + write cualquiera | task OK, write DENEGADO | P1/P2 |
| G11 | cdad-reviewer | bash `rtk read docs/x.md` | PERMITIDO | P4 |
| G12 | cdad-reviewer | bash `rtk err ls` | DENEGADO | P4 |
| G13 | cdad-scribe | `task` aceptado | sin rechazo | P1 |
| G14 | cdad-test-writer-odoo | write `tests/__probe_g14__.py` | PERMITIDO | P2 |
| G15 | cdad-implementer-odoo | bash `pylint --version` | PERMITIDO | P4 |
| G16 | todos | grep logs durante la batería | cero `action.action=ask`, cero `permission=write` | P3 |

### Resultados GREEN

#### Fase 1 — install + cierre del drift (2026-09-13, sesión primaria, post-restart)

```
$ bash install.sh --dry-run → Would install: 8 skills x 2 runtimes + 11 cdad agents
$ bash install.sh           → Verify: PASS — 11 cdad agents present after install
$ bash install.sh --check   → Check: PASS (27/27 in sync, perfil basic)
$ rm ~/.config/opencode/agents/cdad-test-writer-local.md → REMOVED (huérfana del spike)
$ bash tests/validate-consistency.sh → Assert PASS: 124, Assert FAIL: 0
$ bash scripts/validate-subagents.sh → RESULTADO: PASS (todas las verificaciones OK)
$ bash docs/specs/cdad-010-opencode-permissions/run-checks.sh → 174 PASS, 0 FAIL
```

Criterio 4 ✓ (3 validadores PASS simultáneo) · Criterio 5 ✓ (dry-run/check/idempotente).
A10 en PASS — el drift preexistente quedó cerrado por install desde el repo.

#### Fase 2 — probes de runtime (matriz G1-G16)

**Lección de procedimiento (2026-09-13, primer intento invalidado):** los
probes corrieron contra config STALE — el restart de opencode ocurrió ANTES
de los `install.sh`, y la config de agentes se carga solo al boot (no hay
hot-reload; el endpoint `/agent` del server siguió sirviendo
`write: [{*, deny}, {tests/**, allow}]` viejo). Resultados descartados como
evidencia GREEN. **Orden correcto: install → restart → probes.** Tras el
restart siguiente, `/agent` sirvió `write: [{*, ask}]` fresco → batería
re-ejecutada desde sesión primaria (7 tasks en paralelo, uno por agente).

```
G1  task→cdad-test-writer: ACEPTADO (corrió; sin rechazo "read-only")        ✓ P1
G2  write tests/__probe_g2__.md: PERMITIDO                                   ✓ P2
G3  write src/__probe_g3__.ts: DENEGADO (edit solo tests/**)                 ✓ P2
G4  bash rtk pytest --version: PERMITIDO (par rtk pytest*)                   ✓ P4
G5  bash rtk read docs/x.md: DENEGADO (rtk read* deny explícito)             ✓ P4
G6  bash python3 -c "print(1)": DENEGADO (catch-all deny, sin prompt)        ✓ P3
G7  cdad-implementer write tests/__probe_g7__.md: DENEGADO (tests/** deny)   ✓ P2
G8  cdad-implementer write src/__probe_g8__.ts: PERMITIDO                    ✓ P2
G9  cdad-implementer bash go version: DENEGADO — ver enmienda abajo
G9b cdad-implementer bash rtk pytest --version: PERMITIDO                    ✓ P4
G10 cdad-architect: task ACEPTADO (P1 ✓); write docs/__probe_g10__.md
    DENEGADO — el runtime NI SIQUIERA expone el tool write (edit sin
    ningún allow → toolset sin write/edit; defensa en profundidad extra)     ✓ P1/P2
G11 cdad-reviewer bash rtk read docs/x.md: PERMITIDO (falló solo por
    archivo inexistente: cat: No such file or directory)                     ✓ P4
G12 cdad-reviewer bash rtk err ls: DENEGADO (rtk err* deny explícito,
    "no se ejecutó ningún comando")                                          ✓ P4
G13 task→cdad-scribe: ACEPTADO (corrió y reportó)                            ✓ P1
G14 cdad-test-writer-odoo write tests/__probe_g14__.py: PERMITIDO en
    re-test (ver nota abajo)                                                 ✓ P2
G15 cdad-implementer-odoo bash pylint --version: PERMITIDO
    (pylint 3.3.8 / astroid 4.0.1)                                           ✓ P4
```

Evidencia de log (delta del opencode.log, toda la batería + re-test):

```
$ grep "action.action=ask\|permission=write" <delta> | wc -l → 0
7× permission=task pattern=cdad-<rol> -> allow (los 7 spawns)
permission=edit pattern=tests/__probe_g2__.md   | tests/** -> allow
permission=edit pattern=src/__probe_g3__.ts     | *         -> deny
permission=edit pattern=tests/__probe_g7__.md   | tests/** -> deny
permission=edit pattern=src/__probe_g8__.ts     | *         -> allow
permission=edit pattern=tests/__probe_g14__.py  | tests/** -> allow
permission=bash "rtk pytest --version"          | rtk pytest* -> allow  (×2)
permission=bash "rtk read docs/x.md"            | rtk read*  -> deny (test-writer)
permission=bash "rtk read docs/x.md"            | rtk read*  -> allow (reviewer)
permission=bash "rtk err ls"                    | rtk err*   -> deny
permission=bash "python3 -c ..."                | *          -> deny
permission=bash "go version"                    | *          -> deny
```

**Enmienda G9 (justificada, regla AUDIT):** la fila decía `go version →
PERMITIDO (si go en stack)`, pero el spec P4 (fuente de verdad) exige para
implementer solo `rtk pytest --version` PERMITIDO — `go version` no es
comando de suite y el allowlist lo niega por diseño (catch-all deny; solo
`go test/vet/build/gofmt`). El RED ya había validado esta misma denegación
como CORRECTA (probe-B: "go version: DENEGADO — allowlist sin go"). La fila
estaba over-specified respecto del spec; resultado real DENEGADO = diseño
correcto. El requerimiento P4 real de implementer quedó cubierto por G9b
(PERMITIDO). Fila corregida a: DENEGADO-esperado + G9b como probe canónico.

**Nota G14 (primer run invalidado, re-test válido):** el primer task odoo
reportó "write tool not found" — pero el log muestra CERO evaluaciones
permission=edit para `__probe_g14__.py`: el agente nunca invocó la
herramienta (misreport del modelo, no del runtime). Re-test de diagnóstico
(listado de toolset real + write): write disponible y PERMITIDO con
evaluación loggeada `tests/** -> allow`. Los dos test-writers tienen config
instalada estructuralmente idéntica (diff: solo globs de dominio Odoo +
allowlist bash; sin bloques `tools:` en ninguno). El sistema de permisos
funcionó correcto en ambos runs; lo que falló fue el reporte del agente.

**Limpieza:** los 3 archivos probe creados (G2, G8, G14) fueron eliminados
post-batería; árbol del repo limpio (git status sin cambios).

#### Fase 3 — loop de fixes de Etapa 4 (2026-09-13)

Review Capa 1 (`review.md`): 4 bloqueantes (H1-H4), 4 opcionales (H5-H8),
veredicto RECHAZADO, bucket h 4/4. Capa 2 (Pablo): política de enforcement +
priorización (transcripta en review.md). Fixes ejecutados:

- **H1 (desviación registrada):** el commit `5f9f4d2` mezcló el fix de la
  palanca anidada (10 agentes) con la edición del assert A1 de
  `run-checks.sh` — el implementer tocó el artefacto de tests fuera de rol
  (AP-4). Bajo la política del dueño, esto se registra como precedente: la
  violación ocurrió, el diseño era correcto (verificado empíricamente), y la
  resolución es documental (enmienda P1 en spec.md + este registro). Una
  violación así futura = tarea NO cumplida.
- **H2 (cerrado con evidencia):** corrida post-fix del validador pegada abajo.
- **H3 (cerrado):** `"find *": allow` eliminado de los 10 agentes + generador
  (`emit_base_allow`). Vector directo (`-delete`/`-exec sh`) bloqueado según
  la política del dueño. `ls *`, `wc *`, `pwd`, `cd *` y pares `rtk find*` de
  lectores se preservan (navegación cubierta).
- **H4 (cerrado):** 16 globs de lectura de tests colocados (src/lib ×
  _test.go/test_*.py/.test.js/.test.ts/.test.mjs/.test.cjs/.spec.ts/.spec.js)
  agregados al `read:` de ambos test-writers, simétricos al `edit:`.
- **H5 (cerrado):** docs stale corregidos (systemPatterns: palanca anidada;
  comentarios de reviewer/scribe).
- **H6 (cerrado):** 5 pares rtk agregados al default agnóstico del repo
  (implementer + test-writer genéricos).
- **H7 (desestimado con motivo):** variantes odoo read-only sin probe runtime
  — estructuralmente idénticas a pares base probados + cobertura estática
  A1/A6 de los 10; la clasificación del plugin es por-config, no por-nombre.
- **H8 (cerrado):** loop muerto de run-checks.sh:155 eliminado.

Evidencia del loop (RED → GREEN, Regla de Oro):

```
# RED (asserts nuevos de H3/H4, commit 17ce985):
$ bash docs/specs/cdad-010-opencode-permissions/run-checks.sh
RESULTADO: 184 PASS, 31 FAIL        # 11 FAIL A11 (find) + 20 FAIL A4 (globs)

# GREEN (fixes implementer en agents/ + generador):
$ bash install.sh                   → Verify: PASS — 11 cdad agents present
$ bash install.sh --check           → Check: PASS (27/27 in sync, perfil basic)
$ bash tests/validate-consistency.sh → Assert FAIL: 0
$ bash scripts/validate-subagents.sh → RESULTADO: PASS
$ bash docs/specs/cdad-010-opencode-permissions/run-checks.sh
RESULTADO: 215 PASS, 0 FAIL
```

**Hallazgo nuevo para ciclo futuro (registrado, NO fixeado acá):** el
test-writer observó en vivo que el matcher de permisos valida el comando
compuesto por PREFIJO allowlist-eado — `cd X && <cualquier cosa>` y
`find ... -exec ...` pasan el gate si el prefijo matchea un allow. Es la
misma clase de exploit que H3 describe a nivel de patrón. Candidato a
feature de hardening posterior (política de matching de compuestos).

**CORRECCIÓN de la premisa anterior (re-review, N1, 2026-09-13):** el
reviewer falsificó la premisa con probes directos y el orquestador la
re-verificó desde sesión de agente (cdad-architect, que tiene `cd *` allow +
catch-all deny):

```
P1: cd . && pwd        → PERMITIDO (<workspace>/projects/cdad)
P2: cd . && uname -sr  → DENEGADO por permisos
P3: pwd; uname -sr     → DENEGADO por permisos
```

El matcher evalúa compuestos **POR SEGMENTO**: cada segmento debe pasar
independientemente (`cd .` permitido en ambos P1/P2, resultado distinto según
el segundo segmento). `cd X && <arbitrario>` NO bypassa. El vector real
residual era solo `find -exec/-delete` dentro del patrón `find *` (cerrado
por H3). Re-probe pegado por la Regla de Oro: la observación del test-writer
era narrada, no evidencia. Corrida de run-checks al árbol HEAD (post
`9875917`, docs-only) exigida por el re-review (H2): **RESULTADO: 215 PASS,
0 FAIL.**

**Fixes de observaciones del re-review (Capa 2 segunda pasada, "De acuerdo"):
N2 aplicado, N3 aplicado, N4 descartado → bucket de hardening.**

- **N2:** assert de orden findLast en A4 (extensión diseñada por
  test-writer, semántica fiel: última allow del globo > último deny invasor
  — catch-all `*` + deny de prefijo `src/**`/`lib/**` condicional; la
  variante Odoo no tiene denies src/lib, solo catch-all + dominio). Evidencia:
  ```
  $ bash run-checks.sh → RESULTADO: 217 PASS, 0 FAIL   (positivo)
  # test negativo: allow movida antes del deny (temporal, revertido):
  FAIL: A4: agents/cdad-test-writer.md/read: orden findLast violado:
        'src/\*\*/\*_test\.go': allow (línea 3) NO queda después de su
        deny (línea 4) — la excepción queda inerte
  RESULTADO: 214 PASS, 3 FAIL → revert → 217 PASS, 0 FAIL
  ```
- **N3:** definición operativa de "vector directo y evidente" en
  systemPatterns.md (probe de una sola invocación con output pegado; lo que
  no califique → candidato de hardening con premisa explícita a verificar).
- **N4:** `find *: allow` global del usuario — descartado de esta feature
  (invariante de no-modificación), anotado para el epic de hardening junto
  con la re-evaluación de matching con la premisa corregida (N1).

## Checklist de criterios de aceptación

1. [x] run-checks.sh todo PASS (RED definido antes de editar) — 215/215
   post-fixes de review (184/31 RED → 215/0 GREEN; ver Fase 3)
2. [x] Matriz G1-G16 con output pegado (Fase 2; G14 con re-test justificado)
3. [x] Cero prompts ask / cero `permission=write` en logs (grep pegado → 0)
4. [x] 3 validadores en PASS simultáneo (Fase 1)
5. [x] install.sh --dry-run / --check / idempotencia (Fase 1)
6. [x] Cero diff agents/claude-code/ (diff 492d6ba^..HEAD → vacío)
7. [x] Docs P6 + ADR-009 completos (ADR-009-politica-rtk-allowlists.md,
   opencode-delegation.md con política write:ask, systemPatterns)
