Ahora escribo el RED. Primero fijo el diseño leyendo el patrón de u5/u1 (ya visto) y las piezas que reuso.
## Role report — test-writer / RED (U6 de `006-002-delegation-by-layer`)

### 1. Archivos

| Archivo | Cambio |
|---|---|
| `tests/test_006_002_u6_context_discipline.py` | **NUEVO** (508 líneas) — RED de PD-6 (4 reglas de contexto) + INV-4 |
| `tests/validate-consistency.sh` | **sin cambio** (regresión de la ficha; corre) |
| `tests/test_005_009_t3_spawn_reconciliation.py` | **sin cambio** (regresión de la ficha; verde) |

No se tocó `skills/`, `sources/`, `scripts/`, `agents/`, `docs/`. Los untracked ajenos (`docs/planning/`, `findings/incremental-construction-…-2026-10-17.md`) quedan intactos y **no** fueron `git add`.

### 2. Mapa test → PD

| # | Test | PD | Estado observado |
|---|---|---|---|
| 1 | `TestPd6Rule1OrientationFirst::test_pd6_rule1_orient_first_with_the_compact_status_view_without_dumps` | PD-6(1) | **FAIL** (AssertionError: conceptos presentes pero NO co-ubicados — la regla no está declarada como regla) |
| 2 | `TestPd6Rule2SessionRotation::test_pd6_rule2_rotate_the_session_at_task_boundaries_not_mid_unit` | PD-6(2) | **FAIL** (concepto ausente `no a mitad de la unidad`) |
| 3 | `TestPd6Rule3NoSelfRepair::test_pd6_rule3_no_self_repair_redispatch_the_role_naming_the_defect` | PD-6(3) | **FAIL** (concepto ausente `no auto-reparación`) |
| 4 | `TestPd6Rule4NoTmp::test_pd6_rule4_never_tmp_as_channel_or_workspace` | PD-6(4)/INV-4 | **FAIL** (los orquestadores no mencionan `/tmp` en absoluto) |
| 5 | `…::test_pd6_rule4_declares_the_sanctioned_alternative_to_tmp` | PD-6(4)/INV-4 | **FAIL** (sin mención de `/tmp` → sin alternativa sancionada co-ubicada) |
| 6 | `TestPd6OrientationOwnerCited::test_pd6_orchestrators_reference_the_view_first_owner` | PD-6 (cita, no duplica) | PASS → **GUARD pre-satisfecho** (la cita a `references/orientation.md` ya existe en ambos orquestadores; no la introduce U6) |
| 7 | `TestPd6NoTmpInstructionInInstallableText::test_pd6_no_installable_text_instructs_tmp` | PD-6(4)/INV-4 (ausencia) | PASS → **GUARD pre-satisfecho** (ningún texto instalable actual manda usar `/tmp`; se conserva contra degradación) |

Oráculo: conceptos con alternativas (`require_any` reusado de u2), nunca frases exactas; dos nombres normativos del contrato (`orientation.md`, `/tmp`). Co-ubicación por **unidad de regla** (bloque / ítem de lista) con respaldo declarado ±10 líneas alrededor de un ancla propia de la regla. Superficie: los dos orquestadores generados con `make staging PROFILE=basic` en copia temporal (fixture de u1, nunca se escribe en el repo) + el texto instalable `skills/**` + `agents/**` para el oráculo de ausencia de INV‑4. Los únicos imports son de `tests/` (no se leyó implementación para derivar aserciones).

### 3. Comandos y salida

```
$ python3 -m pytest tests/test_006_002_u6_context_discipline.py -q
5 failed, 2 passed in 1.56s
  FAILED …test_pd6_rule1_orient_first_with_the_compact_status_view_without_dumps
  FAILED …test_pd6_rule2_rotate_the_session_at_task_boundaries_not_mid_unit
  FAILED …test_pd6_rule3_no_self_repair_redispatch_the_role_naming_the_defect
  FAILED …test_pd6_rule4_never_tmp_as_channel_or_workspace
  FAILED …test_pd6_rule4_declares_the_sanctioned_alternative_to_tmp
# los 5 fallos son AssertionError de contenido ausente/no co-ubicado:
#   grep -cE "ImportError|SyntaxError|ModuleNotFound|NameError" → 0

$ python3 -m pytest tests/test_005_009_t3_spawn_reconciliation.py -q
19 passed in 0.82s                     # regresión de la ficha, verde

$ bash tests/validate-consistency.sh
Assert PASS: 161 / Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL

$ python3 -m pytest tests/test_006_002_u1 … u5 -q
31 passed in 7.39s                     # superficie 006-002 sana (10+4+6+5+6)

$ python3 -m pytest tests/test_005_003_t1_compact_view.py tests/test_005_003_t2_examples_execute.py -q
21 passed in 8.82s                     # dueño de «vista primero» intacto
```

Suite completa: **no** corrida (política del packet — la cierra el closer).

### 4. Commit

```
git add tests/test_006_002_u6_context_discipline.py
git commit -m "test: 006-002 U6 RED — disciplina de contexto de los orquestadores (PD-6)"
→ edc58ae  (1 archivo, 508 inserciones, todo bajo tests/; git diff HEAD~1 HEAD → solo ese archivo)
```
Sin `--no-verify`, sin `git stash`, sin push; los untracked ajenos siguen sin agregar.

### 5. Acoplados (enmienda A-1) — sin reformulación, justificado

U6 **agrega** texto (sección directiva del orquestador fuente, `orientation.md` §1, una frase de `SKILL.md`) y **no cambia** ningún texto que fijen `test_005_009_t3_spawn_reconciliation.py` (SPAWN GUARD, anti-recursión, distinción de delegación externa, escritor único del state, paridad fuente↔generado) ni `validate-consistency.sh` (F001/F004/F007/F010/F011). Por eso no hay nada que reformular: ambos se corren como regresión. La paridad fuente↔generado depende de que el GREEN regenere los agentes (`make agents`) — trabajo del implementer, no reformulación de tests.

### 6. Bloqueo declarado (no introducido por este RED)

`validate-consistency.sh` F011 falla por **drift de las copias instaladas en el HOME** contra el repo (`install.sh --check`): lista 22 agentes de `.config/opencode/agents` + `.claude/agents` y las 3 bases de `skills/cdad-cycle` — consecuencia de los movimientos de U1–U5 frente a la instalación del owner, **no** de este RED (mi diff es un archivo nuevo bajo `tests/`, que no es una entrada de ese check). Es un gate de PD‑7 que el closer/owner deberá resolver refrescando la instalación; queda declarado, sin workaround.

### 7. Declaraciones honestas

- **No abrí** `skills/`, `sources/`, `scripts/` ni `agents/` para derivar aserciones: el oráculo sale del spec (§2 PD-6, §3 INV-4) y del plan (ficha U6 + A-1) más el encargo del packet. Los artefactos se leen **al ejecutarse** el test (caja negra).
- Los dos PASS son **guards pre-satisfechos declarados en el docstring**; la no-duplicación del §1 por el orquestador es prosa → review de stage 4 (límite honesto, ya declarado también por PD‑6: el test prueba que la regla existe, no que se obedezca).
