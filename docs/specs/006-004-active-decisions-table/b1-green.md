GREEN complete. Report below.

---

# 006-004 B-1 — GREEN (implementer, subfase `green`)

## 1. Qué se cambió

**Un solo archivo** (write scope: `skills/**`): `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`.

La sección `## Current decisions` de la plantilla ahora tiene **encabezado + separador y CERO filas de datos**. El ejemplo de fila **no se borró**: se explicita **fuera** de la tabla, en prosa (la viñeta `**File**` nombra la ruta de ejemplo `docs/adr/ADR-NNN-<slug>.md`; ninguna línea empieza por `|`, así que ningún comprobador lo lee como decisión). Se añadió una frase que declara la semántica de la tabla vacía (una fila se agrega al aprobarse una decisión; la de una decisión reemplazada se conserva marcada obsoleta).

Diff (commit `fc1179b`): `1 file changed, 6 insertions(+), 2 deletions(-)` — la fila de datos sale, la explicación queda en prosa.

**Nada que regenerar:** `build/staging/` y `agents/` derivan de `sources/**` (`scripts/cdad-generate.py`), no de `assets/**`; `grep -rln "Current decisions" agents/ build/staging/` → **0 coincidencias**. La plantilla se instala por copia archivo a archivo (`install.sh`, `stage_owned_file`), sin artefacto derivado versionado. **No toqué HOME** (ni config, ni store, ni runtime, ni agentes instalados).

## 2. Mapa test → resultado

| # | Test (focal / regresión) | Postcondición | Resultado |
|---|---|---|---|
| 1 | `test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row` | PD-7 / E5 | **GREEN** (antes: FALLA) |
| 2 | `test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker` | PD-7 / E5 / PD-11 | **GREEN** (antes: FALLA `PD-11-FILE`) |
| 3 | `test_b1_the_template_still_declares_the_row_shape_outside_the_data_rows` (control) | PD-7 | **GREEN** (verde antes y después) |
| 4 | `tests/test_006_004_u4_decisions_table.py` (9 casos: PD-7-SECTION, PD-7-SHAPE/NOTE, exit gate, upkeep, CAS, scribe, bloque de texto) | PD-7/8/9 | **GREEN** (no regresión) |
| 5 | `tests/test_006_004_u2_decisions_section.py` (incluye `prepare`/render **sin filas** byte-idéntico — PD-5/E5) | PD-5 | **GREEN** |
| 6 | `tests/test_006_004_u7_seed_verification.py` (bloque permanente U7) | PD-11 | **GREEN** |
| 7 | `tests/test_004_002_t2_bootstrap.py` (bootstrap que copia la plantilla) | PD-7 | **GREEN** |
| 8 | `test_005_006_t2_intake.py`, `test_005_006_t5_acceptance.py`, `test_004_002_t1_policy.py`, `test_003_002_t2_reviewfix.py`, `test_006_005_u7_scribe_role_report.py`, `test_role_packets.py` | regresiones de la ficha | **GREEN** (71 passed) |

## 3. Comandos y salida

```sh
cd <home>/clawd/projects/cdad/cdad
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_004_b1_template_empty.py -v
```
```
tests/test_006_004_b1_template_empty.py::TestB1TemplateIsBornEmpty::test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row PASSED [ 33%]
tests/test_006_004_b1_template_empty.py::TestB1TemplateIsBornEmpty::test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker PASSED [ 66%]
tests/test_006_004_b1_template_empty.py::TestB1TemplateIsBornEmpty::test_b1_the_template_still_declares_the_row_shape_outside_the_data_rows PASSED [100%]
============================== 3 passed in 0.14s ===============================
```

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_004_*.py -q
→ 56 passed in 27.32s

# focales + bootstrap (estado ya commiteado)
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider \
  tests/test_006_004_*.py tests/test_004_002_t2_bootstrap.py -q
→ 73 passed in 33.89s

# regresiones declaradas en la ficha
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider \
  tests/test_005_006_t2_intake.py tests/test_005_006_t5_acceptance.py tests/test_004_002_t1_policy.py \
  tests/test_003_002_t2_reviewfix.py tests/test_006_005_u7_scribe_role_report.py tests/test_role_packets.py \
  tests/test_004_002_t2_bootstrap.py -q
→ 71 passed in 64.28s (0:01:04)
```

```sh
make validate
→ PASS: 006-004 U4 PD-7-SECTION / PD-7-SHAPE / PD-7-NOTE / PD-8-UPKEEP / PD-9-CAS / PD-9-SCRIBE / PD-7-GATE
→ PASS: 006-004 U7 PD-11-SECTION / PD-11-FILE / PD-11-REPLACEMENT / PD-11-ROLES / PD-11-PRINCIPLE / PD-11-NOTE / PD-11-NO-ID
→ Assert PASS: 182
→ Assert FAIL: 1
→ FAIL: 1 assert(s) failed.
```

**F011 — declarado como ambiental (el gate lo preveía).** El único FAIL es `F011: scripts/validate-subagents.sh (active profile) → FAIL`, **preexistente** (ya registrado en `b1-red.md`:62 y en `review.md:113-114`): es la **deriva entre el árbol instalado y el repo** (`~/.claude/agents/cdad-*.md`, `~/.config/opencode/agents/cdad-*.md`, `staged agents/opencode/cdad-orchestrator.md` y `cdad-reviewer.md` ausentes, `~/.claude/skills/cdad-cycle/…` distintos, más `cdad-reviewer.md declares model:`). **No lo corrijo**: arreglarlo exige `install.sh` sobre HOME, que este paquete prohíbe explícitamente ("nunca leas ni escribas … los agentes instalados en HOME"). Mi cambio añade una línea más a esa lista de deriva (la plantilla del repo ahora difiere de la copia instalada, que es lo esperado hasta que el dueño redespliegue), pero **no cambia el veredicto** del sub-validador ni el conteo de asserts: `Assert PASS: 182 | Assert FAIL: 1` es idéntico al del RED. `validate-odoo-specialization.sh` → PASS.

## 4. Commit

```
fc1179b fix: 006-004 B-1 — la plantilla nace sin decisiones
 skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md | 8 ++++++--
 1 file changed, 6 insertions(+), 2 deletions(-)
```
Sin `--no-verify`, sin `git stash`, sin `push`. `git status` tras el commit: sólo `M docs/.cdad-state.json` (del orquestador, no mío) y los sin trackear de `docs/planning/` y `findings/` (no míos). **No toqué `tests/` ni `docs/`.**

## 5. Límites y honestidad

- **No edité tests** (invariante del rol); leí el RED y el oráculo de U4 sólo para implementar.
- **Alcance**: un archivo de `skills/`; nada fuera del write scope.
- **Suite completa**: no la corrí — la política del paquete la reserva a quien cierra la tarea.
- **Deuda declarada**: F011 sigue rojo por deriva de la copia instalada; su corrección (redespliegue con `install.sh`) es del dueño/orquestador, no de este rol.