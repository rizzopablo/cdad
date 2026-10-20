GREEN de U3 completo. Informe de rol:

## Archivos modificados (write scope: `agents/`, `skills/`, `sources/`)

| Archivo | Acción | Qué aporta |
|---|---|---|
| `skills/cdad-cycle/references/design-principles.md` | **nuevo** (23 líneas) | La **casa canónica** única: sección «General before specific» con el texto del principio y su límite. Dueño canónico del texto normativo. |
| `skills/cdad-cycle/SKILL.md` | +1 línea | Fila de `design-principles.md` en la tabla «How to read the references». |
| `sources/roles/architect.md` | +5 líneas | **Obligación del architect** (alternativas generales y específicas + criterio elegido) + puntero al dueño canónico + prohibición de re-enunciar. |
| `sources/roles/reviewer.md` | +11 líneas | **Criterio del reviewer** (duplicación que puede divergir · complejidad innecesaria · pérdida de capacidades · acoplamiento) + **límite** («la falta de una abstracción, por sí sola, no es un defecto») + puntero; y el **deber sobre la tabla** con puntero a su procedimiento. |
| `skills/cdad-cycle/packets/roles/architect.md` | +1 línea | Bloque estático: obligación mínima + puntero (D-2: en la ruta de paquete el rol no carga el skill). |
| `skills/cdad-cycle/packets/roles/reviewer.md` | +1 línea | Bloque estático: límite + puntero + puntero al deber sobre la tabla. |
| `skills/cdad-cycle/references/stage-4-review.md` | +18 líneas | Sección canónica del **deber del reviewer sobre la tabla**: (a) alineación con `docs/adr/`, (b) respeto de las decisiones vigentes de su rol. |
| `agents/cdad-{architect,reviewer}[-odoo].md`, `agents/claude-code/cdad-{architect,reviewer}[-odoo].md` | +5/+11 cada uno | **Salidas declaradas** regeneradas con `make agents` (nunca editadas a mano). |

`tests/` **intacto**. `docs/.cdad-state.json` (orquestador), `docs/planning/` y `findings/` sin tocar ni commitear. La instalación de HOME no se leyó ni se escribió.

## Tabla test → resultado

| # | Test (focal) | PD | Resultado |
|---|---|---|---|
| 1 | `…CanonicalHouse::…canonical_file_exists_and_carries_the_principle_and_its_limit` | PD-10 | ✅ |
| 2 | `…::…normative_text…_in_exactly_one_installable_file` | PD-10/INV-1 | ✅ |
| 3 | `…::…no_installable_surface_copies_the_principle_text` (control neg.) | PD-10/INV-12 | ✅ |
| 4 | `…ArchitectDuty::…architect_source_names_its_duty_and_points_to_the_canonical_owner` | PD-10 | ✅ |
| 5 | `…::…architect_static_block_carries_the_duty_and_the_pointer` | PD-10/D-2 | ✅ |
| 6 | `…ReviewerCriterion::…reviewer_source_names_its_duty_and_points_to_the_canonical_owner` | PD-10 | ✅ |
| 7 | `…::…reviewer_static_block_carries_the_limit_and_the_pointer` | PD-10/D-2 | ✅ |
| 8 | `…::…reviewer_criterion_names_the_four_consequences_and_the_limit` | PD-10 | ✅ |
| 9 | `…ReviewerDutyOverTheTable::…alignment_check_against_docs_adr` | PD-8 | ✅ |
| 10 | `…::…respect_check_for_the_role_decisions` | PD-8 | ✅ |
| 11 | `…SkillReferenceRow::…skill_md_references_table_has_the_row_of_the_new_file` | PD-10 | ✅ |
| 12 | `…GeneratedAgents::…generated_agents_carry_the_duty_after_make_agents` | PD-13 | ✅ |
| 13 | `…::…promoted_agents_of_the_repo_carry_the_duty` | PD-13 | ✅ |
| 14 | `…::…make_staging_is_deterministic_across_two_runs` (control) | PD-13/V-2 | ✅ |
| 15 | `…StaticBlockCeiling::…static_block…is_under_the_ceiling` (control) | PD-13/V-4 | ✅ |

## Comandos y salida

```
$ python3 -m pytest tests/test_006_004_u3_principle_single_source.py -q
15 passed in 3.10s

$ python3 -m pytest tests/test_cdad_generate.py tests/test_role_packet_render.py \
    tests/test_role_packets.py tests/test_static_block_ceiling.py \
    tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t6_templates.py \
    tests/test_006_003_u3_texts_without_profiles.py tests/test_bash_policy_selection.py -q
53 passed in 217.88s (0:03:37)

$ make agents            # 12 files -> build/staging/... ; segunda corrida: sin diff pendiente
$ git status --short -- agents skills sources   # (vacío = sin diff pendiente)
```

**Unicidad de la casa (PD-10/INV-1) — `grep -rl` sobre `skills/ sources/ agents/`:**
```
$ grep -rl "it does not increase the justifications that agents" skills/ sources/ agents/
skills/cdad-cycle/references/design-principles.md
$ grep -rl "prefer the general one, and narrow it with a stated" skills/ sources/ agents/
skills/cdad-cycle/references/design-principles.md
```

**`make staging` determinista (V-2):** dos corridas (`--runtime opencode/claude-code --stack odoo`) → `diff -r` sin diferencias; digest agregado de ambos árboles idéntico (`abc4393f…`).

**Medición V-4 registrada** (14 pares rol/subfase, composición del producto `common.md` + `roles/<r>.md` + `substages/<r>-<s>.md`):
máx **3397 bytes** (`reviewer/plan-review`, antes 3033), mín **1311** (`scribe/memory`), techo declarado **12000** → holgura **8603**. Bajo el techo.

**`make validate`:**
- Con el HOME por defecto: `Assert PASS: 168 · Assert FAIL: 1` — el único fallo es **F011 ambiental** (`scripts/validate-subagents.sh` compara el repo contra la instalación de `$HOME`, que está desactualizada respecto de HEAD). **Es pre-existente**: `git archive HEAD` en un árbol descartable falla el mismo assert (168/1, idéntico).
- Con raíz de instalación **aislada** (`CDAD_INSTALL_ROOT=/tmp/opencode/u3-install-root`, `install.sh` + `install.sh --check` → `Check: PASS (405 artifact groups in sync)`, `validate-subagents.sh` → `== RESULT: PASS ==`, `make validate` → rc=0, 68/0): **verde**. La casa nueva viaja al árbol instalado (89 archivos de `cdad-cycle`).

## Commit

```
cbba5d1 feat: 006-004 U3 — principio con una casa y dos obligaciones
 15 files changed, 124 insertions(+)
 create mode 100644 skills/cdad-cycle/references/design-principles.md
```
Sin `--no-verify`, sin `git stash`, sin `push`.

## Límites y notas declaradas

1. **A-1**: no se reemplazó ningún oráculo vigente; no se tocó `tests/`. El bloque bash de `tests/validate-consistency.sh` que nombra la ficha U3 **no** se añadió: su autor es el RED de U3 y el plan asigna los bloques del validador a U4 (plantilla + procedimiento) y U7 (siembra) — queda a decisión del orquestador (ya declarado en `u3-red.md` §Desviaciones 1).
2. **Suite completa**: no ejecutada (política declarada en el paquete: la corre una vez quien cierra).
3. `docs/systemPatterns.md` y `docs/adr/ADR-034-*.md` (la siembra) **no** se tocaron: son de U5/U7, y el materializador es el orquestador, no el implementer.
4. El `deber del reviewer sobre la tabla` quedó escrito en las dos superficies que la ficha declara (fuente de rol + bloque estático), que **referencian** `references/stage-4-review.md` sin copiarlo (INV-9/INV-12).