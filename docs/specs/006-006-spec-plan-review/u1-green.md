GREEN complete. Here is the role report.

## Modified files

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | **only file touched** — the four zones of the U1 ficha: (1) closed contract key set + forge guard, (2) `prepare` flags/digest/all-or-none, (3) the plan-checks branch + diagnostic aid, (4) `inputs` construction + additive render. +167/−13. |

No test file, no doc, no `docs/.cdad-state.json` (the orchestrator's dispatch edit), no `docs/planning/`, no `findings/`, nothing in HOME.

## Test → result

| Test (focal) | PD | Before | After |
|---|---|---|---|
| `pd1_object_kind_is_carried_in_the_request_and_in_the_packet_metadata` | PD-1 | FALLA | **PASSED** |
| `pd1_object_kind_outside_the_closed_set_is_rejected_naming_the_value` | PD-1/R-3 | FALLA | **PASSED** |
| `pd1_the_contract_key_set_stays_closed` | PD-1/R-1 (control) | verde | **PASSED** |
| `pd1_an_approved_kind_declaring_object_kind_is_rejected_before_publishing` | PD-1/R-2, PD-15 g4 | FALLA | **PASSED** |
| `pd2_without_object_kind_a_draft_without_plan_tasks_is_still_rejected` | PD-2 (control) | verde | **PASSED** |
| `pd2_without_object_kind_a_malformed_plan_tasks_block_is_still_rejected` | PD-2 (control) | verde | **PASSED** |
| `pd2_the_render_without_the_new_keys_is_byte_identical_to_this_revision` | PD-2/PD-5/PD-16a (control) | verde | **PASSED** |
| `pd3_a_spec_without_plan_tasks_is_accepted_with_object_kind_spec` | PD-3 | FALLA | **PASSED** |
| `pd3_the_same_bytes_declared_plan_are_rejected_by_the_plan_tasks_gate` | PD-3 | FALLA | **PASSED** |
| `pd4_the_companion_identity_is_carried_in_the_contract` | PD-4/R-5/R-6 | FALLA | **PASSED** |
| `pd4_a_missing_companion_file_is_rejected_naming_the_path` | PD-4 | FALLA | **PASSED** |
| `pd4_the_companion_identity_is_all_or_none` | PD-4/R-6 | FALLA | **PASSED** |
| `pd4_a_companion_over_a_spec_principal_is_rejected` | PD-4/R-7/R-8 | FALLA | **PASSED** |
| `pd4_an_approved_kind_declaring_the_companion_is_rejected` | PD-4/R-2, PD-15 g4 | FALLA | **PASSED** |
| `pd5_inputs_carry_one_entry_per_fixed_document_in_order` | PD-5/R-9 | FALLA | **PASSED** |
| `pd5_the_render_names_the_form_and_the_companion_identity` | PD-5/R-9 | FALLA | **PASSED** |
| `pd5_the_published_package_carrying_the_new_keys_is_valid` | PD-5 | FALLA | **PASSED** |
| `pd5_the_installed_product_renders_the_declared_form_like_the_repo` | PD-5 + V-1 | FALLA | **PASSED** |
| `pd15_draft_plan_with_another_substage_is_rejected` | PD-15 g1 (control) | verde | **PASSED** |
| `pd15_plan_review_over_an_approved_kind_is_rejected` | PD-15 g2 (control) | verde | **PASSED** |
| `pd15_draft_plan_for_a_role_other_than_the_reviewer_is_rejected` | PD-15 g3 (control) | verde | **PASSED** |

Regressions of the ficha U1 (15 files): **124 passed** (same count as the RED baseline). Focal + regressions together: **145 passed**.

## Commands and output

```
$ python3 -m pytest -q tests/test_006_006_u1_draft_object_form.py
21 passed in 16.80s

$ python3 -m pytest -q <focal + the 15 regressions of the U1 ficha>
145 passed in 223.53s (0:03:43)

$ ruff check skills/cdad-cycle/scripts/cdad_packet.py
All checks passed!

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: 1 assert(s) failed.
make: *** [Makefile:22: validate] Error 1
```

**F011 (ambiental, declarado — preexistente, no introducido por esta unidad).** `FAIL: F011: scripts/validate-subagents.sh (active profile)`: el producto instalado en HOME está desfasado del repo (`.pyc` volátiles, dos agentes opencode sin staging, el reviewer instalado declarando `model`, 83 archivos fuente vs 88 instalados). Verificado de forma independiente con un árbol **pristine de HEAD** (`git archive HEAD` + `build/staging` copiado) → `install.sh --check` falla igual (rc=1). Los conteos son los del RED (168/1). No toqué la instalación de HOME (instrucción expresa), así que tampoco la reparé; el drift de `cdad_packet.py` es una línea más de una comparación que ya fallaba.

**Suite completa: no ejecutada** (política declarada en el paquete: la corre una sola vez quien cierra).

## Comportamiento implementado (decisiones dentro de la latitude de la spec)

- **R-1/R-2**: las cuatro claves nuevas son una extensión **aditiva** del conjunto cerrado; la forja se hace cumplir en **dos capas**: salida rápida en `prepare` (opción que no pertenece a la superficie draft) y punto de aplicación en `validate_request` (documento forjado → `prepare`, `render`, `validate-request`, `validate-packet`, `--resume-packet`).
- **R-3/R-4**: `_declared_object_form` centraliza el conjunto cerrado `spec|plan`; **ausente ⇒ `plan`** (fail-closed) en ambos caminos — la misma forma resuelta se usa en la puerta del acompañante, para que `prepare` y `validate_request` no puedan divergir.
- **R-5**: `prepare` **calcula** el digest del acompañante de los bytes; `validate_request` lo **verifica** contra el archivo (un digest afirmado que no coincide se rechaza nombrando la divergencia).
- **R-6/R-7/R-8**: todo-o-nada; el acompañante es la spec y sólo sobre principal de forma `plan`; la ruta ausente se nombra.
- **§2.2**: los checks del plan se aplican **sólo** al principal de forma `plan`; una spec se revisa sin tareas artificiales (no se inyecta `plan-tasks`).
- **Ayuda de diagnóstico (§2.2)**: cuando la puerta `plan-tasks` rechaza y la forma **no** fue declarada, el diagnóstico nombra `--object-kind spec`; el rechazo no cambia.
- **R-9**: render **aditivo** — `- form:` y la identidad del acompañante aparecen sólo cuando el contrato las declara; sin las claves nuevas los bloques `## Contract` y `## Inputs` conservan sus bytes exactos (garantía **intra-revisión**; entre revisiones el RED no afirma nada, PD-16a).
- Las tres banderas nuevas entran en los conjuntos de flags del modo ordinario (`--resume-packet`, `--propose-policy`, mezcla de modos): son opciones de `prepare` y no se aceptan en otros sub-modos.

## Commit

```
0a6e7fa feat: 006-006 U1 GREEN — objeto declarado en el contrato
 skills/cdad-cycle/scripts/cdad_packet.py | 180 ++++++++++++++++++++++++++++---
 1 file changed, 167 insertions(+), 13 deletions(-)
```

Sin `--no-verify`, sin `git stash`, sin `push`. Working tree tras el commit: sólo `M docs/.cdad-state.json` (despacho del orquestador, fuera de mi write scope) y los untracked que no son míos.