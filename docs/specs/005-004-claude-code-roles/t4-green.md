# Informe GREEN — 005-004-claude-code-roles / T4 (implementer, subetapa green)

- **Paquete:** `005-004-claude-code-roles-implementer-green-004`
- **Rol / subetapa:** implementer / green (GREEN de T4, etapa 3)
- **Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…`), referencias aplicables PD-4 y PD-9
- **Plan / ficha:** `docs/specs/005-004-claude-code-roles/plan.md` → T4 (sha256 `f7c61a59…`)
- **Focal congelado:** `tests/test_005_004_t4_cc_guard_decisions.py` (no editado)
- **Commit:** `65a0de95db116ee4dda02c67d9498983b3cf46e6` — `feat:` (sin `--no-verify`)

## 1. Cambio (mínimo, solo las superficies declaradas por la tarea)

| Archivo:línea | Qué quedó declarado |
|---|---|
| `sources/agents/adapters/claude-code.md:34-52` | El **mapa de hooks** por rol: 6 pares `matcher → modo` (`Read|Grep|Glob → test-writer-read`, `Edit|Write → test-writer-write`, `…-odoo-read/-odoo-write`, `Edit|Write → implementer`, `Edit|Write → implementer-odoo`), la **raíz única** que resuelve el comando y los **roles sin hooks** (architect/reviewer/scribe base+odoo y orchestrator). Declara que la emisión del frontmatter proviene de `CC_GUARDS` (`scripts/cdad-generate.py`) y que es una **referencia** — no una segunda copia de las decisiones, globs o clasificador del guard. |
| `skills/cdad-cycle/references/claude-code-delegation.md:43-48` | El consumidor **referencia** el mapa a su dueño (adaptador fuente + `CC_GUARDS`) y declara que no lo re-enuncia. |
| `…claude-code-delegation.md:50-57` | El **mecanismo vigente**: guard v2 que **clasifica** con la **política del proyecto** (`docs/cdad-policy.json`), `Grep`/`Glob` **acotados** a un `path` (sin `path` se rechaza) y **fail-closed** sin clasificador (INV-3); los globs v1 (`src/**`/`lib/**`) quedan **superseded**, ya no son el mecanismo. |
| `…claude-code-delegation.md:62,68,70-71` | Comportamiento por rol reescrito al clasificador (se quitó `src/**`/`lib/**` como mecanismo; tampoco hay `exit code 2` en el detalle por rol). |
| `…claude-code-delegation.md:73-92` | **Afirmación de `exit 2` acotada**: la negativa se observó en sesión **interactiva**; en modo **no interactivo** (`-p` / print / headless) es **desconocido** con causa (PD-8, VERIFY 1). Caveat e implicación reescritos sin contradecir el desconocido. |

Focalizado en la tensión que el orquestador adjudicó: se reconcilió el mapa del adaptador con lo que el generador **ya** emite; **no** se copió el contrato del guard (decisiones, globs legacy o clasificador) y **no** se tocó `scripts/cdad-generate.py`.

## 2. Tabla test → resultado

| Test | Qué verifica | Resultado |
|---|---|---|
| `…::TestGeneratedHookFrontmatter::test_pd4_generated_hook_map_matches_its_owner` | PD-4/PD-9: los pares (matcher, modo) de los derivados están declarados en su dueño | **RED → PASS** (antes: `[mode-missing]` en el adaptador fuente para los 5 pares) |
| `…::TestConsumerReference::test_pd4_consumer_references_the_guard_contract` | PD-4/PD-9: el consumidor referencia clasificador/acotado/fail-closed y no presenta los globs legacy como vigentes | **RED → PASS** |
| `…::TestConsumerReference::test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown` | PD-8/VERIFY 1: `exit 2` acotado a lo observado y desconocido conservado en `-p` | **RED → PASS** |
| `…::TestUnknownRole::test_pd4_unknown_role_fails_open` | PD-4 rol desconocido → fail-open (control la carga bloquea rc 2) | PASS (control, ya verde) |
| `…::TestRolesWithoutHooks::test_pd4_roles_without_hooks_have_no_route_barrier` | PD-4 roles sin hooks → sin barrera de ruta | PASS (control, ya verde) |
| `…::TestGeneratedHookFrontmatter::test_pd4_generated_hook_frontmatter_is_coherent` | PD-4 frontmatter generado (matcher, modo, comando, sin `Bash`, raíz única) | PASS (control, ya verde) |

Focal completo: **3 RED → 3 verdes** (los 3 fallos eran por `AssertionError`, no por import/sintaxis), sin tocar el oráculo.

## 3. Comandos exactos y salida

**Focal (verde):**
```
$ python3 -m pytest tests/test_005_004_t4_cc_guard_decisions.py -q
......                                                                   [100%]
6 passed in 0.92s
```

**Regresión 1 — validador del repo:**
```
$ bash tests/validate-consistency.sh
# RESULT
Assert PASS: 154
Assert FAIL: 2
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
FAIL: F011: tests/validate-odoo-specialization.sh → FAIL
FAIL: 2 assert(s) failed.
```
Las **2 fallas son preexistentes y ajenas a esta tarea** (delta 0): el `git log` del epic registra para T1 «validador 4→2 FAIL» y para T2 «delta 0», y ninguna de las dos lista archivos de esta tarea.
- `F011: scripts/validate-subagents.sh (active profile)` — deuda heredada de perfil/staging (spec §8 D-6); también falla en un worktree fijado a HEAD.
- `A3` de `validate-odoo-specialization.sh` — barrido de patrones sensibles que reporta archivos **preexistentes** de `docs/**` y de `tests/**` (incluidos `__pycache__`); **ninguno** de los dos archivos de esta tarea aparece. Comprobado: un `grep` de rutas del dueño en mis dos archivos no devuelve nada (mi edición no introduce rutas absolutas ni ids de sesión).

**Regresión 2:**
```
$ python3 -m pytest tests/test_005_008_t1_nested_tests.py -q
.........                                                                [100%]
9 passed in 3.18s
```

**Regresión 3:**
```
$ python3 -m pytest tests/test_004_002_t5_runtime.py -q
...................                                                      [100%]
19 passed in 7.14s
```

**Widening (contrato compartido: el adaptador lo leen T1/T2) — focales hermanos:**
```
$ python3 -m pytest tests/test_005_004_t1_dispatch_tool_name.py -q   →  7 passed in 0.96s
$ python3 -m pytest tests/test_005_004_t2_installer_claims.py -q     →  8 passed in 14.09s
$ python3 -m pytest tests/test_005_004_t3_version_check_cc.py -q     →  8 passed in 0.97s
```

**Procedencia / no-regresión de los derivados (INV-2/INV-4):**
```
$ python3 scripts/cdad-generate.py --runtime claude-code --stack odoo --profile optimus --out <tmp>
$ diff -rq <tmp>/agents/claude-code agents/claude-code
(empty)
GEN-OK: repo agents/claude-code byte-identical to a fresh generation
```
La edición vive en secciones de **declaración** del adaptador que no se embeben en los derivados: `make agents` no cambia bytes y ningún archivo de `agents/` fue modificado.

## 4. Diff acotado y hash

```
$ git diff --stat HEAD~1 HEAD
 skills/cdad-cycle/references/claude-code-delegation.md | 40 ++++++++++++++++++++++++++++++++++++--------
 sources/agents/adapters/claude-code.md                 | 17 +++++++++++++++--
 2 files changed, 57 insertions(+), 13 deletions(-)
```
```
$ git show --name-only --format="" HEAD | grep -c '^tests/'
0
$ git status --porcelain
 M docs/.cdad-state.json     # bookkeeping del orquestador (preexistente), NO commiteado
```

**Commit:** `65a0de95db116ee4dda02c67d9498983b3cf46e6`
`feat: declare the Claude Code hook map in its owner and scope the exit-2 claim (005-004 PD-4/T4)`

## 5. Invariantes y declaraciones honestas

- **No edité tests/** (focal congelado intacto; `git show` no referencia ninguna ruta `tests/`).
- No habilité ningún hook `Bash`; **no** prometo que Claude Code honre `exit 2` en modo no interactivo (se conserva `unknown` con causa); no dupliqué la tabla de roles ni el contrato del guard; no toqué `scripts/cdad-generate.py` (fuera de los archivos de la tarea).
- Sin rutas absolutas del dueño, sin ids de sesión, sin push, sin desplegar, sin tocar HOME, sin `git stash` sobre el árbol compartido.
- Para comparar el `rc` del validador contra HEAD usé un **worktree temporal** (`/tmp/opencode/…`) y lo removí al terminar; el árbol principal quedó con solo mis dos archivos commiteados.
- Sin suite completa: la corre una vez quien cierra (política declarada en el paquete).
