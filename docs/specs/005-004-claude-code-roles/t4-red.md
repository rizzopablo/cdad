# RED 005-004 T4 — decisiones del guard CC y mapa de hooks declarado una vez

- **Paquete:** `005-004-claude-code-roles-test-writer-red-004` (packet_version 1) · **feature** `005-004-claude-code-roles` · **ejecución** `exec-005-004-claude-code-roles-001`
- **Contrato:** `docs/specs/005-004-claude-code-roles/spec.md` (sha256 `79d57e0a…`) + `plan.md` (sha256 `f7c61a59…`) — **PD-4, PD-9**, **AC-4**, §10 (VERIFY 1/2/4)
- **Subetapa:** RED (etapa 3) · **rol:** test-writer · **commit:** `0cdec7755bcc7400f46f2629a328fe604594adf1` (prefijo `test:`)
- **Archivos modificados:** `tests/test_005_004_t4_cc_guard_decisions.py` (nuevo, 626 líneas, +626/−0). Ningún otro archivo.

## 1. Entregable

Focal declarado por el paquete: `tests/test_005_004_t4_cc_guard_decisions.py` — **6 tests, un test por afirmación observable**.
Oráculo: el guard se **ejecuta como programa** con cargas PreToolUse sintéticas (JSON por stdin, forma real de cada herramienta, `cwd` y `CLAUDE_PROJECT_DIR` = **proyecto fixture propio** en tempdir, política válida del layout CDAD) y se leen sólo las superficies que el contrato declara por su ruta: los **artefactos generados** `agents/claude-code/*.md`, el **dueño del mapa** (`sources/agents/adapters/claude-code.md`, `scripts/cdad-generate.py`) y el **consumidor** (`skills/cdad-cycle/references/claude-code-delegation.md`).

## 2. Tabla test → postcondición/criterio

| test | postcondición / criterio | estado hoy |
|---|---|---|
| `TestUnknownRole::test_pd4_unknown_role_fails_open` | PD-4 (rol desconocido → **fail-open**), AC-4 — ítem 1 del encargo | **verde** (control) |
| `TestRolesWithoutHooks::test_pd4_roles_without_hooks_have_no_route_barrier` | PD-4 (roles **sin hooks** → sin barrera de ruta), AC-4 — ítem 2 | **verde** (control) |
| `TestGeneratedHookFrontmatter::test_pd4_generated_hook_frontmatter_is_coherent` | PD-4 (frontmatter de hooks generado: **matcher, modo y comando**; sin matcher `Bash`; una sola raíz), AC-4 — ítem 3 (coherencia) | **verde** (control) |
| `TestGeneratedHookFrontmatter::test_pd4_generated_hook_map_matches_its_owner` | PD-4/PD-9 (esos pares **coinciden con el mapa declarado una vez en su dueño**), AC-4 — ítem 3 (coincidencia) | **RED** |
| `TestConsumerReference::test_pd4_consumer_references_the_guard_contract` | PD-4/PD-9 (el consumidor **referencia el contrato del guard** —clasificador de la política, paths acotados, fail-closed sin clasificador— y **no repite globs legacy** como mecanismo), AC-4 — ítem 4 | **RED** |
| `TestConsumerReference::test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown` | PD-8/§10 **VERIFY 1** (la afirmación sobre `exit 2` acotada a su alcance observado y con el desconocido del modo no interactivo declarado) — ítem 5 | **RED** |

Alcance acotado respetado: **no se repiten** las decisiones del guard ya cubiertas —implementer/test-writer contra implementación y tests— de `tests/test_004_002_t5_runtime.py` (`pd8_i10_c2_*`) y `tests/test_005_008_t1_nested_tests.py`; se **referencian** como las regresiones declaradas del paquete.

## 3. Comandos exactos y su salida

### 3.1 Focal (RED)

```
$ python3 -m pytest tests/test_005_004_t4_cc_guard_decisions.py -q -rA
PASSED …::TestUnknownRole::test_pd4_unknown_role_fails_open
PASSED …::TestRolesWithoutHooks::test_pd4_roles_without_hooks_have_no_route_barrier
PASSED …::TestGeneratedHookFrontmatter::test_pd4_generated_hook_frontmatter_is_coherent
FAILED …::TestGeneratedHookFrontmatter::test_pd4_generated_hook_map_matches_its_owner
FAILED …::TestConsumerReference::test_pd4_consumer_references_the_guard_contract
FAILED …::TestConsumerReference::test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown
3 failed, 3 passed in 1.25s
```

Los 3 fallos son **AssertionError** (ninguno es ImportError/SyntaxError/NameError ni error de entorno): el arnés de fixtures reutilizado (`tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t5_runtime.py`) construye el proyecto fixture y ejecuta el guard con éxito en los 3 controles.

### 3.2 Motivo de cada RED

1. **`test_pd4_generated_hook_map_matches_its_owner` — el dueño declarado del mapa no declara los pares que los derivados llevan** (5 de 6 pares, `mode-missing` en el **adaptador fuente**; el **generador** sí los declara):

   ```
   que el dueño del mapa NO declara:
   ["adaptador fuente: cdad-implementer-odoo (['Edit', 'Write'] → 'implementer-odoo') [mode-missing]",
    "adaptador fuente: cdad-test-writer (['Edit', 'Write'] → 'test-writer-write') [mode-missing]",
    "adaptador fuente: cdad-test-writer (['Glob', 'Grep', 'Read'] → 'test-writer-read') [mode-missing]",
    "adaptador fuente: cdad-test-writer-odoo (['Edit', 'Write'] → 'test-writer-odoo-write') [mode-missing]",
    "adaptador fuente: cdad-test-writer-odoo (['Glob', 'Grep', 'Read'] → 'test-writer-odoo-read') [mode-missing]"]
   (modos en forma de invocación por superficie: {'adaptador fuente': [], 'generador': []})
   ```

   Contraste positivo del mismo test: el par del `cdad-implementer` (`Edit|Write → implementer`) **no figura como no declarado** — la ventana del modo `implementer` en el adaptador nombra `Edit`/`Write`, de modo que el oráculo lo resuelve `ok`. Es decir: el mapa hoy está **parcial y desactualizado** en su dueño, mientras los derivados generados ya llevan los 6 pares. Falla por aserción de comportamiento declarado (PD-4/PD-9), no por forma de archivo: el test acepta cualquier forma (tabla, lista, comentario o literal), exigiendo el modo con el matcher de su ventana (±2 líneas).

2. **`test_pd4_consumer_references_the_guard_contract` — el consumidor describe los globs legacy como mecanismo y no referencia el clasificador**:

   ```
   AssertionError: Regex didn't match: 'clasificad|classifier|cdad-policy|pol[íi]tica|policy'
   not found in <bloque de hooks de claude-code-delegation.md>
   ```

   El bloque de hooks del consumidor declara el mecanismo con `src/**` / `lib/**` («blocks `Read`/`Grep`/`Glob` on `src/**` and `lib/**`») y no menciona el clasificador de la política del proyecto, el fail-closed sin clasificador ni el acotado de `Grep`/`Glob`.

3. **`test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown` — el tratamiento del `exit 2` no está acotado**:

   ```
   AssertionError: [] is not true : PD-8/§10 (VERIFY 1): el tratamiento del `exit 2` en
   skills/cdad-cycle/references/claude-code-delegation.md no está acotado: ninguna ventana declara
   a la vez el alcance observado (sesión interactiva), el modo no interactivo (`-p`) y el
   desconocido conservado con causa
   ```

   El consumidor sí afirma el bloqueo por `exit 2` («exit 2 prevents execution», «requires trust that the runtime honors exit code 2 (it does, verified empirically …)») pero **sin alcance**: no dice sesión interactiva ni conserva el desconocido del modo no interactivo (VERIFY 1 de PD-8).

### 3.3 Controles verdes hoy (no-regresión, misma corrida)

- `test_pd4_unknown_role_fails_open`: con la política del proyecto presente (aserción de control), el **rol desconocido** deja pasar (rc 0) las **mismas** cargas que un modo declarado bloquea (control positivo: `test-writer-read` → `Read` de implementación = rc 2; `implementer` → `Edit` de tests = rc 2).
- `test_pd4_roles_without_hooks_have_no_route_barrier`: los 7 roles sin hooks del mapa (`architect`, `reviewer`, `scribe` base y `-odoo`, `orchestrator`) **no declaran** `PreToolUse`/`matcher` en su frontmatter generado y su `Edit` sobre una ruta de tests **no se bloquea** (rc 0; control positivo: `implementer` = rc 2).
- `test_pd4_generated_hook_frontmatter_is_coherent`: los 4 agentes con guard declaran, por entrada, un matcher de herramientas conocidas, un modo y un comando; **ningún matcher habilita `Bash`** (decisión del dueño 2026-09-29) y **todos los comandos resuelven una sola raíz**.

### 3.4 Regresiones declaradas por el paquete

```
$ python3 -m pytest tests/test_005_008_t1_nested_tests.py tests/test_004_002_t5_runtime.py -q
28 passed in 10.98s

$ python3 -m pytest tests/ -q --collect-only
921 tests collected in 1.49s          # 0 errores de colección

$ bash tests/validate-consistency.sh
Assert PASS: 154
Assert FAIL: 2
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
FAIL: F011: tests/validate-odoo-specialization.sh → FAIL
```

Los 2 `FAIL` de `validate-consistency.sh` son **pre-existentes** y ajenos al focal: perfil local activo `basic` (`validate-subagents.sh`: «basic profile: no fixed models … the reviewer≠implementer anti-bias is NOT verified in this profile (ADR-007)») y estado RED esperado de otra feature (`validate-odoo-specialization.sh`: «incomplete feature (expected RED state)»). **Delta 0 verificado**: la corrida se repitió con el focal fuera del árbol (archivo movido temporalmente) y el resultado por aserción fue **idéntico** (`diff` de las dos salidas sin diferencias fuera del resumen).

## 4. `git diff --stat` acotado y commit

```
$ git diff --cached --stat
 tests/test_005_004_t4_cc_guard_decisions.py | 626 ++++++++++++++++++++++++++++
 1 file changed, 626 insertions(+)

$ git show --stat --oneline HEAD
0cdec77 test: RED 005-004 T4 — decisiones del guard CC y mapa de hooks declarado una vez (PD-4/PD-9, AC-4)
 tests/test_005_004_t4_cc_guard_decisions.py | 626 ++++++++++++++++++++++++++++
 1 file changed, 626 insertions(+)

$ git log -1 --format=%H
0cdec7755bcc7400f46f2629a328fe604594adf1
```

Commit con pathspec explícito (`-- tests/test_005_004_t4_cc_guard_decisions.py`), sin `--no-verify`, sin push. Al cerrar, el árbol sólo conserva la modificación de `docs/.cdad-state.json` que ya traía el orquestador (no fue tocada, agregada ni commiteada por esta sesión).

## 5. Declaraciones honestas y límites (PD-15)

- **Aislamiento de fase:** no se leyó `scripts/`, `sources/` ni `skills/` para escribir el oráculo (regla del paquete). Sí se leyeron los **artefactos generados** `agents/claude-code/*.md` (salidas declaradas del generador, mismo precedente que el focal T1 de esta feature) y **archivos de `tests/`** (arnés y parser de frontmatter, reutilizados por import, no reimplementados).
- **Contaminación parcial declarada:** la propia salida del test (diagnóstico de AssertionError) mostró fragmentos del **consumidor** (`skills/cdad-cycle/references/claude-code-delegation.md`) —documentación ya citada por la spec §9 y por la ficha T4— y el **estado de declaración** del adaptador (qué pares declara). No se usó para aflojar el oráculo: la corrida previa y la posterior difieren sólo en la agregación del diagnóstico.
- **Lo que el focal NO afirma:** no promete que Claude Code honre `exit 2` ni que los hooks del frontmatter se apliquen a los subagentes nativos (VERIFY 1/2 conservados por PD-8); no habilita ningún hook `Bash`; no usa HOME como política (proyecto fixture en tempdir) ni escribe fuera de `tests/`.
- **Riesgo declarado para el GREEN (condición de detención de la ficha T4):** el focal exige que **ambas** superficies del dueño (adaptador fuente **y** generador) declaren cada par (matcher, modo). Hoy el generador los declara y el adaptador no. Si el orquestador determina que la declaración única vive en `CC_GUARDS` y el adaptador sólo la **referencia**, la cita de PD-4/§9 (`sources/agents/adapters/claude-code.md:18-25,28-43`) debe enmendarse: es exactamente la incertidumbre que la ficha T4 manda **detener y reportar** si el enunciado no puede corregirse sin introducir una segunda copia (PD-9).
- **Evidencia sin rutas absolutas del dueño:** todos los comandos y mensajes del reporte usan rutas relativas al repo.
