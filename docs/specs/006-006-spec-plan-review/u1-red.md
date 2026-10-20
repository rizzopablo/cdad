RED de U1 completo y commiteado.

## Archivos modificados

| Archivo | Estado |
|---|---|
| `tests/test_006_006_u1_draft_object_form.py` | **NUEVO** (942 líneas) — único archivo commiteado |
| `docs/.cdad-state.json`, `docs/planning/`, `findings/*` | intactos (no míos, no tocados) |

No se editó nada fuera de `tests/`. No se leyó `skills/cdad-cycle/scripts/` (todo por CLI black-box: `--help`, `prepare`, `render`, `validate-packet`). No se leyó `tests/.sensitive-patterns.local`. Fixtures **propios** (`docs/drafts/006-006-u1-{spec,plan}-draft.md`); el fixture compartido `DRAFT_PLAN_RELPATH` y sus 11 archivos quedan sin tocar.

## Mapa test → postcondición (21 tests)

| Test | PD | Estado hoy |
|---|---|---|
| `pd1_object_kind_is_carried_in_the_request_and_in_the_packet_metadata` | PD-1 | FALLA |
| `pd1_object_kind_outside_the_closed_set_is_rejected_naming_the_value` | PD-1 (R-3) | FALLA |
| `pd1_the_contract_key_set_stays_closed` | PD-1 (R-1) | **control verde** |
| `pd1_an_approved_kind_declaring_object_kind_is_rejected_before_publishing` | PD-1 (R-2) + PD-15 guard 4 | FALLA |
| `pd2_without_object_kind_a_draft_without_plan_tasks_is_still_rejected` | PD-2 (control) | **control verde** |
| `pd2_without_object_kind_a_malformed_plan_tasks_block_is_still_rejected` | PD-2 (control) | **control verde** |
| `pd2_the_render_without_the_new_keys_is_byte_identical_to_this_revision` | PD-2 + PD-5 + **PD-16(a)** | **control verde** |
| `pd3_a_spec_without_plan_tasks_is_accepted_with_object_kind_spec` | PD-3 | FALLA |
| `pd3_the_same_bytes_declared_plan_are_rejected_by_the_plan_tasks_gate` | PD-3 | FALLA |
| `pd4_the_companion_identity_is_carried_in_the_contract` | PD-4 (R-5/R-6) | FALLA |
| `pd4_a_missing_companion_file_is_rejected_naming_the_path` | PD-4 | FALLA |
| `pd4_the_companion_identity_is_all_or_none` | PD-4 (R-6) | FALLA |
| `pd4_a_companion_over_a_spec_principal_is_rejected` | PD-4 (R-7/R-8) | FALLA |
| `pd4_an_approved_kind_declaring_the_companion_is_rejected` | PD-4 (R-2) + PD-15 guard 4 | FALLA |
| `pd5_inputs_carry_one_entry_per_fixed_document_in_order` | PD-5 (R-9) | FALLA |
| `pd5_the_render_names_the_form_and_the_companion_identity` | PD-5 (R-9) | FALLA |
| `pd5_the_published_package_carrying_the_new_keys_is_valid` | PD-5 | FALLA |
| `pd5_the_installed_product_renders_the_declared_form_like_the_repo` | PD-5 + V-1 (gate U1) | FALLA |
| `pd15_draft_plan_with_another_substage_is_rejected` | PD-15 guard 1 | **control verde** |
| `pd15_plan_review_over_an_approved_kind_is_rejected` | PD-15 guard 2 | **control verde** |
| `pd15_draft_plan_for_a_role_other_than_the_reviewer_is_rejected` | PD-15 guard 3 | **control verde** |

**14 fallan (comportamiento nuevo ausente) · 7 verdes son controles negativos declarados** (pasan hoy y deben seguir pasando). Ningún oráculo vigente fue reemplazado (A-1: ninguno) — el oráculo de `test_004_003_t4_validation_fields.py:427` se re-comprueba con fixtures propios, sin reescribirlo.

## Comandos y salida resumida

```
$ python3 -m pytest -q tests/test_006_006_u1_draft_object_form.py
14 failed, 7 passed in 13.51s
```
Las 14 son `AssertionError` sobre comportamiento ausente (p.ej. `2 != 0 : prepare failed: ERROR: cdad_packet.py: unrecognized arguments: --object-kind spec`); **ninguna** es ImportError/sintaxis. El helper `assert_rejected` rechaza explícitamente un stderr con `unrecognized arguments`: un error de uso no es un rechazo de comportamiento, así que el RED no puede pasar en falso por un flag desconocido.

```
$ python3 -m pytest -q <las 15 regresiones de la ficha U1>
124 passed in 178.70s
```

```
$ make validate
Assert PASS: 168 | Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile)
```
**Fallo preexistente y ajeno a esta unidad** (el RED no lo introduce): el producto instalado en `~/.config/opencode` y `~/.claude` está desfasado del repo (`.pyc` volátiles, dos agentes opencode sin staging, y el reviewer instalado declarando `model`). Verificado moviendo mi archivo fuera del repo y reejecutando: **salida idéntica**. `install.sh` no instala `tests/`, luego mi archivo no puede causarlo. Se declara al orquestador.

```
$ ruff check tests/test_006_006_u1_draft_object_form.py
All checks passed!
```

## Decisiones de oráculo que conviene auditar

- **Byte-identidad intra-revisión (PD-2/PD-5/PD-16a)**: se mide sobre los **dos bloques aditivos** (`## Contract` y `## Inputs`) contra los bytes del HEAD calculados desde mi propio fixture. El `PACKET.md` completo **no** se congela: embebe las fuentes de instrucción y sus digests, que cambian legítimamente entre revisiones (R-10) — congelarlos rompería U2/U3/U4. El RED **no afirma nada entre revisiones**.
- **F Digest = `sha256sum`**: el digest del acompañante se compara con `hashlib.sha256(bytes)` **y** con la salida real de `sha256sum` sobre el archivo.
- **Forja (PD-1/PD-4)**: se exige `rc≠0` + `ERROR:` + out-dir vacío + state byte-idéntico (lo que la spec证据 pide), **sin** exigir el texto exacto del diagnóstico: el producto puede nombrar la clave ofensora o la exigencia del trío `--contract-kind/--contract-path/--plan-version`, y el contrato no fija ese literal. En cambio, donde la spec **sí** exige nombrar (valor fuera del conjunto, ruta ausente, clave ausente) el test lo exige con regex tolerante (`spec[-_]version`).
- **R-9 literal**: el render debe emitir `- form: spec` / `- form: plan` (literal de la spec aprobada); las tres identidades del acompañante se exigen por **valor** (ruta, digest, versión) en la sección `## Contract`, no por nombre de clave.
- **V-1**: incluido el caso de la installed product (patrón `test_004_003_t2_plan_review.py`:290) porque la ficha U1 lo exige en su Gate.

## Commit

```
20cfbda236a121a9c626fe4bc642cd7c2bd825d6
test: 006-006 U1 RED — objeto declarado en el contrato
 tests/test_006_006_u1_draft_object_form.py | 942 +++++++++++++++++++++++++++++
 1 file changed, 942 insertions(+)
```
Sin `--no-verify`, sin `git stash`, sin `push`. No se ejecutó la suite completa (la corre una sola vez quien cierra).